"""Reproducible, incremental Text-Fabric adapter; standard library only.

Inputs must match sources/syriac-lock.json; no source downloads during a build.
The two ETCBC datasets retain their CC BY-NC 4.0 terms. Source locations are
preserved as immutable TF node/slot IDs, not invented manuscript folios.
"""
from pathlib import Path
import argparse, collections, gzip, hashlib, json, re
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'releases/v1.25'
MORPH = ['sp', 'vs', 'vt', 'ps', 'gn', 'nu', 'st']
PESH = dict(zip(
    'Gn Ex Lv Nm Dt Jb Jos Jd Sm1 Sm2 Ps Rg1 Rg2 Pr Sap Ec Ct Is Jr Thr EpJr EpBar_A EpBar_B Bar Ez Hs Jl Am Ob Jon Mi Na Hb Zf Hg Sa Ml Dn BelDr Ru Sus Est Jdt Sir Chr1 Chr2 ApBar Esr4 Ezr Neh Mc1_A Mc1_B Mc2 Mc3 Mc4 Oda OrM_A OrM_B ApcPs_A ApcPs_B ApcPs PsS Tb_A Tb_B Esr3'.split(),
    'GEN EXO LEV NUM DEU JOB JOS JDG 1SA 2SA PSA 1KI 2KI PRO WIS ECC SNG ISA JER LAM LJE EBA EBB BAR EZK HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL DAN BEL RUT SUS EST JDT SIR 1CH 2CH ABR E4S EZR NEH 1MA M1B 2MA 3MA 4MA ODA MAN MNB APA APB APC PSS TOB TBB E3S'.split()))
ANNOT = dict(zip(
    'Genesis Exodus Leviticus Numbers Deuteronomy Joshua Judges Psalms 1_Kings 2_Kings EpBarA EpBarB Jeremiah Ezekiel Jonah Zechariah Daniel Sir ApBar 4Esr OrManA OrManB PsS 3Esr PsH ApDn'.split(),
    'GEN EXO LEV NUM DEU JOS JDG PSA 1KI 2KI EBA EBB JER EZK JON ZEC DAN SIR ABR E4S MAN MNB PSS E3S PSA ADN'.split()))
EXTRA_NAMES = {
    'EBA': 'Epistle of Baruch — version A', 'EBB': 'Epistle of Baruch — version B',
    'ABR': 'Apocalypse of Baruch (Syriac source)', 'E4S': '4 Ezra (Syriac source)',
    'M1B': '1 Maccabees — source version B', 'MNB': 'Prayer of Manasseh — version B',
    'APA': 'Apocryphal Psalms — source A', 'APB': 'Apocryphal Psalms — source B',
    'APC': 'Apocryphal Psalms — source collection', 'TBB': 'Tobit — source version B',
    'E3S': '3 Ezra (Syriac source)', 'ADN': 'Apocalypse of Daniel (Syriac source)',
}
NT_BOOKS = dict(zip([100, 119, 120, 121, 122, 123, 124, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145],
                    'MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV'.split()))


def canonical(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), sort_keys=True).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def span_ranges(value):
    result = []
    for part in value.split(','):
        first, dash, last = part.partition('-')
        result.append((int(first), int(last) if dash else int(first)))
    return result


def nodes(value):
    for first, last in span_ranges(value):
        yield from range(first, last + 1)


def feature(path):
    """Read explicit/implicit TF nodes, ranges and escaped string values.

    Empty data lines are implicit empty values and advance the node ID.
    Space-valued trailers must not be stripped.
    """
    data = path.read_text().split('\n\n', 1)[1]
    values, previous = {}, 0
    for line in data.splitlines():
        if '\t' in line:
            ids, value = line.split('\t', 1)
            ids = list(nodes(ids))
        else:
            ids, value = [previous + 1], line
        value = re.sub(r'\\([tn\\])', lambda m: {'t': '\t', 'n': '\n', '\\': '\\'}[m[1]], value)
        for node in ids:
            values[node] = value
        previous = ids[-1]
    return values


