"""Import licensed UHB/UGNT USFM into the existing authoring SQLite database.
Preserve raw sources, verse numbers and original glyphs; export lazy static overlays.
"""
from pathlib import Path
from zipfile import ZipFile
import sqlite3,re,json,hashlib,ctypes as C,ctypes.util
ROOT=Path(__file__).resolve().parents[1];SOURCES=Path('/workspace/reader-new-sources');OUT=ROOT/'releases/v1.5'
libname=ctypes.util.find_library('icui18n');lib=C.CDLL(libname);icu_version=re.search(r'(\d+)$',libname).group(1);U=C.c_uint16;I=C.c_int32
op=getattr(lib,'utrans_openU_'+icu_version);op.argtypes=[C.POINTER(U),I,I,C.POINTER(U),I,C.c_void_p,C.POINTER(I)];op.restype=C.c_void_p
tr=getattr(lib,'utrans_transUChars_'+icu_version);tr.argtypes=[C.c_void_p,C.POINTER(U),C.POINTER(I),I,I,C.POINTER(I),C.POINTER(I)]
cl=getattr(lib,'utrans_close_'+icu_version);cl.argtypes=[C.c_void_p]
def utf(s):
 b=s.encode('utf-16-le');return (U*(len(b)//2)).from_buffer_copy(b)
def handle(name):
 name=utf(name);status=I(0);h=op(name,len(name),0,None,0,None,C.byref(status));assert h and status.value<=0,status.value;return h
def latin(h,text):
 data=utf(text);cap=max(100,len(data)*8);out=(U*cap)();out[:len(data)]=data;n=I(len(data));lim=I(n.value);status=I(0);tr(h,out,C.byref(n),cap,0,C.byref(lim),C.byref(status));assert status.value<=0,status.value;return bytes(out)[:n.value*2].decode('utf-16-le')
def extract(text):
 book=re.search(r'\\id\s+(\w+)',text)[1];expected=len(re.findall(r'\\v\s+\d+',text));chapter=None;rows=[]
 # Remove alternate numbering and notes; full structures remain in raw USFM.
 for marker in ['f','va','ca']:
  text=re.sub(r'\\'+marker+r'\s.*?\\'+marker+r'\*','',text,flags=re.S)
 text=re.sub(r'\\w\s+([^|\\]*)(?:\|[^\\]*)?\\w\*',lambda m:m[1],text)
 # Descriptive headings are not part of a numbered verse.
 text=re.sub(r'\\d[^\n]*','',text)
 matches=list(re.finditer(r'\\(c|v)\s+(\d+)(?:-(\d+))?',text))
 for i,m in enumerate(matches):
  if m[1]=='c':chapter=int(m[2]);continue
  assert chapter is not None
  end=matches[i+1].start() if i+1<len(matches) else len(text);payload=text[m.end():end];payload=re.sub(r'\\p\b',' ',payload);assert '\\' not in payload,(book,chapter,m[2],payload[:80]);payload=re.sub(r'\s+',' ',payload).strip();row=[chapter,int(m[2]),payload]
  if m[3]:row.append(int(m[3]))
  rows.append(row)
 assert len(rows)==expected,(book,len(rows),expected)
 assert len({(r[0],r[1]) for r in rows})==len(rows)
 return book,rows

def main():
 OUT.mkdir(exist_ok=True);(OUT/'extra-data').mkdir(exist_ok=True);(OUT/'sources').mkdir(exist_ok=True)
 db=sqlite3.connect('/workspace/biblical-encyclopedia/encyclopedia.sqlite3')
 db.execute('CREATE TABLE IF NOT EXISTS reader_source_usfm(edition TEXT,book TEXT,sha256 TEXT,usfm TEXT,PRIMARY KEY(edition,book))')
 base=json.loads((ROOT/'catalog.js').read_text().split('=',1)[1].rstrip(';\n'));overlays={};reports=[]
 for kind,id,script,lang,scope in [('hebrew','hbo-source','Hebrew','hbo','Old Testament'),('greek','grc-source','Greek','grc','New Testament')]:
  h=handle(script+'-Latin');rawfile=SOURCES/(kind+'.zip');allrows=[];files=[]
  with ZipFile(rawfile) as z:
   licensefile=next(n for n in z.namelist() if n.endswith('/LICENSE.md'));license=z.read(licensefile).decode();assert 'Attribution-ShareAlike 4.0' in license
   (OUT/'sources'/(kind+'-LICENSE.md')).write_text(license)
   manifest=next(n for n in z.namelist() if n.endswith('/manifest.yaml'));(OUT/'sources'/(kind+'-manifest.yaml')).write_bytes(z.read(manifest))
   for name in sorted(z.namelist()):
    if not name.endswith('.usfm'):continue
    raw=z.read(name).decode('utf-8-sig');book,rows=extract(raw);files.append(book)
    db.execute('INSERT OR REPLACE INTO reader_source_usfm VALUES(?,?,?,?)',(id,book,hashlib.sha256(raw.encode()).hexdigest(),raw))
    data=[]
    for r in rows:
     c,v,text=r[:3];rom=latin(h,text);export=[c,v,text,rom]+([r[3]] if len(r)>3 else []);data.append(export);allrows.append((id,book,c,v,text,rom,1))
    overlays.setdefault(book,{'book':book,'editions':{}})['editions'][id]=data
  cl(h);assert len(files)==(39 if kind=='hebrew' else 27)
  db.executemany('INSERT OR REPLACE INTO bible_verses VALUES(?,?,?,?,?,?,?)',allrows)
  label='Biblical Hebrew / Aramaic — source + Latin' if kind=='hebrew' else 'Koine Greek — source + Latin'
  source='https://git.door43.org/unfoldingWord/'+('hbo_uhb' if kind=='hebrew' else 'el-x-koine_ugnt')
  meta=dict(id=id,label=label,title=label,script=script,language=lang,latin_language=lang+'-Latn',direction='rtl' if kind=='hebrew' else 'ltr',scope=scope,available=True,source=source,license='CC BY-SA 4.0',license_url='https://creativecommons.org/licenses/by-sa/4.0/',attribution='Original work by unfoldingWord available from https://www.unfoldingword.org/'+('uhb' if kind=='hebrew' else 'ugnt')+'. Copyright © 2022 unfoldingWord. Display extraction and ICU orthographic Latin adaptation by this project; no endorsement. See source license and raw USFM.',method='ICU '+script+'-Latin '+icu_version+' orthographic conversion. Vowels/diacritics retained in original; not a spoken reconstruction. USFM alternate numbering and notes retained in raw source, omitted from verse display.',book_codes=[b for b,_ in base['books'] if b in files],positions=sorted({(r[1],r[2]) for r in allrows},key=lambda p:([b for b,_ in base['books']].index(p[0]),p[1])),has_transliteration=True)
  db.execute('INSERT OR REPLACE INTO reader_catalog VALUES(?,?)',(id,json.dumps(meta,ensure_ascii=False)));base['editions'].append(meta)
  reports.append(dict(id=id,books=len(files),verses=len(allrows),raw_source_sha256=hashlib.sha256(rawfile.read_bytes()).hexdigest(),source=source,license='CC BY-SA 4.0',latin_scheme='ICU '+script+'-Latin '+icu_version))
  # Keep original source archive available for USFM users.
  import shutil
  shutil.copy(rawfile,OUT/'sources'/(kind+'-usfm.zip'))
 db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS reader_search_originals_v1 USING fts5(edition UNINDEXED,book UNINDEXED,chapter UNINDEXED,verse UNINDEXED,original,latin,tokenize='unicode61 remove_diacritics 0')")
 db.execute('DELETE FROM reader_search_originals_v1');db.execute("INSERT INTO reader_search_originals_v1 SELECT edition,book,chapter,verse,original,latin FROM bible_verses WHERE edition IN ('hbo-source','grc-source')");db.commit();db.close()
 for book,data in overlays.items():(OUT/'extra-data'/(book+'.js')).write_text('window.ExtraBibleBooks=window.ExtraBibleBooks||{};window.ExtraBibleBooks['+json.dumps(book)+']='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';')
 base['version']=str(base.get('version',''))+'-originals-1.5';(OUT/'catalog.js').write_text('window.BibleCatalog='+json.dumps(base,ensure_ascii=False,separators=(',',':'))+';')
 (OUT/'sources/import-report.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports,indent=2))
if __name__=='__main__':main()
