import os, re, json, time, hashlib, io
from PIL import Image, ImageOps
import requests, yaml

ISSUE_BODY   = os.environ["ISSUE_BODY"]
ISSUE_AUTHOR = os.environ["ISSUE_AUTHOR"]

# Find pasted/dragged attachments (hosted by GitHub)
ATTACH_URLS = re.findall(r'(https://user-images\.githubusercontent\.com/[^\s)]+)', ISSUE_BODY)

# Try to pull a free-text alt from the form (optional)
ALT_RE = re.compile(r'Alt text / caption.*?\n\n([\s\S]*?)\n(?:\w+:|$)', re.M)
m = ALT_RE.search(ISSUE_BODY)
ALT_TEXT = (m.group(1).strip() if m else "")[:300]

# Output
OUT_DIR = "images"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs("metadata", exist_ok=True)

# Limits / behavior
MAX_FILES   = 5
MAX_BYTES   = 6_000_000    # ~6 MB per file from the issue attachments
ALLOWED_EXT = (".jpg", ".jpeg", ".png", ".webp")

# --- Resize policy ---
# Set to False if you want to keep originals (still normalized to JPEG below unless you change SAVE_FORMAT)
RESIZE    = True          # toggle this to False if you don't need space savings
MAX_WIDTH = 1600          # only used if RESIZE is True
SAVE_FORMAT = "JPEG"      # "JPEG" yields big savings; change to None to preserve original format

def sha16(b): return hashlib.sha256(b).hexdigest()[:16]

records = []
for url in ATTACH_URLS[:MAX_FILES]:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    if len(r.content) > MAX_BYTES:
        continue

    # Load image
    im = Image.open(io.BytesIO(r.content))
    im = ImageOps.exif_transpose(im).convert("RGB")

    # Optionally resize to save repo space/bandwidth
    if RESIZE and im.width > MAX_WIDTH:
        new_h = round(im.height * (MAX_WIDTH / im.width))
        im = im.resize((MAX_WIDTH, new_h), Image.LANCZOS)

    # Name by time + content hash for immutability
    base = f"{int(time.time())}-{sha16(r.content)}"
    # Choose extension
    if SAVE_FORMAT == "JPEG":
        fname = f"{base}.jpg"
        out_path = os.path.join(OUT_DIR, fname)
        im.save(out_path, format="JPEG", quality=88, optimize=True)
    else:
        # preserve original extension based on URL, default .png
        ext = ".png"
        for e in ALLOWED_EXT:
            if url.lower().endswith(e): ext = e; break
        fname = f"{base}{ext}"
        out_path = os.path.join(OUT_DIR, fname)
        im.save(out_path, optimize=True)

    records.append({
        "uploader": ISSUE_AUTHOR,
        "source_url": url,
        "path": f"{OUT_DIR}/{fname}",
        "alt": ALT_TEXT,
        "ts": int(time.time())
    })

# Update index.json
index_path = os.path.join("images", "index.json")
index = []
if os.path.exists(index_path):
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
    except Exception:
        index = []
index.extend(records)
with open(index_path, "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

# Stash last ingest for the comment step
with open("metadata/last_ingest.json", "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)
