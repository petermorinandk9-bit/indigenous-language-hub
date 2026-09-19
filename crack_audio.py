import requests
import re

url = "https://ojibwe.lib.umn.edu/main-entry/makwa-na"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) DivergentEngines/4.0'}

print(f"Fetching raw source from {url}...\n")
response = requests.get(url, headers=headers)
html = response.text

# 1. Look for any JW Player scripts or Media IDs
jw_scripts = re.findall(r'<script[^>]*jwplayer[^>]*>.*?</script>', html, re.IGNORECASE | re.DOTALL)
jw_setup = re.findall(r'jwplayer\(.*?\)\.setup\(.*?\);', html, re.IGNORECASE | re.DOTALL)

# 2. Look for any alternative audio extensions (maybe they use m4a, ogg, or wav)
media_links = re.findall(r'https?://[^\s"\'<>]+(?:\.mp3|\.m4a|\.wav|\.ogg|\.mp4)', html, re.IGNORECASE)

print("--- JW PLAYER SCRIPTS FOUND ---")
if jw_scripts:
    for script in jw_scripts:
        print(script.strip())
else:
    print("No direct <script> tags for JW Player found.")

print("\n--- JW PLAYER SETUP CONFIG ---")
if jw_setup:
    for setup in jw_setup:
        print(setup.strip())
else:
    print("No .setup() config found in raw text.")

print("\n--- ANY RAW MEDIA LINKS FOUND ---")
if media_links:
    for link in media_links:
        print(link)
else:
    print("Zero media links found in the source code.")