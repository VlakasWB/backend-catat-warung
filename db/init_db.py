import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "data.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS Transaction (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL,
  item TEXT NOT NULL,
  qty REAL NOT NULL,
  unit TEXT,
  price REAL,
  total REAL,
  type TEXT,
  phone TEXT DEFAULT ''
);
"""


def ensure_phone_column(conn: sqlite3.Connection) -> None:
  # Add phone column if the table already existed without it.
  cur = conn.execute("PRAGMA table_info(Transaction)")
  columns = {row[1] for row in cur.fetchall()}
  if "phone" not in columns:
    conn.execute("ALTER TABLE Transaction ADD COLUMN phone TEXT DEFAULT ''")


def main():
  DB_PATH.parent.mkdir(parents=True, exist_ok=True)
  conn = sqlite3.connect(DB_PATH)
  try:
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute(CREATE_TABLE_SQL)
    ensure_phone_column(conn)
    conn.commit()
    print(f"Database ready at {DB_PATH}")
  finally:
    conn.close()


if __name__ == "__main__":
  main()
