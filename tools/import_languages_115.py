"""Import historical Danish NT and Esperanto; preserve supplied source positions."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import tarfile,json,re,hashlib
from import_global_sample import extract
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'releases/v1.15';SRC=Path('/workspace/reader-new-sources/v115')
def read(p):return json.loads(p.read_text().split('=',1)[1].rstrip(';\n'))
cat=read(OUT/'catalog.js');directory=read(OUT/'translations/metadata.js');overlays={};reports=[]
(OUT/'sources').mkdir(exist_ok=True);(OUT/'extra-data').mkdir(exist_ok=True)
specs=[('dan-1819','Danish — New Testament 1819','da','dan','dant1819','Danish','Germanic',['Denmark'],['dansk','Dansk','1819'],'https://github.com/emg/Danish-Bible-NT-1819'),('epo-londona','Esperanto — Londona Biblio','eo','epo','esperanto','Esperanto','Constructed language',[],['Esperanto','Londona','Zamenhof'],'https://github.com/thiagobodruk/bible/blob/master/json/eo_esp.json')]
with tarfile.open('/workspace/reader-new-sources/Brenton-catalog.tgz') as tar:
 for id,label,lang,iso,module,language,branch,countries,aliases,url in specs:
  conf=tar.extractfile('mods.d/'+module+'.conf').read().decode();assert 'DistributionLicense=Public Domain' in conf
  raws={};books={}
  if iso=='dan':
   for p in sorted((SRC/'dan').glob('*.SFM')):
    raw=p.read_text();book,rows=extract(raw);books[book]=rows;raws[p.name]=p.read_bytes()
   assert len(books)==27
  else:
   p=SRC/'eo_esp.json';raws[p.name]=p.read_bytes();data=json.loads(raws[p.name]);assert len(data)==66
   for (book,_),b in zip(cat['books'][:66],data):
    books[book]=[[c,v,text] for c,ch in enumerate(b['chapters'],1) for v,text in enumerate(ch,1) if text.strip()]
  provenance=dict(source=url,files=[dict(file=n,sha256=hashlib.sha256(b).hexdigest(),git_blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()) for n,b in raws.items()])
  for book,rows in books.items():
   assert len({(r[0],r[1]) for r in rows})==len(rows)
   overlays.setdefault(book,{})[id]=[[r[0],r[1],r[2],r[2]] for r in rows]
  method='Original Latin script with historical spelling and accents retained; no phonetic reconstruction. Source footnotes remain in raw USFM; display contains verse text.' if iso=='dan' else 'Original Latin script and Esperanto diacritics retained. Chapter/verse positions follow the source arrays; no modernized spelling or phonetic reconstruction.'
  meta=dict(id=id,label=label,title=label,language=lang,latin_language=lang,script='Latin',direction='ltr',available=True,scope='New Testament (27 source books)' if iso=='dan' else 'Full Bible (66 source books)',source=url,license='Public Domain',license_url='https://creativecommons.org/publicdomain/mark/1.0/',attribution=label+'. Public Domain declaration: CrossWire '+module+'. '+method,method=method,has_transliteration=False,book_codes=[b for b,_ in cat['books'] if b in books],positions=[[b,c] for b,_ in cat['books'] if b in books for c in dict.fromkeys(r[0] for r in books[b])],preserve_source_refs=True,versification_label='Source positions; equal labels do not prove alignment',data_group='languages-1.15')
  cat['editions']=[e for e in cat['editions'] if e['id']!=id]+[meta];directory=[e for e in directory if e['id']!=id]+[dict(id=id,language=language,iso6393=iso,aliases=aliases,family='Indo-European' if iso=='dan' else 'Constructed languages',branch=branch,countries=countries,continents=['Europe'] if iso=='dan' else [],states=[],script='Latin',variety=label,classification_source='ISO identity and project browsing groups; no asserted UBS identifier',ubs_id=None)]
  with ZipFile(OUT/'sources'/(id+'-raw.zip'),'w',ZIP_DEFLATED) as z:
   for n,b in raws.items():z.writestr(n,b)
   z.writestr(module+'.conf',conf);z.writestr('PROVENANCE.json',json.dumps(provenance,indent=2))
  with ZipFile(OUT/'sources'/(id+'-display-usfm.zip'),'w',ZIP_DEFLATED) as z:
   for book,rows in books.items():
    lines=['\\id '+book,'\\usfm 3.0','\\ide UTF-8'];last=None
    for c,v,text,*_ in rows:
     if c!=last:lines.append('\\c '+str(c));last=c
     lines.append('\\v '+str(v)+' '+text)
    z.writestr(book+'.usfm','\n'.join(lines)+'\n')
  reports.append(dict(id=id,books=len(books),units=sum(map(len,books.values())),license='Public Domain',method=method,**provenance))
for book,editions in overlays.items():(OUT/'extra-data'/(book+'.js')).write_text('window.ExtraBibleBooks=window.ExtraBibleBooks||{};window.ExtraBibleBooks['+json.dumps(book)+']='+json.dumps(dict(book=book,editions=editions),ensure_ascii=False,separators=(',',':'))+';')
(OUT/'catalog.js').write_text('window.BibleCatalog='+json.dumps(cat,ensure_ascii=False,separators=(',',':'))+';');(OUT/'translations/metadata.js').write_text('window.TranslationDirectory='+json.dumps(directory,ensure_ascii=False,separators=(',',':'))+';');(OUT/'sources/languages-import.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
p=OUT/'LICENSES.md';base=p.read_text().split('\n<!-- 1.15 additions -->')[0];p.write_text(base+'\n<!-- 1.15 additions -->\n'+''.join('\n## '+s[1]+'\n\nPublic Domain; corresponding CrossWire module declaration and exact source retained in sources/'+s[0]+'-raw.zip. '+s[-1]+'\n' for s in specs))
print([(r['id'],r['books'],r['units']) for r in reports])
