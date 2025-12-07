from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.api.deps import get_ocr
from app.services.ocr_service import OcrService

router = APIRouter()


@router.post("/ocr")
async def run_ocr(
  image: UploadFile = File(...),
  ocr_service: OcrService = Depends(get_ocr),
):
  if not image.content_type or not image.content_type.startswith("image/"):
    raise HTTPException(status_code=400, detail="File harus bertipe gambar.")

  content = await image.read()
  if not content:
    raise HTTPException(status_code=400, detail="File kosong.")

  result = ocr_service.extract(content)
  return result
