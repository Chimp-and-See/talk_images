import os
import shutil
from pathlib import Path
from PIL import Image

DEFAULT_SIZE_LIMIT_KB = int(os.environ.get("SIZE_LIMIT_KB", "150"))


def process_directory(input_dir, output_dir, size_limit_kb=None, verbose=True):
    """Process images from input_dir and write outputs to output_dir.

    Rules:
    - Images larger than size_limit_kb are resized/compressed and saved as JPEG
      with the same base filename and a .jpg extension.
    - Images smaller than or equal to the limit are copied unchanged, retaining
      their original extension and format.
    - After a successful processed copy is written to output_dir, the original
      input file is deleted.

    Returns None. Prints per-file logs when verbose=True.
    """
    size_kb = size_limit_kb if size_limit_kb is not None else DEFAULT_SIZE_LIMIT_KB
    size_limit = int(size_kb) * 1024

    inp = Path(input_dir)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for item in inp.iterdir():
        if not item.is_file():
            continue

        try:
            original_size = item.stat().st_size

            if original_size > size_limit:
                # Resize/compress -> save as JPEG
                with Image.open(item) as img:
                    img = img.convert("RGB")
                    base = item.stem
                    out_path = out / f"{base}.jpg"
                    temp_path = out / f".tmp_{out_path.name}"
                    quality = 85
                    while True:
                        img.save(temp_path, "JPEG", quality=quality)
                        if temp_path.stat().st_size <= size_limit or quality <= 10:
                            break
                        quality -= 5
                    temp_path.replace(out_path)

                if verbose:
                    print(f"Resized {item.name} ({original_size} bytes) -> {out_path.name} ({out_path.stat().st_size} bytes)")

            else:
                # Keep original format
                out_path = out / item.name
                shutil.copy2(item, out_path)
                if verbose:
                    print(f"Kept {item.name} ({original_size} bytes) -> {out_path.name}")

            # Delete original input file after successful processing
            item.unlink()

        except Exception as e:
            # Do not delete the input file on error; print and continue
            print(f"Error processing {item.name}: {e}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process images from an input dir into an output dir.')
    parser.add_argument('--input', '-i', required=True, help='Input directory containing images to process')
    parser.add_argument('--output', '-o', required=True, help='Output directory to write processed images')
    parser.add_argument('--size-limit-kb', type=int, help='Size limit in KB (overrides env var)')

    args = parser.parse_args()
    process_directory(args.input, args.output, size_limit_kb=args.size_limit_kb)
