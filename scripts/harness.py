import argparse
import os
from pathlib import Path
from process_images import process_directory


def run(input_dir, output_dir, size_limit_kb=None):
    if size_limit_kb is not None:
        os.environ['SIZE_LIMIT_KB'] = str(size_limit_kb)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    process_directory(input_dir, output_dir, size_limit_kb=size_limit_kb)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--size-limit-kb', type=int)
    args = parser.parse_args()
    run(args.input, args.output, args.size_limit_kb)
