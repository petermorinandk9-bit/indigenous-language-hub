#!/usr/bin/env python3
import csv
import re
from pathlib import Path

def parse_raw_text(input_file="powhatan_master.txt", output_csv="powhatan_seed.csv"):
    inp = Path(input_file)
    if not inp.exists():
        print(f"[ERROR] '{input_file}' not found. Create it and paste your word list there.")
        return
    
    entries = []
    with inp.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Automatically splits lines separated by hyphens or dashes
            parts = re.split(r'\s*[-–—]\s*', line, maxsplit=1)
            if len(parts) == 2:
                word = parts[0].strip()
                definition = parts[1].strip()
                
                entries.append({
                    "powhatan_word": word,
                    "english_translation": definition,
                    "word_class": "n/a",
                    "source": "Smith (1624) & Strachey (1612)",
                    "license": "Public Domain",
                    "orthography": "Historical Colonial",
                    "notes": "Bulk ingested",
                    "audio_url": ""
                })

    if entries:
        out = Path(output_csv)
        with out.open("w", newline="", encoding="utf-8-sig") as out_f:
            writer = csv.DictWriter(out_f, fieldnames=[
                "powhatan_word", "english_translation", "word_class", 
                "source", "license", "orthography", "notes", "audio_url"
            ])
            writer.writeheader()
            writer.writerows(entries)
        print(f"[SUCCESS] Converted {len(entries)} raw lines into '{output_csv}' ready for the database.")
    else:
        print("[WARNING] No valid word pairs found.")

if __name__ == "__main__":
    parse_raw_text()