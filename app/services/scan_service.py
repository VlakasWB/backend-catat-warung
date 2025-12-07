import logging
from typing import List

from app.core.config import Settings
from app.domain.models import Detection, ParsedRow, ScanResult
from app.services.groq_service import GroqService
from app.services.image_service import ImagePreprocessor
from app.services.ocr_service import OcrService
from app.services.parsing_service import parse_lines_rule_based
from app.services.visualization import save_annotated_image

logger = logging.getLogger(__name__)


class ScanService:
  """
  Orchestrates preprocessing, OCR, rule-based parsing, and Groq fallback.
  """

  def __init__(
    self,
    settings: Settings,
    ocr_service: OcrService,
    groq_service: GroqService,
    preprocessor: ImagePreprocessor | None = None,
  ) -> None:
    self._settings = settings
    self._ocr = ocr_service
    self._groq = groq_service
    self._preprocessor = preprocessor or ImagePreprocessor()
    self._output_dir = settings.output_dir

  async def run_scan(
    self, image_bytes: bytes, mime: str | None = None, needs_llm: bool = False
  ) -> ScanResult:
    processed = self._preprocessor.preprocess(image_bytes)
    ocr_result = self._ocr.extract(processed)

    detections = self._build_detections(ocr_result.lines, ocr_result.boxes, ocr_result.scores)
    annotated_path = None
    image_width = None
    image_height = None
    try:
      annotated_path, image_width, image_height = save_annotated_image(
        processed, ocr_result.boxes, ocr_result.lines, self._output_dir
      )
    except Exception as exc:
      logger.warning("Gagal membuat gambar anotasi OCR: %s", exc)

    rule_based = parse_lines_rule_based(ocr_result.lines)
    use_llm = needs_llm or len(rule_based) == 0 or self._should_use_llm(ocr_result.lines)

    llm_rows: List[ParsedRow] = []
    if use_llm:
      try:
        llm_rows = await self._groq.normalize(ocr_result.lines)
      except Exception as exc:
        logger.warning("Groq normalize failed, fallback to rule-based: %s", exc)

    merged = llm_rows if llm_rows else rule_based
    final_rows: List[ParsedRow] = []
    for row in merged:
      source = "groq" if llm_rows else (row.source or "rule")
      final_rows.append(row.copy(update={"source": source}))

    return ScanResult(
      lines=ocr_result.lines,
      parsed=final_rows,
      used_llm=len(llm_rows) > 0,
      detections=detections,
      annotated_image_path=annotated_path,
      image_width=image_width,
      image_height=image_height,
    )

  @staticmethod
  def _should_use_llm(lines: List[str]) -> bool:
    """
    Trigger LLM when many currency-like tokens are present to improve normalization.
    """
    currency_hits = 0
    for line in lines:
      if "rp" in line.lower():
        currency_hits += 1
      if any(token.isdigit() and len(token) >= 5 for token in line.replace(".", " ").split()):
        currency_hits += 1
    return currency_hits >= 2

  @staticmethod
  def _build_detections(lines: List[str], boxes: List[list], scores: List[float]) -> List[Detection]:
    detections: List[Detection] = []
    for idx, (line, box, score) in enumerate(zip(lines, boxes, scores)):
      detections.append(Detection(index=idx, text=line, score=score, box=box))
    return detections
