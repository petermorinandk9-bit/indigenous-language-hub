import sqlite3
import requests
import time
import re
import urllib.parse

def setup_database(db_name="ojibwe_dictionary.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    return conn, cursor

def deep_scrape_missing_audio():
    conn, cursor = setup_database()
    
    # Target only the words that currently lack an audio URL
    cursor.execute('''
        SELECT id, ojibwe_word 
        FROM dictionary 
        WHERE audio_url IS NULL OR audio_url = ''
    ''')
    
    missing_words = cursor.fetchall()
    
    if not missing_words:
        print("No missing audio entries found. Database is 100% mapped!")
        conn.close()
        return

    print(f"Starting Deep Search Scraper for {len(missing_words)} missing words...")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) DivergentEngines/DeepSearch 1.0'}
    base_url = "https://ojibwe.lib.umn.edu"
    success_count = 0
    
    for row_id, word in missing_words:
        # URL encode the word to cleanly handle special characters
        safe_word = urllib.parse.quote(word)
        target_url = f"{base_url}/search?q={safe_word}&type=ojibwe"
        
        try:
            response = requests.get(target_url, headers=headers, timeout=10)
            
            # Fallback alternate search path if needed
            if response.status_code != 200:
                target_url = f"{base_url}/main/search?q={safe_word}"
                response = requests.get(target_url, headers=headers, timeout=10)
                
            response.raise_for_status()
            
            # Hunt for any AWS S3 media links on the search results page
            media_links = re.findall(r'https?://[^\s"\'<>]+(?:\.mp3|\.m4a|\.wav|\.ogg|\.mp4)', response.text, re.IGNORECASE)
            
            if media_links:
                audio_link = media_links[0]
                
                cursor.execute("UPDATE dictionary SET audio_url = ? WHERE id = ?", (audio_link, row_id))
                conn.commit()
                filename = audio_link.split('/')[-1]
                print(f"[RECOVERED] {word} -> {filename}")
                success_count += 1
            else:
                # Silent pass for words that truly have no human audio in the archives
                pass
                
        except Exception as e:
            print(f"[ERROR] Failed on '{word}': {str(e)}")
            
        # Standard polite throttle to protect IP and connection stability
        time.sleep(1.0)

    print(f"\nDeep sweep complete. Successfully recovered {success_count} additional audio files.")
    
    # Audit final numbers
    cursor.execute("SELECT COUNT(*) FROM dictionary WHERE audio_url IS NOT NULL AND audio_url != ''")
    new_total = cursor.fetchone()[0]
    print(f"New total audio coverage: {new_total} entries.")
    
    conn.close()

if __name__ == "__main__":
    deep_scrape_missing_audio()