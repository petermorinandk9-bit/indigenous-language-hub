import fitz  # PyMuPDF
from pathlib import Path
import sys

def rip_pdf_to_text(pdf_path="dictionary.pdf", output_txt="ojibwe_raw_archive.txt"):
    pdf_file = Path(pdf_path)
    
    if not pdf_file.exists():
        print(f"[ERROR] Could not find '{pdf_path}'. Check the filename.")
        sys.exit(1)
        
    print(f"Cracking open '{pdf_path}'...")
    
    try:
        doc = fitz.open(pdf_file)
        total_pages = len(doc)
        
        with open(output_txt, "w", encoding="utf-8") as f:
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                # Extract raw text, preserving layout blocks where possible
                text = page.get_text("text") 
                f.write(text + "\n")
                
                if page_num % 50 == 0:
                    print(f"Processed {page_num} / {total_pages} pages...")
                    
        print(f"[SUCCESS] Ripped {total_pages} pages into '{output_txt}'.")
        
    except Exception as e:
        print(f"[ERROR] Failed to read PDF: {e}")

if __name__ == "__main__":
    rip_pdf_to_text()