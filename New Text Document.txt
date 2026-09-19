#!/usr/bin/env python3
"""Extract Strachey dictionary from Hakluyt Society 1849 OCR text."""

import re
from pathlib import Path

import requests

IA_TXT = (
    "https://archive.org/download/historietravail01majogoog/"
    "historietravail01majogoog_djvu.txt"
)
OUT = Path("strachey_expansion.txt")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

SKIP = re.compile(
    r"(historie of travaile|hakluyt|page \d+|chapter|index|"
    r"a dictionarie of the indian|short dictionary|added unto)",
    re.I,
)


def clean(s: str) -> str:
    s = s.replace("\u2014", "-").replace("\u2013", "-")
    s = re.sub(r"[\[\]]", " ", s)
    s = re.sub(r"\s+", " ", s).strip(" \t.,;:")
    return s


def main():
    print("Fetching", IA_TXT)
    text = requests.get(IA_TXT, headers=HEADERS, timeout=60).text
    text = text.replace("\r\n", "\n")

    start = None
    for mark in ("Ahone", "A DICTIONARIE", "A Dictionarie"):
        i = text.find(mark)
        if i != -1:
            start = i
            break
    if start is None:
        raise SystemExit("Could not find dictionary start in OCR text")

    chunk = text[start:]
    end_hits = []
    for mark in ("APPENDIX", "INDEX", "FINIS", "NOTES TO"):
        j = chunk.find(mark)
        if j != -1:
            end_hits.append(j)
    if end_hits:
        chunk = chunk[: min(end_hits)]

    pairs = []
    seen = set()
    for raw in chunk.splitlines():
        line = clean(raw)
        if not line or SKIP.search(line):
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
        key = (word.lower(), gloss.lower())
        if key in seen:
            continue
        seen.add(key)
        pairs.append((word, gloss))

    lines = [f"{w} - {g}" for w, g in pairs]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(lines)} pairs -> {OUT.resolve()}")
    for row in lines[:10]:
        print("  ", row)


if __name__ == "__main__":
    main()