"""Import the public-domain 1776 module; never publish private modern Finnish texts."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,re,shutil,hashlib,sqlite3
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'releases/v1.10';SRC=Path('/workspace/reader-new-sources')
if not OUT.exists():shutil.copytree(ROOT/'releases/v1.9',OUT)
def jsread(p):return json.loads(p.read_text().split('=',1)[1].rstrip(';\n'))
cat=jsread(OUT/'catalog.js');names=dict(cat['books']);names.update({'ESG':'Greek additions to Esther','S3Y':'Prayer of Azariah / Song of the Three'})
for code in ['ESG','S3Y']:
 if code not in dict(cat['books']):cat['books'].append([code,names[code]])
mapping={v:k for k,v in names.items()}
for name,code in list(mapping.items()):
 for n,r in [('1 ','I '),('2 ','II '),('3 ','III '),('4 ','IV ')]:
  if name.startswith(n):mapping[r+name[len(n):]]=code
mapping.update({'Song of Solomon':'SNG','Revelation of John':'REV','Wisdom':'WIS','Prayer of Manasses':'MAN','Esther (Greek)':'ESG','Prayer of Azariah':'S3Y','Additional Psalm':'PS2'})
assert 'Public Domain' in (SRC/'fin1776-rights.md').read_text()
books={}
for b in json.loads((SRC/'fin1776.json').read_text())['books']:
 rows=[[int(c['chapter']),int(v['verse']),v['text'],v['text']] for c in b['chapters'] for v in c['verses'] if v['text'].strip()]
 if rows:books[mapping[b['name']]]=rows
id='fin-biblia1776';meta=dict(id=id,label='Finnish — Biblia 1776',title='Biblia 1776 (Finnish)',language='fi',latin_language='fi',script='Latin',direction='ltr',scope=str(len(books))+' nonempty source books; historical Finnish',available=True,source='https://github.com/scrollmapper/bible_databases/tree/master/sources/fi/FinBiblia',license='Public Domain',license_url='https://creativecommons.org/publicdomain/mark/1.0/',attribution='Historical Finnish Biblia 1776. FinBiblia digital module declares Public Domain; source proof and SHA-256 retained. Plain-verse extraction by this project; original spelling retained.',method='Original Finnish Latin script; no transliteration needed. Source numbering retained.',book_codes=list(books),positions=[list(p) for p in dict.fromkeys((b,r[0]) for b,rows in books.items() for r in rows)],has_transliteration=False,preserve_source_refs=True,versification_label='FinBiblia source numbering; no verified cross-edition alignment')
cat['editions']=[e for e in cat['editions'] if e['id']!=id]+[meta];(OUT/'catalog.js').write_text('window.BibleCatalog='+json.dumps(cat,ensure_ascii=False,separators=(',',':'))+';')
directory=jsread(OUT/'translations/metadata.js');directory=[e for e in directory if e['id']!=id];directory.append(dict(id=id,language='Finnish',iso6393='fin',aliases=['suomi','Biblia','1776','Vanha kirkkoraamattu','Uralic','Finnic'],family='Uralic',branch='Finnic',countries=['Finland','Sweden'],continents=['Europe'],states=[],script='Latin',variety='Biblia 1776',classification_source='Project browsing group; ISO identity, no asserted UBS identifier',ubs_id=None));(OUT/'translations/metadata.js').write_text('window.TranslationDirectory='+json.dumps(directory,ensure_ascii=False,separators=(',',':'))+';')
(OUT/'extra-data').mkdir(exist_ok=True);(OUT/'sources').mkdir(exist_ok=True)
for book,rows in books.items():(OUT/'extra-data'/(book+'.js')).write_text('window.ExtraBibleBooks=window.ExtraBibleBooks||{};window.ExtraBibleBooks['+json.dumps(book)+']='+json.dumps(dict(book=book,editions={id:rows}),ensure_ascii=False,separators=(',',':'))+';')
shutil.copyfile(SRC/'fin1776-rights.md',OUT/'sources/fin1776-rights.md')
with ZipFile(OUT/'sources/fin1776-source.zip','w',ZIP_DEFLATED) as z:z.write(SRC/'fin1776.json','FinBiblia.json');z.write(SRC/'fin1776-rights.md','README.md')
with ZipFile(OUT/'sources/fin1776-display-usfm.zip','w',ZIP_DEFLATED) as z:
 for book,rows in books.items():
  text=['\\id '+book,'\\usfm 3.0','\\ide UTF-8'];last=None
  for c,v,t,_ in rows:
   if c!=last:text.append('\\c '+str(c));last=c
   text.append('\\v '+str(v)+' '+t)
  z.writestr(book+'.usfm','\n'.join(text)+'\n')
report=dict(id=id,books=len(books),source_units=sum(map(len,books.values())),source=meta['source'],license='Public Domain',source_sha256=hashlib.sha256((SRC/'fin1776.json').read_bytes()).hexdigest());(OUT/'sources/fin1776-import.json').write_text(json.dumps(report,indent=2)+'\n')
db=sqlite3.connect('/workspace/biblical-encyclopedia/encyclopedia.sqlite3');db.execute('DELETE FROM reader_source_units WHERE edition=?',(id,));db.executemany('INSERT INTO reader_source_units VALUES(?,?,?,?,?,?,?)',[(id,b,r[0],str(r[1]),i,r[2],r[3]) for b,rows in books.items() for i,r in enumerate(rows)]);db.execute('INSERT OR REPLACE INTO reader_catalog VALUES(?,?)',(id,json.dumps(meta,ensure_ascii=False)));db.execute('DELETE FROM reader_search_source_units_v1 WHERE edition=?',(id,));db.execute('INSERT INTO reader_search_source_units_v1 SELECT edition,book,chapter,verse_key,original,latin FROM reader_source_units WHERE edition=?',(id,));db.commit();db.close()
# Numeric facts of standard KJV order for 31,102-line theWord modules.
s=(SRC/'kjv-verse-map.java').read_text().split('new int[][] {',1)[1].split('});',1)[0];counts=[[int(v) for v in re.findall(r'\d+',r)] for r in re.findall(r'\{([^{}]+)\}',s)];assert len(counts)==66 and sum(map(sum,counts))==31102
(OUT/'ont-map.js').write_text('window.OntVerseMap='+json.dumps([[cat['books'][i][0],row] for i,row in enumerate(counts)],separators=(',',':'))+';')
(OUT/'sources/ont-map-provenance.json').write_text(json.dumps(dict(source='https://github.com/schierlm/BibleMultiConverter/blob/master/biblemulticonverter/src/main/java/biblemulticonverter/data/StandardVersification.java',description='Numeric reference counts only; KJV standard 66 books / 31,102 units. No Java implementation copied.',sha256=hashlib.sha256((SRC/'kjv-verse-map.java').read_bytes()).hexdigest()),indent=2)+'\n')
print(json.dumps(report))
