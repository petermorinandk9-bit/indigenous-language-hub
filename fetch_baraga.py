from pathlib import Path
import requests

URLS = [
    "https://archive.org/download/dictionaryofotch00bara/dictionaryofotch00bara_djvu.txt",
    "https://archive.org/stream/cihm_12987/cihm_12987_djvu.txt",
    "https://archive.org/download/rosettaproject_ciw_book-3/rosettaproject_ciw_book-3_djvu.txt",
]
OUT = Path("baraga_raw.txt")
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
        raise SystemExit(0)
    except SystemExit:
        raise
    except Exception as e:
        last_err = e
        print("  failed:", e)

raise SystemExit(f"Could not fetch Baraga text: {last_err}")