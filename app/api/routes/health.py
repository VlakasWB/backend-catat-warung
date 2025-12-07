from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
  return {"ok": True, "service": "catat-warung-api"}


@router.get("/ocr/health")
async def ocr_health():
  # keep backward compatibility with previous OCR-only service path
  return {"ok": True, "service": "catat-warung-api"}
