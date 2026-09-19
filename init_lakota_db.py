#!/usr/bin/env python3
"""Build / migrate lakota_dictionary.db from licensed CSVs."""

import argparse
import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "lakota_dictionary.db"
SEED = ROOT / "lakota_seed.csv"

SCHEMA = """
CREATE TABLE IF NOT EXISTS dictionary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lakota_word TEXT NOT NULL,
    english_translation TEXT NOT NULL,
    word_class TEXT,
    source TEXT,
    license TEXT,
    orthography TEXT DEFAULT 'SLO',
    notes TEXT,
    audio_url TEXT
);
CREATE INDEX IF NOT EXISTS idx_lakota_word ON dictionary(lakota_word);
CREATE INDEX IF NOT EXISTS idx_english ON dictionary(english_translation);
"""

NEEDED_COLS = {
    "lakota_word": "TEXT",
    "english_translation": "TEXT",
    "word_class": "TEXT",
    "source": "TEXT",
    "license": "TEXT",
    "orthography": "TEXT",
    "notes": "TEXT",
    "audio_url": "TEXT",
}


def migrate(conn):
    conn.executescript(SCHEMA)
    existing = {row[1] for row in conn.execute("PRAGMA table_info(dictionary)")}
    for col, typ in NEEDED_COLS.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE dictionary ADD COLUMN {col} {typ}")
            print(f"Added column: {col}")
    conn.commit()


def load_csv(conn, path: Path) -> int:
    inserted = 0
    with path.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"lakota_word", "english_translation", "source", "license"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"{path.name} missing columns: {missing}")
        for row in reader:
            word = (row.get("lakota_word") or "").strip()
            eng = (row.get("english_translation") or "").strip()
            if not word or not eng:
                continue
            conn.execute(
                """
                INSERT INTO dictionary
                (lakota_word, english_translation, word_class, source, license,
                 orthography, notes, audio_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    word,
                    eng,
                    (row.get("word_class") or "").strip(),
                    row["source"].strip(),
                    row["license"].strip(),
                    (row.get("orthography") or "SLO").strip(),
                    (row.get("notes") or "").strip(),
                    (row.get("audio_url") or "").strip(),
                ),
            )
            inserted += 1
    return inserted


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db", default=str(DB_PATH))
    p.add_argument("--csv", action="append", default=[])
    p.add_argument("--reset", action="store_true", help="drop and rebuild table")
    args = p.parse_args()

    conn = sqlite3.connect(args.db)
    if args.reset:
        conn.execute("DROP TABLE IF EXISTS dictionary")
        print("Dropped old dictionary table")
    migrate(conn)

    paths = [Path(c) for c in args.csv] or [SEED]
    total = 0
    for path in paths:
        n = load_csv(conn, path)
        total += n
        print(f"Loaded {n} rows from {path.name}")

    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM dictionary").fetchone()[0]
    print(f"Database {args.db}: {count} rows now ({total} inserted this run)")
    conn.close()


if __name__ == "__main__":
    main()