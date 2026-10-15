import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('build', Path(__file__).resolve().parents[1] / 'scripts/build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = build.SKETCH, build.OUT
        build.SKETCH = Path(self.tmp.name) / 'sketch'
        build.OUT = Path(self.tmp.name) / 'out'
        build.SKETCH.mkdir()
        (build.SKETCH / 'firmware_version.h').write_text('#define FW_VERSION "0.1.0"')

    def tearDown(self):
        build.SKETCH, build.OUT = self.old
        self.tmp.cleanup()

    def test_fresh_identity_even_within_same_second(self):
        self.assertNotEqual(build.generate()['marker'], build.generate()['marker'])

    def test_valid_binary_manifest(self):
        identity = build.generate()
        binary = build.OUT / 'app.bin'
        binary.write_bytes(b'prefix' + identity['marker'].encode() + b'suffix')
        manifest = build.verify(identity, binary)
        self.assertEqual(len(manifest['sha256']), 64)
        self.assertEqual(manifest['bytes'], binary.stat().st_size)

    def test_missing_identity_rejected(self):
        identity = build.generate()
        binary = build.OUT / 'app.bin'
        binary.write_bytes(b'no identity')
        with self.assertRaisesRegex(ValueError, 'Missing or stale'):
            build.verify(identity, binary)

    def test_old_binary_rejected(self):
        old = build.generate()
        binary = build.OUT / 'app.bin'
        binary.write_bytes(old['marker'].encode())
        with self.assertRaisesRegex(ValueError, 'Missing or stale'):
            build.verify(build.generate(), binary)

    def test_version_changed_rejected(self):
        identity = build.generate()
        (build.SKETCH / 'firmware_version.h').write_text('#define FW_VERSION "0.2.0"')
        with self.assertRaisesRegex(ValueError, 'Version changed'):
            build.verify(identity, build.OUT / 'app.bin')

if __name__ == '__main__':
    unittest.main()
