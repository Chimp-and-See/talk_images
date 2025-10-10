import os
import shutil
from pathlib import Path
import tempfile
import pytest

from scripts.process_images import process_directory


def create_dummy_png(path, width=10, height=10, color=(255, 0, 0)):
    from PIL import Image
    im = Image.new('RGB', (width, height), color)
    im.save(path, 'PNG')


def test_resize_and_jpg_creation(tmp_path):
    inp = tmp_path / 'in'
    out = tmp_path / 'out'
    inp.mkdir()
    out.mkdir()

    # create a reasonably sized PNG that will exceed a small limit when saved
    big = inp / 'big.png'
    create_dummy_png(big, width=2000, height=2000)  # large image

    os.environ['SIZE_LIMIT_KB'] = '150'
    process_directory(str(inp), str(out), size_limit_kb=150, verbose=False)

    out_files = list(out.iterdir())
    assert any(p.suffix.lower() == '.jpg' for p in out_files), 'No JPG output found for large image'
    # Check original removed
    assert not big.exists()


def test_keep_small_file(tmp_path):
    inp = tmp_path / 'in'
    out = tmp_path / 'out'
    inp.mkdir()
    out.mkdir()

    small = inp / 'small.png'
    create_dummy_png(small, width=10, height=10)

    os.environ['SIZE_LIMIT_KB'] = '150'
    process_directory(str(inp), str(out), size_limit_kb=150, verbose=False)

    assert (out / 'small.png').exists()
    # original removed
    assert not small.exists()
