import io
import uuid
from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw


def save_annotated_image(
  image_bytes: bytes, boxes: List[list], texts: List[str], output_dir: str
) -> Tuple[str, int, int]:
  """
  Render OCR boxes with indices and snippets, save to disk, and return (path, width, height).
  """
  output_path = Path(output_dir)
  output_path.mkdir(parents=True, exist_ok=True)

  image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
  draw = ImageDraw.Draw(image)

  for idx, box in enumerate(boxes):
    points = [(float(p[0]), float(p[1])) for p in box]
    color = "red"
    draw.line(points + [points[0]], fill=color, width=3)

    label = f"{idx + 1}: {texts[idx][:30]}" if idx < len(texts) else f"{idx + 1}"
    text_anchor = (points[0][0], max(points[0][1] - 12, 0))
    draw.rectangle(
      [
        text_anchor,
        (text_anchor[0] + 6 + len(label) * 6, text_anchor[1] + 14),
      ],
      fill="black",
    )
    draw.text(text_anchor, label, fill="yellow")

  filename = output_path / f"annotated_{uuid.uuid4().hex}.jpg"
  image.save(filename, format="JPEG", quality=85, optimize=True)

  width, height = image.size
  return str(filename), width, height
