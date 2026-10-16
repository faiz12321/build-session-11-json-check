"""Makes made-up JSON files in a folder called sample: one good, one with a missing comma,
one with a repeated name, and one that starts with a byte order mark.

Run only in a new empty lesson folder: python make_sample.py
Setup refuses existing sample paths and exclusively creates fictional JSON files.
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
    folder.mkdir()
    for name, data in FILES.items():
        with (folder / name).open("xb") as handle:
            handle.write(data)
    return folder


if __name__ == "__main__":
    try:
        make(Path(__file__).resolve().parent / "sample")
    except FileExistsError:
        raise SystemExit("Stopped: sample already exists. Nothing was replaced or deleted.")
    print("Made sample/good.json, broken.json, repeated.json and bom.json")
    sys.exit(0)
