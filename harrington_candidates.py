import re
from pathlib import Path

text = Path("harrington_raw.txt").read_text(encoding="utf-8", errors="replace")
EN = {
    "the", "and", "or", "a", "an", "to", "of", "in", "on", "for", "from",
    "with", "this", "that", "key", "sheet", "page", "see", "also", "one",
    "any", "thing", "like", "such", "being", "made", "will", "keep",
}
rows = []
for raw in text.splitlines():
    line = re.sub(r"\s+", " ", raw).strip(" .,;:[]{}")
    if not line or line.startswith("====="):
        continue
    if re.fullmatch(r"[A-Za-z][A-Za-z']{2,24}", line):
        if line.lower() not in EN and not line.lower().startswith("sheet"):
            rows.append(line)

uniq = []
seen = set()
for w in rows:
    k = w.lower()
    if k not in seen:
        seen.add(k)
        uniq.append(w)

Path("harrington_candidates.txt").write_text("\n".join(uniq) + "\n", encoding="utf-8")
print("candidate forms", len(uniq))
for w in uniq[:20]:
    print(" ", w)