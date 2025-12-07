from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.config import Settings
from app.services.ocr_service import OcrService, get_ocr_service
from app.services.groq_service import GroqService, get_groq_service
from app.services.scan_service import ScanService
from app.services.image_service import ImagePreprocessor


@lru_cache
def get_settings() -> Settings:
  return Settings()


def get_ocr(  # Dependency for routes
  settings: Annotated[Settings, Depends(get_settings)]
) -> OcrService:
  return get_ocr_service(settings)


def get_groq(
  settings: Annotated[Settings, Depends(get_settings)]
) -> GroqService:
  return get_groq_service(settings)


def get_scan(
  settings: Annotated[Settings, Depends(get_settings)],
  ocr: Annotated[OcrService, Depends(get_ocr)],
  groq: Annotated[GroqService, Depends(get_groq)],
) -> ScanService:
  return ScanService(settings=settings, ocr_service=ocr, groq_service=groq, preprocessor=ImagePreprocessor())
