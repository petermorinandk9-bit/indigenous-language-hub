import re
import sqlite3
from pathlib import Path

RAW = Path("williams_raw.txt")
DB = Path("narragansett_dictionary.db")

PAIR = re.compile(
    r"^([A-Za-z][A-Za-z\-']{1,40})\s{2,}(.+)$"
)
COMMA = re.compile(
    r"^([A-Za-z][A-Za-z\-']{1,40}),\s+(.{3,120})$"
)
SKIP = re.compile(
    r"(roger williams|key into the language|chapter|observation|"
    r"printed by|new-england|gutenberg)",
    re.I,
)


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\u2014", "-")).strip(" \t.;")


def main():
    staged, seen = [], set()
    started = False
    for raw in RAW.read_text(encoding="utf-8", errors="replace").splitlines():
        line = clean(raw)
        if re.search(r"of salutation|netop|cowwewonck|what cheare", line, re.I):
            started = True
        if not started or not line or SKIP.search(line):
            continue
        m = PAIR.match(line) or COMMA.match(line)
        if not m:
            continue
        word, gloss = clean(m.group(1)), clean(m.group(2))
        if word.lower() in {"the", "and", "chapter", "observation"}:
            continue
        if len(gloss) < 3:
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
            narragansett_word TEXT NOT NULL,
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
            (narragansett_word, english_translation, source, license, orthography)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                word,
                gloss,
                "Roger Williams, A Key into the Language of America, 1643",
                "public-domain",
                "Historical Narragansett",
            ),
        )
    conn.commit()
    print(f"Wrote {len(staged)} rows -> {DB.resolve()}")
    for row in conn.execute(
        "SELECT narragansett_word, english_translation FROM dictionary LIMIT 10"
    ):
        print(" ", row[0], "-", row[1][:90])
    conn.close()


if __name__ == "__main__":
    main()