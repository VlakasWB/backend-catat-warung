import re
from typing import List, Optional

from app.domain.models import ParsedRow

date_regexes = [
  re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b"),
  re.compile(r"\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b"),
]


def _parse_date(line: str) -> Optional[str]:
  for pattern in date_regexes:
    match = pattern.search(line)
    if match:
      raw = match.group(1)
      tokens = re.sub(r"\s+", "", raw).split("/")
      if len(tokens) == 1:
        tokens = raw.replace(" ", "").split("-")
      if len(tokens) == 3:
        first = tokens[0]
        if len(first) == 4:
          return raw
        d, m, y = tokens
        year = f"20{y}" if len(y) == 2 else y
        return f"{year}-{m.zfill(2)}-{d.zfill(2)}"
  return None


def _parse_number(token: str) -> Optional[float]:
  cleaned = re.sub(r"[^\d.,-]", "", token).replace(",", ".")
  try:
    value = float(cleaned)
  except ValueError:
    return None
  return value


def _parse_line(line: str, detected_date: Optional[str]) -> Optional[ParsedRow]:
  tokens = [t for t in re.split(r"\s+", line) if t]
  if not tokens:
    return None

  price = None
  for idx in range(len(tokens) - 1, -1, -1):
    num = _parse_number(tokens[idx])
    if num is not None:
      price = num
      tokens.pop(idx)
      break

  qty = None
  for idx in range(len(tokens) - 1, -1, -1):
    num = _parse_number(tokens[idx])
    if num is not None:
      qty = num
      tokens.pop(idx)
      break

  if price is None and qty is None:
    return None

  item = " ".join(tokens).strip()
  if not item:
    return None

  total = None
  if qty is not None and price is not None:
    total = round(qty * price)
  elif price is not None:
    total = price

  return ParsedRow(
    date=detected_date or "",
    item=item,
    qty=qty or 1,
    unit="pcs",
    price=price,
    total=total,
    type="penjualan",
    source="rule",
  )


def parse_lines_rule_based(lines: List[str]) -> List[ParsedRow]:
  detected_date = None
  for line in lines:
    detected = _parse_date(line)
    if detected:
      detected_date = detected
      break

  rows: List[ParsedRow] = []
  for line in lines:
    parsed = _parse_line(line, detected_date)
    if parsed:
      rows.append(parsed)

  if not rows and detected_date:
    rows.append(
      ParsedRow(
        date=detected_date,
        item="Tanggal",
        qty=1,
        unit="",
        price=None,
        total=None,
        type="meta",
        source="rule",
      )
    )

  return rows
