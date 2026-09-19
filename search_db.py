import sqlite3
import sys

def search_dictionary(query):
    conn = sqlite3.connect("ojibwe_dictionary.db")
    cursor = conn.cursor()

    # Add wildcards to search anywhere in the text
    search_term = f"%{query}%"

    cursor.execute('''
        SELECT ojibwe_word, word_class, english_translation 
        FROM dictionary 
        WHERE ojibwe_word LIKE ? OR english_translation LIKE ?
        LIMIT 15
    ''', (search_term, search_term))

    results = cursor.fetchall()
    conn.close()

    if not results:
        print(f"\nNo results found for '{query}'.")
        return

    print(f"\n--- Top Results for '{query}' ---")
    for row in results:
        ojibwe, w_class, english = row
        print(f"[{w_class.upper()}] {ojibwe} -> {english}")
    print("---------------------------------\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_db.py <word>")
    else:
        # Join arguments in case they search a multi-word phrase like "look at"
        query = " ".join(sys.argv[1:])
        search_dictionary(query)