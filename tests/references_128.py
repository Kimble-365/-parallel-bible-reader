"""Independent checks of every reference pack and retained source tag."""
from pathlib import Path
import json,gzip,re,html,hashlib,collections
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'releases/v1.28'
def js(p):return json.loads(p.read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
old=js(ROOT/'releases/v1.27/catalog.js');new=js(R/'catalog.js');manifest=js(R/'reference-manifest.js')
assert new['version']==old['version'],'Existing IndexedDB revision must remain unchanged'
assert new['editions'][:len(old['editions'])]==old['editions']
assert len(new['editions'])==len(old['editions'])+3
raw=[json.loads(line) for line in gzip.decompress((R/'sources/tsk/source-entries.jsonl.gz').read_bytes()).decode().splitlines()]
rawmap={x['reference']:x['thml'] for x in raw};assert len(rawmap)==31090
packs={code:json.loads((R/f'study-data/{code}.json').read_text(encoding='utf-8')) for code in manifest}
keys={f'{code} {r[0]}:{r[1]}' for code,p in packs.items() for r in p['editions']['tsk-crosswire']}
assert len(keys)==31102
fin=json.loads((ROOT/'texts/finnish-study-v005/bible.json').read_text(encoding='utf-8'))['verses']
expected={f"{v['book']} {v['chapter']}:{v['verse']}":v['text'] for v in fin};got={}
notes=[];links=0;tags=0;frefs=0
for code,data in packs.items():
    body=(R/f'study-data/{code}.json').read_bytes();assert hashlib.sha256(body).hexdigest()==manifest[code]['sha256'] and len(body)==manifest[code]['bytes']
    for r in data['editions']['fin-study-v005']:got[f'{code} {r[0]}:{r[1]}']=r[2]
    for r in data['editions']['fin-study-notes-v005']:
        for b in r[7]['blocks']:
            if b.get('note_id'):notes.append((f'{code} {r[0]}:{r[1]}',b['note_id'],b['text']))
            for t in b.get('targets',[]):assert f"{t['book']} {t['chapter']}:{t['verse']}" in expected;frefs+=1
    for r in data['editions']['tsk-crosswire']:
        ref=f'{code} {r[0]}:{r[1]}';source=rawmap.get(ref,'')
        source_refs=[]
        for attrs,text in re.findall(r'<scripRef\b([^>]*)>(.*?)</scripRef>',source,re.I|re.S):
            m=re.search(r'passage="([^"]*)"',attrs);source_refs.append(html.unescape(m[1] if m else re.sub('<[^>]+>','',text)))
        actual=[b['source_reference'] for b in r[7]['blocks'] if 'source_reference' in b]
        assert actual==source_refs,ref
        tags+=len(source_refs)
        for block in r[7]['blocks']:
            for t in block.get('targets',[]):
                assert f"{t['book']} {t['chapter']}:{t['verse']}" in keys,(ref,t)
                assert f"{t.get('end_book',t['book'])} {t['end_chapter']}:{t['end_verse']}" in keys,(ref,t)
                links+=1
assert got==expected and len(got)==31170
source_notes=json.loads((ROOT/'texts/finnish-study-v005/footnotes.json').read_text(encoding='utf-8'))['notes']
assert sorted(notes)==sorted((x['reference'],x['id'],x['text']) for x in source_notes)
assert frefs==110 and len(notes)==24531 and tags==85312
report=json.loads((R/'sources/tsk/validation.json').read_text());assert links==report['validated_target_links']
assert hashlib.sha256((R/'sources/tsk/TSK-1.4.zip').read_bytes()).hexdigest()==report['source_archive_sha256']
assert hashlib.sha256(gzip.decompress((R/'sources/tsk/source-entries.jsonl.gz').read_bytes())).hexdigest()==report['source_entries_sha256']
print('PASS:',len(packs),'packs;',len(raw),'source entries;',tags,'source tags;',links,'validated links;',len(notes),'Finnish notes; existing editions/store revision preserved')
