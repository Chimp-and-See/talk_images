import os, json, hashlib, shutil, glob, time
from PIL import Image, ImageOps
import yaml

INCOMING = "incoming"
FULL_DIR = "images/full"
THUMB_DIR = "images/thumbs"
INDEX = "images/index.json"
ALT_TEXT_FILE = "metadata/alt-text.yaml"

MAX_FULL_W = 1600  # px, adjust as needed
MAX_THUMB_W = 400

os.makedirs(FULL_DIR, exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)
os.makedirs("metadata", exist_ok=True)

# Load alt-text map if present
alt_map = {}
if os.path.exists(ALT_TEXT_FILE):
    with open(ALT_TEXT_FILE, "r", encoding="utf-8") as f:
        alt_map = yaml.safe_load(f) or {}

def sha256_of_file(path, chunk=8192):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()[:16]

def process_one(src_path):
    base = os.path.basename(src_path)
    stem, ext = os.path.splitext(base)
    ext = ext.lower()

    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        return None

    # Hash for content-addressed filename (guards against dup names)
    filehash = sha256_of_file(src_path)
    full_name = f"{stem}.{filehash}{ext}"
    thumb_name = f"{stem}.{filehash}.thumb{ext}"

    # Open and convert
    im = Image.open(src_path).convert("RGB")

    # Full size
    full = ImageOps.exif_transpose(im)
    if full.width > MAX_FULL_W:
        h = round(full.height * (MAX_FULL_W / full.width))
        full = full.resize((MAX_FULL_W, h), Image.LANCZOS)
    full_out = os.path.join(FULL_DIR, full_name)
    full.save(full_out, quality=88, optimize=True)

    # Thumb
    thumb = ImageOps.exif_transpose(im)
    if thumb.width > MAX_THUMB_W:
        h = round(thumb.height * (MAX_THUMB_W / thumb.width))
        thumb = thumb.resize((MAX_THUMB_W, h), Image.LANCZOS)
    thumb_out = os.path.join(THUMB_DIR, thumb_name)
    thumb.save(thumb_out, quality=80, optimize=True)

    # Return index record
    alt = alt_map.get(base) or alt_map.get(f"{stem}{ext}") or ""
    ts = int(time.time())
    return {
        "original_name": base,
        "full": f"{FULL_DIR}/{full_name}",
        "thumb": f"{THUMB_DIR}/{thumb_name}",
        "width_full": full.width,
        "height_full": full.height,
        "width_thumb": thumb.width,
        "height_thumb": thumb.height,
        "alt": alt,
        "timestamp": ts,
    }

# Load existing index
index = []
if os.path.exists(INDEX):
    with open(INDEX, "r", encoding="utf-8") as f:
        try:
            index = json.load(f)
        except Exception:
            index = []

# Process new files
incoming_files = sorted(glob.glob(os.path.join(INCOMING, "*")))
new_records = []
for path in incoming_files:
    rec = process_one(path)
    if rec:
        new_records.append(rec)

# Update index & write
if new_records:
    index.extend(new_records)
    with open(INDEX, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

# Move processed files to an archive (keeps /incoming clean)
ARCHIVE = "incoming-archived"
os.makedirs(ARCHIVE, exist_ok=True)
for path in incoming_files:
    dest = os.path.join(ARCHIVE, os.path.basename(path))
    shutil.move(path, dest)
