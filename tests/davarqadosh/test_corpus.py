"""Structural and deterministic book/pack acceptance checks against actual source bytes."""
from pathlib import Path
import importlib.util, json, os, sqlite3, tempfile, unittest, zipfile
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('corpus',ROOT/'tools/davarqadosh/corpus.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
SOURCE=Path(os.environ.get('OSHB_SOURCE','/workspace/morphhb/wlc'))
LEXICON=Path(os.environ.get('OSHB_LEXICON','/workspace/HebrewLexicon/HebrewStrong.xml'))

class Corpus(unittest.TestCase):
 def test_genesis_roundtrip_pack_and_resume(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);r=c.build_book(SOURCE,'Gen',p,lexicon=LEXICON);db=p/'GEN.sqlite'
   self.assertEqual(r['verses'],1533);self.assertEqual(r['coverage']['ingested'],20629)
   self.assertEqual(c.audit_book(db,(SOURCE/'Gen.xml').read_bytes())['source_reconstruction'],'exact')
   m=c.pack_book(db,p/'a');n=c.pack_book(db,p/'b');self.assertEqual(m,n)
   self.assertEqual((p/'a/GEN.wlexpack').read_bytes(),(p/'b/GEN.wlexpack').read_bytes())
   self.assertEqual(c.verify_pack(p/'a/GEN.wlexpack',m),db.read_bytes())
   self.assertTrue(c.build_book(SOURCE,'Gen',p,lexicon=LEXICON)['resumed'])
   other=p/'fresh';c.build_book(SOURCE,'Gen',other,lexicon=LEXICON)
   self.assertEqual(db.read_bytes(),(other/'GEN.sqlite').read_bytes())
   with sqlite3.connect(db) as d:
    self.assertEqual(d.execute("SELECT COUNT(*) FROM tokens WHERE attestation='qere'").fetchone()[0],17)
    self.assertEqual(d.execute("SELECT COUNT(*) FROM occurrence_senses").fetchone()[0],0)
    self.assertTrue(d.execute("SELECT COUNT(*) FROM lemmas WHERE gloss IS NOT NULL").fetchone()[0]>1000)
    self.assertEqual(d.execute("SELECT COUNT(*) FROM tokens WHERE attestation='qere' AND display_start IS NOT NULL").fetchone()[0],0)
   damaged=bytearray((p/'a/GEN.wlexpack').read_bytes());damaged[120]^=1;(p/'bad.wlexpack').write_bytes(damaged)
   with self.assertRaises(ValueError):c.verify_pack(p/'bad.wlexpack',m)
   with self.assertRaises(ValueError):c.verify_pack(p/'a/GEN.wlexpack',m|{'version':2})
 def test_aramaic_and_distinct_homographs(self):
  with tempfile.TemporaryDirectory() as tmp:
   c.build_book(SOURCE,'Dan',tmp,lexicon=LEXICON)
   with sqlite3.connect(Path(tmp)/'DAN.sqlite') as d:
    self.assertGreater(d.execute("SELECT COUNT(*) FROM tokens WHERE language='arc' AND verse_key='Dan.2.4'").fetchone()[0],0)
    self.assertEqual(d.execute("SELECT COUNT(*) FROM tokens WHERE language='arc' AND verse_key='Dan.1.1'").fetchone()[0],0)
    self.assertGreater(d.execute("SELECT COUNT(*) FROM tokens WHERE aligned_to IS NOT NULL").fetchone()[0],0)
 def test_no_silent_empty_audit(self):
  self.assertEqual(len(c.BOOKS),39)
  self.assertEqual(len({code for _,code in c.BOOKS}),39)

if __name__=='__main__':unittest.main(verbosity=2)
