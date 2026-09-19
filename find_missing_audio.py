import sqlite3
import csv
import os

def audit_missing_audio(db_name="ojibwe_dictionary.db"):
    if not os.path.exists(db_name):
        print(f"[ERROR] Database '{db_name}' not found in current directory.")
        return

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Get total count of words in database
    cursor.execute("SELECT COUNT(*) FROM dictionary")
    total_words = cursor.fetchone()[0]
    
    # Get count of words missing audio
    cursor.execute("SELECT COUNT(*) FROM dictionary WHERE audio_url IS NULL OR audio_url = ''")
    missing_count = cursor.fetchone()[0]
    
    has_audio_count = total_words - missing_count
    
    print("==========================================")
    print("       OJIBWE DICTIONARY AUDIO AUDIT      ")
    print("==========================================")
    print(f"Total entries in DB: {total_words}")
    print(f"Entries with audio : {has_audio_count} ({round((has_audio_count/total_words)*100, 1)}%)")
    print(f"Entries missing    : {missing_count} ({round((missing_count/total_words)*100, 1)}%)")
    print("==========================================")
    
    # Fetch all missing records
    cursor.execute("SELECT id, ojibwe_word, word_class, english_translation FROM dictionary WHERE audio_url IS NULL OR audio_url = ''")
    missing_records = cursor.fetchall()
    
    if missing_records:
        csv_filename = "missing_audio.csv"
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Ojibwe Word", "Word Class", "English Translation"])
            for row in missing_records:
                writer.writerow(row)
        
        abs_path = os.path.abspath(csv_filename)
        print(f"\n[EXPORTED] Saved all missing audio entries to: {abs_path}")
        
        print("\nFirst 10 missing words preview:")
        for idx, word, w_class, translation in missing_records[:10]:
            print(f"  - [{w_class}] {word}: {translation[:40]}...")
            
    conn.close()

if __name__ == "__main__":
    audit_missing_audio()