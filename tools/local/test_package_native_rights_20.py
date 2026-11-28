"""Source-sidecar byte preservation and corruption/identity gates."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from package_native_rights_20 import build_inputs, write_bundle, verify_bundle, digest, safe_name, PROJECT_FILES, REGISTRY


class SourceBundle(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.identity = {'source_commit':'fixture', 'external_archives':1, 'public_release_approved':False,
                         'actual_shipped_file_assessment_complete':False}
        self.files = {'crates/sample-1.0.0.crate': b'original archive\x00', 'notices/original.txt': '© Author\r\n'.encode()}
    def test_repeat_bytes_and_original_notice(self):
        a, b = self.root/'a.zip', self.root/'b.zip'
        write_bundle(self.files, self.identity, a); write_bundle(self.files, self.identity, b)
        self.assertEqual(a.read_bytes(), b.read_bytes())
        with zipfile.ZipFile(a) as z: self.assertEqual(z.read('notices/original.txt'), self.files['notices/original.txt'])
    def test_altered_member_rejected(self):
        a = self.root/'a.zip'; write_bundle(self.files, self.identity, a)
        with zipfile.ZipFile(a) as z: entries = {n:z.read(n) for n in z.namelist()}
        entries['crates/sample-1.0.0.crate'] = b'changed'
        with zipfile.ZipFile(a,'w') as z:
            for n,b in entries.items(): z.writestr(n,b)
        with self.assertRaisesRegex(ValueError,'checksum'): verify_bundle(a)
    def test_extra_member_rejected(self):
        a = self.root/'a.zip'; write_bundle(self.files,self.identity,a)
        with zipfile.ZipFile(a,'a') as z: z.writestr('unexpected.txt',b'extra')
        with self.assertRaisesRegex(ValueError,'inventory'): verify_bundle(a)
    def test_unsafe_paths(self):
        for name in ('../outside','/absolute','a/../outside','a\\outside','a//b'):
            with self.assertRaises(ValueError): safe_name(name)
    def test_clearance_flag_rejected(self):
        with self.assertRaisesRegex(ValueError,'clearance'):
            write_bundle(self.files,{**self.identity,'public_release_approved':True},self.root/'a.zip')
    def fixture(self):
        for name in PROJECT_FILES:
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'project')
        archive=self.root/'cache/registry/sample-1.0.0.crate';archive.parent.mkdir(parents=True);archive.write_bytes(b'original')
        checksum=digest(archive.read_bytes())
        lock=self.root/'apps/native-20/src-tauri/Cargo.lock'
        lock.write_text('[[package]]\nname="sample"\nversion="1.0.0"\nsource='+json.dumps(REGISTRY)+'\nchecksum='+json.dumps(checksum)+'\n')
        audit=self.root/'audit';(audit/'target-graphs').mkdir(parents=True)
        inv={'source_commit':'fixture','lock_sha256':digest(lock.read_bytes()),'notice_gaps':[],
             'packages':[{'name':'sample','version':'1.0.0','archive_sha256':checksum}]}
        (audit/'DEPENDENCY-RIGHTS.json').write_text(json.dumps(inv))
        for n in ('ARCHIVED-NOTICES.txt','SHA256SUMS'): (audit/n).write_bytes(b'original')
        (audit/'target-graphs/TARGET-RIGHTS.json').write_text(json.dumps({'source_commit':'fixture','lock_sha256':inv['lock_sha256']}))
        p=self.root/'editor-notes/research/native-notice-review-20.json';p.parent.mkdir(parents=True);p.write_text('{"sources":[]}')
        return archive,audit
    @patch('package_native_rights_20.verify_review')
    def test_changed_original_archive_rejected(self, review):
        archive,audit=self.fixture();archive.write_bytes(b'altered')
        with self.assertRaisesRegex(ValueError,'altered original'): build_inputs(self.root,audit,self.root/'cache','fixture')
    @patch('package_native_rights_20.verify_review')
    def test_stale_source_commit_rejected(self, review):
        archive,audit=self.fixture()
        with self.assertRaisesRegex(ValueError,'Stale source'): build_inputs(self.root,audit,self.root/'cache','other')


if __name__ == '__main__': unittest.main()
