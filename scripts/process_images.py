import os
from PIL import Image

UPLOAD_DIR = "upload_here"
OUTPUT_DIR = "images"
SIZE_LIMIT = int(os.environ.get("SIZE_LIMIT_KB", 150)) * 1024  # in bytes

os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in os.listdir(UPLOAD_DIR):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.isfile(filepath):
        continue

    try:
        with Image.open(filepath) as img:
            original_size = os.path.getsize(filepath)
            if original_size > SIZE_LIMIT:
                # Resize and convert to JPEG
                img = img.convert("RGB")
                output_path = os.path.join(OUTPUT_DIR, os.path.splitext(filename)[0] + ".jpg")
                quality = 85
                while True:
                    img.save(output_path, "JPEG", quality=quality)
                    if os.path.getsize(output_path) <= SIZE_LIMIT or quality <= 10:
                        break
                    quality -= 5
            else:
                # Save without resizing, retain original format
                output_path = os.path.join(OUTPUT_DIR, filename)
                img.save(output_path)

        os.remove(filepath)

    except Exception as e:
        print(f"Skipping {filename}: {e}")
