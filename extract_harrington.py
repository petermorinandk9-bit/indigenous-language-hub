from pathlib import Path

PDF = Path("harrington_strachey_bae157.pdf")
OUT = Path("harrington_raw.txt")

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

reader = PdfReader(str(PDF))
print("pages", len(reader.pages))
chunks = []
for i, page in enumerate(reader.pages, 1):
    text = page.extract_text() or ""
    chunks.append(f"\n\n===== PAGE {i} =====\n{text}")
    print(f"page {i}: {len(text)} chars")

raw = "".join(chunks)
OUT.write_text(raw, encoding="utf-8")
print("wrote", OUT.resolve(), "total chars", len(raw))