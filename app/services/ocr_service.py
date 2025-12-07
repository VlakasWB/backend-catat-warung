import io
from typing import List

from paddleocr import PaddleOCR

from app.domain.models import OcrResult
from app.core.config import Settings


class OcrService:
  """
  Thin wrapper around PaddleOCR so it can be injected and mocked in handlers.
  """

  @staticmethod
  def _normalize_version(version: str) -> str:
    # PaddleOCR only accepts PP-OCR/PP-OCRv2/PP-OCRv3/PP-OCRv4; strip legacy `_mobile` suffix.
    return (version or "").removesuffix("_mobile")

  def __init__(self, settings: Settings) -> None:
    version = self._normalize_version(settings.ocr_version)
    try:
      self._ocr = PaddleOCR(
        use_angle_cls=settings.ocr_use_angle_cls,
        lang=settings.ocr_lang,
        ocr_version=version,
      )
    except AssertionError as exc:
      raise RuntimeError(
        f"OCR_VERSION tidak valid: '{settings.ocr_version}'. "
        "Gunakan salah satu: PP-OCR, PP-OCRv2, PP-OCRv3, PP-OCRv4."
      ) from exc

  def extract(self, image_bytes: bytes) -> OcrResult:
    result: List = self._ocr.ocr(image_bytes, cls=True)

    lines: List[str] = []
    boxes: List[list] = []
    scores: List[float] = []

    for block in result:
      for box, (text, score) in block:
        lines.append(text)
        boxes.append(box)
        scores.append(score)

    return OcrResult(lines=lines, boxes=boxes, scores=scores)


def get_ocr_service(settings: Settings) -> OcrService:
  return OcrService(settings)
