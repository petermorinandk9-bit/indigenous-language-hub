from pathlib import Path
import requests

URLS = [
    "https://archive.org/stream/notesoniroquois00schogoog/notesoniroquois00schogoog_djvu.txt",
    "https://archive.org/download/notesiroquois00schorich/notesiroquois00schorich_djvu.txt",
]
OUT = Path("schoolcraft_raw.txt")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

last_err = None
for url in URLS:
    print("Trying", url)
    try:
        r = requests.get(url, headers=HEADERS, timeout=90)
        r.raise_for_status()
        if len(r.text) < 20000:
            print("  too short", len(r.text))
            continue
        OUT.write_text(r.text, encoding="utf-8", errors="replace")
        print("Saved", OUT.resolve(), "chars", len(r.text))
        low = r.text.lower()
        print("has chew", "chew" in low)
        print("has ehn kweh", "ehn kweh" in low)
        print("has ya wuhn", "ya wuhn" in low)
        raise SystemExit(0)
    except SystemExit:
        raise
    except Exception as e:
        last_err = e
        print("  failed:", e)

raise SystemExit(f"Could not fetch Schoolcraft text: {last_err}")