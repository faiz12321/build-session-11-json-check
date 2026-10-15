"""Makes made-up JSON files in a folder called sample: one good, one with a missing comma,
one with a repeated name, and one that starts with a byte order mark.

Run: python make_sample.py
"""
import sys
from pathlib import Path

FILES = {
    "good.json": b'{\n  "name": "Report",\n  "pages": 12,\n  "draft": true\n}\n',
    "broken.json": b'{\n  "name": "Report",\n  "pages": 12\n  "draft": true\n}\n',
    "repeated.json": b'{"title": "Old", "size": 3, "title": "New"}\n',
    "bom.json": b'\xef\xbb\xbf{"ok": true}\n',
}


def make(folder):
    folder = Path(folder)
    folder.mkdir(exist_ok=True)
    for name, data in FILES.items():
        (folder / name).write_bytes(data)
    return folder


if __name__ == "__main__":
    make(Path(__file__).resolve().parent / "sample")
    print("Made sample/good.json, broken.json, repeated.json and bom.json")
    sys.exit(0)
