## Download MP3 for Top Tracks

This project downloads MP3 audio files for a list of tracks defined in a JSON file, saves them locally, and records the relative file paths back into the same JSON for later use.

### Project Structure

- **`top_tracks_with_urls.json`**: Source data containing track metadata, including `Title` and `youtube_url` for each track.
- **`download_mp3.py`**: Downloads audio from YouTube for each track, converts it to MP3, saves it to `mp3_downloads`, and writes the relative `mp3_path` back into the JSON.
- **`update_json_with_mp3_paths.py`**: Utility script that scans existing MP3s in `mp3_downloads`, matches them to JSON entries by title, and fills in missing `mp3_path` values.
- **`mp3_downloads/`**: Output folder where all downloaded MP3 files are stored.

### Requirements

- Python 3.8+  
- `ffmpeg` installed and available in your system `PATH`  
- Python packages:
  - `yt-dlp`

Install the Python dependency:

```bash
pip install yt-dlp
```

Make sure `ffmpeg` is installed (on Windows you can install it via package managers like `chocolatey`, or download from the official site and add it to `PATH`).

### 1. Download all MP3s and update JSON

This is the main flow: it reads `top_tracks_with_urls.json`, downloads audio for each track that has a `youtube_url`, and updates the JSON with the relative path to the downloaded MP3.

```bash
python download_mp3.py
```

What it does:

- Creates `mp3_downloads/` if it doesn’t exist.
- For each track:
  - Skips the track if `youtube_url` is missing.
  - Sanitizes the track title to a safe Windows filename.
  - Checks if the expected MP3 already exists:
    - If it exists, only sets `mp3_path` in the JSON (no re-download).
    - If it doesn’t exist, downloads and converts the audio to MP3.
  - After a successful download, sets `mp3_path` to a relative path like:
    - `mp3_downloads/Some Track Name.mp3`
- At the end, rewrites `top_tracks_with_urls.json` including the new `mp3_path` fields.

### 2. Backfill JSON with paths for already-downloaded MP3s

If you already have MP3 files in `mp3_downloads` (for example, downloaded earlier), you can sync them into the JSON without downloading anything again:

```bash
python update_json_with_mp3_paths.py
```

What it does:

- Loads `top_tracks_with_urls.json`.
- Scans all `.mp3` files in `mp3_downloads/`.
- For each track **without** an `mp3_path`:
  - Sanitizes the `Title` the same way as `download_mp3.py`.
  - Checks if a matching MP3 file exists.
  - If found, sets `mp3_path` to its relative path.
  - If not found, prints a warning and skips that track.
- Saves the updated JSON back to `top_tracks_with_urls.json` and prints a small summary.

### Notes

- Filenames are sanitized to be compatible with Windows (removing characters like `<>:"/\|?*` and trimming trailing spaces/dots).
- Paths stored in JSON use forward slashes (`/`), which are easier to handle across platforms.


