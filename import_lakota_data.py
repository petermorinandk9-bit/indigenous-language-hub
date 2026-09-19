import sqlite3
import csv
import os

def import_csv_to_lakota_db(csv_filename="lakota_words.csv", db_name="lakota_dictionary.db"):
    if not os.path.exists(csv_filename):
        print(f"[ERROR] CSV file '{csv_filename}' not found.")
        print("Please create a CSV with headers: lakota_word, word_class, english_translation, audio_url, source_notes")
        return

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    imported_count = 0
    
    with open(csv_filename, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lakota_word = row.get("lakota_word", "").strip()
            word_class = row.get("word_class", "").strip()
            english = row.get("english_translation", "").strip()
            audio_url = row.get("audio_url", "").strip()
            source_notes = row.get("source_notes", "").strip()
            
            if lakota_word and english:
                cursor.execute('''
                    INSERT INTO dictionary (lakota_word, word_class, english_translation, audio_url, source_notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (lakota_word, word_class, english, audio_url, source_notes))
                imported_count += 1
                
    conn.commit()
    
    # Verify final count
    cursor.execute("SELECT COUNT(*) FROM dictionary")
    total_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"[SUCCESS] Imported {imported_count} records from {csv_filename}.")
    print(f"[STATUS] Total records in Lakota database: {total_count}")

if __name__ == "__main__":
    import_csv_to_lakota_db()