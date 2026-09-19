import re
import sqlite3
from pathlib import Path

RAW = Path("baraga_raw.txt")
DB = Path("baraga_dictionary.db")

HEAD = re.compile(
    r"^([A-Za-z][A-Za-z\-']{1,40}),\s+"
    r"(s\.|n\.|v\.|a\.|adv\.|prep\.|pron\.|int\.|num\.|part\.)\s*(.*)$",
    re.I,
)
SKIP = re.compile(
    r"(baraga|otchipwe language|montreal|cincinnat|preface|grammar)",
    re.I,
)


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\u2014", "-")).strip(" \t")


def main():
    staged, seen = [], set()
    word = pos = None
    blob = []
    for raw in RAW.read_text(encoding="utf-8", errors="replace").splitlines():
        line = clean(raw)
        if not line or SKIP.search(line):
            continue
        hit = HEAD.match(line)
        if hit:
            if word and blob:
                gloss = clean(" ".join(blob))[:180]
                if len(gloss) >= 3:
                    key = (word.lower(), gloss.lower())
                    if key not in seen:
                        seen.add(key)
                        staged.append((word, gloss, pos))
            word = hit.group(1)
            pos = clean(hit.group(2)).rstrip(".")
            blob = [hit.group(3)]
            continue
        if word and len(" ".join(blob)) < 180:
            blob.append(line)
    if word and blob:
        gloss = clean(" ".join(blob))[:180]
        if len(gloss) >= 3:
            staged.append((word, gloss, pos))

    conn = sqlite3.connect(DB)
    conn.execute("DROP TABLE IF EXISTS dictionary")
    conn.execute(
        """
        CREATE TABLE dictionary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ojibwe_word TEXT NOT NULL,
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
    added = 0
    for w, g, p in staged:
        conn.execute(
            """
            INSERT INTO dictionary
            (ojibwe_word, english_translation, word_class, source, license, orthography)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                w,
                g,
                p,
                "Baraga, Dictionary of the Otchipwe Language, 1878",
                "public-domain",
                "Historical Baraga",
            ),
        )
        added += 1
    conn.commit()
    print(f"Wrote {added} rows -> {DB.resolve()}")
    for row in conn.execute(
        "SELECT ojibwe_word, english_translation FROM dictionary LIMIT 10"
    ):
        print(" ", row[0], "-", row[1][:90])
    conn.close()


if __name__ == "__main__":
    main()