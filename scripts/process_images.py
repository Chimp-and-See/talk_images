import os
from PIL import Image
import shutil

# 🔧 Configurable size limit in bytes
SIZE_LIMIT = 150 * 1024  # 150KB

# 📁 Define folders
upload_folder = "upload_here"
output_folder = "images"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Process each file in the upload folder
for filename in os.listdir(upload_folder):
    file_path = os.path.join(upload_folder, filename)

    # Skip non-files
    if not os.path.isfile(file_path):
        continue

    # Check file size
    file_size = os.path.getsize(file_path)

    # Open image
    try:
        with Image.open(file_path) as img:
            if file_size > SIZE_LIMIT:
                # Resize image by reducing quality until under size limit
                quality = 85
                resized_path = os.path.join(output_folder, os.path.splitext(filename)[0] + ".jpg")
                while True:
                    img.convert("RGB").save(resized_path, format="JPEG", quality=quality)
                    if os.path.getsize(resized_path) <= SIZE_LIMIT or quality <= 10:
                        break
                    quality -= 5
            else:
                # Copy image as-is to output folder
                output_path = os.path.join(output_folder, filename)
                shutil.copy2(file_path, output_path)
    except Exception as e:
        print(f"Skipping {filename}: {e}")
        continue

    # Delete original file
    os.remove(file_path)
