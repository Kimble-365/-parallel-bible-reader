"""Build provider-hosted links from retained metadata, without copying provider texts."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'releases/v1.14'
def readjs(p):return json.loads(p.read_text().split('=',1)[1].rstrip(';\n'))
cat=readjs(OUT/'catalog.js');proof=OUT/'sources/provider-checks.json'
if not proof.exists():proof.write_text(Path('/workspace/reader-new-sources/v114/bibleis-checks.json').read_text())
checks=json.loads(proof.read_text());local={'JPNJCB':['jpn-bungo'],'JPNNIT':['jpn-bungo'],'MYAOJV':['mya-judson'],'CEBRPV':['ceb-pinadayag']}
for r in checks:
    if not r.get('identity_verified'):continue
    id=r['active_id'];targets=local.get(id,[])
    for e in cat['editions']:
        if e['id'] in targets or e['id']=='ceb-pinadayag' and id=='CEBCBV':
            links=e.setdefault('provider_links',[])
            if not any(link['url']==r['url'] for link in links):links.append(dict(label='Bible.is — '+r['title']+' (external edition)',url=r['url']))
    audio=[f for f in r['filesets'] if str(f.get('type','')).startswith('audio')]
    if not audio or not targets:continue
    scopes={f.get('size') for f in audio};nt='NT' in scopes;ot='OT' in scopes;allowed={b for b,_ in cat['books'][:39] if ot}|{b for b,_ in cat['books'][39:66] if nt};books=[b for b in r['books'] if b.get('book_id') in allowed]
    assert books
    item=dict(id=id,label={'jpn':'Japanese','mya':'Burmese','ceb':'Cebuano'}[r['language_code']]+' — '+r['title'],url=r['url'],full_bible=nt and ot,local_editions=targets,audio_scope='Old and New Testament' if nt and ot else 'New Testament' if nt else 'Old Testament',book_codes=[b['book_id'] for b in books],available_chapters={b['book_id']:b['chapters'] for b in books},same_text_edition=False)
    cat['audio_editions']=[e for e in cat['audio_editions'] if e['id']!=id]+[item]
(OUT/'catalog.js').write_text('window.BibleCatalog='+json.dumps(cat,ensure_ascii=False,separators=(',',':'))+';')
films=[]
for id,label,slug,tags in [('eng','English','english',['en']),('fin','Finnish — suomi','finnish',['fi']),('hin','Hindi — हिन्दी','hindi',['hi']),('jpn','Japanese — 日本語','japanese',['ja']),('mya','Burmese — မြန်မာ','burmese',['my']),('vie','Vietnamese — tiếng Việt','vietnamese',['vi']),('ceb','Cebuano — Bisaya','cebuano',['ceb']),('tgl','Tagalog — Filipino','tagalog',['tl','fil'])]:
    films.append(dict(id=id,label=label,language_tags=tags,url='https://www.jesusfilm.org/watch/jesus.html/'+slug+'.html',provider='Jesus Film Project',access='Provider-hosted streaming; internet required',same_bible_edition=False))
data=dict(films=films,more_languages='https://www.jesusfilm.org/watch/jesus.html/english.html',sharing_terms='https://www.jesusfilm.org/about/faq/',checked='2026-10-26',verification='Official language watch pages located through web research. Direct automated HTTP requests were blocked (403); actual movie playback was not exercised. No embedded player, film files or unverified media IDs are bundled.')
(OUT/'media-resources.js').write_text('window.ReaderMediaResources='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';')
(OUT/'sources/media-research.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('Built',len(films),'official film links;',len(cat['audio_editions']),'verified audio choices; external Bible.is/YouVersion links only')
