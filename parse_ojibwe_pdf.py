#!/usr/bin/env python3
import re
import csv
from pathlib import Path

def parse_pdf_text():
    raw_file = Path("ojibwe_raw_archive.txt")
    output_csv = Path("ojibwe_pdf_batch.csv")
    
    if not raw_file.exists():
        print(f"[ERROR] '{raw_file.name}' not found. Ensure the raw text file exists.")
        return
        
    # Complete set of Nichols & Nyholm grammatical tags
    pos_tags = {
        "ni", "na", "nad", "nid", 
        "vai", "vii", "vti", "vta", "via", 
        "adv", "pc", "pron", "conj", "num", 
        "ptx", "pv", "pn", "interj", "ij", "p"
    }
    
    # Regex supporting optional parentheses, roots, and hyphens: e.g. "(w)iiba adv", "abaabas /abaabasw-/ via"
    entry_pattern = re.compile(
        r'^(\(?[a-zA-Z-]+(?:\)?[a-zA-Z-]+)*)(?:\s+/[a-zA-Z-]+/)?\s+([a-zA-Z]{1,6})\s+(.+)', 
        re.IGNORECASE
    )
    
    entries = []
    current_entry = ""
    
    print("Re-scanning and stitching multiline text blocks...")
    with raw_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            match = entry_pattern.match(line)
            if match and match.group(2).lower() in pos_tags:
                if current_entry:
                    entries.append(current_entry)
                current_entry = line
            else:
                if current_entry:
                    if current_entry.endswith("-"):
                        current_entry = current_entry[:-1] + line
                    else:
                        current_entry += " " + line
                        
    if current_entry:
        entries.append(current_entry)
        
    print(f"Reconstructed {len(entries)} entries. Extracting clean definitions...")
    
    csv_data = []
    for entry in entries:
        match = entry_pattern.match(entry)
        if match:
            word = match.group(1).strip()
            pos = match.group(2).strip().lower()
            rest = match.group(3).strip()
            
            # Extract primary English definition prior to grammatical paradigms
            translation = rest.split(";")[0].strip()
            
            notes = ""
            if ";" in rest:
                notes = rest.split(";", 1)[1].strip()
                
            csv_data.append({
                "ojibwe_word": word,
                "english_translation": translation,
                "word_class": pos,
                "source": "Nichols & Nyholm PDF Archive",
                "license": "Public Domain / Open Educational",
                "orthography": "Fiero Double Vowel",
                "notes": notes,
                "audio_url": ""
            })
            
    with output_csv.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "ojibwe_word", "english_translation", "word_class", 
            "source", "license", "orthography", "notes", "audio_url"
        ])
        writer.writeheader()
        writer.writerows(csv_data)
        
    print(f"[SUCCESS] Wrote {len(csv_data)} formatted entries to '{output_csv.name}'")

if __name__ == "__main__":
    parse_pdf_text()