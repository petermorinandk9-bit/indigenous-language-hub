import sqlite3

def deep_clean_database(db_name="ojibwe_dictionary.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    print("Checking database before deep clean...")
    cursor.execute("SELECT COUNT(*) FROM dictionary")
    initial_count = cursor.fetchone()[0]
    print(f"Initial entry count: {initial_count}")

    print("\nExecuting deep purge of corrupted entries...")
    
    # 1. Delete entries where the Ojibwe word contains weird characters (likely from index)
    # Valid Ojibwe words in this dictionary only use a-z, ', and hyphens.
    # If it has uppercase letters or colons, it's garbage from the index.
    cursor.execute('''
        DELETE FROM dictionary 
        WHERE ojibwe_word GLOB '*[A-Z:;0-9]*' 
        OR english_translation LIKE '%:%'
    ''')
    count_1 = cursor.rowcount
    print(f"Deleted {count_1} entries containing index formatting or uppercase noise.")

    # 2. Delete entries where the 'ojibwe_word' is exceptionally long (run-on index errors)
    cursor.execute('''
        DELETE FROM dictionary 
        WHERE length(ojibwe_word) > 40
    ''')
    count_2 = cursor.rowcount
    print(f"Deleted {count_2} run-on garbage entries.")

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM dictionary")
    final_count = cursor.fetchone()[0]
    print(f"\nTotal entries purged: {count_1 + count_2}")
    print(f"Final clean entry count: {final_count}")

    # Optimize the database after deletions
    cursor.execute("VACUUM")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    deep_clean_database()