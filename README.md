## Download MP3 for Top Tracks

This project downloads MP3 audio files for a list of tracks defined in a JSON file, saves them locally, records the relative file paths back into the same JSON, and can upload them to Cloudflare R2 CDN for public access.

### Project Structure

- **`top_tracks_with_urls.json`**: Source data containing track metadata, including `Title` and `youtube_url` for each track.
- **`download_mp3.py`**: Downloads audio from YouTube for each track, converts it to MP3, saves it to `mp3_downloads`, and writes the relative `mp3_path` back into the JSON.
- **`update_json_with_mp3_paths.py`**: Utility script that scans existing MP3s in `mp3_downloads`, matches them to JSON entries by title, and fills in missing `mp3_path` values.
- **`upload_to_cdn.py`**: Uploads MP3 files from `mp3_downloads/` to Cloudflare R2 CDN and saves all CDN URLs to files.
- **`mp3_downloads/`**: Output folder where all downloaded MP3 files are stored.
- **`cdn_urls.json`**: JSON file containing all uploaded CDN URLs with metadata.
- **`cdn_urls.txt`**: Simple text file with one CDN URL per line.

### Requirements

- Python 3.8+  
- `ffmpeg` installed and available in your system `PATH`  
- Python packages:
  - `yt-dlp` (for downloading)
  - `boto3` (for CDN uploads)
  - `python-dotenv` (for environment variables)

Install the Python dependencies:

```bash
pip install yt-dlp boto3 python-dotenv
```

Make sure `ffmpeg` is installed (on Windows you can install it via package managers like `chocolatey`, or download from the official site and add it to `PATH`).

### Environment Variables (for CDN Upload)

Create a `.env` file in the project root with your Cloudflare R2 credentials:

```env
R2_ACCESS_KEY=your_access_key_here
R2_SECRET_KEY=your_secret_key_here
R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
R2_BUCKET=your-bucket-name
R2_PUBLIC_BASE=https://pub-xxxx.r2.dev
```

**Important Notes:**
- Get your `R2_ENDPOINT` and credentials from Cloudflare Dashboard → R2 → Manage R2 API Tokens
- Get your `R2_PUBLIC_BASE` from Cloudflare Dashboard → R2 → Your Bucket → Settings → Public Access → Public Development URL
- The `R2_PUBLIC_BASE` must match exactly (including the account ID) or you'll get 401 errors

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

### 3. Upload MP3s to Cloudflare R2 CDN

Upload all MP3 files from `mp3_downloads/` to Cloudflare R2 CDN and get public URLs:

```bash
python upload_to_cdn.py
```

**Prerequisites:**
- Ensure your `.env` file is configured with R2 credentials (see Environment Variables section above)
- Make sure your R2 bucket has **Public Access** enabled in Cloudflare Dashboard
- Verify that `R2_PUBLIC_BASE` matches your bucket's Public Development URL exactly

What it does:

- Validates that `R2_PUBLIC_BASE` is set correctly
- Scans all `.mp3` and `.mp4` files in `mp3_downloads/`
- For each file:
  - Uploads to Cloudflare R2 using S3-compatible API
  - Generates the public CDN URL in format: `https://pub-xxxx.r2.dev/filename.mp3`
  - URL-encodes filenames properly (spaces → `%20`, etc.)
- Saves all CDN URLs to two files:
  - **`cdn_urls.json`**: Structured JSON with metadata, timestamps, and filename-to-URL mapping
  - **`cdn_urls.txt`**: Simple text file with one URL per line
- Displays upload summary with success/failure counts

**Output Files:**

`cdn_urls.json` example:
```json
{
  "generated_at": "2024-01-15T10:30:45.123456",
  "total_files": 2,
  "urls": {
    "8 AM.mp3": "https://pub-xxxx.r2.dev/8%20AM.mp3",
    "My Song.mp3": "https://pub-xxxx.r2.dev/My%20Song.mp3"
  }
}
```

`cdn_urls.txt` example:
```
# CDN URLs generated at 2024-01-15T10:30:45.123456
# Total files: 2

https://pub-xxxx.r2.dev/8%20AM.mp3
https://pub-xxxx.r2.dev/My%20Song.mp3
```

**Troubleshooting:**

- **401 Error**: Check that your bucket has Public Access enabled and `R2_PUBLIC_BASE` matches the dashboard URL exactly
- **SSL Errors**: The script handles SSL verification automatically for Cloudflare R2
- **ACL Errors**: If ACL setting fails, the script falls back to bucket-level public access (which is the standard for R2)

### Notes

- Filenames are sanitized to be compatible with Windows (removing characters like `<>:"/\|?*` and trimming trailing spaces/dots).
- Paths stored in JSON use forward slashes (`/`), which are easier to handle across platforms.
- CDN URLs are properly URL-encoded to handle spaces and special characters in filenames.
- The script generates URLs in the exact format shown in Cloudflare R2 dashboard (no bucket name in the path).


