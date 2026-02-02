import os
import json
from pathlib import Path
from datetime import datetime
import boto3
from dotenv import load_dotenv
from botocore.config import Config
from urllib.parse import quote

load_dotenv()

# Environment variables
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_BUCKET = os.getenv("R2_BUCKET")
R2_PUBLIC_BASE = os.getenv("R2_PUBLIC_BASE")  # https://pub-xxxx.r2.dev

# Validate R2_PUBLIC_BASE
if R2_PUBLIC_BASE:
    # Remove trailing slash if present
    R2_PUBLIC_BASE = R2_PUBLIC_BASE.rstrip('/')
    print(f"ℹ️  Using Public Base URL: {R2_PUBLIC_BASE}")
    print(f"⚠️  IMPORTANT: Ensure this matches your Cloudflare R2 dashboard 'Public Development URL'")
    print(f"   Expected format: https://pub-xxxx.r2.dev\n")
else:
    print("❌ ERROR: R2_PUBLIC_BASE not set in .env file")
    print("   Please set R2_PUBLIC_BASE=https://pub-xxxx.r2.dev in your .env file")
    print("   Get the correct URL from Cloudflare R2 dashboard → Your Bucket → Settings → Public Access\n")

VIDEOS_DIR = Path("mp3_downloads")
CDN_URLS_FILE = "cdn_urls.json"  # JSON file to store all CDN URLs
CDN_URLS_TXT = "cdn_urls.txt"     # Simple text file with URLs

# Create S3-compatible client
s3 = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    region_name="auto",
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"},
    ),
)

def upload_file(file_path: Path):
    """
    Upload file to Cloudflare R2 and return public URL.
    
    Returns URL in format: https://pub-xxxx.r2.dev/filename.mp3
    (matches Cloudflare dashboard format, no bucket name)
    
    Note: If you get 401 errors, ensure:
    1. Bucket has "Public Access" enabled in Cloudflare dashboard
    2. The public URL domain matches your R2_PUBLIC_BASE
    """
    key = file_path.name
    # URL-encode the key for public URL (spaces -> %20, special chars encoded)
    encoded_key = quote(key)

    try:
        with open(file_path, "rb") as f:
            s3.put_object(
                Bucket=R2_BUCKET,
                Key=key,  # Use original key for S3 (boto3 handles encoding internally)
                Body=f,
                ContentType="audio/mpeg",
                ACL="public-read",  # Try to make object publicly accessible
            )
    except Exception as e:
        # If ACL fails (some R2 configs don't support it), try without ACL
        # Public access is usually controlled at bucket level in R2
        if "ACL" in str(e) or "InvalidArgument" in str(e):
            print(f"⚠️  ACL not supported, uploading without ACL (bucket-level public access required)")
            with open(file_path, "rb") as f:
                s3.put_object(
                    Bucket=R2_BUCKET,
                    Key=key,
                    Body=f,
                    ContentType="audio/mpeg",
                )
        else:
            raise

    # ✅ Correct Cloudflare R2 public URL format (matches dashboard)
    # Format: https://pub-xxxx.r2.dev/filename.mp3 (NO bucket name)
    return f"{R2_PUBLIC_BASE}/{encoded_key}"

def save_cdn_urls(urls_data, json_file=CDN_URLS_FILE, txt_file=CDN_URLS_TXT):
    """
    Save CDN URLs to both JSON and text files.
    
    Args:
        urls_data: Dictionary mapping filenames to URLs
        json_file: Path to JSON output file
        txt_file: Path to text output file
    """
    # Save as JSON (structured data)
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "total_files": len(urls_data),
            "urls": urls_data
        }, f, indent=2, ensure_ascii=False)
    
    # Save as simple text file (one URL per line)
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(f"# CDN URLs generated at {datetime.now().isoformat()}\n")
        f.write(f"# Total files: {len(urls_data)}\n\n")
        for filename, url in urls_data.items():
            f.write(f"{url}\n")
    
    print(f"\n💾 CDN URLs saved to:")
    print(f"   📄 JSON: {json_file}")
    print(f"   📄 TXT: {txt_file}")

def main():
    if not VIDEOS_DIR.exists():
        print("❌ mp3_downloads folder not found")
        return

    # Dictionary to store all uploaded file URLs
    cdn_urls = {}
    uploaded_count = 0
    failed_count = 0

    print("🚀 Starting upload process...\n")
    
    for file in VIDEOS_DIR.iterdir():
        if file.suffix.lower() in [".mp3", ".mp4"]:
            print(f"⬆️ Uploading: {file.name}")
            try:
                url = upload_file(file)
                cdn_urls[file.name] = url
                uploaded_count += 1
                print(f"✅ CDN URL: {url}\n")
            except Exception as e:
                failed_count += 1
                print(f"❌ Failed to upload {file.name}: {e}\n")
    
    # Save all URLs to files
    if cdn_urls:
        save_cdn_urls(cdn_urls)
    
    # Print summary
    print("\n" + "="*50)
    print("📊 UPLOAD SUMMARY")
    print("="*50)
    print(f"✅ Successfully uploaded: {uploaded_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📝 Total URLs saved: {len(cdn_urls)}")
    print("="*50)

if __name__ == "__main__":
    main()
