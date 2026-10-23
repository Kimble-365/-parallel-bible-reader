"""Version 1.8 imports. Preserve source verse identifiers and raw provenance."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from collections import OrderedDict
import json,re,sqlite3,hashlib,shutil,html
from import_original_languages import handle,latin,cl,extract
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'releases/v1.8'; SRC=Path('/workspace/reader-new-sources')
def readjs(p):return json.loads(p.read_text().split('=',1)[1].rstrip(';\n'))
cat=readjs(OUT/'catalog.js'); directory=readjs(OUT/'translations/metadata.js'); names=dict(cat['books'])
extras={'1ES':'1 Esdras','JDT':'Judith','TOB':'Tobit','1MA':'1 Maccabees','2MA':'2 Maccabees','3MA':'3 Maccabees','4MA':'4 Maccabees','ODA':'Odes','WIS':'Wisdom of Solomon','SIR':'Sirach','PSS':'Psalms of Solomon','BAR':'Baruch','LJE':'Letter of Jeremiah','SUS':'Susanna','BEL':'Bel and the Dragon','MAN':'Prayer of Manasseh','2ES':'2 Esdras','PS2':'Psalm 151 (separate source book)'}
for k,v in extras.items():
 if k not in names:cat['books'].append([k,v]);names[k]=v
mapping={v:k for k,v in names.items()}
for name,code in list(mapping.items()):
 for n,r in [('1 ','I '),('2 ','II '),('3 ','III '),('4 ','IV ')]:
  if name.startswith(n):mapping[r+name[len(n):]]=code
mapping.update({'Wisdom':'WIS','Song of Solomon':'SNG','Revelation of John':'REV','Prayer of Manasses':'MAN','Epistle of Jeremiah':'LJE'})
db=sqlite3.connect('/workspace/biblical-encyclopedia/encyclopedia.sqlite3')
db.execute('CREATE TABLE IF NOT EXISTS reader_source_units(edition TEXT,book TEXT,chapter INTEGER,verse_key TEXT,source_order INTEGER,original TEXT,latin TEXT,PRIMARY KEY(edition,book,chapter,verse_key))')
overlays={}; reports=[]
def install(id,label,lang,script,books,license,source,attribution,archives=(),scope='',labels=None):
 h=handle(script+'-Latin') if script!='Latin' else None;positions=[];count=0; records=[]
 for book,rows in books.items():
  assert book in names,book
  data=[];seen=set();usfm=['\\id '+book,'\\usfm 3.0','\\ide UTF-8','\\h '+names[book]];lastc=None;export_verses={};verse_counts={};normalize_chapters={c for c,v,t in rows if not isinstance(v,int)}
  for c,v,t in rows:
   verse_counts[c]=verse_counts.get(c,0)+1;export_verses[(c,str(v))]=verse_counts[c] if c in normalize_chapters else v
  export_chapters={c:i+1 for i,c in enumerate(dict.fromkeys(r[0] for r in rows))}
  for c,v,text in rows:
   assert (c,str(v)) not in seen,(id,book,c,v);seen.add((c,str(v)))
   assert re.fullmatch(r'\d+[A-Za-z0-9]*',str(v)),(id,v)
   if not text.strip():continue
   rom=latin(h,text) if h else text;data.append([c,v,text,rom]);records.append((id,book,c,str(v),len(data),text,rom));positions.append((book,c));count+=1
   if c!=lastc:
    usfm.append('\\c '+str(export_chapters[c] if any(not isinstance(k,int) for k in export_chapters) else c));usfm.append('\\rem Source chapter key: '+str(c));lastc=c
   usfm.append('\\rem Source verse key: '+str(v));usfm.append('\\v '+str(export_verses[(c,str(v))])+' '+text)
  overlays.setdefault(book,{})[id]=data
  raw='\n'.join(usfm)+'\n';db.execute('INSERT OR REPLACE INTO reader_source_usfm VALUES(?,?,?,?)',(id,book,hashlib.sha256(raw.encode()).hexdigest(),raw))
  (OUT/'sources'/f'{id}-{book}.usfm').write_text(raw)
 if h:cl(h)
 db.execute('DELETE FROM reader_source_units WHERE edition=?',(id,));db.executemany('INSERT INTO reader_source_units VALUES(?,?,?,?,?,?,?)',records)
 meta=dict(id=id,label=label,title=label,language=lang,latin_language=lang+'-Latn',script=script,direction='rtl' if script=='Hebrew' else 'ltr',scope=scope or str(len(books))+' source books',available=True,source=source,license=license,license_url=('https://creativecommons.org/publicdomain/mark/1.0/' if license=='Public Domain' else 'https://creativecommons.org/licenses/'+('by/4.0/' if license=='CC BY 4.0' else 'by-sa/4.0/')),attribution=attribution,method='ICU 76 orthographic '+script+'-Latin; written-form conversion, not a spoken reconstruction. Source numbering retained.' if h else 'Original Latin script; source numbering retained.',book_codes=list(books),positions=[list(p) for p in dict.fromkeys(positions)],has_transliteration=bool(h),preserve_source_refs=True,versification_label='Native source numbering; no verified cross-edition verse alignment',book_labels=labels or {})
 cat['editions']=[e for e in cat['editions'] if e['id']!=id]+[meta];directory[:]=[e for e in directory if e['id']!=id]
 directory.append(dict(id=id,language={'hbo':'Biblical Hebrew / Aramaic','heb':'Hebrew','grc':'Ancient Greek','ell':'Greek','fra':'French','eng':'English','chu':'Church Slavonic'}.get(lang,lang),iso6393=lang,aliases=[label],family='Afro-Asiatic' if script=='Hebrew' else 'Indo-European',branch='Semitic' if script=='Hebrew' else 'Hellenic' if script=='Greek' else 'Romance' if lang=='fra' else 'Slavic' if lang=='chu' else 'Germanic',countries=['Israel'] if script=='Hebrew' else ['Greece'] if script=='Greek' else ['France'] if lang=='fra' else ['Russia','Ukraine','Belarus','Bulgaria','Serbia'] if lang=='chu' else ['United Kingdom'],continents=['Asia'] if script=='Hebrew' else ['Europe'],states=[],script=script,variety=label,classification_source='Project browsing group; ISO 639-3 identity; no asserted UBS provider identifier',ubs_id=None))
 db.execute('INSERT OR REPLACE INTO reader_catalog VALUES(?,?)',(id,json.dumps(meta,ensure_ascii=False)))
 with ZipFile(OUT/'sources'/f'{id}-display-usfm.zip','w',ZIP_DEFLATED) as z:
  for p in (OUT/'sources').glob(id+'-*.usfm'):z.write(p,p.name)
  z.writestr('PROVENANCE.txt',label+'\n'+source+'\n'+license+'\n'+attribution+'\nDerived plain-verse USFM; raw source archives retain apparatus. Not a critical edition.\n')
 for p in (OUT/'sources').glob(id+'-*.usfm'):p.unlink()
 sources=[]
 for file in archives:
  file=Path(file);shutil.copyfile(file,OUT/'sources'/(id+'-'+file.name));sources.append(dict(file=file.name,sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
 reports.append(dict(id=id,books=len(books),verses=count,license=license,source=source,raw_sources=sources,source_numbering=True));print(id,len(books),count,flush=True)
# Westminster source rights retained verbatim with raw SFM.
p=Path('/workspace/sab-hindi-pilot/tools/sab/data/bibles/heb - Westminster Leningrad Codex');books=OrderedDict()
with ZipFile(SRC/'wlc-raw.zip','w',ZIP_DEFLATED) as z:
 for f in sorted(p.iterdir()):
  if f.suffix.lower()=='.sfm':
   raw=f.read_text(encoding='utf-8-sig');b,rows=extract(raw);books[b]=[r[:3] for r in rows];z.writestr(f.name,raw)
 z.writestr('copyright.xml',(p/'!books.xml').read_bytes())
install('hbo-wlc','Hebrew / Aramaic — Westminster Leningrad Codex','hbo','Hebrew',books,'CC BY 4.0','https://github.com/openscriptures/morphhb','© 2019 Open Scriptures Hebrew Bible Project. Original work at https://github.com/openscriptures/morphhb . Display and Latin adaptation by this project; no endorsement.',[SRC/'wlc-raw.zip'],scope='Old Testament, 39 books')
# Historical Delitzsch: exact Wikisource revision archive.
books=OrderedDict();manifest=json.loads((SRC/'delitzsch/manifest.json').read_text())
for item in manifest:
 d=json.loads((SRC/'delitzsch'/item['cache']).read_text());text=d['parse']['wikitext']['*'];div=re.search(r'<div\b[^>]*>(.*?)(?:</div\s*>|$)',text,re.S|re.I)
 if div:text=div[1]
 else:text=text.split('==')[0]
 text=re.sub(r'\{\{נוסח\|([^|{}]+)(?:\|[^{}]*)?\}\}',r'\1',text)
 for _ in range(6):text=re.sub(r'\{\{[^{}]*\}\}',' ',text)
 text=re.sub(r'<ref\b.*?</ref>',' ',text,flags=re.S);text=re.sub(r'<[^>]*>',' ',text);text=re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]',r'\2',text);text=re.sub(r'\[\[([^\]]+)\]\]',r'\1',text);text=html.unescape(text)
 marks=list(re.finditer(r'(?<!\S)(\d{1,3})\s+',text));rows=[]
 for i,m in enumerate(marks):
  verse=int(m[1]);body=re.sub(r'\s+',' ',text[m.end():marks[i+1].start() if i+1<len(marks) else len(text)]).strip()
  if body:rows.append([item['chapter'],verse,body])
 opening=re.sub(r'\s+',' ',text[:marks[0].start()] if marks else '').strip()
 if opening:rows.insert(0,[item['chapter'],0,opening])
 assert rows and [r[1] for r in rows]==sorted(set(r[1] for r in rows)),(item,rows[:2])
 if [r[1] for r in rows]!=list(range(0 if rows[0][1]==0 else 1,rows[-1][1]+1)):print('SOURCE GAP',item['book'],item['chapter'],[v for v in range(1,rows[-1][1]+1) if v not in [r[1] for r in rows]],flush=True)
 books.setdefault(item['book'],[]).extend(rows)
with ZipFile(SRC/'delitzsch-wikisource.zip','w',ZIP_DEFLATED) as z:
 z.write(SRC/'delitzsch/manifest.json','manifest.json')
 for item in manifest:z.write(SRC/'delitzsch'/item['cache'],item['cache'])
 z.writestr('LICENSE.txt','Wikisource text: CC BY-SA 4.0. https://creativecommons.org/licenses/by-sa/4.0/ . Attribution: respective page authors, exact revision IDs in manifest; page and history at https://he.wikisource.org/wiki/ . Franz Delitzsch historical Hebrew translation. Not the latest modern Hebrew NT.')
install('heb-delitzsch-historical','Hebrew — Delitzsch, historical Wikisource text','heb','Hebrew',books,'CC BY-SA 4.0','https://he.wikisource.org/wiki/הברית_החדשה','Historical Franz Delitzsch translation; Wikisource page contributors, exact page titles and revision IDs in source manifest. CC BY-SA 4.0. Plain-verse extraction and Latin adaptation by this project. Not the latest modern Hebrew NT.',[SRC/'delitzsch-wikisource.zip'],scope='Historical New Testament, 27 books')
# Structured public-domain French / historical Greek modules.
for filename,id,label,lang,script,proof,archive in [('lxx-next-4.txt','fra-giguet-lxx','French — Giguet Septuagint 1872','fra','Latin','lxx-verified-3.txt','FreLXXGiguet-source.zip'),('lxx-next-5.txt','ell-vamvas1850','Greek — Vamvas 1850 (Katharevousa)','ell','Greek','lxx-verified-4.txt','GreVamvas-source.zip')]:
 books=OrderedDict()
 for b in json.loads((SRC/filename).read_text())['books']:
  if b['name']=='I Enoch':continue
  rows=[[int(c['chapter']),int(v['verse']),v['text']] for c in b['chapters'] for v in c['verses'] if v['text'].strip()]
  if rows:books[mapping[b['name']]]=rows
 install(id,label,lang,script,books,'Public Domain','https://github.com/scrollmapper/bible_databases',('Giguet and other translators, 1872; source module public domain. Enoch omitted from LXX selection; raw archive retained.' if lang=='fra' else 'Neophytos Vamvas, 1850; public-domain historical Greek Bible. Old Testament translated from Hebrew, not the Septuagint.'),[SRC/filename,SRC/proof,SRC/archive])
# Swete: retain Old Greek and Theodotion as separate options.
order=['GEN','EXO','LEV','NUM','DEU','JOS','JDG','RUT','1SA','2SA','1KI','2KI','1CH','2CH','1ES','EZR','EST','JDT','TOB','1MA','2MA','3MA','4MA','PSA','ODA','PRO','SNG','JOB','WIS','SIR','PSS','HOS','AMO','MIC','JOL','OBA','JON','NAM','HAB','ZEP','HAG','ZEC','MAL','ISA','JER','BAR','LAM','LJE','EZK','SUS','SUS','DAN','DAN','BEL','BEL'];main=OrderedDict();variant=OrderedDict()
with ZipFile(SRC/'swete.zip') as z:
 files=sorted(n for n in z.namelist() if '/data/' in n and n.endswith('.txt'));assert len(files)==len(order)
 for n,book in zip(files,order):
  grouped=OrderedDict()
  for line in z.read(n).decode('utf-8-sig').splitlines():
   if not line.strip():continue
   m=re.match(r'\d+\.([A-Za-z0-9]+)\.(\d+[A-Za-z0-9]*)\s+(.*)',line);assert m,(n,line[:100]);key=(int(m[1]) if m[1].isdigit() else m[1],int(m[2]) if m[2].isdigit() else m[2]);grouped.setdefault(key,[]).append(m[3])
  target=variant if 'Theodotionis' in n else main;target[book]=[[c,v,' '.join(words)] for (c,v),words in grouped.items()]
for id,label,books in [('grc-swete','Greek — Swete Septuagint (Ecclesiastes absent)',main),('grc-swete-theodotion','Greek — Theodotion: Daniel, Susanna, Bel',variant)]:
 install(id,label,'grc','Greek',books,'CC BY-SA 4.0','https://github.com/nathans/lxx-swete','Swete Greek text and annotations, Open Greek and Latin / First1KGreek, digital corpus by nathans/lxx-swete. CC BY-SA 4.0. Source README retained. Plain-verse and Latin adaptation by this project; no endorsement. Ecclesiastes absent from supplied corpus.',[SRC/'swete.zip',SRC/'lxx-verified-2.txt'],labels={'EZR':'Esdras B (combined Ezra–Nehemiah source chapters)'})
# Another non-English Septuagint tradition: historic Church Slavonic.
books=OrderedDict()
for b in json.loads((SRC/'slavonic.json').read_text())['books']:
 rows=[[int(c['chapter']),int(v['verse']),v['text']] for c in b['chapters'] for v in c['verses'] if v['text'].strip()]
 if rows:books[mapping[b['name']]]=rows
install('chu-elizabeth','Church Slavonic — Elizabeth Bible 1757','chu','Cyrillic',books,'Public Domain','https://github.com/scrollmapper/bible_databases/tree/master/sources/cu/CSlElizabeth','Elizabeth Bible, historic Church Slavonic, source module dated 1757. Public Domain. Old Testament in the Septuagint tradition; not a translation of the specific Swete edition.',[SRC/'slavonic.json',SRC/'slavonic-rights.md'])
# Thomson is an explicitly incomplete alternative English LXX translation.
from import_global_sample import extract as extract_general
books=OrderedDict()
with ZipFile(SRC/'thomson.zip') as z:
 for n in sorted(z.namelist()):
  if '/usfm/' in n and n.endswith('.usfm'):
   book,rows=extract_general(z.read(n).decode('utf-8-sig'));books[book]=[r[:3] for r in rows]
install('eng-thomson-partial','English — Thomson Septuagint (11 source books)','eng','Latin',books,'Public Domain','https://github.com/jackvandrunen/thomson-septuagint','Charles Thomson, historical English Septuagint translation, 1808. Digital transcription project by jackvandrunen; public-domain notice retained. Only 11 completed source files imported; in-progress Exodus and Proverbs excluded. Source project uses KJV-style numbering; no verified verse alignment.',[SRC/'thomson.zip'],scope='Partial Septuagint: 11 source books')
for book,editions in overlays.items():
 p=OUT/'extra-data'/(book+'.js');old=json.loads(p.read_text().split(']=',1)[1].rstrip(';\n')) if p.exists() else {'book':book,'editions':{}};old['editions'].update(editions);p.write_text('window.ExtraBibleBooks=window.ExtraBibleBooks||{};window.ExtraBibleBooks['+json.dumps(book)+']='+json.dumps(old,ensure_ascii=False,separators=(',',':'))+';')
cat['version']='1.8-source-references';(OUT/'catalog.js').write_text('window.BibleCatalog='+json.dumps(cat,ensure_ascii=False,separators=(',',':'))+';');(OUT/'translations/metadata.js').write_text('window.TranslationDirectory='+json.dumps(directory,ensure_ascii=False,separators=(',',':'))+';');(OUT/'sources/import-1.8-report.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2))
db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS reader_search_source_units_v1 USING fts5(edition UNINDEXED,book UNINDEXED,chapter UNINDEXED,verse_key UNINDEXED,original,latin,tokenize='unicode61 remove_diacritics 0')");db.execute('DELETE FROM reader_search_source_units_v1');db.execute('INSERT INTO reader_search_source_units_v1 SELECT edition,book,chapter,verse_key,original,latin FROM reader_source_units');db.commit();db.close()
print('Imported',sum(r['verses'] for r in reports),'source units')
