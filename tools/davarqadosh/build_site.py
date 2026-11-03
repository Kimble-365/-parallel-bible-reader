"""Build book packs and a self-contained parallel reader artifact; never edit releases."""
from pathlib import Path
import argparse, gzip, json, re, shutil, sys
from corpus import BOOKS, SOURCE_REVISION, atomic, build_book, canonical, digest, pack_book

READER_REVISION='9554e05a170e2a44e3cfa7156b6d3ccbd421c197'

def parse_bundle(path, code):
    if not path.exists(): return {}
    text=(gzip.decompress(path.read_bytes()).decode() if path.suffix=='.gz' else path.read_text())
    if not text.lstrip().startswith('{'):
        m=re.search(r'window\.(?:ExtraBibleBooks|BibleBooks)\["'+code+r'"\]\s*=\s*',text)
        if not m:raise ValueError('Unexpected bundle '+str(path))
        text=text[m.end():].strip().rstrip(';')
    return json.loads(text).get('editions',{})

def build(source,lexicon,repo,out,books,work,research=None):
    repo=Path(repo);out=Path(out);work=Path(work)
    if out.resolve()==repo.resolve() or repo.resolve() in out.resolve().parents and out.name=='davarqadosh':
        raise ValueError('Build into an artifact directory, not the source reader')
    out.mkdir(parents=True,exist_ok=True)
    shutil.copytree(repo/'davarqadosh',out,dirs_exist_ok=True)
    packs=out/'packs';packs.mkdir(exist_ok=True)
    catalog=json.loads((repo/'releases/v1.27/catalog.js').read_text().split('=',1)[1].strip().rstrip(';'))
    edition_ids=['engwebp','grc-swete','hbo-mam']
    editions={x['id']:x for x in catalog['editions'] if x['id'] in edition_ids}
    manifest={'format':'davarqadosh-library','version':1,'research_complete':False,'reader_baseline':READER_REVISION,'books':[],'comparison_editions':editions}
    reports=[]
    public_records=[json.loads(line) for line in (repo/'releases/v1.27/lxxl-source-register.jsonl').read_text().splitlines() if line.strip()]
    for book in books:
        code=dict(BOOKS)[book]
        report=build_book(source,book,work,SOURCE_REVISION,research,lexicon);reports.append(report)
        meta=pack_book(work/(code+'.sqlite'),packs)
        paths=[repo/'data'/(code+'.js'),repo/'releases/v1.8/extra-data'/(code+'.js'),repo/'releases/v1.23/bhh-data'/(code+'.json.gz')]
        data={};provenance=[]
        for path in paths:
            payload=parse_bundle(path,code)
            for eid in edition_ids:
                if eid in payload:
                    data[eid]=[[row[0],row[1],row[2]] for row in payload[eid]]
                    provenance.append({'edition':eid,'path':str(path.relative_to(repo)),'sha256':digest(path.read_bytes()),'repository_revision':READER_REVISION})
        # Publicly published source reports are reused as reports, not manuscript collations.
        records=[r for r in public_records if r.get('locus','').startswith(book+'.')]
        companion=canonical({'book':code,'editions':data,'provenance':provenance,'research_records':records,'research_source':'releases/v1.27/lxxl-source-register.jsonl','research_source_sha256':digest((repo/'releases/v1.27/lxxl-source-register.jsonl').read_bytes()),'comparison_rule':'Source verse labels only; no asserted verse or word equivalence'})
        compressed=gzip.compress(companion,mtime=0);name=code+'.parallel.json.gz';atomic(packs/name,compressed)
        meta['parallel']={'url':name,'packed_bytes':len(compressed),'packed_sha256':digest(compressed),'bytes':len(companion),'sha256':digest(companion)}
        manifest['books'].append(meta)
        print(json.dumps({'book':code,'pack_bytes':meta['packed_bytes'],'sqlite_bytes':meta['sqlite_bytes'],'resumed':report.get('resumed',False),'coverage':report['coverage']}),flush=True)
    atomic(packs/'manifest.json',canonical(manifest)+b'\n')
    totals={key:sum(r['coverage'][key] for r in reports) for key in reports[0]['coverage']}
    summary={'books':len(reports),'verses':sum(r['verses'] for r in reports),'coverage':totals,'sqlite_bytes':sum(r['sqlite_bytes'] for r in reports),'pack_bytes':sum(m['packed_bytes'] for m in manifest['books']),'companion_bytes':sum(m['parallel']['packed_bytes'] for m in manifest['books']),'research_complete':False,'reports':reports}
    atomic(out/'coverage.json',canonical(summary)+b'\n')
    # Retain per-edition notices in the distributable artifact.
    shutil.copyfile(repo/'releases/v1.27/LICENSES.md',out/'COMPARISON-LICENSES.md')
    print(json.dumps({k:v for k,v in summary.items() if k!='reports'}),flush=True)
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--lexicon',required=True);p.add_argument('--repo',default=str(Path(__file__).resolve().parents[2]));p.add_argument('--out',required=True);p.add_argument('--work',required=True);p.add_argument('--book',default='Gen');p.add_argument('--research')
    a=p.parse_args();books=[b for b,_ in BOOKS] if a.book=='all' else a.book.split(',')
    build(a.source,a.lexicon,a.repo,a.out,books,a.work,a.research)
