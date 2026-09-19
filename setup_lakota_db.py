import sqlite3
import os

def initialize_lakota_database(db_name="lakota_dictionary.db"):
    # Ensure UTF-8 connection to properly handle Lakota diacritics and special characters
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Create the core dictionary table tailored for Lakota data fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dictionary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lakota_word TEXT NOT NULL,
            word_class TEXT,
            english_translation TEXT,
            audio_url TEXT,
            source_notes TEXT
        )
    ''')
    
    conn.commit()
    print(f"[SUCCESS] Initialized database '{db_name}' with Lakota schema.")
    
    # Insert a sample baseline entry to test UI integration and character rendering
    sample_entries = [
        ("Lakȟóta", "n", "Lakota person, ally; speak Lakota", "", "Core vocabulary baseline"),
        ("iyápi", "n", "language, speech, word", "", "Core vocabulary baseline")
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO dictionary (lakota_word, word_class, english_translation, audio_url, source_notes)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_entries)
    
    conn.commit()
    
    # Verify row count
    cursor.execute("SELECT COUNT(*) FROM dictionary")
    count = cursor.fetchone()[0]
    print(f"[STATUS] Current Lakota database records: {count}")
    
    conn.close()

if __name__ == "__main__":
    initialize_lakota_database()