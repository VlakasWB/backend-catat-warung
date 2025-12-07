from pydantic import BaseModel
from typing import List, Optional


class OcrResult(BaseModel):
  lines: List[str]
  boxes: List[list]
  scores: List[float]


class ParsedRow(BaseModel):
  date: str
  item: str
  qty: float
  unit: Optional[str] = None
  price: Optional[float] = None
  total: Optional[float] = None
  type: Optional[str] = None
  confidence: Optional[float] = None
  source: Optional[str] = None


class Detection(BaseModel):
  index: int
  text: str
  score: float
  box: list


class ScanResult(BaseModel):
  lines: List[str]
  parsed: List[ParsedRow]
  used_llm: bool
  detections: List[Detection] = []
  annotated_image_path: Optional[str] = None
  image_width: Optional[int] = None
  image_height: Optional[int] = None
