"""Verified, space-efficient Nordic additions. No unknown-license Est module."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,re,gzip,hashlib,tarfile
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'releases/v1.18';SRC=Path('/workspace/reader-new-sources/v118')
def js(p):return json.loads(p.read_text().split('=',1)[1].rstrip(';\n'))
def gitsha(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
cat=js(OUT/'catalog.js');directory=js(OUT/'translations/metadata.js');canonical=cat['books'][:66];names={name:code for code,name in canonical}
for name,code in list(names.items()):
 for n,roman in [('1 ','I '),('2 ','II '),('3 ','III ')]:
  if name.startswith(n):names[roman+name[len(n):]]=code
names.update({'Song of Solomon':'SNG','Revelation of John':'REV'})
source_specs=[dict(id='swe-1917',label='Swedish — Bibeln 1917',lang='sv',iso='swe',language='Swedish',country='Sweden',aliases=['svenska','Bibeln','Sverige'],license='Public Domain',module='swe1917',source='https://github.com/midvash/bible-data/tree/main/versions/sv/sv1917'),dict(id='nob-1930',label='Norwegian Bokmål — Bibelen 1930',lang='nb',iso='nob',language='Norwegian Bokmål',country='Norway',aliases=['norsk','bokmål','Norge'],license='Public Domain',module='norsk',file='Norsk.txt',blob='501dc4a70e1f0d2c4dc16f59b8ae43d55254fcc8',source='https://github.com/scrollmapper/bible_databases/blob/master/formats/txt/Norsk.txt'),dict(id='nno-1921',label='Norwegian Nynorsk — Studentmållagsbibelen 1921',lang='nn',iso='nno',language='Norwegian Nynorsk',country='Norway',aliases=['nynorsk','landsmål','Studentmållagsbibelen'],license='Public Domain',module='norsmb',file='NorSMB.txt',blob='1de229c584fd168be1460701772ce939a8582448',source='https://github.com/scrollmapper/bible_databases/blob/master/formats/txt/NorSMB.txt'),dict(id='isl-olo1995',label='Icelandic — Open Living New Testament and Psalms',lang='is',iso='isl',language='Icelandic',country='Iceland',aliases=['íslenska','Opna Lifandi Orð','Ísland'],license='CC BY-SA 4.0',file='is_olo.json',blob='3b67a9a17cb7e3b5092273d76ad9c39dcdc98ae7',source='https://github.com/thiagobodruk/bible/blob/master/json/is_olo.json',rights='https://ebible.org/isl/copyright.htm',copyright='Biblica® Opna Lifandi Orð Nýja testamentið og Sálmarnir™. Copyright © 1979, 1995 Biblica, Inc. Original work available at www.biblica.com and open.bible.'),dict(id='ekk-ocv2022',label='Estonian — Open Contemporary New Testament 2022',lang='et',iso='ekk',language='Estonian',country='Estonia',aliases=['eesti','Uus Testament','Pühakiri kaasaegses eesti keeles'],license='CC BY-SA 4.0',file='et_opkek.json',blob='77c9bbd5a4f8b6fc9dd4495f68ff9978647b8c36',source='https://github.com/thiagobodruk/bible/blob/master/json/et_opkek.json',rights='https://ebible.org/ekk/copyright.htm',copyright='Biblica® Vaba kasutusega Uus Testament, Pühakiri kaasaegses eesti keeles™. Copyright © 2022 Biblica, Inc. Original work available at www.biblica.com and open.bible.')]
(OUT/'packed-data').mkdir(exist_ok=True);(OUT/'sources').mkdir(exist_ok=True);overlays={};reports=[];labels={}
abbr=['mt','mc','lc','jo','atos','rm','1co','2co','gl','ef','fp','cl','1ts','2ts','1tm','2tm','tt','fm','hb','tg','1pe','2pe','1jo','2jo','3jo','jd','ap'];nt={a:code for a,(code,_) in zip(abbr,canonical[39:])};nt['sl']='PSA'
with tarfile.open('/workspace/reader-new-sources/Brenton-catalog.tgz') as tar:
 for s in source_specs:
  books={};raws={};proofs=[];booklabels={}
  if s['id']=='swe-1917':
   manifest=json.loads((SRC/'swe1917-manifest.json').read_text())
   for f in manifest:
    raw=(SRC/'swe1917'/f['file']).read_bytes();assert gitsha(raw)==f['sha'];d=json.loads(raw);code=canonical[d['bookId']-1][0];assert d['englishName'] in names and names[d['englishName']]==code;books[code]=[[c['chapter'],v['number'],v['text'],None] for c in d['chapters'] for v in c['verses'] if v['text'].strip()];raws[f['file']]=raw
   assert len(books)==66;raws['metadata.json']=(SRC/'swe1917-metadata.json').read_bytes()
  elif s['id'] in ['nob-1930','nno-1921']:
   raw=(SRC/s['file']).read_bytes();assert gitsha(raw)==s['blob'];raws[s['file']]=raw;code=None
   for line in raw.decode('utf-8-sig').splitlines():
    if line.startswith('### '):code=names[line[4:].strip()];assert code not in books;books[code]=[]
    elif line.strip():
     m=re.fullmatch(r'\[(\d+):(\d+)\] (.*)',line);assert m,(s['id'],line[:100]);
     if m[3].strip():books[code].append([int(m[1]),int(m[2]),m[3],None])
   assert len(books)==66
  else:
   raw=(SRC/s['file']).read_bytes();assert gitsha(raw)==s['blob'];raws[s['file']]=raw;data=json.loads(raw.decode('utf-8-sig'))
   for b in data:
    code=nt[b['abbrev']];assert code not in books;booklabels[code]=b['name'];books[code]=[[c,v,text,None] for c,ch in enumerate(b['chapters'],1) for v,text in enumerate(ch,1) if text.strip()]
   assert len(books)==(28 if s['iso']=='isl' else 27)
  if s.get('module'):
   conf=tar.extractfile('mods.d/'+s['module']+'.conf').read().decode();assert 'DistributionLicense=Public Domain' in conf;raws[s['module']+'.conf']=conf.encode();proofs.append('CrossWire '+s['module']+' explicitly declares Public Domain')
  scope='Full Bible (66 source books)' if len(books)==66 else 'New Testament and Psalms (28 books)' if len(books)==28 else 'New Testament (27 books; not a complete Old Testament)'
  attribution=s.get('copyright',s['label']+'. Historical Public Domain translation. '+'. '.join(proofs)+'.')+' Source spelling and supplied source positions retained; source arrays use their published chapter/verse slots. Plain verse extraction; no publisher endorsement. No phonetic reconstruction. Latin-script spelling is shown directly without a duplicate transliteration.'
  if s['id']=='ekk-ocv2022':attribution+=' This is a separate 27-book edition, not an invented completion of the existing five-book Piibel Kõigile snapshot.'
  codes=[b for b,_ in cat['books'] if b in books];positions=[]
  for b,rows in books.items():
   assert rows and len({(r[0],r[1]) for r in rows})==len(rows);overlays.setdefault(b,{})[s['id']]=rows;positions.extend([b,c] for c in dict.fromkeys(r[0] for r in rows))
  meta=dict(id=s['id'],label=s['label'],title=s['label'],language=s['lang'],latin_language=s['lang'],script='Latin',direction='ltr',available=True,scope=scope,source=s['source'],license=s['license'],license_url='https://creativecommons.org/licenses/by-sa/4.0/' if s['license'].startswith('CC') else 'https://creativecommons.org/publicdomain/mark/1.0/',attribution=attribution,method='Original Latin script; immutable source spelling/positions. Gzip JSON text pack; no translation/phonetic conversion.',has_transliteration=False,book_codes=codes,positions=positions,preserve_source_refs=True,versification_label='Source references retained; cross-edition alignment not verified',data_group='nordic-1.18',book_labels=booklabels)
  cat['editions']=[e for e in cat['editions'] if e['id']!=s['id']]+[meta];directory=[e for e in directory if e['id']!=s['id']]+[dict(id=s['id'],language=s['language'],iso6393=s['iso'],aliases=s['aliases'],family='Uralic' if s['iso']=='ekk' else 'Indo-European',subfamily='Finnic' if s['iso']=='ekk' else 'Germanic',branch='Finnic' if s['iso']=='ekk' else 'North Germanic',countries=[s['country']],continents=['Europe'],states=[],script='Latin',variety=s['label'],classification_source='ISO language identity and standard family hierarchy; project browsing metadata, no asserted UBS identifier',ubs_id=None)]
  provenance=dict(id=s['id'],source=s['source'],rights=s.get('rights'),license=s['license'],attribution=attribution,books=len(books),units=sum(map(len,books.values())),files=[dict(file=n,sha256=hashlib.sha256(b).hexdigest(),git_blob=gitsha(b)) for n,b in raws.items()])
  with ZipFile(OUT/'sources'/(s['id']+'-source.zip'),'w',ZIP_DEFLATED) as z:
   for n,b in raws.items():z.writestr(n,b)
   z.writestr('PROVENANCE.json',json.dumps(provenance,ensure_ascii=False,indent=2))
  with ZipFile(OUT/'sources'/(s['id']+'-usfm.zip'),'w',ZIP_DEFLATED) as z:
   z.writestr('ATTRIBUTION.txt',attribution+'\n'+s['source']+'\n'+s['license'])
   for b,rows in books.items():
    lines=['\\id '+b,'\\usfm 3.0','\\ide UTF-8'];last=None
    for c,v,text,_ in rows:
     if c!=last:lines.append('\\c '+str(c));last=c
     lines.append('\\v '+str(v)+' '+text)
    z.writestr(b+'.usfm','\n'.join(lines)+'\n')
  reports.append(provenance)
manifest={}
for book,editions in overlays.items():
 raw=json.dumps(dict(book=book,editions=editions),ensure_ascii=False,separators=(',',':')).encode();packed=gzip.compress(raw,compresslevel=9,mtime=0);(OUT/'packed-data'/(book+'.json.gz')).write_bytes(packed);manifest[book]=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),packed_sha256=hashlib.sha256(packed).hexdigest(),packed_bytes=len(packed))
(OUT/'catalog.js').write_text('window.BibleCatalog='+json.dumps(cat,ensure_ascii=False,separators=(',',':'))+';');(OUT/'translations/metadata.js').write_text('window.TranslationDirectory='+json.dumps(directory,ensure_ascii=False,separators=(',',':'))+';');(OUT/'sources/nordic-import.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n');(OUT/'pack-manifest.js').write_text('window.ReaderTextPacks='+json.dumps(manifest,separators=(',',':'))+';');p=OUT/'LICENSES.md';base=p.read_text().split('\n<!-- Nordic 1.18 -->')[0];p.write_text(base+'\n<!-- Nordic 1.18 -->\n'+''.join('\n## '+r['id']+'\n\n'+r['attribution']+'\n\n'+r['license']+'\n'+r['source']+'\n'+(r['rights'] or '')+'\n' for r in reports))
print(json.dumps([dict(id=r['id'],books=r['books'],units=r['units']) for r in reports],indent=2));print('Packed text bytes',sum(x['packed_bytes'] for x in manifest.values()));print('Source/USFM archive bytes',sum(f.stat().st_size for f in (OUT/'sources').glob('*.zip')))
