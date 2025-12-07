import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.api.deps import get_scan
from app.services.scan_service import ScanService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/scan")
async def scan(
  image: UploadFile = File(...),
  needs_llm: bool = Form(False),
  scan_service: ScanService = Depends(get_scan),
):
  if not image.content_type or not image.content_type.startswith("image/"):
    raise HTTPException(status_code=400, detail="File harus bertipe gambar.")

  content = await image.read()
  if not content:
    raise HTTPException(status_code=400, detail="File kosong.")

  try:
    result = await scan_service.run_scan(content, mime=image.content_type, needs_llm=needs_llm)
    return result
  except HTTPException:
    raise
  except Exception as exc:
    logger.exception("Scan gagal diproses")
    message = str(exc) or exc.__class__.__name__
    raise HTTPException(status_code=500, detail=message)
