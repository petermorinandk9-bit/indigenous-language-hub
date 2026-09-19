import re
import sqlite3
from pathlib import Path

RAW = Path("byington_raw.txt")
DB = Path("choctaw_dictionary.db")

HEAD = re.compile(r"^([A-Za-z][A-Za-z\-']{1,39}),\s+(.*)$")
POS = re.compile(
    r"^(v\.|n\.|a\.|adv\.|pron\.|pp\.|int\.|conj\.|num\.|i\.|t\.)\s*(.*)$",
    re.I,
)
SKIP_FILE = re.compile(
    r"(bureau of american ethnology|smithsonian institution|"
    r"dictionary of the choctaw language|washington.*government)",
    re.I,
)


def clean(s: str) -> str:
    s = s.replace("\u2014", "-").replace("\u2013", "-")
    s = re.sub(r"\s+", " ", s).strip(" \t")
    return s


def flush(entries, word, blob):
    blob = clean(blob)
    if not word or len(blob) < 3:
        return
    pos = ""
    gloss = blob
    m = POS.match(blob)
    if m:
        pos = clean(m.group(1)).rstrip(".")
        gloss = clean(m.group(2))
    gloss = re.split(r"\s+see\s+", gloss, maxsplit=1, flags=re.I)[0]
    gloss = gloss.strip(" ;,.")
    if len(gloss) < 3:
        return
    entries.append((word, gloss, pos))


def main():
    if not RAW.exists():
        raise SystemExit("Missing byington_raw.txt")

    current_word = None
    current_blob = []
    staged = []
    started = False

    for raw in RAW.read_text(encoding="utf-8", errors="replace").splitlines():
        line = clean(raw)
        if not line or SKIP_FILE.search(line):
            continue
        if re.match(r"^[A-Z]$", line):
            continue
        hit = HEAD.match(line)
        if hit:
            started = True
            if current_word:
                flush(staged, current_word, " ".join(current_blob))
            current_word = hit.group(1)
            current_blob = [hit.group(2)]
        elif started and current_word:
            if line.lower() in {"a", "b", "c", "d", "e", "f", "g"}:
                continue
            current_blob.append(line)

    if current_word:
        flush(staged, current_word, " ".join(current_blob))

    conn = sqlite3.connect(DB)
    conn.execute("DROP TABLE IF EXISTS dictionary")
    conn.execute(
        """
        CREATE TABLE dictionary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            choctaw_word TEXT NOT NULL,
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
    for word, gloss, pos in staged:
        key = (word.lower(), gloss.lower())
        if key in seen:
            continue
        seen.add(key)
        conn.execute(
            """
            INSERT INTO dictionary
            (choctaw_word, english_translation, word_class, source, license, orthography)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                word,
                gloss,
                pos,
                "Byington / Swanton / Halbert, BAE 1915",
                "public-domain",
                "Historical Byington",
            ),
        )
        added += 1
    conn.commit()
    print(f"Wrote {added} rows -> {DB.resolve()}")
    for row in conn.execute(
        "SELECT choctaw_word, english_translation FROM dictionary "
        "WHERE choctaw_word LIKE 'nita%' OR english_translation LIKE '%bear%' "
        "LIMIT 12"
    ):
        print(" ", row[0], "-", row[1][:90])
    conn.close()


if __name__ == "__main__":
    main()