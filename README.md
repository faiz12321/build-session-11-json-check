# Check a JSON file for mistakes

A small read-only Python tool built step by step. Give it a JSON file and it reports mistakes with the line and column where Python's parser found them, a byte order mark, text that is not UTF-8, names repeated inside one object, and NaN or Infinity. It only reads the file.

## Run it

    python make_sample.py                     # makes made-up JSON files in sample/
    python jsoncheck.py sample/broken.json    # report on one file
    python -m unittest -v                     # 22 temporary-fixture tests

On Windows, if `python` is not found, use `py`.

## Files

- `jsoncheck.py` - the tool
- `make_sample.py` - makes four made-up files: good, missing comma, repeated name, byte order mark
- `test_jsoncheck.py` - tests

## Setup safety and evidence

Setup creates only a new sample folder and exclusively writes its four fictional JSON files. It refuses existing paths without resetting or replacing data. Start in a new empty lesson folder. Four added collision/repeat checks preserve nested unrelated bytes and modification times. The checker is unchanged. Source paths can follow links and error reports reveal excerpts and paths. Keep private output private.

Two Windows and two Ubuntu recordings pass all 22 tests. Each platform pair differs only in unittest time. Displays use first Windows output. Versions and test-name rendering can differ. The recorder writes the exact visible first/final versions in its own unique temporary folder and removes only that folder. Setup itself refuses a repeat run. These are limited tests, not proof for all filesystems or JSON-consuming applications.

## Notes

- The tool reports a syntax error at the first place the parser gets stuck. It does not list every syntax mistake in a file, so fix one and run it again.
- Python's json module accepts repeated names (it keeps the last value), NaN and Infinity by default, and rejects a byte order mark. These behaviours are described in the Python documentation (https://docs.python.org/3/library/json.html). This tool reports all three.
- "No problems found by these checks" only means those checks passed. It does not check what the data means, that numbers are in a sensible range, or that another program will accept the file.
- Tested only on small made-up files, not on large or real-world files. Python 3.10 (Linux) and, by GitHub Actions, Python 3.12 on Windows and Ubuntu. Not tested on a Windows 10 or 11 desktop.
- Educational example, no warranty. Use at your own risk.
- Code is MIT licensed (see LICENSE). Python is a separate project with its own license; this repository does not include it.
