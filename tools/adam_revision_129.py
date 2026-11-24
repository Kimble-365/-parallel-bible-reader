from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parents[1];S=R/'releases/v1.28';D=R/'releases/v1.29';shutil.copytree(S,D,dirs_exist_ok=True)
change=json.loads(Path(r'E:\FinnishTranslation-edition\edition\v006\authorized_changes.json').read_text(encoding='utf-8'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
for name in ['index.html','boot.js','reader.js','sw.js','study-menu.js','manifest.webmanifest','VERSION']:
 p=D/name;p.write_text(p.read_text(encoding='utf-8').replace('1.28','1.29'),encoding='utf-8',newline='\n')
pack=D/'study-data/GEN.json';data=json.loads(pack.read_text(encoding='utf-8'))
for v in data['editions']['fin-study-v005']:
 ref=f'Gen {v[0]}:{v[1]}'
 if ref in change['changes']:assert v[2]==change['changes'][ref]['before'];v[2]=change['changes'][ref]['after']
for v in data['editions']['fin-study-notes-v005']:
 if v[0:2]==[2,20]:
  v[2]=v[2].replace(change['note_before'],change['note_after'])
  for b in v[7]['blocks']:
   if b.get('note_id')=='note-38':assert b['text']==change['note_before'];b['text']=change['note_after']
dump(pack,data)
# Use a new offline revision only for the changed companions; existing stores remain intact.
p=D/'offline-library.js';s=p.read_text(encoding='utf-8').replace("revision+'|'+id+'|'+book","revision+'|'+id+'|'+(['fin-study-v005','fin-study-notes-v005'].includes(id)?'adam-20261124|':'')+book");p.write_text(s,encoding='utf-8',newline='\n')
manifest=json.loads((D/'reference-manifest.js').read_text().split('=',1)[1].strip().rstrip(';'));b=pack.read_bytes();manifest['GEN']={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()};(D/'reference-manifest.js').write_text('window.ReaderReferencePacks='+json.dumps(manifest,separators=(',',':'))+';\n',encoding='utf-8',newline='\n')
cat=json.loads((D/'catalog.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'));cat['release_version']='1.29'
for e in cat['editions']:
 if e['id'] in ['fin-study-v005','fin-study-notes-v005']:e['label']=e['label'].replace('v005','v006');e['title']=e['label'];e['method']+=' User-authorized Adam revision 2026-11-24; five verses and note 38.'
(D/'catalog.js').write_text('window.BibleCatalog='+json.dumps(cat,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8',newline='\n')
dump(D/'verification/adam-authorized-changes.json',change)
(D/'README.md').write_text('# Parallel Bible Reader 1.29\n\nUser-authorized Adam revision: Genesis 2:20 (both occurrences), 3:17, 3:20, 3:21 and 4:1. Note 38 at Genesis 2:20 explains Hebrew adam, the article forms and the name choice. Other verse words, notes and all TSK links remain unchanged. New companion cache keys retain old saved copies without serving stale wording. Source/editorial status remains unreviewed. Version 1.28 is preserved.\n',encoding='utf-8')
p=R/'index.html';p.write_text(p.read_text(encoding='utf-8').replace('1.28','1.29'),encoding='utf-8',newline='\n')
p=R/'releases/index.html';p.write_text(p.read_text(encoding='utf-8').replace('</ul>','<li><a href="v1.29/">1.29 — Authorized Adam wording and explanatory note</a></li></ul>'),encoding='utf-8',newline='\n')
print('Prepared 1.29: five verses, one note, cache revision')
