"""Check a JSON file for mistakes. It only reads the file.

Usage:  python jsoncheck.py FILE
Checks: the text is UTF-8, it has no byte order mark, it follows JSON syntax (as Python's
json module reads it), no name is repeated inside one object, and NaN or Infinity are not used.
It does not check what the data means.
"""
import json
import sys
import stat
from pathlib import Path

def safe_input(value, directory=False):
    path = Path(value).absolute()
    if '..' in path.parts:
        raise OSError('Parent-traversal paths are unsupported.')
    for part in [*reversed(path.parents), path]:
        info = part.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise OSError('Links/reparse points are unsupported.')
    info = path.lstat()
    if directory:
        if not stat.S_ISDIR(info.st_mode):
            raise NotADirectoryError('Expected an ordinary directory.')
    elif not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise OSError('Expected an ordinary singly linked file.')
    return path






BOM = b"\xef\xbb\xbf"


class NotStandard(ValueError):
    pass


def refuse_constant(name):
    raise NotStandard(name)


def show_line(text, error):
    lines = text.split("\n")
    if not 1 <= error.lineno <= len(lines):
        return ""
    line = lines[error.lineno - 1].rstrip("\r").replace("\t", " ")
    start = max(0, error.colno - 30)
    return "\n     " + line[start:start + 70] + "\n     " + " " * (error.colno - 1 - start) + "^"


def describe(value):
    if isinstance(value, dict):
        return f"an object with {len(value)} names"
    if isinstance(value, list):
        return f"an array with {len(value)} items"
    if isinstance(value, str):
        return "a string"
    if isinstance(value, bool):
        return "true or false"
    if value is None:
        return "null"
    return "a number"


def check(data):
    """Return (problems, top-level description). problems is a list of messages."""
    problems = []
    if data.startswith(BOM):
        problems.append("The file starts with a byte order mark (BOM). Python's json module rejects it, and other tools may too.")
        data = data[len(BOM):]
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        problems.append(f"The file is not valid UTF-8 text (first problem at byte {error.start}).")
        return problems, ""
    repeated = []

    def pairs(items):
        seen = set()
        for name, _ in items:
            if name in seen and name not in repeated:
                repeated.append(name)
            seen.add(name)
        return dict(items)

    top = ""
    try:
        top = describe(json.loads(text, object_pairs_hook=pairs, parse_constant=refuse_constant))
    except NotStandard as error:
        problems.append(f"{error} is not allowed in standard JSON, although Python accepts it by default.")
    except json.JSONDecodeError as error:
        problems.append(f"Line {error.lineno}, column {error.colno}: {error.msg}" + show_line(text, error))
    except RecursionError:
        problems.append("The data is nested too deeply for Python to read.")
    for name in repeated:
        problems.append(f"The name {name!r} appears more than once in one object. Python keeps only the last value.")
    return problems, top


def main(argv):
    if len(argv) != 2:
        print("Usage: python jsoncheck.py FILE")
        return 2
    try:
        with open(safe_input(argv[1]), "rb") as handle:
            data = handle.read()
    except OSError as error:
        print(f"Could not read {argv[1]}: {error.strerror or error}")
        return 2
    problems, top = check(data)
    print(f"File: {argv[1]}")
    if not problems:
        print(f"No problems found by these checks. Top level: {top}.")
        return 0
    print(f"Problems found: {len(problems)}")
    for number, message in enumerate(problems, start=1):
        print(f"  {number}. {message}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
