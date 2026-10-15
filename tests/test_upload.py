"""No hardware: verify explicit erase mode and that all guards precede erasure."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import upload

class UploadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name)
        data = b'test-fresh-marker'
        (self.out / 'app.bin').write_bytes(data)
        self.images = {'application': {'file': 'app.bin', 'offset': 0x90000}}
        self.manifest = {'fqbn': upload.build.FQBN, 'version': '0.2.0', 'binary': 'app.bin',
                         'marker': 'test-fresh-marker', 'sha256': hashlib.sha256(data).hexdigest(),
                         'images': self.images}
        self.save_manifest()

    def save_manifest(self):
        (self.out / 'manifest.json').write_text(json.dumps(self.manifest))

    def tearDown(self):
        self.tmp.cleanup()

    def invoke(self, probe='ESP32-S3\nDetected flash size: 16MB', args=None):
        if args is None:
            args = ['--erase-all']
        with patch.object(sys, 'argv', ['upload.py', '--port', 'COM10', '--esptool', 'esptool'] + args), \
             patch.object(upload.build, 'OUT', self.out), \
             patch.object(upload.build, 'version', return_value='0.2.0'), \
             patch.object(upload.build, 'verify_bundle', return_value=self.images), \
             patch.object(upload.subprocess, 'check_output', return_value=probe), \
             patch.object(upload.subprocess, 'run') as run, \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                upload.main()
            except SystemExit as error:
                return error, run.call_args_list
            return None, run.call_args_list

    def test_explicit_erase_precedes_write(self):
        error, calls = self.invoke()
        self.assertIsNone(error)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0].args[0][-1], 'erase-flash')
        self.assertIn('write-flash', calls[1].args[0])

    def test_wrong_chip_never_erases(self):
        error, calls = self.invoke('ESP32\nDetected flash size: 16MB')
        self.assertIsNotNone(error)
        self.assertEqual(calls, [])

    def test_bad_hash_never_erases(self):
        self.manifest['sha256'] = 'bad'
        self.save_manifest()
        error, calls = self.invoke()
        self.assertIsNotNone(error)
        self.assertEqual(calls, [])

    def test_missing_mode_never_erases(self):
        error, calls = self.invoke(args=[])
        self.assertIsNotNone(error)
        self.assertEqual(calls, [])

if __name__ == '__main__':
    unittest.main()
