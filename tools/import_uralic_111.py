"""1.11: licensed Hungarian Károli 1908 and five-book Estonian Piibel Kõigile."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,hashlib,shutil,sqlite3,tarfile,sys
from import_global_sample import extract
ROOT=Path(__file__).resolve().parents[1];SRC=Path('/workspace/reader-new-sources');OUT=ROOT/'releases/v1.11'
if not OUT.exists():shutil.copytree(ROOT/'releases/v1.10',OUT,ignore=shutil.ignore_patterns('extra-data','sources'))
def readjs(p):return json.loads(p.read_text().split('=',1)[1].rstrip(';\n'))
cat=readjs(OUT/'catalog.js');directory=readjs(OUT/'translations/metadata.js');known=dict(cat['books']);mapping={v:k for k,v in known.items()}
for name,code in list(mapping.items()):
 for n,r in [('1 ','I '),('2 ','II '),('3 ','III '),('4 ','IV ')]:
  if name.startswith(n):mapping[r+name[len(n):]]=code
mapping.update({'Song of Solomon':'SNG','Revelation of John':'REV'})
(OUT/'extra-data').mkdir(exist_ok=True);(OUT/'sources').mkdir(exist_ok=True)
with tarfile.open(SRC/'Brenton-catalog.tgz') as t:proof=t.extractfile(next(n for n in t.getnames() if n.lower().endswith('/hunkar.conf'))).read().decode()
assert 'DistributionLicense=Public Domain' in proof and '1908' in proof;(OUT/'sources/hunkar-module.conf').write_text(proof)
hun={mapping[b['name']]:[[int(c['chapter']),int(v['verse']),v['text']] for c in b['chapters'] for v in c['verses'] if v['text'].strip()] for b in json.loads((SRC/'hunkar.json').read_text())['books']}
est={}
with ZipFile(SRC/'ekkpkp-mirror.zip') as z:
 rights=z.read('copr.htm').decode('utf-8-sig');assert 'Attribution Share-Alike license 4.0' in rights and 'Sihtasutus Piibel Kõigile' in rights;(OUT/'sources/ekkpkp-copyright.html').write_text('\n'.join(line.rstrip() for line in rights.splitlines())+'\n')
 for n in z.namelist():
  if n.endswith('.usfm'):book,rows=extract(z.read(n).decode('utf-8-sig'));est[book]=rows
assert len(hun)==66 and len(est)==5
specs=[dict(id='hun-karoli1908',label='Hungarian — Károli 1908',language='hu',iso='hun',books=hun,license='Public Domain',source='https://github.com/scrollmapper/bible_databases/tree/master/sources/hu/HunKar',attribution='Historical Károli Gáspár translation, revised 1908. HunKar digital module explicitly declares Public Domain; module 2.0 uses Calvin versification. Source JSON and module declaration retained. Plain-verse display extraction by this project.',scope='Full Bible (66 source books)',branch='Hungarian',countries=['Hungary','Romania','Slovakia','Serbia'],aliases=['magyar','Károli','Karoli','hun','hu'],numbering='HunKar source / Calvin versification; no verified cross-edition alignment',files=[SRC/'hunkar.json',SRC/'hunkar-rights.md',OUT/'sources/hunkar-module.conf']),dict(id='ekk-pkp-partial',label='Estonian — Piibel Kõigile (5 source books)',language='et',iso='ekk',books=est,license='CC BY-SA 4.0',source='https://harmony.cx/ekkpkp/copyright.htm',attribution='© 2023 Sihtasutus Piibel Kõigile. Piibel Kõigile, Standard Estonian. CC BY-SA 4.0. Supplied USFM snapshot contains Matthew, Mark, Luke, John and Romans only; archive dated 10 January 2025. Plain-verse extraction by this project omits headings and footnotes from display; exact USFM retained. No endorsement implied.',scope='Partial Bible: Matthew, Mark, Luke, John, Romans (5 books)',branch='Finnic',countries=['Estonia'],aliases=['eesti','eesti keel','Estonian','est','ekk','Piibel Kõigile'],numbering='Piibel Kõigile source numbering; no verified cross-edition alignment',files=[SRC/'ekkpkp-mirror.zip'])]
db=sqlite3.connect('/workspace/biblical-encyclopedia/encyclopedia.sqlite3');overlays={};reports=[]
for spec in specs:
 id=spec['id'];books=spec['books'];records=[];meta=dict(id=id,label=spec['label'],title=spec['label'],language=spec['language'],latin_language=spec['language'],script='Latin',direction='ltr',available=True,scope=spec['scope'],source=spec['source'],license=spec['license'],license_url='https://creativecommons.org/licenses/by-sa/4.0/' if spec['license'].startswith('CC') else 'https://creativecommons.org/publicdomain/mark/1.0/',attribution=spec['attribution'],method='Original Latin script with accents retained; not a pronunciation guide. Source reference labels retained; original source material available separately.',has_transliteration=False,book_codes=[b for b,_ in cat['books'] if b in books],positions=[list(p) for p in dict.fromkeys((b,r[0]) for b in books for r in books[b])],preserve_source_refs=True,versification_label=spec['numbering'])
 with ZipFile(OUT/'sources'/(id+'-raw.zip'),'w',ZIP_DEFLATED) as z:
  for f in spec['files']:z.write(f,f.name)
 with ZipFile(OUT/'sources'/(id+'-display-usfm.zip'),'w',ZIP_DEFLATED) as z:
  z.writestr('PROVENANCE.txt',spec['attribution']+'\n'+spec['source']+'\n'+spec['license']+'\n')
  for book,rows in books.items():
   data=[];text=['\\id '+book,'\\usfm 3.0','\\ide UTF-8'];last=None;seen=set()
   for i,row in enumerate(rows):
    c,v,original=row[:3];assert (c,v) not in seen,(id,book,c,v);seen.add((c,v));data.append([c,v,original,original]+row[3:]);records.append((id,book,c,str(v),i,original,original))
    if last!=c:text.append('\\c '+str(c));last=c
    text.append('\\v '+str(v)+' '+original)
   overlays.setdefault(book,{})[id]=data;z.writestr(book+'.usfm','\n'.join(text)+'\n')
 cat['editions']=[e for e in cat['editions'] if e['id']!=id]+[meta];directory=[e for e in directory if e['id']!=id]+[dict(id=id,language='Hungarian' if id.startswith('hun') else 'Estonian',iso6393=spec['iso'],aliases=spec['aliases'],family='Uralic',branch=spec['branch'],countries=spec['countries'],continents=['Europe'],states=[],script='Latin',variety=spec['label'],classification_source='Project browsing groups and ISO language identity; no asserted UBS identifier',ubs_id=None)]
 db.execute('DELETE FROM reader_source_units WHERE edition=?',(id,));db.executemany('INSERT INTO reader_source_units VALUES(?,?,?,?,?,?,?)',records);db.execute('INSERT OR REPLACE INTO reader_catalog VALUES(?,?)',(id,json.dumps(meta,ensure_ascii=False)));db.execute('DELETE FROM reader_search_source_units_v1 WHERE edition=?',(id,));db.execute('INSERT INTO reader_search_source_units_v1 SELECT edition,book,chapter,verse_key,original,latin FROM reader_source_units WHERE edition=?',(id,));reports.append(dict(id=id,books=len(books),units=len(records),license=spec['license'],source=spec['source'],raw=[dict(file=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in spec['files']]))
db.commit();db.close()
for book,editions in overlays.items():(OUT/'extra-data'/(book+'.js')).write_text('window.ExtraBibleBooks=window.ExtraBibleBooks||{};window.ExtraBibleBooks['+json.dumps(book)+']='+json.dumps(dict(book=book,editions=editions),ensure_ascii=False,separators=(',',':'))+';')
(OUT/'catalog.js').write_text('window.BibleCatalog='+json.dumps(cat,ensure_ascii=False,separators=(',',':'))+';');(OUT/'translations/metadata.js').write_text('window.TranslationDirectory='+json.dumps(directory,ensure_ascii=False,separators=(',',':'))+';');(OUT/'sources/uralic-import.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n');(OUT/'sources/est-exclusion.txt').write_text('The unrelated SWORD Est module was NOT imported: copyright status unknown / license null. No claim that it is the 1914 edition. The supplied Piibel Kõigile snapshot is a separately licensed five-book resource. Broader Uralic texts and matched recordings remain pending verification.\n');print(json.dumps(reports,ensure_ascii=False,indent=2))
