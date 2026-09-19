from pathlib import Path
import requests

URL = "https://repository.si.edu/bitstreams/7cfe0169-aa79-46bf-bd80-16cc1fdc96c1/download"
OUT = Path("harrington_strachey_bae157.pdf")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

print("Downloading Harrington BAE 157 ...")
r = requests.get(URL, headers=HEADERS, timeout=120)
r.raise_for_status()
OUT.write_bytes(r.content)
print("Saved", OUT.resolve(), "bytes", OUT.stat().st_size)