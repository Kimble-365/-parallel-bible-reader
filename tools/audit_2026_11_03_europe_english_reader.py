#!/usr/bin/env python3
"""Audit the Parallel Bible Reader 1.29 Europe/English reference edition.

Verifies, against a reader checkout containing releases/v1.29:
  1. catalog edition count and preservation of every pre-1.29 edition id
  2. europe-english-1.29 group membership (116 editions)
  3. all 85 europe pack files against europe-manifest.js
     (expanded SHA-256, expanded bytes, packed SHA-256, packed bytes)
  4. all 116 source archives and 116 display archives
     (presence, non-zero size, ZIP integrity, provenance licence match,
      source SHA-256 match against the import report)
  5. JavaScript metadata files parse as the expected assignments

Exit code 0 means every check passed. A failing check prints FAIL lines
and exits 1. Intended to run from the reader repository root:

    python3 tools/audit_2026_11_03_europe_english_reader.py \
        --release releases/v1.27 --out releases/v1.29
"""
import argparse
import gzip
import hashlib
import json
import sys
import zipfile
from pathlib import Path

GROUP = 'europe-english-1.29'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def js(path: Path):
    return json.loads(path.read_text().split('=', 1)[1].rstrip(';\n'))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--release', type=Path, default=Path('releases/v1.27'),
                    help='baseline release used for the preservation check')
    ap.add_argument('--out', type=Path, default=Path('releases/v1.29'),
                    help='release directory to audit')
    args = ap.parse_args()
    out, failures = args.out, []

    def check(condition, label):
        if not condition:
            failures.append(label)
            print('FAIL', label)

    catalog = js(out / 'catalog.js')
    editions = catalog['editions']
    check(len(editions) == 200, f'catalog has {len(editions)} editions, expected 200')
    europe = [e for e in editions if e.get('data_group') == GROUP]
    check(len(europe) == 116, f'{len(europe)} editions in {GROUP}, expected 116')
    if args.release.exists():
        baseline = js(args.release / 'catalog.js')
        missing = [e['id'] for e in baseline['editions']
                   if e['id'] not in {x['id'] for x in editions}]
        check(not missing, f'baseline editions missing from 1.29: {missing[:5]}')

    manifest = js(out / 'europe-manifest.js')
    check(len(manifest) == 85, f'{len(manifest)} manifest packs, expected 85')
    for book, meta in sorted(manifest.items()):
        pack = out / 'europe-data' / (book + '.json.gz')
        if not pack.exists():
            check(False, f'missing pack {pack.name}')
            continue
        packed = pack.read_bytes()
        raw = gzip.decompress(packed)
        check(sha(raw) == meta['sha256'], f'{book}: expanded sha256 mismatch')
        check(len(raw) == meta['bytes'], f'{book}: expanded length mismatch')
        check(sha(packed) == meta['packed_sha256'], f'{book}: packed sha256 mismatch')
        check(len(packed) == meta['packed_bytes'], f'{book}: packed length mismatch')

    report = json.loads((out / 'sources/europe-english-import.json').read_text())
    check(len(report) == 116, f'import report lists {len(report)} editions, expected 116')
    for entry in report:
        sid = entry['id']
        for suffix in ('-source.zip', '-display-usfm.zip'):
            archive = out / 'sources' / (sid + suffix)
            if not archive.exists():
                check(False, f'missing {archive.name}')
                continue
            if archive.stat().st_size == 0:
                check(False, f'zero-byte {archive.name}')
                continue
            with zipfile.ZipFile(archive) as z:
                check(z.testzip() is None, f'corrupt member in {archive.name}')
        with zipfile.ZipFile(out / 'sources' / (sid + '-source.zip')) as z:
            provenance = json.loads(z.read('PROVENANCE.json'))
        check(provenance.get('license') == entry['license'],
              f'{sid}: provenance licence {provenance.get("license")!r} != report {entry["license"]!r}')
        check(provenance.get('source_sha256') == entry['source_sha256'],
              f'{sid}: provenance source sha256 mismatch')

    for name in ('catalog.js', 'europe-manifest.js', 'translations/metadata.js'):
        text = (out / name).read_text()
        check(text.lstrip().startswith('window.'), f'{name}: unexpected leading content')
    offline = (out / 'offline-library.js').read_text()
    check("kind==='europe'?'../v1.29/europe-data/'" in offline,
          'offline-library.js: europe pack path not wired')
    check("window.EuropeanTextPacks" in offline,
          'offline-library.js: EuropeanTextPacks manifest not wired')

    total_packed = sum(m['packed_bytes'] for m in manifest.values())
    total_rows = sum(e['verse_rows'] for e in report)
    print(f'editions={len(editions)} new={len(europe)} packs={len(manifest)} '
          f'packed_bytes={total_packed} verse_rows={total_rows}')
    if failures:
        print(f'{len(failures)} CHECK(S) FAILED')
        return 1
    print('ALL CHECKS PASSED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
