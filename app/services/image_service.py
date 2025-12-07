import io
from typing import Optional

from PIL import Image


class ImagePreprocessor:
  """
  Basic image resizing and JPEG conversion to stabilize OCR input.
  """

  def __init__(self, max_width: int = 1280, quality: int = 85) -> None:
    self.max_width = max_width
    self.quality = quality

  def preprocess(self, image_bytes: bytes) -> bytes:
    stream = io.BytesIO(image_bytes)
    image = Image.open(stream)
    image = image.convert("RGB")

    width, height = image.size
    if width and width > self.max_width:
      ratio = self.max_width / float(width)
      new_height = int(height * ratio)
      image = image.resize((self.max_width, new_height))

    output = io.BytesIO()
    image.save(output, format="JPEG", quality=self.quality, optimize=True)
    return output.getvalue()
