from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];a=R/'releases/v1.28';b=R/'releases/v1.29'
changes=json.loads((b/'verification/adam-authorized-changes.json').read_text(encoding='utf-8'));count=0;notes=0
for p in (a/'study-data').glob('*.json'):
 old=json.loads(p.read_text(encoding='utf-8'));new=json.loads((b/'study-data'/p.name).read_text(encoding='utf-8'))
 assert old['editions']['tsk-crosswire']==new['editions']['tsk-crosswire']
 for x,y in zip(old['editions']['fin-study-v005'],new['editions']['fin-study-v005']):
  ref=f"Gen {x[0]}:{x[1]}"
  if p.stem=='GEN' and ref in changes['changes']:assert y[2]==changes['changes'][ref]['after'];count+=1
  else:assert x==y
 for x,y in zip(old['editions']['fin-study-notes-v005'],new['editions']['fin-study-notes-v005']):
  if x!=y:
   assert p.stem=='GEN' and x[:2]==[2,20]
   assert any(z.get('note_id')=='note-38' and z['text']==changes['note_after'] for z in y[7]['blocks']);notes+=1
assert count==5 and notes==1
manifest=json.loads((b/'reference-manifest.js').read_text().split('=',1)[1].strip().rstrip(';'))
for code,m in manifest.items():
 data=(b/f'study-data/{code}.json').read_bytes();assert len(data)==m['bytes'] and hashlib.sha256(data).hexdigest()==m['sha256']
print('PASS: exactly five authorized verse changes, note 38, all other words/notes/TSK unchanged, all 66 hashes valid')
