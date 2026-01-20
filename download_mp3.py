import json
import yt_dlp
import os

# JSON file name
JSON_FILE = "top_tracks_with_urls.json"

# Folder to save files
OUTPUT_FOLDER = "mp3_downloads"

# Create folder if not exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load JSON file containing 200 objects
with open(JSON_FILE, "r", encoding="utf-8") as f:
    tracks = json.load(f)

# Configure yt-dlp settings
ydl_opts = {
    "format": "bestaudio/best",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
    "quiet": False,
}

# Start downloading all tracks
for track in tracks:
    title = track.get("Title", "unknown_title").replace("/", "-")
    url = track.get("youtube_url")

    if not url:
        print(f"Skipping {title} — No YouTube URL found")
        continue

    # Sanitize filename - remove invalid characters for Windows
    invalid_chars = '<>:"/\\|?*'
    safe_title = title
    for char in invalid_chars:
        safe_title = safe_title.replace(char, '-')
    # Remove any trailing dots or spaces (Windows doesn't allow these at the end)
    safe_title = safe_title.rstrip('. ')
    if not safe_title:
        safe_title = "unknown_title"
    
    output_path = os.path.join(OUTPUT_FOLDER, f"{safe_title}.%(ext)s")
    
    # Create new options for each download with the correct output template
    current_opts = ydl_opts.copy()
    current_opts["outtmpl"] = output_path

    print(f"\n🔽 Downloading: {title}")
    print(f"URL: {url}")
    try:
        with yt_dlp.YoutubeDL(current_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"❌ Error downloading {title}: {e}")

print("\n🎉 DONE! All available MP3s downloaded.")
