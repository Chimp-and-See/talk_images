import os
from PIL import Image

IMAGE_DIR = "images"
SIZE_LIMIT = int(os.environ.get("SIZE_LIMIT_KB", 150)) * 1024

for filename in os.listdir(IMAGE_DIR):
    filepath = os.path.join(IMAGE_DIR, filename)
    if not os.path.isfile(filepath):
        continue

    try:
        with Image.open(filepath) as img:
            original_size = os.path.getsize(filepath)
            if original_size > SIZE_LIMIT:
                img = img.convert("RGB")
                output_path = os.path.join(IMAGE_DIR, os.path.splitext(filename)[0] + ".jpg")
                quality = 85
                while True:
                    img.save(output_path, "JPEG", quality=quality)
                    if os.path.getsize(output_path) <= SIZE_LIMIT or quality <= 10:
                        break
                    quality -= 5
                os.remove(filepath)
            else:
                # Keep original format and name
                pass
    except Exception as e:
        print(f"Error processing {filename}: {e}")
