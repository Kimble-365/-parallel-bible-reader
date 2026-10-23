"""Import a licensed six-language sample from the verified SAB 14.7 distribution.
Source copyright declarations are retained verbatim; unspecified-license resources excluded.
"""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import sqlite3,json,re,shutil,hashlib,sys,xml.etree.ElementTree as E
from import_original_languages import handle,latin,cl
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'releases/v1.7';BASE=Path('/workspace/sab-hindi-pilot/tools/sab/data/bibles')
SPECS=[('fra - Louis Segond 1910','fra-lsg1910','French — Louis Segond 1910','fra','Latin','Public Domain','Indo-European','Romance',['France','Belgium','Canada','Democratic Republic of the Congo'],['Europe','North America','Africa'],['français']),('spa - Reina Valera 1909','spa-rv1909','Spanish — Reina Valera 1909','spa','Latin','Public Domain','Indo-European','Romance',['Spain','Mexico','Argentina','United States'],['Europe','North America','South America'],['español','castellano']),('rus - Russian Synodal Bible','rus-synodal','Russian — Synodal','rus','Cyrillic','Public Domain','Indo-European','Slavic',['Russia','Kazakhstan'],['Europe','Asia'],['русский']),('zht - Chinese Union Version Traditional','cmn-cuv-hant','Chinese — Union Version, Traditional','cmn','Han (Traditional)','Public Domain','Sino-Tibetan','Sinitic',['China','Taiwan','Singapore'],['Asia'],['中文','國語','華語','Mandarin','zht']),('arb - Van Dyck Bible','arb-vandyck','Arabic — Van Dyck','arb','Arabic','Public Domain','Afro-Asiatic','Semitic',['Egypt','Lebanon','Syria'],['Africa','Asia'],['العربية','Standard Arabic']),('bis - Open Bislama Bible Revised','bis-obbr','Bislama — Open Revised','bis','Latin','CC BY-SA 4.0','Creole (project grouping)','English-lexifier',['Vanuatu'],['Australasia'],['Bislama'])]
def extract(raw):
 book=re.search(r'\\id\s+(\w+)',raw)[1];text=raw
 for marker in ['f','fe','x','va','ca','vp']:text=re.sub(r'\\'+marker+r'\s.*?\\'+marker+r'\*','',text,flags=re.S)
 rows=[];chapter=None;verse=None;endverse=None;parts=[]
 def flush():
  if verse is None:return
  text=re.sub(r'\s+',' ',''.join(parts)).strip();assert '\\' not in text,(book,chapter,verse,text[:100]);rows.append([chapter,verse,text]+([endverse] if endverse else []))
 skip={'id','h','toc1','toc2','toc3','mt','mt1','mt2','mt3','s','s1','s2','s3','r','d','ms','mr','sp','is','ip','iot','io1','io2','ie','rem','ide','usfm','cl'}
 for m in re.finditer(r'\\(\+?[a-zA-Z][a-zA-Z0-9]*)(\*)?\s*([^\\]*)',text):
  tag,end,payload=m.groups();tag=tag.lstrip('+')
  if tag=='c':flush();chapter=int(payload.split()[0]);verse=None;parts=[];continue
  if tag=='v':
   flush();v=re.match(r'(\d+)(?:-(\d+))?\s*(.*)',payload,re.S);assert v,payload[:50];verse=int(v[1]);endverse=int(v[2]) if v[2] else None;parts=[v[3]];continue
  if tag in skip:continue
  if verse is not None:
   if tag=='w' and not end:payload=payload.split('|')[0]
   parts.append(payload if tag in ['w','add','it','bd','bk','ord','nd','wj','sc','qt'] or end else ' '+payload)
 flush();assert len(rows)==len(re.findall(r'\\v\s+\d+',raw)),book
 merged={}
 for row in rows:
  key=(row[0],row[1])
  if key in merged:
   old=merged[key];old[2]+='\n'+row[2]
   if len(old)<4:old.append(None)
   if len(old)<5:old.append(1)
   old[4]+=1
  else:merged[key]=row
 return book,list(merged.values())

