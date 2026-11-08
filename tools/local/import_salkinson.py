"""Pinned eBible hebsg intake. Preserve original archive and every USFM member byte."""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json,re,shutil
ROOT=Path(__file__).resolve().parents[2]
archive=ROOT/'original-documents/reference-editions/salkinson-ginsburg/hebsg_usfm.zip'
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='71f137fd188b81b12e1379e52389bb4ab32efee6deb863a0ebad35102c535986','Unexpected source archive; review rights and identity before replacing the pin.'
out=ROOT/'releases/v2.0/salkinson-data';out.mkdir(exist_ok=True)
raw=ROOT/'original-documents/reference-editions/salkinson-ginsburg';raw.mkdir(parents=True,exist_ok=True)
assert archive.resolve()==(raw/archive.name).resolve()
manifest={'id':'heb-salkinson-ginsburg-ebible-2025','label':'Salkinson–Ginsburg Hebrew NT — eBible hebsg','source':'https://ebible.org/Scriptures/hebsg_usfm.zip','rights_source':'https://ebible.org/hebsg/copyright.htm','license':'Public Domain','source_date':'2025-12-12','retrieved':'2026-11-08','archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'books':{},'raw_files':[],'notes':'eBible digital edition; not identified as the SDHS 2012/2018 revision. Separate from Delitzsch and the 84-edition main catalog. No mobile feed or EPUB changes.'}
with ZipFile(archive) as z:
 assert b'Public Domain' in z.read('copr.htm')
 for n in z.namelist():
  if not n.endswith(('.usfm','.htm','.asc')):continue
  b=z.read(n)
  if n=='copr.htm':(raw/n).write_bytes(b)
  manifest['raw_files'].append({'path':n,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
  if not n.endswith('.usfm'):continue
  source=b.decode('utf-8-sig');book=re.search(r'\\id\s+(\w+)',source)[1]
  if book=='INT':continue
  rows=[];chapter=None
  for line in source.splitlines():
   if line.startswith('\\c '):chapter=int(line.split()[1])
   elif line.startswith('\\v '):
    m=re.fullmatch(r'\\v (\d+)\s+(.*)',line);assert m,(book,line)
    text=re.sub(r'\\vp\s+.*?\\vp\*\s*','',m[2]).rstrip()
    assert '\\' not in text and text.strip(),(book,line)
    rows.append([chapter,int(m[1]),text])
  assert len(rows)==len(re.findall(r'(?m)^\\v ',source));assert len({(r[0],r[1]) for r in rows})==len(rows)
  payload=(json.dumps({'book':book,'rows':rows},ensure_ascii=False,separators=(',',':'))+'\n').encode();(out/(book+'.json')).write_bytes(payload)
  manifest['books'][book]={'rows':len(rows),'chapters':sorted({r[0] for r in rows}),'sha256':hashlib.sha256(payload).hexdigest(),'bytes':len(payload)}
assert len(manifest['books'])==27
manifest['verse_count']=sum(b['rows'] for b in manifest['books'].values());assert manifest['verse_count']==7957
(ROOT/'releases/v2.0/salkinson-manifest.js').write_text('window.SalkinsonVolume='+json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+';\n')
(raw/'IMPORT-REPORT.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('PASS: 27 books /',manifest['verse_count'],'rows;',len(manifest['raw_files']),'raw source members preserved; archive SHA-256',manifest['archive_sha256'])
