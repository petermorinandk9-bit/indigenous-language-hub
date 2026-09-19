import csv
import re
from pathlib import Path

def parse_raw_text_corpus(input_txt_path: str, output_csv_path: str):
    """
    Parses a raw public-domain text lexicon file and converts it 
    into a structured CSV ready for Grok's init_lakota_db.py pipeline.
    """
    txt_file = Path(input_txt_path)
    if not txt_file.exists():
        print(f"[ERROR] Input file '{input_txt_path}' not found.")
        return

    entries = []
    
    # Regular expression to catch typical dictionary line patterns: Word — Definition
    # e.g., "wičháša n. man, human being."
    pattern = re.compile(r"^([a-zA-ZȟčšąįųȯřǧþđłŋA-Z\s·’'-]+)\s+([a-z]{1,3}\.)\s+(.+)$")

    with txt_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            match = pattern.match(line)
            if match:
                word = match.group(1).strip()
                w_class = match.group(2).replace(".", "").strip()
                definition = match.group(3).strip()
                
                entries.append({
                    "lakota_word": word,
                    "english_translation": definition,
                    "word_class": w_class,
                    "source": "Riggs 1890 Dakota-English Dictionary (Public Domain)",
                    "license": "Public Domain",
                    "orthography": "SLO/Historical",
                    "notes": "Extracted via public domain corpus parser",
                    "audio_url": ""
                })

    # Write out to Grok's expected seed format
    out_path = Path(output_csv_path)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "lakota_word", "english_translation", "word_class", 
            "source", "license", "orthography", "notes", "audio_url"
        ])
        writer.writeheader()
        writer.writerows(entries)

    print(f"[SUCCESS] Parsed {len(entries)} public domain entries into '{output_csv_path}'.")

if __name__ == "__main__":
    # Point this to any downloaded raw text export of a public domain dictionary
    source_file = "raw_riggs_corpus.txt"
    target_csv = "lakota_seed.csv"
    
    parse_raw_text_corpus(source_file, target_csv)