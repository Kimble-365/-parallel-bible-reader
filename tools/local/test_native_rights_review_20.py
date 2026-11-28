"""Exercise evidence tampering, stale identity and out-of-root rejection."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from verify_native_rights_review_20 import verify


class ReviewChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / 'editor-notes/research/native-notice-review-20.json'
        self.path.parent.mkdir(parents=True)
        lock = b'[[package]]\nname="sample"\nversion="1.0.0"\nchecksum="abc"\n'
        lp = self.root / 'apps/native-20/src-tauri/Cargo.lock'
        lp.parent.mkdir(parents=True); lp.write_bytes(lock)
        body = b'Original notice\r\n'
        ep = self.root / 'editor-notes/research/native-notice-evidence/sample.txt'
        ep.parent.mkdir(); ep.write_bytes(body)
        rev = '1' * 40
        self.review = {'lock_sha256': hashlib.sha256(lock).hexdigest(), 'public_release_approved': False,
            'sources': [{'path': str(ep.relative_to(self.root)), 'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest(),
                'git_blob': hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest(),
                'revision': rev, 'repository': 'https://github.com/example/source', 'upstream_path': 'LICENSE',
                'url': 'https://raw.githubusercontent.com/example/source/'+rev+'/LICENSE'}],
            'cases': [{'name': 'sample', 'version': '1.0.0', 'archive_sha256': 'abc', 'repository': 'https://github.com/example/source',
                'vcs': {'git': {'sha1': rev}}, 'distribution_clearance': False, 'status': 'open', 'next_action': 'Review', 'source_ids': [0]}]}

    def run_review(self, change=None):
        r = copy.deepcopy(self.review)
        if change: change(r)
        self.path.write_text(json.dumps(r), encoding='utf-8')
        return verify(self.root)

    def test_original_bytes(self):
        self.assertEqual(self.run_review()['cases'], 1)
    def test_tampered_notice(self):
        (self.root/self.review['sources'][0]['path']).write_text('Altered notice')
        with self.assertRaisesRegex(ValueError, 'bytes differ'): self.run_review()
    def test_stale_lock(self):
        with self.assertRaisesRegex(ValueError, 'lock identity'): self.run_review(lambda r:r.update(lock_sha256='stale'))
    def test_path_escape(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe'): self.run_review(lambda r:r['sources'][0].update(path='../outside'))
    def test_revision_mismatch(self):
        with self.assertRaisesRegex(ValueError, 'archived VCS'): self.run_review(lambda r:r['cases'][0]['vcs']['git'].update(sha1='2'*40))
    def test_approval_rejected(self):
        with self.assertRaisesRegex(ValueError, 'clearance'): self.run_review(lambda r:r.update(public_release_approved=True))


if __name__ == '__main__':
    unittest.main()
