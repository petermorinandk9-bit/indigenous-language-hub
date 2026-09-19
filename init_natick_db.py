import re
import sqlite3
from pathlib import Path

RAW = Path("trumbull_raw.txt")
DB = Path("natick_dictionary.db")

HEAD = re.compile(
    r"^\*?([A-Za-z][A-Za-z\-']{1,40}),\s+"
    r"(n\.|v\.|a\.|adv\.|prep\.|pron\.|interj\.|num\.|part\.|vbl\.|adj\.)\s*(.*)$",
    re.I,
)
NEWISH = re.compile(r"^\*?[A-Za-z][A-Za-z\-']{1,40},")
SKIP = re.compile(
    r"(bureau of american ethnology|smithsonian|government printing|"
    r"trumbull|introduction by|abbreviations|announcement)",
    re.I,
)
ENGLISH_HEADS = {
    "building", "man", "woman", "water", "oil", "the", "and", "from", "with",
    "this", "that", "morton", "eliot", "survey",
}


def clean(s: str) -> str:
    s = s.replace("\u2014", "-").replace("\u2013", "-")
    return re.sub(r"\s+", " ", s).strip(" \t")


def flush(entries, word, pos, blob):
    if not word or word.lower() in ENGLISH_HEADS:
        return
    gloss = clean(blob)
    gloss = re.split(r"\s+(?:see|cf\.|syn\.)\s+", gloss, maxsplit=1, flags=re.I)[0]
    gloss = clean(gloss).strip(" ;,.")
    if len(gloss) < 3:
        return
    if len(gloss) > 160:
        gloss = gloss[:157].rsplit(" ", 1)[0] + "..."
    entries.append((word, gloss, pos))


def main():
    staged = []
    word = pos = None
    blob = []
    for raw in RAW.read_text(encoding="utf-8", errors="replace").splitlines():
        line = clean(raw)
        if not line or SKIP.search(line):
            continue
        if re.search(r"ENGLISH.?NATICK", line, re.I) and staged:
            break
        hit = HEAD.match(line)
        if hit:
            if word:
                flush(staged, word, pos, " ".join(blob))
            word = hit.group(1)
            pos = clean(hit.group(2)).rstrip(".")
            blob = [hit.group(3)]
            continue
        if word and NEWISH.match(line):
            flush(staged, word, pos, " ".join(blob))
            word = pos = None
            blob = []
            continue
        if word and len(" ".join(blob)) < 180:
            blob.append(line)
    if word:
        flush(staged, word, pos, " ".join(blob))

    conn = sqlite3.connect(DB)
    conn.execute("DROP TABLE IF EXISTS dictionary")
    conn.execute(
        """
        CREATE TABLE dictionary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            natick_word TEXT NOT NULL,
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
    seen = set()
    added = 0
    for w, g, p in staged:
        key = (w.lower(), g.lower())
        if key in seen:
            continue
        seen.add(key)
        conn.execute(
            """
            INSERT INTO dictionary
            (natick_word, english_translation, word_class, source, license, orthography)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                w,
                g,
                p,
                "Trumbull Natick Dictionary, BAE 25, 1903",
                "public-domain",
                "Historical Natick / Eliot",
            ),
        )
        added += 1
    conn.commit()
    print(f"Wrote {added} rows -> {DB.resolve()}")
    for row in conn.execute("SELECT natick_word, english_translation FROM dictionary LIMIT 10"):
        print(" ", row[0], "-", row[1])
    conn.close()


if __name__ == "__main__":
    main()