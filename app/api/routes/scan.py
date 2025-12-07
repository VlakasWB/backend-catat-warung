import logging
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.api.deps import get_scan, get_settings
from app.core.config import Settings
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


def _gather_outputs(settings: Settings):
  out_dir = Path(settings.output_dir)
  files = []
  if out_dir.exists():
    for path in out_dir.iterdir():
      if path.is_file():
        stat = path.stat()
        files.append(
          {
            "name": path.name,
            "url": f"/output/{path.name}",
            "size_bytes": stat.st_size,
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
          }
        )

  files.sort(key=lambda x: x["modified_at"], reverse=True)
  return {"count": len(files), "files": files}


@router.get("/scan/outputs")
async def list_outputs(settings: Settings = Depends(get_settings)):
  return _gather_outputs(settings)


@router.get("/outputs")
async def list_outputs_root(settings: Settings = Depends(get_settings)):
  return _gather_outputs(settings)


@router.get("/api/outputs")
async def list_outputs_api(settings: Settings = Depends(get_settings)):
  return _gather_outputs(settings)
