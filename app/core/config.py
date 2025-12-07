from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
  app_name: str = Field("Catat Warung API", env="APP_NAME")
  host: str = Field("0.0.0.0", env="HOST")
  port: int = Field(8000, env="PORT")
  # PaddleOCR: use "latin" so angka + teks Indonesia lebih stabil
  ocr_lang: str = Field("latin", env="OCR_LANG")
  ocr_use_angle_cls: bool = Field(True, env="OCR_USE_ANGLE_CLS")
  ocr_version: str = Field("PP-OCRv4", env="OCR_VERSION")
  output_dir: str = Field("output", env="OUTPUT_DIR")
  groq_api_key: str = Field("", env="GROQ_API_KEY")
  groq_model: str = Field("llama-3.1-8b-instant", env="GROQ_MODEL")
  groq_fallback_model: str = Field("mixtral-8x7b-32768", env="GROQ_FALLBACK_MODEL")
  groq_enable_fallback: bool = Field(True, env="GROQ_ENABLE_FALLBACK")
  groq_url: str = Field("https://api.groq.com/openai/v1/chat/completions", env="GROQ_URL")

  class Config:
    env_file = ".env"
