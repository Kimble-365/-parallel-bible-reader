"""Target graph identity, reachability and failed command contracts."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from native_target_rights_20 import parse_tree, classify, collect, PROJECT


class TargetGraphs(unittest.TestCase):
    def setUp(self):
        self.records = {('sample', '1.0.0'): {'archive_sha256': 'a', 'source_archive_url': 'https://example.invalid/a', 'declared_license': 'MIT'},
                        ('sample', '2.0.0'): {'archive_sha256': 'b', 'source_archive_url': 'https://example.invalid/b', 'declared_license': 'MPL-2.0'}}
    def test_duplicate_and_distinct_versions(self):
        tree = 'parallel-bible-reader v2.0.0 (/tmp/project)\nsample v1.0.0\nsample v1.0.0 (*)\nsample v2.0.0\n'
        self.assertEqual(len(parse_tree(tree)), 3)
    def test_unknown_and_empty_output_rejected(self):
        for text in ('', 'cargo command failed', 'parallel-bible-reader v2.0.0\n? unknown'):
            with self.assertRaises(ValueError): parse_tree(text)
    def test_locations(self):
        normal = {PROJECT, ('sample','1.0.0')}
        result = classify(normal, normal|{('sample','2.0.0')}, self.records, set(self.records)|{('absent','1.0.0')})
        self.assertEqual([p['location'] for p in result['notice_cases']], ['absent','normal_graph','build_graph_only'])
        self.assertEqual(result['mpl_cases'][0]['location'], 'build_graph_only')
    def test_unknown_archive_and_subset_rejected(self):
        with self.assertRaises(ValueError): classify({PROJECT}, {PROJECT,('unknown','1.0')}, self.records, set())
        with self.assertRaises(ValueError): classify({PROJECT,('sample','1.0.0')}, {PROJECT}, self.records, set())
    def test_failed_cargo_cannot_be_reported_absent(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); lock = root/'apps/native-20/src-tauri/Cargo.lock'; lock.parent.mkdir(parents=True);lock.write_bytes(b'lock')
            inventory = root/'inventory.json';inventory.write_text(json.dumps({'lock_sha256':hashlib.sha256(b'lock').hexdigest(), 'all_archive_checksums_verified':True, 'packages':[], 'notice_gaps':[]}))
            def fail(*args, **kwargs): raise subprocess.CalledProcessError(1, args[0])
            with self.assertRaises(subprocess.CalledProcessError): collect(root, inventory, root/'out', 'fixture', run=fail)
            self.assertFalse((root/'out/TARGET-RIGHTS.json').exists())


if __name__ == '__main__': unittest.main()
