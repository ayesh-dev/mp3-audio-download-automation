import json
import os

# JSON file name
JSON_FILE = "top_tracks_with_urls.json"

# Folder containing MP3 files
OUTPUT_FOLDER = "mp3_downloads"

def sanitize_title(title):
    """Sanitize title to match the filename format used in download_mp3.py"""
    # Replace / with -
    safe_title = title.replace("/", "-")
    
    # Remove invalid characters for Windows
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        safe_title = safe_title.replace(char, '-')
    
    # Remove any trailing dots or spaces (Windows doesn't allow these at the end)
    safe_title = safe_title.rstrip('. ')
    
    if not safe_title:
        safe_title = "unknown_title"
    
    return safe_title

# Load JSON file
print("📖 Loading JSON file...")
with open(JSON_FILE, "r", encoding="utf-8") as f:
    tracks = json.load(f)

print(f"📋 Found {len(tracks)} tracks in JSON\n")

# Get all existing MP3 files
if not os.path.exists(OUTPUT_FOLDER):
    print(f"❌ Folder '{OUTPUT_FOLDER}' does not exist!")
    exit(1)

existing_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.lower().endswith('.mp3')]
print(f"🎵 Found {len(existing_files)} MP3 files in '{OUTPUT_FOLDER}'\n")

# Create a mapping of sanitized filenames to actual filenames
file_map = {}
for filename in existing_files:
    # Remove .mp3 extension for matching
    base_name = filename[:-4]  # Remove .mp3
    file_map[base_name] = filename

# Track statistics
matched_count = 0
skipped_count = 0
already_has_path = 0

# Process each track
print("🔄 Matching tracks with MP3 files...\n")
for track in tracks:
    title = track.get("Title", "unknown_title")
    
    # Check if mp3_path already exists
    if "mp3_path" in track and track["mp3_path"]:
        already_has_path += 1
        continue
    
    # Sanitize title to match filename format
    safe_title = sanitize_title(title)
    expected_filename = f"{safe_title}.mp3"
    expected_path = os.path.join(OUTPUT_FOLDER, expected_filename)
    
    # Check if file exists
    if os.path.exists(expected_path):
        # Use forward slashes for relative path (works on all platforms)
        relative_path = os.path.join(OUTPUT_FOLDER, expected_filename).replace("\\", "/")
        track["mp3_path"] = relative_path
        matched_count += 1
        print(f"✓ Matched: {title}")
    else:
        skipped_count += 1
        print(f"⚠ Skipped: {title} (file not found)")

# Save updated JSON
print(f"\n💾 Saving updated JSON...")
with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(tracks, f, indent=2, ensure_ascii=False)

# Print summary
print("\n" + "="*50)
print("📊 SUMMARY")
print("="*50)
print(f"✓ Matched and added paths: {matched_count}")
print(f"⚠ Skipped (file not found): {skipped_count}")
print(f"ℹ Already had paths: {already_has_path}")
print(f"📝 Total tracks processed: {len(tracks)}")
print("="*50)
print("\n🎉 DONE! JSON file updated with MP3 paths.")

