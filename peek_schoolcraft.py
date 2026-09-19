from pathlib import Path

t = Path("schoolcraft_raw.txt").read_text(encoding="utf-8")
for key in ["CHEW", "TUSCARORA", "Ehn kweh", "Ya wuhn", "1 God", "1. God", "Rockwood"]:
    i = t.lower().find(key.lower())
    print("---", key, i)
    print(t[max(0, i - 80) : i + 500] if i >= 0 else "NOT FOUND")
    print()