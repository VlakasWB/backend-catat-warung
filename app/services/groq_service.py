import json
import logging
from typing import List

import httpx

from app.core.config import Settings
from app.domain.models import ParsedRow

logger = logging.getLogger(__name__)


class GroqService:
  """
  Thin async client for Groq chat completions.
  """

  def __init__(self, settings: Settings) -> None:
    self._api_key = settings.groq_api_key
    self._model = settings.groq_model
    self._fallback_model = settings.groq_fallback_model
    self._enable_fallback = settings.groq_enable_fallback
    self._url = settings.groq_url.rstrip("/")

  @staticmethod
  def _build_prompt(lines: List[str]) -> str:
    joined = "\n".join(lines)
    return (
      "Kamu adalah sistem yang menormalkan hasil OCR catatan warung.\n"
      "Output harus JSON VALID tanpa teks lain.\n"
      "Format:\n"
      '[\n  {"date":"YYYY-MM-DD","item":"nama","qty":number,"unit":"pcs","price":number,"total":number,"type":"penjualan|pengeluaran"}\n'
      "]\n\n"
      "Gunakan Bahasa Indonesia. Isi field kosong dengan null jika tidak ada. "
      "Gunakan date dari teks jika ada, atau pakai tanggal hari ini jika tidak ditemukan.\n"
      f"Teks OCR:\n{joined}"
    )

  async def _call_model(self, model: str, lines: List[str]) -> List[ParsedRow]:
    payload = {
      "model": model,
      "messages": [
        {"role": "system", "content": "Keluarkan JSON valid saja tanpa penjelasan."},
        {"role": "user", "content": self._build_prompt(lines)},
      ],
      "temperature": 0.1,
      "response_format": {"type": "json_object"},
    }

    headers = {
      "Authorization": f"Bearer {self._api_key}",
      "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30) as client:
      response = await client.post(self._url, json=payload, headers=headers)

    if response.status_code >= 300:
      raise RuntimeError(f"Groq error: {response.status_code} {response.text}")

    data = response.json()
    content = (
      data.get("choices", [{}])[0]
      .get("message", {})
      .get("content", "")
      .strip()
    )

    try:
      parsed = json.loads(content)
      if isinstance(parsed, list):
        return [ParsedRow(**row) for row in parsed]
      if isinstance(parsed, dict) and isinstance(parsed.get("items"), list):
        return [ParsedRow(**row) for row in parsed["items"]]
    except Exception as exc:
      logger.warning("Failed to parse Groq response: %s", exc)

    return []

  async def normalize(self, lines: List[str]) -> List[ParsedRow]:
    if not self._api_key:
      raise RuntimeError("GROQ_API_KEY belum di-set.")

    primary_model = self._model or "llama-3.1-8b-instant"
    try:
      return await self._call_model(primary_model, lines)
    except Exception as exc:
      logger.warning("Groq primary model failed (%s): %s", primary_model, exc)
      if self._enable_fallback and self._fallback_model:
        try:
          return await self._call_model(self._fallback_model, lines)
        except Exception as fallback_exc:
          logger.warning("Groq fallback model failed (%s): %s", self._fallback_model, fallback_exc)
      raise


def get_groq_service(settings: Settings) -> GroqService:
  return GroqService(settings)
