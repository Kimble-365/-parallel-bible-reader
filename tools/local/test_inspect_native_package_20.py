import io
import json
from pathlib import Path
import plistlib
import struct
import subprocess
import tarfile
import tempfile
import unittest
import zipfile
from inspect_native_package_20 import inspect,identity


class Packages(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
    def apk(self,name='lib/arm64-v8a/libreader.so',machine=183):
        p=self.root/'review.apk'
        with zipfile.ZipFile(p,'w') as z:
            z.writestr('AndroidManifest.xml',b'manifest')
            z.writestr(name,b'\x7fELF\x02\x01'+b'\0'*12+machine.to_bytes(2,'little')+b'\0'*44)
        return p
    def test_android_actual_bytes_and_arch(self):
        r=inspect(self.apk(),'android');self.assertEqual(len(r['members']),2);self.assertFalse(r['application_executed'])
    def test_wrong_android_arch_rejected(self):
        with self.assertRaisesRegex(ValueError,'ARM64'):inspect(self.apk(machine=62),'android')
    def test_traversal_is_not_extracted(self):
        with self.assertRaisesRegex(ValueError,'Unsafe'):inspect(self.apk('../outside'),'android')
        self.assertFalse((self.root/'outside').exists())
    def test_mac_plist_and_macho_without_execution(self):
        p=self.root/'review.tar.gz'
        with tarfile.open(p,'w:gz') as t:
            files={'Reader.app/Contents/Info.plist':plistlib.dumps({'CFBundleIdentifier':'org.kimble365.parallelbiblereader','CFBundleExecutable':'reader'}),
                   'Reader.app/Contents/MacOS/reader':b'\xcf\xfa\xed\xfe'+struct.pack('<I',0x0100000c)+b'\0'*56}
            for name,b in files.items():
                m=tarfile.TarInfo(name);m.size=len(b);t.addfile(m,io.BytesIO(b))
            m=tarfile.TarInfo('Reader.app/link');m.type=tarfile.SYMTYPE;m.linkname='../../outside';t.addfile(m)
        r=inspect(p,'macos');self.assertEqual(r['members'][-1]['link_dereferenced'],False)
        self.assertEqual(r['bundle_identities'][0]['identifier'],'org.kimble365.parallelbiblereader')
    def test_failed_installer_listing_is_not_success(self):
        p=self.root/'review.exe';p.write_bytes(b'MZ'+b'\0'*100)
        def fail(*a,**k):raise subprocess.CalledProcessError(1,a[0])
        with self.assertRaises(subprocess.CalledProcessError):inspect(p,'windows',run=fail)
    def test_installer_stub_not_payload_architecture(self):
        r=identity(io.BytesIO(b'MZ'+b'\0'*100));self.assertTrue(r['binary']['payload_architecture_not_inferred'])


if __name__=='__main__':unittest.main()
