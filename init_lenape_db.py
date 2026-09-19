import re
import sqlite3
from pathlib import Path

RAW = Path("brinton_raw.txt")
DB = Path("lenape_dictionary.db")

HEAD = re.compile(r"^([A-Z][A-Za-z\-']{1,40}),\s+(.{3,160})$")
SKIP = re.compile(
    r"(historical society|philadelphia|preface|moravian|brinton|"
    r"lenape-english dictionary|press of)",
    re.I,
)


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\u2014", "-")).strip(" \t.;")


def main():
    if not RAW.exists():
        raise SystemExit("Run fetch_brinton.py first")
    started = False
    staged = []
    seen = set()
    for raw in RAW.read_text(encoding="utf-8", errors="replace").splitlines():
        line = clean(raw)
        if re.search(r"LENAPE.?ENGLISH", line, re.I):
            started = True
            continue
        if not started or not line or SKIP.search(line):
            continue
        if re.match(r"^[A-Z]$", line):
            continue
        m = HEAD.match(line)
        if not m:
            continue
        word, gloss = clean(m.group(1)), clean(m.group(2))
        if word.lower() in {"the", "and", "from"}:
            continue
        key = (word.lower(), gloss.lower())
        if key in seen:
            continue
        seen.add(key)
        staged.append((word, gloss))

    conn = sqlite3.connect(DB)
    conn.execute("DROP TABLE IF EXISTS dictionary")
    conn.execute(
        """
        CREATE TABLE dictionary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lenape_word TEXT NOT NULL,
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
    for word, gloss in staged:
        conn.execute(
            """
            INSERT INTO dictionary
            (lenape_word, english_translation, source, license, orthography)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                word,
                gloss,
                "Brinton & Anthony, Lenape-English Dictionary, 1888",
                "public-domain",
                "Historical Unami / Moravian",
            ),
        )
    conn.commit()
    print(f"Wrote {len(staged)} rows -> {DB.resolve()}")
    for row in conn.execute("SELECT lenape_word, english_translation FROM dictionary LIMIT 10"):
        print(" ", row[0], "-", row[1])
    conn.close()


if __name__ == "__main__":
    main()