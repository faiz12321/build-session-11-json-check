from unittest import mock
import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path

import jsoncheck
import make_sample


class CheckTests(unittest.TestCase):
    def test_good_object(self):
        problems, top = jsoncheck.check(b'{"a": 1, "b": [1, 2]}')
        self.assertEqual((problems, top), ([], "an object with 2 names"))

    def test_top_level_kinds(self):
        for data, expected in ((b"[1, 2, 3]", "an array with 3 items"), (b'"hi"', "a string"), (b"12", "a number"),
                               (b"true", "true or false"), (b"null", "null")):
            self.assertEqual(jsoncheck.check(data), ([], expected))

    def test_missing_comma_gives_line_column_and_pointer(self):
        problems, _ = jsoncheck.check(b'{\n  "a": 1\n  "b": 2\n}')
        self.assertEqual(len(problems), 1)
        self.assertIn("Line 3, column 3: Expecting ',' delimiter", problems[0])
        self.assertIn('"b": 2', problems[0])
        self.assertIn("^", problems[0])

    def test_trailing_comma_is_a_problem(self):
        problems, _ = jsoncheck.check(b'{"a": 1,}')
        self.assertEqual(len(problems), 1)
        self.assertIn("Line 1", problems[0])

    def test_single_quotes_and_comments_are_problems(self):
        self.assertEqual(len(jsoncheck.check(b"{'a': 1}")[0]), 1)
        self.assertEqual(len(jsoncheck.check(b'{"a": 1} // note')[0]), 1)

    def test_empty_file_is_a_problem(self):
        problems, _ = jsoncheck.check(b"")
        self.assertEqual(len(problems), 1)
        self.assertIn("Line 1, column 1", problems[0])

    def test_repeated_name_in_one_object(self):
        problems, top = jsoncheck.check(b'{"a": 1, "b": 2, "a": 3}')
        self.assertEqual(len(problems), 1)
        self.assertIn("'a'", problems[0])
        self.assertEqual(top, "an object with 2 names")

    def test_same_name_in_different_objects_is_fine(self):
        self.assertEqual(jsoncheck.check(b'[{"a": 1}, {"a": 2}]')[0], [])

    def test_repeated_name_in_nested_object(self):
        self.assertEqual(len(jsoncheck.check(b'{"x": {"k": 1, "k": 2}}')[0]), 1)

    def test_nan_and_infinity_are_refused(self):
        for word in (b"NaN", b"Infinity", b"-Infinity"):
            problems, _ = jsoncheck.check(b'{"v": ' + word + b"}")
            self.assertEqual(len(problems), 1, word)
            self.assertIn(word.decode(), problems[0])

    def test_bom_is_reported_and_rest_is_still_checked(self):
        self.assertEqual(len(jsoncheck.check(b'\xef\xbb\xbf{"ok": true}')[0]), 1)
        problems, _ = jsoncheck.check(b'\xef\xbb\xbf{"ok": }')
        self.assertEqual(len(problems), 2)

    def test_not_utf8(self):
        problems, _ = jsoncheck.check(b'{"a": "caf\xe9"}')
        self.assertEqual(len(problems), 1)
        self.assertIn("UTF-8", problems[0])

    def test_deep_nesting_does_not_crash(self):
        problems, _ = jsoncheck.check(b"[" * 100000 + b"]" * 100000)
        self.assertEqual(len(problems), 1)

    def test_windows_line_endings_keep_line_numbers(self):
        problems, _ = jsoncheck.check(b'{\r\n  "a": 1\r\n  "b": 2\r\n}')
        self.assertIn("Line 3", problems[0])


class MainTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def run_main(self, args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = jsoncheck.main(["jsoncheck.py"] + args)
        return code, buf.getvalue()

    def test_sample_files(self):
        folder = make_sample.make(self.dir / "sample")
        self.assertEqual(self.run_main([str(folder / "good.json")])[0], 0)
        for name in ("broken.json", "repeated.json", "bom.json"):
            code, out = self.run_main([str(folder / name)])
            self.assertEqual(code, 1, name)
            self.assertIn("Problems found: 1", out)

    def test_good_file_message(self):
        folder = make_sample.make(self.dir / "sample")
        code, out = self.run_main([str(folder / "good.json")])
        self.assertIn("No problems found by these checks. Top level: an object with 3 names.", out)

    def test_missing_file_folder_and_no_argument(self):
        self.assertEqual(self.run_main([str(self.dir / "nothing.json")])[0], 2)
        self.assertEqual(self.run_main([str(self.dir)])[0], 2)
        self.assertEqual(self.run_main([])[0], 2)

    def test_file_not_changed(self):
        folder = make_sample.make(self.dir / "sample")
        path = folder / "broken.json"
        before = (path.read_bytes(), os.stat(path).st_mtime_ns)
        self.run_main([str(path)])
        self.assertEqual((path.read_bytes(), os.stat(path).st_mtime_ns), before)


class SetupSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sample = self.root / 'sample'

    def test_existing_folder_preserves_nested_bytes_and_metadata(self):
        (self.sample / 'nested').mkdir(parents=True)
        keep = self.sample / 'nested' / 'keep.bin'
        keep.write_bytes(b'KEEP')
        before = (keep.read_bytes(), keep.stat().st_mtime_ns)
        with self.assertRaises(FileExistsError):
            make_sample.make(self.sample)
        self.assertEqual(before, (keep.read_bytes(), keep.stat().st_mtime_ns))
        self.assertEqual(sorted(p.relative_to(self.sample).as_posix() for p in self.sample.rglob('*')), ['nested','nested/keep.bin'])

    def test_existing_file_preserved(self):
        self.sample.write_bytes(b'KEEP')
        before = (self.sample.read_bytes(), self.sample.stat().st_mtime_ns)
        with self.assertRaises(FileExistsError):
            make_sample.make(self.sample)
        self.assertEqual(before, (self.sample.read_bytes(), self.sample.stat().st_mtime_ns))

    def test_repeat_setup_preserves_generated_bytes_and_metadata(self):
        make_sample.make(self.sample)
        before = {p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in self.sample.iterdir()}
        with self.assertRaises(FileExistsError):
            make_sample.make(self.sample)
        self.assertEqual(before, {p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in self.sample.iterdir()})

    def test_cli_refuses_without_replacing(self):
        import shutil, subprocess, sys
        script = self.root / 'make_sample.py'
        shutil.copyfile(Path(__file__).resolve().parent / 'make_sample.py', script)
        self.sample.mkdir()
        keep = self.sample / 'keep'
        keep.write_bytes(b'KEEP')
        result = subprocess.run([sys.executable,str(script)],capture_output=True,text=True)
        self.assertEqual(result.returncode,1)
        self.assertIn('Nothing was replaced or deleted',result.stderr)
        self.assertEqual(keep.read_bytes(),b'KEEP')



class PathSafety(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.root=self.base/'sample'
        make_sample.make(self.root);self.file=self.root/'good.json'
    def link(self,path,target,directory=False):
        try:path.symlink_to(target,target_is_directory=directory)
        except OSError:self.skipTest('Symlink creation unavailable')
    def code(self,path):
        with contextlib.redirect_stdout(io.StringIO()) as out:code=jsoncheck.main(['jsoncheck.py',str(path)])
        return code,out.getvalue()
    def test_file_link_refuses(self):
        p=self.base/'linked';self.link(p,self.file)
        with self.assertRaises(OSError):jsoncheck.safe_input(p)
        self.assertEqual(self.code(p)[0],2)
    def test_linked_ancestor_refuses(self):
        p=self.base/'linked';self.link(p,self.root,True)
        self.assertEqual(self.code(p/'good.json')[0],2)
    def test_dangling_link_refuses(self):
        p=self.base/'linked';self.link(p,self.base/'missing')
        self.assertEqual(self.code(p)[0],2)
    def test_self_loop_refuses(self):
        p=self.base/'linked';self.link(p,p)
        self.assertEqual(self.code(p)[0],2)
    def test_hardlink_refuses(self):
        p=self.base/'hard';os.link(self.file,p)
        self.assertEqual(self.code(p)[0],2)
    def test_pipe_refuses_without_blocking(self):
        if not hasattr(os,'mkfifo'):self.skipTest('Unix pipe unavailable')
        p=self.base/'pipe';os.mkfifo(p)
        self.assertEqual(self.code(p)[0],2)
    def test_directory_refuses(self):self.assertEqual(self.code(self.root)[0],2)
    def test_traversal_refuses(self):self.assertEqual(self.code(self.root/'..'/'sample'/'good.json')[0],2)
    def test_reparse_attribute_refuses(self):
        real=Path.lstat;target=self.file
        def fake(path,*args,**kwargs):
            value=real(path,*args,**kwargs)
            if path==target:return type('Reparse',(),{'st_mode':value.st_mode,'st_file_attributes':0x400})()
            return value
        with mock.patch.object(Path,'lstat',fake):self.assertEqual(self.code(self.file)[0],2)
    def test_metadata_failure_nonzero(self):
        with mock.patch.object(Path,'lstat',side_effect=OSError('forced metadata error')):
            code,text=self.code(self.file);self.assertEqual(code,2);self.assertIn('forced metadata error',text)
    def test_setup_linked_parent_refuses(self):
        p=self.base/'linked';self.link(p,self.root,True)
        with self.assertRaises(OSError):make_sample.make(p/'new')
        self.assertFalse((self.root/'new').exists())
    def test_setup_traversal_refuses(self):
        with self.assertRaises(OSError):make_sample.make(self.root/'..'/'new')


if __name__ == "__main__":
    unittest.main()
