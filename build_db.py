import re
import sqlite3
import pdfplumber

def init_db(db_name="ojibwe_dictionary.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dictionary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ojibwe_word TEXT NOT NULL,
            word_class TEXT,
            english_translation TEXT NOT NULL,
            full_entry TEXT NOT NULL
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ojibwe ON dictionary(ojibwe_word);')
    conn.commit()
    return conn, cursor

def extract_column_text(page):
    x0, top, x1, bottom = page.bbox
    mid_x = (x0 + x1) / 2

    left_crop = page.crop((x0, top, mid_x, bottom))
    right_crop = page.crop((mid_x, top, x1, bottom))

    left_text = left_crop.extract_text() or ""
    right_text = right_crop.extract_text() or ""

    return left_text + "\n" + right_text

def parse_pdf_to_db(pdf_path="dictionary.pdf", start_page=30, end_page=None):
    conn, cursor = init_db()
    
    # Matches headword followed by standard Ojibwe word class tags
    entry_start_regex = re.compile(
        r'^([a-z\'-]+)\s+(vta|vti\d*|vai|vii|na|ni|nad|nid|adv|pc|m|pn|prt)\b', 
        re.IGNORECASE
    )

    raw_entries = []
    current_entry = ""

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        last_page = end_page if end_page else total_pages
        print(f"Processing pages {start_page} through {last_page} of {total_pages}...")

        for page_idx in range(start_page - 1, last_page):
            page_text = extract_column_text(pdf.pages[page_idx])
            lines = page_text.split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Filter out running headers and single page numbers
                if line.isdigit() or '—' in line or line.startswith('Key to Entries'):
                    continue

                # Check if line begins a new headword entry
                if entry_start_regex.match(line):
                    if current_entry:
                        raw_entries.append(current_entry)
                    current_entry = line
                else:
                    if current_entry:
                        current_entry += " " + line

        if current_entry:
            raw_entries.append(current_entry)

    print(f"Extracted {len(raw_entries)} raw dictionary entries. Indexing into database...")

    inserted_count = 0
    for entry in raw_entries:
        match = re.match(
            r'^([a-z\'-]+)\s+(vta|vti\d*|vai|vii|na|ni|nad|nid|adv|pc|m|pn|prt)\s+(.*)$', 
            entry, 
            re.IGNORECASE
        )
        if match:
            headword = match.group(1).lower()
            word_class = match.group(2).lower()
            translation = match.group(3).strip()

            cursor.execute('''
                INSERT INTO dictionary (ojibwe_word, word_class, english_translation, full_entry)
                VALUES (?, ?, ?, ?)
            ''', (headword, word_class, translation, entry))
            inserted_count += 1

    conn.commit()
    conn.close()
    print(f"Success! {inserted_count} entries stored in ojibwe_dictionary.db.")

if __name__ == "__main__":
    parse_pdf_to_db()