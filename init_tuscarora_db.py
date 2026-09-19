import re
import sqlite3
from pathlib import Path

RAW = Path("schoolcraft_raw.txt")
DB = Path("tuscarora_dictionary.db")

START = re.compile(r"vocabul\w* of the tusca|tuscarora\.\s*$|1\s+god", re.I)
STOP = re.compile(
    r"(letter from rev|asher bliss|mohawk|cayuga|oneida|onondaga|seneca vocabulary)",
    re.I,
)
LINE = re.compile(
    r"^\s*\d+\s+([A-Za-z][A-Za-z \-'()]{1,50}?)\s{1,}([A-Za-z].{1,80})$"
)


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\u2014", "-")).strip(" \t.;")


def main():
    started = False
    staged, seen = [], set()
    for raw in RAW.read_text(encoding="utf-8", errors="replace").splitlines():
        line = clean(raw)
        if not started and START.search(line):
            started = True
        if not started:
            continue
        if STOP.search(line) and staged:
            break
        m = LINE.match(line)
        if not m:
            continue
        english, tus = clean(m.group(1)), clean(m.group(2))
        if english.lower() in {"the", "and", "note"}:
            continue
        if len(tus) < 2:
            continue
        key = (tus.lower(), english.lower())
        if key in seen:
            continue
        seen.add(key)
        staged.append((tus, english))

    conn = sqlite3.connect(DB)
    conn.execute("DROP TABLE IF EXISTS dictionary")
    conn.execute(
        """
        CREATE TABLE dictionary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tuscarora_word TEXT NOT NULL,
            english_translation TEXT NOT NULL,
            word_class TEXT,
            source TEXT,
            license TEXT,
            orthography TEXT,
            notes TEXT,
            audio_url TEXT
        )
        """
    )
    for tus, english in staged:
        conn.execute(
            """
            INSERT INTO dictionary
            (tuscarora_word, english_translation, source, license, orthography)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                tus,
                english,
                "William Chew / Gilbert Rockwood vocabulary in Schoolcraft, Notes on the Iroquois (1846)",
                "public-domain",
                "Historical Tuscarora",
            ),
        )
    conn.commit()
    print(f"Wrote {len(staged)} rows -> {DB.resolve()}")
    for row in conn.execute(
        "SELECT tuscarora_word, english_translation FROM dictionary LIMIT 12"
    ):
        print(" ", row[0], "-", row[1])
    conn.close()


if __name__ == "__main__":
    main()