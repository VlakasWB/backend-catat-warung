from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import health, ocr, scan
from app.core.config import Settings
from app.api.deps import get_settings


def create_app() -> FastAPI:
  settings: Settings = get_settings()
  app = FastAPI(title=settings.app_name, version="0.1.0")

  app.include_router(health.router)
  app.include_router(ocr.router)
  app.include_router(scan.router)

  # Serve annotated OCR images (if generated) under /output
  app.mount("/output", StaticFiles(directory=settings.output_dir), name="output")

  return app


app = create_app()
