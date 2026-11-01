"""BHH 1.23: reproducible, role-aware source import. Standard library only.
Usage: python tools/import_bhh_123.py --sources /path --bhh /path/BHH
External acquisitions are inputs, never executable code. Unknown MAM roles fail closed.
"""
import argparse,collections,csv,gzip,hashlib,json,re,shutil,sqlite3
from pathlib import Path
R=Path(__file__).resolve().parents[1]; O=R/'releases/v1.23'
def dumps(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def readjs(p):return json.loads(p.read_text().split('=',1)[1].rstrip(';\n'))
def writejs(p,name,d):p.write_text('window.'+name+'='+dumps(d)+';\n')
def sha(b):return hashlib.sha256(b).hexdigest()
def packed(path,data):
 raw=data if isinstance(data,bytes) else data.encode() if isinstance(data,str) else dumps(data).encode();b=gzip.compress(raw,mtime=0);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b)
 return dict(sha256=sha(raw),bytes=len(raw),packed_sha256=sha(b),packed_bytes=len(b))
def mam(n):
 t=n['type']
 if t=='scrdfftar':return mam(next(x for x in n['contents'] if x['type']=='sdt-target'))
 if t=='cant-all-three':return mam(next(x for x in n['contents'] if x['type']=='cant-combined'))
 if t=='kq':return ' '.join(mam(x) for x in n['contents'])
 if t in {'sdt-note','good-ending'}:return ''
 if t in {'lp-legarmeih','lp-paseq'}:return '׀' if t=='lp-legarmeih' else ' ׀ '
 if t=='implicit-maqaf':return '־'
 if t=='spi-invnun':return '׆'+(' ' if n.get('class')=='including-trailing-space' else '')
 if t in {'spi-pe2','spi-pe3','spi-samekh2','spi-samekh3','shirah-space'}:return ' '
 if t=='kq-k-velo-q-maq':return '־'
 if t in {'text','verse','slh-word','sdt-target','cant-combined','kq-k','kq-q','kq-trivial','kq-k-velo-q','kq-q-velo-k','letter-large','letter-small','letter-hung','silluq-before-meteg'}:
  return n['text'] if 'text' in n else ''.join(mam(x) for x in n.get('contents',[]))
 raise ValueError('Unknown MAM role: '+t)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--sources',type=Path,required=True);ap.add_argument('--bhh',type=Path,required=True);a=ap.parse_args();S=a.sources
 shutil.copytree(R/'releases/v1.22',O,dirs_exist_ok=True,ignore=shutil.ignore_patterns('related-data','sources'))
 # Version shell; immutable older payload paths and storage revision stay intact.
 for p in O.rglob('*'):
  if p.is_file() and p.suffix in {'.js','.html','.css','.webmanifest','.md'} and p.name not in {'catalog.js','pack-manifest.js','search-manifest.js'}:
   p.write_text(p.read_text().replace('1.22','1.23'))
 (O/'VERSION').write_text('1.23\n')
 C=readjs(R/'releases/v1.22/catalog.js'); books=dict(C['books']); namecodes={n:b for b,n in C['books']};namecodes['Song of Songs']='SNG'
 osis='Gen Exod Lev Num Deut Josh Judg Ruth 1Sam 2Sam 1Kgs 2Kgs 1Chr 2Chr Ezra Neh Esth Job Ps Prov Eccl Song Isa Jer Lam Ezek Dan Hos Joel Amos Obad Jonah Mic Nah Hab Zeph Hag Zech Mal'.split(); omap=dict(zip(osis,[b for b,n in C['books'][:39]]))
 allbooks=collections.defaultdict(lambda:{'editions':{}});reports=[];assets=[];src=O/'bhh-sources';src.mkdir(exist_ok=True)
 db=sqlite3.connect(S/'reader-bhh.sqlite3');db.executescript('CREATE TABLE IF NOT EXISTS verses(edition TEXT,book TEXT,chapter INTEGER,verse INTEGER,text TEXT,PRIMARY KEY(edition,book,chapter,verse)); DELETE FROM verses; CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(edition UNINDEXED,book UNINDEXED,chapter UNINDEXED,verse UNINDEXED,text); DELETE FROM search;')
 def asset(p,label,license,url):
  dest=src/(p.name+'.gz');m=packed(dest,p.read_bytes());assets.append(dict(id=p.stem,title=label,url='bhh-sources/'+dest.name,license=license,source=url,**m));return m
 def edition(id,label,lang,license,url,method,data,attribution):
  positions=[];count=0
  for book,rows in data.items():
   assert rows and len({(r[0],r[1]) for r in rows})==len(rows),(id,book)
   allbooks[book]['book']=book;allbooks[book]['editions'][id]=rows;positions.extend([book,c] for c in sorted({r[0] for r in rows}));count+=len(rows)
   db.executemany('INSERT INTO verses VALUES(?,?,?,?,?)',[(id,book,r[0],r[1],r[2]) for r in rows])
  meta=dict(id=id,label=label,title=label,language=lang,latin_language=lang,script='Latin' if lang=='la' else 'Hebrew',direction='ltr' if lang=='la' else 'rtl',available=True,scope=f'{len(data)} source books; {count} verse records',source=url,license=license,license_url='https://creativecommons.org/licenses/'+('by-nc/4.0/' if 'NC' in license else 'by-sa/4.0/' if 'SA' in license else 'by/4.0/') if license.startswith('CC') else 'https://hebrewbible.dev/license',attribution=attribution,method=method,has_transliteration=False,book_codes=list(data),positions=positions,preserve_source_refs=True,versification_label='Source verse labels; equivalence across traditions not verified',data_group='bhh-1.23')
  C['editions'].append(meta);reports.append(dict(id=id,books=len(data),verses=count,license=license,source=url,method=method))
 # Primary SP preserves morpheme trailers; THB's word JSON lacks those boundaries.
 sp=collections.defaultdict(dict)
 with gzip.open(a.bhh/'data/indexes/sp.tsv.gz','rt') as f:
  for x in csv.DictReader(f,delimiter='\t'):
   loc=json.loads(x['locator']);book=namecodes[loc['book']];key=(int(loc['chapter']),int(loc['verse']));sp[book][key]=sp[book].get(key,'')+x['surface']+loc['trailer']
 data={b:[[c,v,t.strip(),None] for (c,v),t in verses.items()] for b,verses in sp.items()}
 edition('hbo-sp','Samaritan Pentateuch — DT-UCPH 7.2.12','hbo','CC BY-NC 4.0','https://github.com/DT-UCPH/sp','Primary TF morphemes rejoined using source trailers. Samaritan Hebrew in Jewish Hebrew glyphs; consonantal source, no invented pointing. Source verse regrouping retained.',data,'DT-UCPH Samaritan Pentateuch, Text-Fabric 7.2.12; source based on Chester Beatty 751 and Garizim 1. BHH display extraction; no endorsement. Noncommercial reuse only.')
 # Ready Clementine text; drop machine-generated morphology and retain token spelling.
 d=json.loads((S/'thb-vul.json').read_text());data={namecodes[n]:[[c['chapter'],v['verse'],' '.join(w['surface'] for w in v['words']),None] for c in ch for v in c['verses']] for n,ch in d.items()}
 edition('lat-clementine-thb','Latin — Clementine Vulgate (THB OT extract)','la','Public Domain','https://github.com/evenderekh/THB','39-book OT extract, not the complete Vulgate canon. THB surface tokens joined with spaces, including spaces around punctuation; accent spelling retained; inferred morphology excluded.',data,'Clementine Vulgate text via Translator’s Hebrew Bible, Michael Muzar. Ancient/historical text public domain; no claim that ancillary generated morphology is a critically reviewed apparatus.')
 # Native MAM versification, complete 39-book plain-text projection, not complete MAM documentation.
 data={}
 for p in sorted(S.glob('mam-*.json')):
  if p.name in {'mam-sample.json'} or 'dir' in p.name:continue
  try:d=json.loads(p.read_text())
  except ValueError:continue
  if not isinstance(d,dict) or 'versification-tradition' not in d:continue
  for b in d['contents']:
   if b['type'] in {'spi-pe2','spi-pe3','spi-samekh2','spi-samekh3'}:continue
   assert b['type']=='book39',b
   rows=[]
   for c in b['contents']:
    if c['type']!='chapter':continue
    for v in c['contents']:
     if v['type']=='verse':
      _,chapter,verse=v['osisID'].rsplit('.',2);rows.append([int(chapter),int(verse),mam(v),None])
   data[omap[b['osisID']]]=rows
  asset(p,'MAM structured source: '+p.stem[4:],'CC BY-SA 4.0','https://github.com/bdenckla/MAM-basics/tree/main/MAM-simple/json-vtrad-mam')
 assert len(data)==39,len(data)
 edition('hbo-mam','Hebrew — Miqra according to the Masorah (MAM-simple)','hbo','CC BY-SA 4.0','https://en.wikisource.org/wiki/User:Dovi/Miqra_according_to_the_Masorah#beginning','Role-aware MAM-simple projection, native MAM verse labels. Ketiv and qere both shown (unpointed / pointed); combined cantillation selected once. Notes and repeated good endings excluded from running text. Exceptional letters retain text; layout separators become spaces; implicit maqaf shown as maqaf. Original structured files in BHH sources retain roles. This is an incomplete extract of MAM, not a diplomatic Masorah edition.',data,'Hebrew Wikisource — Miqra according to the Masorah, prepared by Seth (Avi) Kadish with Erel Segal-Halevi and Benjamin Denckla. https://en.wikisource.org/wiki/User:Dovi/Miqra_according_to_the_Masorah#beginning . CC BY-SA 4.0; BHH plain-text projection changes described in method.')
 pack={};search=readjs(O/'search-manifest.js')
 for b,d in allbooks.items():
  pack[b]=packed(O/'bhh-data'/(b+'.json.gz'),d)
  for id,rows in d['editions'].items():search['editions'].setdefault(id,{})[b]=sha(dumps(rows).encode())
 writejs(O/'bhh-manifest.js','BHHTextPacks',pack);writejs(O/'catalog.js','BibleCatalog',C);writejs(O/'search-manifest.js','ReaderSearchManifest',search)
 # DSS: physical source units remain distinct, with all flags and locators intact.
 scrolls=collections.defaultdict(list)
 with gzip.open(a.bhh/'data/indexes/dss.tsv.gz','rt') as f:
  for x in csv.DictReader(f,delimiter='\t'):
   x['locator']=json.loads(x['locator']);x['flags']=json.loads(x['flags'] or '{}');scrolls[x['witness']].append(x)
 sm=[]
 for i,(name,units) in enumerate(scrolls.items()):
  p=O/'bhh-dss'/(str(i)+'.json.gz');m=packed(p,units);sm.append(dict(name=name,url='bhh-dss/'+p.name,units=len(units),**m))
 # Ancillary source readers preserve exact source contents rather than silently converting editorial data.
 for n,label,lic,url in [('thb-map.json','THB/Copenhagen versification map — unreviewed equivalence claims','CC BY-SA 4.0','https://github.com/evenderekh/THB'),('thb-lex-mt.json','THB BDB Hebrew lexicon','CC BY 4.0 + Public Domain','https://github.com/evenderekh/THB'),('thb-lex-lxx.json','THB LSJ Greek lexicon','CC BY-SA 4.0','https://github.com/evenderekh/THB')]:asset(S/n,label,lic,url)
 for p in sorted(S.glob('step-TAHOT*.txt')):asset(p,'STEPBible '+p.stem[5:]+' — tagged research text, including editorial readings','CC BY 4.0','https://github.com/STEPBible/STEPBible-Data')
 assert len(list(S.glob('step-TAHOT*.txt')))==4
 for p in [S/'mam-license.json',S/'mam-readme.json',S/'thb-readme.json']:
  shutil.copyfile(p,src/(p.stem+'.md'))
 related=json.loads((a.bhh/'data/related-projects.json').read_text());(src/'related-projects.json').write_text(json.dumps(related,ensure_ascii=False,indent=2))
 writejs(O/'bhh-library.js','BHHLibrary',dict(scrolls=sm,assets=assets,projects=related))
 db.execute('INSERT INTO search SELECT * FROM verses');db.commit();db.close()
 report=dict(release='1.23',editions=reports,dss_labels=len(sm),dss_units=sum(x['units'] for x in sm),ancillary_assets=assets,source_sha256={p.name:sha(p.read_bytes()) for p in S.iterdir() if p.is_file() and p.suffix in {'.json','.txt'}},compressed_text_bytes=sum(x['packed_bytes'] for x in pack.values()),compressed_dss_bytes=sum(x['packed_bytes'] for x in sm))
 (src/'import-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in {'ancillary_assets','source_sha256'}},indent=2))
if __name__=='__main__':main()
