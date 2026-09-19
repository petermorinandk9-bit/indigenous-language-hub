import re
import sqlite3
from pathlib import Path

RAW = Path("loughridge_raw.txt")
DB = Path("creek_dictionary.db")

LINE = re.compile(r"^([A-Za-z][A-Za-z \-']{1,40}),\s+([A-Za-z].{1,80})$")
SKIP = re.compile(
    r"(loughridge|muskokee dictionary|preface|alphabet|westminster|indian territory)",
    re.I,
)


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\u2014", "-")).strip(" \t.;")


def main():
    staged, seen = [], set()
    started = False
    for raw in RAW.read_text(encoding="utf-8", errors="replace").splitlines():
        line = clean(raw)
        if re.search(r"english and muskokee|abase|abdomen", line, re.I):
            started = True
        if not started or not line or SKIP.search(line):
            continue
        m = LINE.match(line)
        if not m:
            continue
        english, creek = clean(m.group(1)), clean(m.group(2))
        if english.lower() in {"the", "and", "dictionary"}:
            continue
        if len(creek.split()) > 8:
            continue
        key = (creek.lower(), english.lower())
        if key in seen:
            continue
        seen.add(key)
        staged.append((creek, english))

    conn = sqlite3.connect(DB)
    conn.execute("DROP TABLE IF EXISTS dictionary")
    conn.execute(
        """
        CREATE TABLE dictionary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creek_word TEXT NOT NULL,
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
    for creek, english in staged:
        conn.execute(
            """
            INSERT INTO dictionary
            (creek_word, english_translation, source, license, orthography)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                creek,
                english,
                "Loughridge & Hodge, English and Muskokee Dictionary, 1890",
                "public-domain",
                "Historical Mvskoke",
            ),
        )
    conn.commit()
    print(f"Wrote {len(staged)} rows -> {DB.resolve()}")
    for row in conn.execute("SELECT creek_word, english_translation FROM dictionary LIMIT 10"):
        print(" ", row[0], "-", row[1])
    conn.close()


if __name__ == "__main__":
    main()