from pathlib import Path
import sqlite3

txt = Path("strachey_expansion.txt").read_text(encoding="utf-8").splitlines()
conn = sqlite3.connect("powhatan_dictionary.db")
existing = {
    (w.lower(), e.lower())
    for w, e in conn.execute(
        "select powhatan_word, english_translation from dictionary"
    )
}

new = []
for line in txt:
    if " - " not in line:
        continue
    w, e = [x.strip() for x in line.split(" - ", 1)]
    if w and e and (w.lower(), e.lower()) not in existing:
        new.append((w, e))

print("txt lines", len(txt))
print("already in db", len(txt) - len(new))
print("new to add", len(new))
for w, e in new[:15]:
    print(" NEW", w, "-", e)

for w, e in new:
    conn.execute(
        """
        insert into dictionary
        (powhatan_word, english_translation, word_class, source, license, orthography, notes)
        values (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            w,
            e,
            "",
            "Strachey 1612 / EV 1849 text",
            "public-domain",
            "Historical Colonial",
            "EV expansion scrape",
        ),
    )
conn.commit()
print("table now", conn.execute("select count(*) from dictionary").fetchone()[0])