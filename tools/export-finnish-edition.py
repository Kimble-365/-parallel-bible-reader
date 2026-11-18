"""Export the frozen Finnish edition; annotations stay outside Bible rows."""
from pathlib import Path
import argparse, hashlib, json, re, sqlite3

p = argparse.ArgumentParser()
p.add_argument('source', type=Path)
p.add_argument('--output', type=Path, default=Path('texts/finnish-study-v005'))
a = p.parse_args(); source = a.source; out = a.output
out.mkdir(parents=True, exist_ok=True)
def read(path): return json.loads(path.read_text(encoding='utf-8'))
def write(name, data):
    (out/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
books = [read(f) for f in sorted((source/'books').glob('*/keruutiedosto.json'))]
codes = 'GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV'.split()
assert len(books)==len(codes)==66
mapping = {b['book']:code for b,code in zip(books,codes)}
def ref(s):
    book, cv = s.split(); return mapping[book]+' '+cv
verses = [{'book':mapping[b['book']], 'chapter':v['chapter'], 'verse':v['verse'], 'text':v['text']} for b in books for v in b['verses']]
keys = {f"{v['book']} {v['chapter']}:{v['verse']}" for v in verses}
db=source/'raw/locked_baseline/output/20261117T121530855037Z/FINNISH_BIBLE_WORKING.sqlite'
assert hashlib.sha256(db.read_bytes()).hexdigest()=='c6479aa2114044c23a4862a128f67bef260e5a3da0c478c68d17a9b29e54157c'
with sqlite3.connect(db.as_uri()+'?mode=ro',uri=True) as c:
    locked={ref(r):t for r,t in c.execute('select reference,text from verses')}
assert locked=={f"{v['book']} {v['chapter']}:{v['verse']}":v['text'] for v in verses}
notes=[]
for f in sorted((source/'books').glob('*/huomautukset_lukijalle_20261118.json')):
    for n in read(f): notes.append({'id':'note-'+n['note_id'], 'reference':ref(n['reference']), 'text':n['text']})
assert len(notes)==24531 and len({n['id'] for n in notes})==24531
assert all(n['reference'] in keys for n in notes)
pairs=read(source/'edition/liitteet/ristiviitteet.json')
xrefs=[]
for i,row in enumerate(pairs,1):
    for reverse in [False,True]:
        xrefs.append({'pair_id':f'xref-{i}', 'reference':ref(row['target'] if reverse else row['reference']), 'target':ref(row['reference'] if reverse else row['target']), 'kind':row['kind'], 'topic':row['topic'], 'status':row['status'], 'pair_source_collation':row['pair_source_collation']})
assert len(xrefs)==110 and all(x['reference'] in keys and x['target'] in keys for x in xrefs)
write('bible.json',{'verses':verses})
write('footnotes.json',{'edition':'finnish-study-v005','notes':notes})
write('crossreferences.json',{'edition':'finnish-study-v005','pairs':55,'links':xrefs})
write('metadata.json',{'id':'finnish-study-v005','title':'Suomenkielinen tutkimusraamattu','language':'fi','version':'v005','editorial_date':'2026-11-18','status':'unreviewed','books':[{'code':mapping[b['book']],'source_code':b['book'],'title':b['title']} for b in books],'bible':'bible.json','footnotes':'footnotes.json','crossreferences':'crossreferences.json','text_format':'Frozen source wording; source emphasis asterisks and poetry slash markers retained. Footnote text and cross-references are separate.','rights':'User-authorized export of this project edition. No third-party source corpora or source modules included; no new license grant inferred.','source_database_sha256':hashlib.sha256(db.read_bytes()).hexdigest()})
write('validation.json',{'status':'PASS','books':66,'chapters':len({(v['book'],v['chapter']) for v in verses}),'verses':len(verses),'footnotes':len(notes),'crossreference_pairs':55,'crossreference_links':110,'all_annotation_references_resolve':True,'verse_text_exactly_matches_frozen_database':True,'translation_review_performed':False,'reader_integration':'Importable Bible JSON; separate annotation datasets, not installed into the reader annotation UI.'})
assert len(verses)==31170
write('SHA256SUMS.json',{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.glob('*.json')) if f.name!='SHA256SUMS.json'})
print('PASS: 31170 verses, 24531 notes, 110 cross-reference links')
