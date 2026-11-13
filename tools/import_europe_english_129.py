"""Import the rights-reviewed eBible.org English/European USFM snapshot as Reader 1.29.

Inputs are pinned local _usfm.zip archives and their details.php rights pages.
The importer preserves every existing edition and creates an independent gzip data
group; it never overwrites base, Nordic, related-English or research packs.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from bs4 import BeautifulSoup
import argparse, concurrent.futures, gzip, hashlib, html, json, re, shutil

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'releases/v1.27'
OUT = ROOT / 'releases/v1.29'
GROUP = 'europe-english-1.29'
CANONICAL = 'GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV'.split()
DEUTERO = '1ES JDT TOB 1MA 2MA 3MA 4MA ODA WIS SIR PSS BAR LJE SUS BEL MAN 2ES PS2 ESG S3Y'.split()
KNOWN = set(CANONICAL + DEUTERO)

# These source IDs are already represented by installed editions. Do not create
# alternate labels for the same translation merely because its host differs.
DUPLICATES = {
    'isl': 'isl-olo1995', 'ces1613': 'ces-bkr1613', 'ekkpkp': 'ekk-pkp-partial',
    'ekk': 'ekk-ocv2022', 'epo': 'epo-londona', 'fraLSG': 'fra-lsg1910',
    'grcsbl': 'grc-sblgnt', 'grc-tisch': 'grc-tischendorf8',
    'hun': 'hun-karoli1908', 'russyn': 'rus-synodal', 'spaRV1909': 'spa-rv1909',
    'engoebus': 'eng-oeb', 'engwebp': 'engwebp',
}
EXCLUSIONS = {
    'swef': 'Copyright notice only; no explicit redistribution licence on the reviewed source page.',
    'engnet': 'Separate licence review required; verse-only display would omit the integral translators’ notes.',
    'ukr1996': 'Source permission imposes a doctrinal condition on redistributors, so it is not a general public redistribution grant.',
    'spav1602p': 'The reviewed notice explicitly permits printing but does not clearly grant electronic redistribution.',
}
LANGUAGE = {
    'rup': ('rup','Aromanian','Indo-European','Romance'), 'bel': ('bel','Belarusian','Indo-European','Slavic'),
    'beln': ('bel','Belarusian','Indo-European','Slavic'), 'nldgbv': ('nld','Dutch','Indo-European','Germanic'),
    'hrv': ('hrv','Croatian','Indo-European','Slavic'), 'hrvbib': ('hrv','Croatian','Indo-European','Slavic'),
    'ronludari': ('ron','Romanian — Ludari','Indo-European','Romance'), 'ceslb': ('ces','Czech','Indo-European','Slavic'),
    'cesnkb': ('ces','Czech','Indo-European','Slavic'), 'dan1931': ('dan','Danish','Indo-European','North Germanic'),
    'fin': ('fin','Finnish','Uralic','Finnic'), 'breBRG': ('bre','Breton','Indo-European','Celtic'),
    'frasbl': ('fra','French','Indo-European','Romance'), 'francl': ('fra','French','Indo-European','Romance'),
    'fra_fob': ('fra','French','Indo-European','Romance'), 'frajnd': ('fra','French','Indo-European','Romance'),
    'deuelbbk': ('deu','German','Indo-European','Germanic'), 'deu1912': ('deu','German','Indo-European','Germanic'),
    'deu1951': ('deu','German','Indo-European','Germanic'), 'deutkw': ('deu','German','Indo-European','Germanic'),
    'deuelo': ('deu','German','Indo-European','Germanic'), 'grcbrent': ('grc','Greek, Ancient','Indo-European','Hellenic'),
    'grcbyz': ('grc','Greek, Ancient','Indo-European','Hellenic'), 'grcmt': ('grc','Greek, Ancient','Indo-European','Hellenic'),
    'grcf35': ('grc','Greek, Ancient','Indo-European','Hellenic'), 'grclxx': ('grc','Greek, Ancient','Indo-European','Hellenic'),
    'grcsr': ('grc','Greek, Ancient','Indo-European','Hellenic'), 'grctcgnt': ('grc','Greek, Ancient','Indo-European','Hellenic'),
    'grctr': ('grc','Greek, Ancient','Indo-European','Hellenic'), 'isl316': ('isl','Icelandic','Indo-European','North Germanic'),
    'ita1885': ('ita','Italian','Indo-European','Romance'), 'ita1927': ('ita','Italian','Indo-European','Romance'),
    'litb': ('lit','Lithuanian','Indo-European','Baltic'), 'lit': ('lit','Lithuanian','Indo-European','Baltic'),
    'nld': ('nld','Dutch','Indo-European','Germanic'), 'nld1939': ('nld','Dutch','Indo-European','Germanic'),
    'nldnbg': ('nld','Dutch','Indo-European','Germanic'), 'noblb': ('nob','Norwegian Bokmål','Indo-European','North Germanic'),
    'polsz': ('pol','Polish','Indo-European','Slavic'), 'polubg': ('pol','Polish','Indo-European','Slavic'),
    'ronBayash': ('ron','Romanian — Bayash','Indo-European','Romance'), 'ron1924': ('ron','Romanian','Indo-European','Romance'),
    'ronbl': ('ron','Romanian','Indo-European','Romance'), 'kca': ('kca','Khanty','Uralic','Ugric'),
    'rusfb': ('rus','Russian','Indo-European','Slavic'), 'rmna': ('rom','Romani','Indo-European','Indo-Aryan'),
    'rmyArli': ('rmy','Romani, Vlax','Indo-European','Indo-Aryan'), 'rmyChergash': ('rmy','Romani, Vlax','Indo-European','Indo-Aryan'),
    'rmyGurbet': ('rmy','Romani, Vlax','Indo-European','Indo-Aryan'), 'srp1868': ('srp','Serbian','Indo-European','Slavic'),
    'srp1865': ('srp','Serbian','Indo-European','Slavic'), 'srponspc': ('srp','Serbian','Indo-European','Slavic'),
    'srponstl': ('srp','Serbian','Indo-European','Slavic'), 'rmc': ('rmc','Romani, Carpathian','Indo-European','Indo-Aryan'),
    'slk': ('slk','Slovak','Indo-European','Slavic'), 'sparvg': ('spa','Spanish','Indo-European','Romance'),
    'spablm': ('spa','Spanish','Indo-European','Romance'), 'spavbl': ('spa','Spanish','Indo-European','Romance'),
    'swe': ('swe','Swedish','Indo-European','North Germanic'), 'rmyvlakh': ('rmy','Romani, Vlax','Indo-European','Indo-Aryan'),
    'rmylovari': ('rmy','Romani, Vlax','Indo-European','Indo-Aryan'), 'rmn': ('rmn','Romani, Balkan','Indo-European','Indo-Aryan'),
    'rmczrb': ('rmc','Romani, Carpathian','Indo-European','Indo-Aryan'), 'rmyservi': ('rmy','Romani, Vlax','Indo-European','Indo-Aryan'),
    'ukr1871': ('ukr','Ukrainian','Indo-European','Slavic'), 'ukrfb': ('ukr','Ukrainian','Indo-European','Slavic'),
    'ukronpu': ('ukr','Ukrainian','Indo-European','Slavic'),
}

def js(path):
    return json.loads(path.read_text().split('=', 1)[1].rstrip(';\n'))

def sha(data):
    return hashlib.sha256(data).hexdigest()

def language_info(spec):
    sid = spec['id']
    if sid.startswith('eng') or sid == 'engWycliffe':
        return ('en','English','Indo-European','Germanic')
    if sid in LANGUAGE:
        return LANGUAGE[sid]
    raise KeyError('Missing language metadata: ' + sid)

def rights_info(spec, soup, text):
    low = text.lower()
    urls = [a.get('href','') for a in soup.find_all('a', href=True)]
    cc = next((u for u in urls if 'creativecommons.org/licenses/' in u), None)
    if cc:
        cc = cc.replace('http://','https://').rstrip("/'")
        m = re.search(r'/licenses/([^/]+)/([0-9.]+)', cc)
        if m:
            return 'CC ' + m[1].upper().replace('-', ' ') + ' ' + m[2], cc
    if spec['id'] == 'nldnbg':
        return 'GNU Free Documentation License 1.3', 'https://www.gnu.org/licenses/fdl-1.3.en.html'
    if spec['id'] == 'dan1931':
        # The historical notice reads "Copyright (C) 1907, 1931 Det Danske Bibelselskab" and the
        # text arrived via a 1990s Project Gutenberg etext distributed "with the permission of the
        # copyright owner". Current status, checked 2026-11-04:
        #   - Det Danske Bibelselskab's official copyright page claims rights ONLY to the 1992 and
        #     2020 translations, not to the 1931 OT / 1907 NT
        #     (bibelselskabet.dk/om-bibelselskabet-menu/copyright-...);
        #   - the society confirmed the 1931 OT is public domain (email reported by the
        #     Danish-Bible-OT-1931 project, github.com/emg/Danish-Bible-OT-1931);
        #   - Project Gutenberg hosts the OT 1931 (ebook #2144) and BibleGateway treats the text
        #     as public domain in the United States.
        return 'Public Domain', 'https://creativecommons.org/publicdomain/mark/1.0/'
    if spec['id'] == 'sparvg':
        return 'Free noncommercial distribution; no textual changes; commercial reproduction prohibited', spec['details_url']
    if 'publicdomain/zero/1.0' in ' '.join(urls).lower() or 'cc0' in low:
        return 'CC0 1.0', 'https://creativecommons.org/publicdomain/zero/1.0/'
    if 'public domain' in low:
        return 'Public Domain', 'https://creativecommons.org/publicdomain/mark/1.0/'
    raise ValueError('Unresolved licence: ' + spec['id'])

def parse_usfm(raw):
    """Plain-verse format conversion; never revise the translated words."""
    m = re.search(r'(?m)^\\id\s+([A-Z0-9]{3})(?:\s|$)', raw)
    if not m:
        raise ValueError('Missing USFM book identifier')
    book = m[1]
    if book not in KNOWN:
        return book, [], 0
    text = raw.replace('\r\n','\n').replace('\r','\n')
    # Remove notes, cross references, publication-only alternate numbers and figures.
    for marker in ['f','fe','ef','x','ex','fig']:
        text = re.sub(r'\\\+?' + marker + r'\s.*?\\\+?' + marker + r'\*', '', text, flags=re.S)
    text = re.sub(r'\\(?:va|vp)\s+[^\s\\]+(?:\s[^\s\\]+)?', '', text)
    text = re.sub(r'\\ca\s+[^\s\\]+\s+\\ca\*', '', text)
    rows, chapter, verse, endverse, parts = [], None, None, None, []
    def flush():
        nonlocal verse, endverse, parts
        if verse is None:
            parts = []
            return
        value = re.sub(r'\s+', ' ', ''.join(parts)).strip()
        if value:
            if '\\' in value:
                raise ValueError(f'Unconverted markup {book} {chapter}:{verse}: {value[:140]}')
            rows.append([chapter, verse, value, None] + ([endverse] if endverse is not None else []))
        verse, endverse, parts = None, None, []
    skip = {'id','h','toc1','toc2','toc3','mt','mt1','mt2','mt3','mt4','s','s1','s2','s3','s4','r','d','ms','ms1','ms2','mr','sp','is','is1','is2','ip','ipi','ipq','ipr','iot','io1','io2','iex','ie','imt','imt1','imt2','imt3','imt4','imi','im','ib','ie','rem','ide','usfm','cl','cp','cd','periph','pb'}
    keep = {'w','add','it','bd','bk','ord','nd','wj','sc','qt','em','bdit','tl','wh','k','sup','qs','qac','sig','sls','fw','fv','jmp'}
    for match in re.finditer(r'\\(\+?[a-zA-Z][a-zA-Z0-9]*)(\*)?\s*([^\\]*)', text):
        tag, end, payload = match.groups(); tag = tag.lstrip('+')
        if tag == 'c':
            flush(); chapter = int(payload.split()[0]); continue
        if tag == 'v':
            flush()
            vm = re.match(r'(\d+[a-z]?)(?:-(\d+[a-z]?))?\s*(.*)', payload, re.S)
            if not vm:
                raise ValueError(f'Unsupported verse label {book} {chapter}: {payload[:60]}')
            verse = int(vm[1]) if vm[1].isdigit() else vm[1]
            endverse = (int(vm[2]) if vm[2].isdigit() else vm[2]) if vm[2] else None
            parts = [vm[3]]; continue
        if tag in skip:
            continue
        if verse is not None:
            if tag == 'w' and not end:
                payload = payload.split('|')[0]
            if tag in keep or end:
                parts.append(payload)
            elif tag not in {'xo','xt','xk','xta','xq','fr','ft','fk','fq','fqa','fl','fa','fv'}:
                parts.append(' ' + payload)
    flush()
    if not rows:
        raise ValueError('No verse text: ' + book)
    # Repeated source verse labels are retained as one display row and explicitly counted.
    merged = {}
    for row in rows:
        key = (row[0], row[1])
        if key in merged:
            old = merged[key]; old[2] += '\n' + row[2]
        else:
            merged[key] = row
    return book, list(merged.values()), len(rows)

def parse_archive(args):
    sid, path = args
    books, source_units, display_units = {}, 0, 0
    with ZipFile(path) as z:
        for name in z.namelist():
            if not name.lower().endswith(('.usfm','.sfm')):
                continue
            raw = z.read(name).decode('utf-8-sig')
            book, rows, units = parse_usfm(raw)
            if book not in KNOWN:
                continue
            if book in books:
                raise ValueError(f'Duplicate book {sid}/{book}')
            if len({(r[0],r[1]) for r in rows}) != len(rows):
                raise ValueError(f'Duplicate verse key {sid}/{book}')
            books[book] = rows; source_units += units; display_units += len(rows)
    if not books:
        raise ValueError('No supported biblical books: ' + sid)
    return sid, books, source_units, display_units

def copyright_line(text):
    matches = re.findall(r'(?:©|Copyright)[^\n]{0,300}', text, re.I)
    return ' '.join(dict.fromkeys(' '.join(m.split()) for m in matches[:3]))

def main():
    global OUT
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', type=Path, default=Path('/mnt/agents/work/europe-english'))
    ap.add_argument('--parse-only', action='store_true')
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--out', type=Path, default=OUT)
    args = ap.parse_args()
    OUT = args.out
    candidates = json.loads((args.work/'rights-scan.json').read_text())
    selected = [x for x in candidates if x['id'] not in DUPLICATES and x['id'] not in EXCLUSIONS]
    jobs = [(x['id'], args.work/'sources'/(x['id']+'_usfm.zip')) for x in selected]
    parsed = {}
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.jobs) as pool:
        for i, (sid, books, source_units, display_units) in enumerate(pool.map(parse_archive, jobs), 1):
            parsed[sid] = books
            print(f'PARSED {i:3}/{len(jobs)} {sid:16} books={len(books):2} verses={display_units}', flush=True)
    if args.parse_only:
        print('Parse-only complete:', len(parsed), 'editions')
        return

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(BASE, OUT)
    (OUT/'europe-data').mkdir(); (OUT/'sources').mkdir(exist_ok=True)
    cat = js(OUT/'catalog.js'); directory = js(OUT/'translations/metadata.js')
    ids = {x['id'] for x in selected}
    cat['editions'] = [e for e in cat['editions'] if e['id'] not in ids]
    directory = [e for e in directory if e['id'] not in ids]
    overlays, reports, licence_sections = {}, [], []
    details_dir = args.work/'details'
    for number, spec in enumerate(selected, 1):
        sid = spec['id']; books = parsed[sid]
        details_path = details_dir/(sid+'.html'); details_html = details_path.read_text()
        soup = BeautifulSoup(details_html, 'html.parser'); rights_text = soup.get_text('\n',strip=True)
        spec['details_url'] = 'https://ebible.org/Scriptures/details.php?id=' + sid
        license_name, license_url = rights_info(spec, soup, rights_text)
        iso, language, family, branch = language_info(spec)
        source_archive = args.work/'sources'/(sid+'_usfm.zip'); source_bytes = source_archive.read_bytes()
        attribution = f"{spec['vernacular']}. {copyright_line(rights_text)} Source: eBible.org, reviewed {spec.get('updated') or 'snapshot date unrecorded'}. {license_name}. Plain-verse format conversion; source words and punctuation retained. Headings, footnotes, cross references and publication-only material are omitted from display, not asserted to be absent from the source. Complete notices are retained in the source archive. No publisher endorsement."
        codes = [b for b,_ in cat['books'] if b in books]
        positions = [[b,c] for b in codes for c in dict.fromkeys(r[0] for r in books[b])]
        label = f"{language} — {spec['vernacular']}"
        meta = dict(id=sid,label=label,title=spec['title'],language=iso,latin_language=iso,script='Latin' if all(ord(ch)<0x400 for rows in books.values() for r in rows[:20] for ch in r[2]) else 'Source script',direction='ltr',available=True,scope=f"{len(books)} source books; exact available coverage",source=spec['details_url'],license=license_name,license_url=license_url,attribution=attribution,method='Source USFM retained; deterministic plain-verse extraction; no textual revision or translation; source references retained.',has_transliteration=False,book_codes=codes,positions=positions,preserve_source_refs=True,versification_label='Source references retained; cross-edition alignment not verified',data_group=GROUP,book_labels={})
        cat['editions'].append(meta)
        directory.append(dict(id=sid,language=language,iso6393=iso,aliases=[spec['language'],spec['vernacular'],spec['title']],family=family,subfamily=branch,branch=branch,countries=[spec['territory']],continents=['Europe'] if spec['territory'] not in {'United States','United States of America','Australia'} else ['North America' if 'United States' in spec['territory'] else 'Australia'],states=[],script=meta['script'],variety=label,classification_source='Source language label and project browsing hierarchy; no asserted UBS identifier',ubs_id=None))
        for book, rows in books.items():
            overlays.setdefault(book,{})[sid] = rows
        provenance = dict(id=sid,title=spec['title'],vernacular_title=spec['vernacular'],source=spec['details_url'],source_archive=spec['usfm'],source_sha256=sha(source_bytes),source_updated=spec.get('updated'),retrieved='2026-11-03',license=license_name,license_url=license_url,books=len(books),verse_rows=sum(map(len,books.values())),conversion='Plain-verse format conversion; headings, notes, cross references and front/back matter omitted from display. Raw USFM and complete source page retained.',attribution=attribution)
        with ZipFile(OUT/'sources'/(sid+'-source.zip'),'w',ZIP_DEFLATED,strict_timestamps=False) as z:
            with ZipFile(source_archive) as original:
                for name in original.namelist():
                    z.writestr(name, original.read(name))
            z.writestr('RIGHTS.txt', rights_text+'\n')
            z.writestr('DETAILS.html', details_html)
            z.writestr('PROVENANCE.json', json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
        with ZipFile(OUT/'sources'/(sid+'-display-usfm.zip'),'w',ZIP_DEFLATED,strict_timestamps=False) as z:
            z.writestr('ATTRIBUTION.txt',attribution+'\n'+spec['details_url']+'\n'+license_name+'\n')
            for book, rows in books.items():
                lines=['\\id '+book,'\\usfm 3.0','\\ide UTF-8']; last=None
                for row in rows:
                    if row[0] != last: lines.append('\\c '+str(row[0])); last=row[0]
                    verses = str(row[1]) + ('-'+str(row[4]) if len(row)>4 and row[4] is not None else '')
                    lines.append('\\v '+verses+' '+row[2])
                z.writestr(book+'.usfm','\n'.join(lines)+'\n')
        reports.append(provenance)
        licence_sections.append('\n## '+label+'\n\n'+attribution+'\n\n**Licence:** '+license_name+'\n\n**Source:** '+spec['details_url']+'\n\nFull source notice: `sources/'+sid+'-source.zip` (`RIGHTS.txt` and `DETAILS.html`). SHA-256 of downloaded USFM archive: `'+provenance['source_sha256']+'`.\n')
        print(f'PACKED SOURCES {number}/{len(selected)} {sid}',flush=True)
    manifest = {}
    for book, editions in overlays.items():
        raw = json.dumps(dict(book=book,editions=editions),ensure_ascii=False,separators=(',',':')).encode()
        packed = gzip.compress(raw,compresslevel=9,mtime=0)
        (OUT/'europe-data'/(book+'.json.gz')).write_bytes(packed)
        manifest[book] = dict(sha256=sha(raw),bytes=len(raw),packed_sha256=sha(packed),packed_bytes=len(packed))
    (OUT/'europe-manifest.js').write_text('window.EuropeanTextPacks='+json.dumps(manifest,separators=(',',':'))+';')
    cat['version'] = '1.29-europe-english'
    (OUT/'catalog.js').write_text('window.BibleCatalog='+json.dumps(cat,ensure_ascii=False,separators=(',',':'))+';')
    (OUT/'translations/metadata.js').write_text('window.TranslationDirectory='+json.dumps(directory,ensure_ascii=False,separators=(',',':'))+';')
    (OUT/'sources/europe-english-import.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
    excluded = [dict(id=x['id'],title=x['title'],source='https://ebible.org/Scriptures/details.php?id='+x['id'],reason=EXCLUSIONS[x['id']]) for x in candidates if x['id'] in EXCLUSIONS]
    duplicates = [dict(id=x['id'],title=x['title'],existing_id=DUPLICATES[x['id']]) for x in candidates if x['id'] in DUPLICATES]
    (OUT/'sources/europe-english-review.json').write_text(json.dumps(dict(inventory='eBible.org Scriptures catalogue',retrieved='2026-11-03',candidate_count=len(candidates),imported_count=len(selected),duplicates=duplicates,excluded=excluded),ensure_ascii=False,indent=2)+'\n')
    licenses = (OUT/'LICENSES.md').read_text().split('\n<!-- Europe and English 1.29 -->')[0]
    (OUT/'LICENSES.md').write_text(licenses+'\n<!-- Europe and English 1.29 -->\n'+''.join(licence_sections))
    (OUT/'VERSION').write_text('1.29\n')
    (OUT/'README.md').write_text('# Parallel Bible Reader 1.29\n\nAdds 116 rights-reviewed English and European source editions to the preserved 84-edition Reader 1.27 catalog (200 total). Texts use an independent gzip data group and retain source USFM, rights pages, attribution, exact available book coverage and SHA-256 provenance.\n\nThe catalog includes public-domain, Creative Commons, GNU FDL and specifically reviewed noncommercial redistribution texts. No-derivatives editions receive format conversion only; their translated words and punctuation are not revised. Four unclear/incompatible candidates and 13 duplicates are recorded in `sources/europe-english-review.json`. Protected translations remain outside the public bundle.\n')
    # Wire the independent group without replacing any earlier manifest or pack.
    offline_path = OUT/'offline-library.js'; offline = offline_path.read_text()
    offline = offline.replace("kind==='bhh'?'../v1.23/bhh-data/'", "kind==='europe'?'../v1.29/europe-data/':kind==='bhh'?'../v1.23/bhh-data/'")
    offline = offline.replace("['bhh','lxxl','ntgl','related','nordic']", "['bhh','lxxl','ntgl','related','nordic','europe']")
    offline = offline.replace("kind==='bhh'?window.BHHTextPacks", "kind==='europe'?window.EuropeanTextPacks:kind==='bhh'?window.BHHTextPacks")
    offline = offline.replace("ReaderCompression.unpack(bytes,expected.bytes,16*1024*1024)", "ReaderCompression.unpack(bytes,expected.bytes,kind==='europe'?32*1024*1024:16*1024*1024)")
    offline = offline.replace("const kindOf=id=>editions.get(id)?.data_group===", "const kindOf=id=>editions.get(id)?.data_group==='europe-english-1.29'?'europe':editions.get(id)?.data_group===")
    assert "kind==='europe'" in offline and 'EuropeanTextPacks' in offline
    offline_path.write_text(offline)
    index_path = OUT/'index.html'; index = index_path.read_text()
    index = index.replace('<script src="pack-manifest.js', '<script src="europe-manifest.js"></script><script src="pack-manifest.js')
    notice = '<details class="reader-extras"><summary>English and European Bible sources</summary><p>Reader 1.29 adds 116 rights-reviewed editions to the preserved 84-edition catalog. Exact available book coverage, source spelling and verse labels are retained. Public-domain, Creative Commons, GNU FDL and specifically reviewed noncommercial redistribution texts keep their own licences. No-derivatives texts receive format conversion only. Four unclear or incompatible candidates and 13 duplicates are recorded in the review register.</p><p><a href="sources/europe-english-review.json">Import review and exclusions</a> · <a href="sources/europe-english-import.json">Source hashes and provenance</a> · <a href="LICENSES.md">Attribution and licences</a></p></details>'
    index = index.replace('<footer>', notice+'<footer>')
    index_path.write_text(index)
    for p in list(OUT.glob('*.js')) + list(OUT.glob('*.html')) + list((OUT/'translations').glob('*.js')) + list((OUT/'translations').glob('*.html')):
        p.write_text(p.read_text().replace('1.27','1.29'))
    sw_path = OUT/'sw.js'; sw = sw_path.read_text().replace("const ASSETS=['lxxl-manifest.js'", "const ASSETS=['europe-manifest.js','lxxl-manifest.js'")
    sw_path.write_text(sw)
    print(json.dumps(dict(editions=len(cat['editions']),added=len(selected),books=len(manifest),packed_bytes=sum(x['packed_bytes'] for x in manifest.values()),verse_rows=sum(r['verse_rows'] for r in reports)),indent=2))

if __name__ == '__main__':
    main()
