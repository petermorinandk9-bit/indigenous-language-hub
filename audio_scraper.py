import sqlite3
import requests
import time
import re

def setup_database(db_name="ojibwe_dictionary.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    return conn, cursor

def scrape_audio_links():
    conn, cursor = setup_database()
    
    # Unleashed: Targeting every single word in the database missing an audio URL
    cursor.execute('''
        SELECT id, ojibwe_word, word_class 
        FROM dictionary 
        WHERE audio_url IS NULL 
    ''')
    
    words_to_scrape = cursor.fetchall()
    
    if not words_to_scrape:
        print("No target words found needing audio links. The database is fully mapped.")
        conn.close()
        return

    print(f"Starting full AWS S3 audio extraction for {len(words_to_scrape)} words...")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) DivergentEngines/4.0'}
    base_url = "https://ojibwe.lib.umn.edu"
    success_count = 0
    
    for row_id, word, w_class in words_to_scrape:
        clean_class = ''.join([c for c in w_class if c.isalpha()])
        target_url = f"{base_url}/main-entry/{word}-{clean_class}"
        
        try:
            response = requests.get(target_url, headers=headers, timeout=10)
            
            # Fall back to the search page if the direct URL fails
            if response.status_code != 200:
                target_url = f"{base_url}/search?q={word}&type=ojibwe"
                response = requests.get(target_url, headers=headers, timeout=10)
                
            response.raise_for_status()
            
            # Regex sniper hunting for AWS media links
            media_links = re.findall(r'https?://[^\s"\'<>]+(?:\.mp3|\.m4a|\.wav|\.ogg|\.mp4)', response.text, re.IGNORECASE)
            
            if media_links:
                audio_link = media_links[0]
                
                cursor.execute("UPDATE dictionary SET audio_url = ? WHERE id = ?", (audio_link, row_id))
                conn.commit()
                filename = audio_link.split('/')[-1]
                print(f"[SUCCESS] {word} -> {filename}")
                success_count += 1
            else:
                print(f"[MISSING] No media links found for '{word}'")
                
        except Exception as e:
            print(f"[ERROR] Failed on '{word}': {str(e)}")
            
        time.sleep(1.5)

    print(f"\nScrape complete. Successfully mapped {success_count} audio files.")
    conn.close()

if __name__ == "__main__":
    scrape_audio_links()