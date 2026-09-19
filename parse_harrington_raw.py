import re
from pathlib import Path

RAW = Path("harrington_raw.txt")
OUT = Path("strachey_expansion.txt")

SKIP = re.compile(
    r"(harrington|smithsonian|bulletin|facsimile|key to sheet|"
    r"original strachey|virginia indian language|page \d+|"
    r"literature cited|introduction|contents)",
    re.I,
)


def clean(s: str) -> str:
    s = s.replace("\u2014", "-").replace("\u2013", "-")
    s = re.sub(r"[\[\]]", " ", s)
    s = re.sub(r"\s+", " ", s).strip(" \t.,;:")
    return s


text = RAW.read_text(encoding="utf-8", errors="replace")
pairs = []
seen = set()
for raw in text.splitlines():
    line = clean(raw)
    if not line or SKIP.search(line):
        continue
    if line.startswith("====="):
        continue
    m = re.match(
        r"^([A-Za-z][A-Za-z\u016b\u00fc\u00ff'/\-]{1,40})\s*[,;:]\s+(.{2,80})$",
        line,
    )
    if not m:
        m = re.match(
            r"^([A-Za-z][A-Za-z'/\-]{1,40})\s+[-]\s+(.{2,80})$",
            line,
        )
    if not m:
        continue
    word, gloss = clean(m.group(1)), clean(m.group(2))
    if len(word) < 2 or len(gloss) < 2:
        continue
    if word.lower() in {"the", "and", "see", "from", "with"}:
        continue
    key = (word.lower(), gloss.lower())
    if key in seen:
        continue
    seen.add(key)
    pairs.append((word, gloss))

lines = [f"{w} - {g}" for w, g in pairs]
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("pairs", len(lines))
for row in lines[:12]:
    print(" ", row)