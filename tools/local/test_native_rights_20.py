"""Real tar/lock fixtures exercise integrity, original notice bytes and review gates."""
import io, json, subprocess, sys, tarfile, tempfile, unittest
from pathlib import Path
from audit_native_rights_20 import audit, write_report, sha, REGISTRY

class RightsAudit(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cache = self.root / 'cache' / 'test-registry'
        self.cache.mkdir(parents=True)
        self.archive = self.cache / 'sample-1.0.0.crate'
        self.metadata = self.root / 'metadata.json'
        self.lock = self.root / 'Cargo.lock'
        self.body = 'Copyright © Fixture Author\r\nPermission fixture; preserve these bytes.\r\n'.encode()

    def fixture(self, notice='LICENSE', link=False):
        with tarfile.open(self.archive, 'w:gz') as tar:
            files = [('sample-1.0.0/src/lib.rs', b'// Source fixture only\n')]
            if notice is not None:
                files.append(('sample-1.0.0/' + notice, self.body))
            for path, body in files:
                item = tarfile.TarInfo(path)
                item.size = len(body)
                if link and path.endswith('LICENSE'):
                    item.type = tarfile.SYMTYPE
                    item.linkname = '../../outside-notice'
                    item.size = 0
                    tar.addfile(item)
                else:
                    tar.addfile(item, io.BytesIO(body))
        self.metadata.write_text(json.dumps({'packages': [
            {'name': 'parallel-bible-reader', 'version': '2.0.0', 'source': None},
            {'name': 'sample', 'version': '1.0.0', 'source': REGISTRY, 'license': 'MIT', 'repository': 'https://example.invalid/source'}]}))
        self.lock.write_text('version = 4\n[[package]]\nname = "parallel-bible-reader"\nversion = "2.0.0"\n[[package]]\nname = "sample"\nversion = "1.0.0"\nsource = ' + json.dumps(REGISTRY) + '\nchecksum = ' + json.dumps(sha(self.archive.read_bytes())) + '\n')

    def run_audit(self):
        return audit(self.metadata, self.lock, self.root / 'cache', 'fixture-commit')

    def test_original_bytes_and_repeat_output(self):
        self.fixture()
        report, texts = self.run_audit()
        self.assertEqual(report['verified_registry_archives'], 1)
        self.assertTrue(report['notice_file_inventory_complete'])
        self.assertFalse(report['public_release_approved'])
        for folder in ['one', 'two']:
            write_report(report, texts, self.root / folder)
        for filename in ['DEPENDENCY-RIGHTS.json', 'ARCHIVED-NOTICES.txt', 'SHA256SUMS']:
            self.assertEqual((self.root / 'one' / filename).read_bytes(), (self.root / 'two' / filename).read_bytes())
        self.assertIn(self.body, (self.root / 'one/ARCHIVED-NOTICES.txt').read_bytes())

    def test_altered_archive_is_rejected(self):
        self.fixture()
        self.archive.write_bytes(self.archive.read_bytes() + b'changed')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            self.run_audit()

    def test_stale_metadata_is_rejected(self):
        self.fixture()
        m = json.loads(self.metadata.read_text());m['packages'][1]['version'] = '2.0.0';self.metadata.write_text(json.dumps(m))
        with self.assertRaisesRegex(ValueError, 'identities differ'):
            self.run_audit()

    def test_path_traversal_is_not_read_or_extracted(self):
        self.fixture('../LICENSE')
        with self.assertRaisesRegex(ValueError, 'Unsafe/nonmatching'):
            self.run_audit()
        self.assertFalse((self.root / 'LICENSE').exists())

    def test_notice_symlink_is_reviewed_without_dereferencing(self):
        self.fixture(link=True)
        report, texts = self.run_audit()
        self.assertFalse(report['notice_file_inventory_complete'])
        self.assertEqual(report['packages'][0]['unresolved_notice_links'], ['LICENSE'])
        self.assertEqual(texts, {})

    def test_nested_spdx_license_text_is_detected(self):
        self.fixture('LICENSES/MIT.txt')
        report, texts = self.run_audit()
        self.assertTrue(report['notice_file_inventory_complete'])
        self.assertEqual(texts[sha(self.body)], self.body)

    def test_declared_license_does_not_clear_missing_notice_gate(self):
        self.fixture(None)
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('audit_native_rights_20.py')),
            '--metadata', str(self.metadata), '--lock', str(self.lock), '--cache', str(self.root / 'cache'),
            '--source-commit', 'fixture', '--out', str(self.root / 'out'), '--require-notices'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        report = json.loads((self.root / 'out/DEPENDENCY-RIGHTS.json').read_text())
        self.assertEqual(report['status'], 'notice-source-review-required')
        self.assertEqual(report['notice_gaps'][0]['declared_license'], 'MIT')

if __name__ == '__main__':
    unittest.main()