def main():
 OUT.mkdir(exist_ok=True);(OUT/'sources').mkdir(exist_ok=True);(OUT/'extra-data').mkdir(exist_ok=True)
 cat=json.loads((OUT/'catalog.js').read_text().split('=',1)[1].rstrip(';\n'));known=[b for b,_ in cat['books']];metadata=json.loads((OUT/'translations/metadata.js').read_text().split('=',1)[1].rstrip(';\n'));existing={spec[1] for spec in SPECS};cat['editions']=[e for e in cat['editions'] if e['id'] not in existing];metadata=[e for e in metadata if e['id'] not in existing];overlays={};db=sqlite3.connect('/workspace/biblical-encyclopedia/encyclopedia.sqlite3');reports=[];licenses=(OUT/'LICENSES.md').read_text()
 for folder,id,label,iso,script,license,family,branch,countries,continents,aliases in SPECS:
  directory=BASE/folder;proof=(directory/'!books.xml').read_text();copyright=E.fromstring(proof).find("metadata/meta[@name='copyright-text']").get('content');assert ('public' in copyright.lower() or 'público' in copyright.lower() or 'by-sa 4.0' in copyright.lower()),copyright
  files=[p for p in directory.iterdir() if p.suffix.lower() in ['.sfm','.usfm']];records=[];books=[];sourcezip=OUT/'sources'/(id+'-usfm.zip');source='https://software.sil.org/scriptureappbuilder/'
  h=handle('Cyrillic-Latin' if script=='Cyrillic' else 'Han-Latin' if script.startswith('Han') else 'Arabic-Latin') if script!='Latin' else None
  with ZipFile(sourcezip,'w',ZIP_DEFLATED) as z:
   z.writestr('source-copyright.xml',proof)
   for f in sorted(files):
    raw=f.read_text(encoding='utf-8-sig');z.writestr(f.name,raw);book,rows=extract(raw);assert book in known,book;books.append(book);db.execute('INSERT OR REPLACE INTO reader_source_usfm VALUES(?,?,?,?)',(id,book,hashlib.sha256(raw.encode()).hexdigest(),raw));data=[]
    for row in rows:
     c,v,text=row[:3];rom=latin(h,text) if h else text;data.append([c,v,text,rom]+([row[3]] if len(row)>3 else [])+([row[4]] if len(row)>4 else []));records.append((id,book,c,v,text,rom,1))
    overlays.setdefault(book,{})[id]=data
  if h:cl(h)
  assert len(books)==66,(id,len(books));db.executemany('INSERT OR REPLACE INTO bible_verses VALUES(?,?,?,?,?,?,?)',records)
  language='zh-Hant' if iso=='cmn' else iso
  meta=dict(id=id,label=label,title=label,language=language,latin_language=iso+'-Latn',script=script,direction='rtl' if script=='Arabic' else 'ltr',scope='Full Bible (66 books)',source=source,available=True,license=license,attribution=copyright+' Source: '+folder+' distributed with Scripture App Builder 14.7. Plain-verse display extraction and orthographic Latin adaptation by this project; no endorsement.',method='Source USFM retained. '+('Original Latin text.' if script=='Latin' else 'ICU 76 orthographic Latin; language/contextual reading is not reconstructed. Chinese readings are mechanical and may be contextually wrong.' if script.startswith('Han') else 'ICU 76 orthographic Latin, not pronunciation. Unwritten Arabic vowels not reconstructed.'),book_codes=[b for b in known if b in books],positions=sorted({(r[1],r[2]) for r in records},key=lambda p:(known.index(p[0]),p[1])),has_transliteration=True)
  if license.startswith('CC'):meta['license_url']='https://creativecommons.org/licenses/by-sa/4.0/'
  cat['editions'].append(meta);db.execute('INSERT OR REPLACE INTO reader_catalog VALUES(?,?)',(id,json.dumps(meta,ensure_ascii=False)))
  metadata.append(dict(id=id,language=label.split(' — ')[0],iso6393=iso,aliases=aliases,family=family,branch=branch,countries=countries,continents=continents,states=[],script=script,variety=label,classification_source='Project browsing group; not a claimed UBS genealogy',ubs_id=None))
  licenses+='\n\n## '+label+'\n\n'+meta['attribution']+'\n\n'+license+'. '+meta['method']+' Raw source and copyright declaration: sources/'+id+'-usfm.zip .\n'
  reports.append(dict(id=id,books=len(books),records=len(records),copyright=copyright,archive_sha256=hashlib.sha256(sourcezip.read_bytes()).hexdigest(),source=source))
 for book,editions in overlays.items():
  p=OUT/'extra-data'/(book+'.js');data=json.loads(p.read_text().split('=',2)[2].rstrip(';')) if False else None
  # Existing overlays have a namespace initialization before the assignment.
  text=p.read_text();start=text.index(']=')+2;data=json.loads(text[start:].rstrip(';'));data['editions'].update(editions);p.write_text('window.ExtraBibleBooks=window.ExtraBibleBooks||{};window.ExtraBibleBooks['+json.dumps(book)+']='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';')
 cat['version']=str(cat['version'])+'-global-1.7';(OUT/'catalog.js').write_text('window.BibleCatalog='+json.dumps(cat,ensure_ascii=False,separators=(',',':'))+';');(OUT/'translations/metadata.js').write_text('window.TranslationDirectory='+json.dumps(metadata,ensure_ascii=False,separators=(',',':'))+';');(OUT/'LICENSES.md').write_text(licenses);(OUT/'sources/global-import-report.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2))
 db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS reader_search_all_v1 USING fts5(edition UNINDEXED,book UNINDEXED,chapter UNINDEXED,verse UNINDEXED,original,latin,tokenize='unicode61 remove_diacritics 0')");db.execute('DELETE FROM reader_search_all_v1');db.execute('INSERT INTO reader_search_all_v1 SELECT edition,book,chapter,verse,original,latin FROM bible_verses');db.commit();db.close();print(json.dumps(reports,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
