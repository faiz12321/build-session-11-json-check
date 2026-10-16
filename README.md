# Check a fictional JSON file

Save three source files in a NEW empty lesson folder.

    python make_sample.py
    python jsoncheck.py sample/broken.json
    python -m unittest -v

Two Windows and two Ubuntu full replays run the exact visible source versions. Final 34 small fixture tests pass (Unix pipe skips on Windows); symlink creation can skip where unavailable. Displayed stdout is first Windows output, not normalized or mixed. Pair differences are unittest time.
Only link/error changes: final reader refuses input/ancestor symbolic links/reparse points, hardlinks, special files and traversal before opening. Metadata/open errors return 2 with readable fallback text. Setup refuses linked parents/traversal and existing sample paths, without reset or deletion. The naive first checker remains fictional-sample-only and must be replaced by the final file.
Original final JSON parsing, UTF-8/BOM, duplicate-name, nonstandard-number, depth and excerpt rules remain unchanged. Original exits remain 0 for no reported problems, 1 for reported problems, 2 for read/usage errors. Passing these checks is not validation of schema, meaning, number ranges, or acceptance by other programs.
The final checker has no write/move/delete/network code, but reads the entire file into memory. No file-size/time/resource limit, atomic snapshot or hostile-race defense. Stop editors/sync. Paths and error excerpts can reveal private data; use fictional files only for this lesson. Small fixtures are not proof for every filesystem. No desktop Windows/macOS recording. Recorder removes only its own temporary fixture folder. Decisions and feedback are teaching text, not recorded output.

MIT code. Python separately licensed/not included.

Windows pair: https://github.com/faiz12321/lesson-lab/actions/runs/38970467744
Ubuntu pair: https://github.com/faiz12321/lesson-lab/actions/runs/38970568349

References: https://docs.python.org/3/library/os.html and https://docs.python.org/3/library/json.html