class Writer:
    def __init__(self):
        self.changed, self.inventory = [], {}

    def put(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_bytes() != data:
            temp = path.with_suffix(path.suffix + '.tmp')
            temp.write_bytes(data)
            temp.replace(path)
            self.changed.append(str(path.relative_to(ROOT)))

    def js(self, path, name, value):
        self.put(path, name.encode() + b'=' + canonical(value) + b';\n')

    def packed(self, path, value):
        data = canonical(value)
        packed = gzip.compress(data, mtime=0)
        self.put(path, packed)
        meta = dict(bytes=len(data), sha256=digest(data), packed_bytes=len(packed), packed_sha256=digest(packed))
        self.inventory[str(path.relative_to(OUT))] = meta
        return meta


def readjs(path):
    return json.loads(path.read_text().split('=', 1)[1].rstrip(';\n'))


def corpus(source, spec):
    base = source / spec['repo'] / 'tf' / spec['version']
    fields = ['otype', 'oslots', 'book', 'chapter', 'verse', spec['text'], 'trailer']
    if spec['annotated']:
        fields += ['lex', 'gloss'] + MORPH
    return {field: feature(base / (field + '.tf')) for field in fields}


def extract(data, spec, vocabulary):
    typ, slots = data['otype'], data['oslots']
    parents = {}
    for level in ['book', 'chapter']:
        lookup = {}
        for node, kind in typ.items():
            if kind == level:
                for word in nodes(slots[node]):
                    if word in lookup:
                        raise ValueError('Overlapping ' + level)
                    lookup[word] = node
        parents[level] = lookup
    editions, annotations, coverage = {}, {}, []
    excluded = collections.Counter()
    mapping = ANNOT if spec['annotated'] else PESH
    for node, kind in typ.items():
        if kind != 'verse':
            continue
        ranges = span_ranges(slots[node])
        words = list(nodes(slots[node]))
        source_book = data['book'][parents['book'][words[0]]]
        code = mapping.get(source_book)
        if not code:
            excluded[source_book] += 1
            continue
        edition = 'syc-syrohexapla-ps' if source_book == 'PsH' else spec['id']
        chapter = int(data['chapter'][parents['chapter'][words[0]]])
        verse = int(data['verse'][node])
        assert all(data['book'][parents['book'][w]] == source_book for w in words)
        text, tokens, missing_surface, offset = [], [], [], 0
        for word in words:
            if word not in data[spec['text']]:
                assert spec['annotated'], (word, 'missing non-annotated source form')
                missing_surface.append(word)
            form = data[spec['text']].get(word, '')
            trailer = data['trailer'].get(word, '')
            if spec['annotated']:
                lemma, gloss = data['lex'].get(word, ''), data['gloss'].get(word, '')
                lexid = 'etcbc:' + digest(canonical([lemma, gloss]))[:24]
                entry = [lemma, gloss]
                assert lexid not in vocabulary or vocabulary[lexid] == entry
                vocabulary[lexid] = entry
                # Python codepoint offsets are converted by Array.from in the UI.
                tokens.append([word, offset, len(form), lexid] + [data[f].get(word, '') for f in MORPH])
            text.extend([form, trailer])
            offset += len(form) + len(trailer)
        text = ''.join(text).rstrip()
        assert text.strip(), (source_book, chapter, verse, node, 'empty source unit')
        editions.setdefault(edition, {}).setdefault(code, []).append([chapter, verse, text])
        key = str(chapter) + ':' + str(verse)
        detail = dict(node=node, source_book=source_book, slots=ranges)
        if missing_surface:
            detail['no_surface_in_source'] = missing_surface
        if not any('\u0710' <= c <= '\u072f' for c in text):
            detail['source_marker_only'] = True
        if spec['annotated']:
            detail['tokens'] = tokens
        else:
            # Keep node/slot evidence without duplicating text or all tokens.
            detail['word_count'] = len(words)
        annotations.setdefault(edition, {}).setdefault(code, {})[key] = detail
    for edition, books in editions.items():
        for code, rows in books.items():
            assert len({(r[0], r[1]) for r in rows}) == len(rows), (edition, code, 'duplicate reference')
            rows.sort(key=lambda r: (r[0], r[1]))
            coverage.append(dict(edition=edition, book=code, verses=len(rows), chapters=sorted({r[0] for r in rows})))
    return editions, annotations, coverage, dict(excluded)


def extract_tei(source, spec, lock):
    ns = {'t': 'http://www.tei-c.org/ns/1.0'}
    texts, evidence, coverage, headers = {}, {}, [], []
    for item in lock['files']:
        if item['repo'] != spec['repo'] or not item['path'].endswith('.xml'):
            continue
        ident = int(Path(item['path']).stem)
        assert ident in NT_BOOKS
        book, rows, notes = NT_BOOKS[ident], [], {}
        root = ET.parse(source / item['repo'] / item['path']).getroot()
        licenses = root.findall('.//t:publicationStmt//t:licence', ns)
        assert licenses and all(e.get('target', '').rstrip('/') in ['http://creativecommons.org/licenses/by/4.0', 'https://creativecommons.org/licenses/by/4.0'] for e in licenses)
        revision = root.find('.//t:revisionDesc', ns)
        title = root.find('.//t:titleStmt/t:title', ns)
        bib = root.find('.//t:sourceDesc', ns)
        credits = root.find('.//t:titleStmt', ns)
        availability = root.find('.//t:availability', ns)
        headers.append(dict(book=book, corpus_id=ident, title=' '.join(''.join(title.itertext()).split()), status=revision.get('status'), source_description=' '.join(''.join(bib.itertext()).split()), contributors=' '.join(''.join(credits.itertext()).split()), rights=' '.join(''.join(availability.itertext()).split()), source_path=item['path']))
        seen = {}
        for chapter in root.findall('.//t:body//t:div[@type="chapter"]', ns):
            c = int(chapter.get('n'))
            for verse in chapter.findall('t:ab[@type="verse"]', ns):
                assert not list(verse), 'Unhandled nested verse markup'
                v = int(verse.get('n'))
                text = ' '.join((verse.text or '').split())
                assert text
                key = str(c) + ':' + str(v)
                xpath = f'//tei:div[@type="chapter"][@n="{c}"]/tei:ab[@type="verse"][@n="{v}"]'
                if key in seen:
                    row = rows[seen[key]]
                    offset = len(row[2]) + 1
                    row[2] += '\n' + text
                    row.extend([None, None, 0, 'Duplicate source label: two distinct source units are retained here. This is an unresolved source numbering defect, not an editorial correction.'])
                    notes[key]['source_units'].append(dict(xpath='(' + xpath + ')[2]', offset=offset, length=len(text)))
                else:
                    seen[key] = len(rows)
                    rows.append([c, v, text])
                    notes[key] = dict(source_path=item['path'], corpus_id=ident, xpath=xpath, status=revision.get('status'), source_units=[dict(xpath='(' + xpath + ')[1]', offset=0, length=len(text))])
        assert rows and len({(r[0], r[1]) for r in rows}) == len(rows), (book, 'duplicate reference')
        texts[book], evidence[book] = rows, notes
        coverage.append(dict(edition=spec['id'], book=book, verses=len(rows), chapters=sorted({r[0] for r in rows})))
    assert len(texts) == 27
    return {spec['id']: texts}, {spec['id']: evidence}, coverage, headers


def build(source):
    lock = json.loads((OUT / 'sources/syriac-lock.json').read_text())
    for obj in lock['files']:
        data = (source / obj['repo'] / obj['path']).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        assert blob == obj['blob_sha'] and digest(data) == obj['sha256'], obj['path']
    writer, vocabulary = Writer(), {}
    cat = readjs(ROOT / 'releases/v1.24/catalog.js')
    directory = readjs(ROOT / 'releases/v1.24/translations/metadata.js')
    search = readjs(ROOT / 'releases/v1.24/search-manifest.js')
    known = dict(cat['books'])
    texts, evidence, all_coverage, exclusions = {}, {}, [], {}
    tei_headers = []
    for spec in lock['datasets']:
        if spec.get('format') == 'tei':
            eds, notes, coverage, headers = extract_tei(source, spec, lock)
            tei_headers.extend(headers)
            excluded = {}
        else:
            data = corpus(source, spec)
            eds, notes, coverage, excluded = extract(data, spec, vocabulary)
        texts.update(eds); evidence.update(notes); all_coverage += coverage
        exclusions[spec['repo']] = excluded
    needed = {book for books in texts.values() for book in books}
    for code in sorted(needed - set(known)):
        assert code in EXTRA_NAMES
        cat['books'].append([code, EXTRA_NAMES[code]])
    order = [b for b, _ in cat['books']]
    labels = {
        'syc-peshitta-ot': 'Syriac — Peshitta Old Testament (ETCBC edition text)',
        'syc-etcbc-biblical': 'Syriac — ETCBC annotated biblical selections',
        'syc-syrohexapla-ps': 'Syriac — Syrohexapla Psalms (partial)',
        'syc-dsc-nt': 'Syriac — New Testament (DSC print transcription)',
    }
    editions = []
    manifest = dict(version='1.25', editions={}, lexicon={}, fields=['slot', 'offset', 'length', 'lexeme'] + MORPH)
    for edition, books in texts.items():
        spec = next(s for s in lock['datasets'] if s['id'] == ('syc-etcbc-biblical' if edition == 'syc-syrohexapla-ps' else edition))
        license = spec.get('license', 'CC BY-NC 4.0')
        report = dict(id=edition, repo=spec['repo'], commit=spec['commit'], version=spec['version'], license=license, books=len(books), verses=sum(map(len, books.values())))
        editions.append(report)
        positions = [[b, c] for b in order if b in books for c in sorted({r[0] for r in books[b]})]
        meta = dict(id=edition, label=labels[edition], title=labels[edition], language='syc', latin_language='syc', script='Syriac', direction='rtl', available=True, scope='Exact available source books only; original source numbering; not a new critical edition.', source='https://github.com/' + spec['repo'] + '/tree/' + spec['commit'], license='CC BY-NC 4.0', license_url='https://creativecommons.org/licenses/by-nc/4.0/', attribution=spec['attribution'] + ' Source revision ' + spec['commit'] + '. Display adaptation by Parallel Bible Reader; no endorsement. Noncommercial use only. See sources/syriac-lock.json.', method='Text-Fabric source forms and trailers joined; trailing whitespace removed. Source node/slot ranges retained. Critical apparatus not included. No manuscript or translation verification claimed.', has_transliteration=False, books=len(books), verses=report['verses'], book_codes=[b for b in order if b in books], positions=positions, preserve_source_refs=True, versification_label='Source labels; matching references do not establish equivalent passages', data_group='syriac-1.25')
        if spec.get('format') == 'tei':
            meta.update(license=license, license_url='https://creativecommons.org/licenses/by/4.0/', attribution=spec['attribution'] + ' Revision ' + spec['commit'] + '. Verse-display adaptation by Parallel Bible Reader. Item-specific credits and printed sources in sources/dsc-items.json.', method='Uncorrected print transcription, not a manuscript or reconstructed critical text. XML whitespace collapsed; Syriac code points retained. Source chapter/verse XPath recorded. Repository Peshitta label retained; later NT additions are not asserted to belong to the early 22-book Peshitta canon.')
        cat['editions'] = [e for e in cat['editions'] if e['id'] != edition] + [meta]
        directory.append(dict(id=edition, language='Classical Syriac', iso6393='syc', aliases=['Syriac', 'Aramaic', 'Peshitta', labels[edition]], family='Afro-Asiatic', branch='Semitic / Aramaic', countries=[], continents=[], states=[], script='Syriac', variety=labels[edition], classification_source='Classical Syriac source identification; project browsing group, not UBS genealogy', ubs_id=None))
        manifest['editions'][edition] = dict(repo=spec['repo'], commit=spec['commit'], books={})
        for book, rows in books.items():
            bundle = dict(book=book, editions={edition: rows})
            embedded = edition in ['syc-peshitta-ot', 'syc-dsc-nt']
            if embedded:
                bundle['source'] = evidence[edition][book]
            # One dataset per book shard: selecting Syrohexapla never downloads Peshitta.
            pack = writer.packed(OUT / 'syriac-data' / edition / (book + '.json.gz'), bundle)
            detail = dict(book=book, edition=edition, verses=evidence[edition][book])
            annotation = pack if embedded else writer.packed(OUT / 'syriac-index' / edition / (book + '.json.gz'), detail)
            manifest['editions'][edition]['books'][book] = dict(text=pack, index=annotation, index_in_text=embedded)
            search.setdefault('editions', {}).setdefault(edition, {})[book] = digest(canonical(rows))
    # Each reusable lexical entry appears once, in a hash-prefix shard.
    lex_shards = collections.defaultdict(dict)
    for lexid, entry in vocabulary.items():
        lex_shards[lexid.split(':')[1][:1]][lexid] = entry
    for prefix, entries in sorted(lex_shards.items()):
        manifest['lexicon'][prefix] = writer.packed(OUT / 'syriac-lexicon' / (prefix + '.json.gz'), dict(entries=entries))
    writer.js(OUT / 'catalog.js', 'window.BibleCatalog', cat)
    writer.js(OUT / 'translations/metadata.js', 'window.TranslationDirectory', directory)
    writer.js(OUT / 'search-manifest.js', 'window.ReaderSearchManifest', search)
    writer.js(OUT / 'syriac-manifest.js', 'window.SyriacPacks', manifest)
    writer.put(OUT / 'sources/dsc-items.json', canonical(tei_headers) + b'\n')
    report = dict(adapter_version='1.0', date=lock['date'], editions=editions, coverage=all_coverage, shared_lexical_entries=len(vocabulary), lexical_shards=len(lex_shards), excluded_nonbiblical_source_units=exclusions, compression='gzip mtime=0', inventory=writer.inventory, source_objects_preserved_remotely=True, limitations=['Edition text, not a newly reconstructed critical text', 'English source glosses only; Finnish glosses not produced', 'Source A/B forms and discontinuous spans retained separately', 'SEDRA NT import blocked by unresolved data redistribution terms', 'Noncommercial data terms remain separate from MIT reader code'])
    writer.put(OUT / 'sources/syriac-import.json', canonical(report) + b'\n')
    # Remove only obsolete generated shards, never source objects or user files.
    for folder in ['syriac-data', 'syriac-index', 'syriac-lexicon']:
        for path in (OUT / folder).rglob('*.json.gz'):
            if str(path.relative_to(OUT)) not in writer.inventory:
                path.unlink()
                writer.changed.append(str(path.relative_to(ROOT)))
    if writer.changed:
        log = OUT / 'sources/syriac-events.jsonl'
        previous = log.read_bytes() if log.exists() else b''
        event = dict(time=datetime.now(timezone.utc).isoformat(), operation='incremental-import', input_lock_sha256=digest((OUT / 'sources/syriac-lock.json').read_bytes()), output_manifest_sha256=digest(canonical(report)), changed_files=len(writer.changed), packed_bytes=sum(v['packed_bytes'] for v in writer.inventory.values()), editions=len(editions), images=0)
        if len(previous) > 256 * 1024:
            archive = log.with_name('syriac-events-' + digest(previous)[:16] + '.jsonl.gz')
            writer.put(archive, gzip.compress(previous, mtime=0))
            previous = b''
        writer.put(log, previous + canonical(event) + b'\n')
    print(json.dumps(dict(editions=editions, shared_lexical_entries=len(vocabulary), changed_files=len(writer.changed), packed_bytes=sum(v['packed_bytes'] for v in writer.inventory.values())), indent=2))
    return writer.changed


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=Path('/workspace/syriac-input'))
    args = parser.parse_args()
    changed = build(args.source)
    print('Changed:', len(changed))
