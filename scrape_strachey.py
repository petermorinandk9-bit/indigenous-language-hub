#!/usr/bin/env python3
"""scrape_strachey.py

Local HTML extractor for William Strachey, A Dictionarie of the Indian Language (1612).
Bypasses 403 Forbidden errors by parsing a manually saved HTML file.
"""

from __future__ import annotations
import argparse
import re
import sys
from html import unescape
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Tag

DEFAULT_FILE = "strachey.html"
DEFAULT_OUT = "strachey_expansion.txt"

SKIP_RE = re.compile(
    r"(encyclopedia virginia|primary document|full text|original images|"
    r"transcription source|context|author:|page \d+|sponsored|"
    r"a dictionarie of the indian|historie of travaile|"
    r"^the [a-z]$|^[a-z]\.$)",
    re.I,
)

def clean(text: str) -> str:
    text = unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\xa0", " ").replace("\u200b", "")
    text = text.replace("[", " ").replace("]", " ")
    text = text.replace("—", "-").replace("–", "-")
    text = re.sub(r"\s+", " ", text).strip(" \t\r\n,.;:")
    text = re.sub(r"^[\*\u2022\-\u2013]+\s*", "", text)
    return text

def looks_english(s: str) -> bool:
    tokens = re.findall(r"[A-Za-z']+", s.lower())
    if not tokens:
        return False
    common = {
        "the", "a", "an", "of", "to", "and", "or", "in", "for", "is",
        "his", "her", "their", "they", "them", "with", "from", "that",
        "this", "which", "who", "one", "two", "man", "woman", "god",
        "water", "fire", "bread", "house", "king", "queen", "child",
        "sun", "moon", "day", "night", "good", "great", "little",
    }
    hits = sum(1 for t in tokens if t in common)
    return hits >= 1 or (len(tokens) >= 3 and hits / len(tokens) >= 0.2)

def pair_cells(left: str, right: str, swap: bool | None):
    left, right = clean(left), clean(right)
    if not left or not right or left.lower() == right.lower():
        return None
    if swap is True:
        powhatan, english = right, left
    elif swap is False:
        powhatan, english = left, right
    else:
        left_en = looks_english(left)
        right_en = looks_english(right)
        if left_en and not right_en:
            powhatan, english = right, left
        else:
            powhatan, english = left, right
    if len(powhatan) < 2 or len(english) < 2:
        return None
    if SKIP_RE.search(powhatan) or SKIP_RE.search(english):
        return None
    return powhatan, english

def extract_tables(soup, swap):
    pairs = []
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells = tr.find_all(["td", "th"])
            texts = [clean(c.get_text(" ", strip=True)) for c in cells]
            texts = [
                t for t in texts
                if t and t.lower() not in {"english", "powhatan", "indian", "virginia"}
            ]
            if len(texts) >= 2:
                got = pair_cells(texts[0], texts[1], swap)
                if got:
                    pairs.append(got)
            elif len(texts) == 1:
                got = split_inline(texts[0], swap)
                if got:
                    pairs.append(got)
    return pairs

def split_inline(raw, swap):
    text = clean(raw)
    if not text or SKIP_RE.search(text):
        return None
    m = re.match(r"^(.{2,60}?)(?:\s*[-–—:,;]\s+|\s+)(.{2,80})$", text)
    if not m:
        return None
    return pair_cells(m.group(1), m.group(2), swap)

def extract_list_italic(soup, swap):
    pairs = []
    for li in soup.find_all("li"):
        em = li.find(["em", "i"])
        if em:
            gloss = clean(em.get_text(" ", strip=True))
            em.extract()
            head = clean(li.get_text(" ", strip=True)).rstrip(" ,;:-")
            got = pair_cells(head, gloss, swap)
            if got:
                pairs.append(got)
            continue
        got = split_inline(li.get_text(" ", strip=True), swap)
        if got:
            pairs.append(got)
    return pairs

def extract_paragraphs(soup, swap):
    pairs = []
    for tag in soup.find_all(["p", "dd", "span", "div"]):
        ems = tag.find_all(["em", "i"])
        if len(ems) == 1:
            gloss = clean(ems[0].get_text(" ", strip=True))
            clone_text = []
            for child in tag.children:
                if isinstance(child, NavigableString):
                    clone_text.append(str(child))
                elif isinstance(child, Tag) and child.name not in {"em", "i"}:
                    clone_text.append(child.get_text(" ", strip=True))
            head = clean(" ".join(clone_text)).rstrip(" ,;:-")
            if head and gloss:
                got = pair_cells(head, gloss, swap)
                if got:
                    pairs.append(got)
    return pairs

def dedupe(pairs):
    seen = set()
    out = []
    for p, e in pairs:
        key = (p.lower(), e.lower())
        if key not in seen:
            seen.add(key)
            out.append((p, e))
    return out

def scrape_local(file_path, swap):
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, "html.parser")
    for junk in soup(["script", "style", "nav", "footer", "header", "form"]):
        junk.decompose()
        
    pairs = []
    pairs.extend(extract_tables(soup, swap))
    pairs.extend(extract_list_italic(soup, swap))
    if len(pairs) < 20:
        pairs.extend(extract_paragraphs(soup, swap))
    return dedupe(pairs)

def main():
    parser = argparse.ArgumentParser(description="Parse local Strachey 1612 HTML")
    parser.add_argument("--file", default=DEFAULT_FILE)
    parser.add_argument("--swap", action="store_true", help="col1 English / col2 Powhatan")
    parser.add_argument("--english-first", action="store_true")
    parser.add_argument("-o", "--output", default=DEFAULT_OUT)
    args = parser.parse_args()
    
    swap = True if (args.swap or args.english_first) else None
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"[ERROR] Could not find {args.file}. Make sure you saved the webpage locally.")
        return 1

    print(f"Parsing local file: {args.file}")
    pairs = scrape_local(args.file, swap)
    lines = [f"{p} - {e}" for p, e in pairs]
    
    out_path = Path(args.output)
    out_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    print(f"Wrote {len(lines)} pairs -> {out_path.resolve()}")
    
    if not lines:
        print("No pairs found. Check the HTML structure.", file=sys.stderr)
        return 1
        
    for sample in lines[:8]:
        print("  ", sample)
    return 0

if __name__ == "__main__":
    sys.exit(main())