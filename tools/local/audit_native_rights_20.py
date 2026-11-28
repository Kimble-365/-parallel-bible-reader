"""Offline Cargo archive/notice audit; never infer legal clearance from an SPDX label."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, re, tarfile, tomllib
from urllib.parse import quote

REGISTRY = 'registry+https://github.com/rust-lang/crates.io-index'
NOTICE = re.compile(r'^(licen[sc]e|copying|notice|copyright)([._-]|$)', re.I)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def notice_path(path):
    p = PurePosixPath(path)
    return bool(NOTICE.match(p.name) or any(x.lower() in {'licenses', 'licences'} for x in p.parts[:-1]))

def audit(metadata_path, lock_path, cache_root, source_commit):
    metadata = json.loads(Path(metadata_path).read_text(encoding='utf-8'))
    raw_lock = Path(lock_path).read_bytes()
    lock = tomllib.loads(raw_lock.decode('utf-8'))
    locked = {(p['name'], p['version'], p.get('source')): p for p in lock['package']}
    packages = {(p['name'], p['version'], p.get('source')): p for p in metadata['packages']}
    if len(packages) != len(metadata['packages']) or packages.keys() != locked.keys():
        raise ValueError('Metadata package identities differ from the exact Cargo.lock.')
    records, texts = [], {}
    cache_root = Path(cache_root).resolve()
    for key, package in sorted(packages.items(), key=lambda item: item[0][:2]):
        name, version, source = key
        if not source:
            if (name, version) != ('parallel-bible-reader', '2.0.0'):
                raise ValueError('Unexpected local/path dependency: ' + name)
            continue
        if source != REGISTRY:
            raise ValueError('Registry/source requires separate verification: ' + source)
        if any('/' in s or '\\' in s or s.startswith('.') for s in (name, version)):
            raise ValueError('Invalid crate identity.')
        filename = name + '-' + version + '.crate'
        candidates = sorted(cache_root.glob('*/' + filename))
        if not candidates:
            raise ValueError('Missing original crate archive: ' + filename)
        archive = None
        for candidate in candidates:
            if candidate.is_symlink() or not candidate.resolve().is_relative_to(cache_root):
                raise ValueError('Archive escapes the supplied cache.')
            data = candidate.read_bytes()
            if sha(data) == locked[key].get('checksum'):
                archive = candidate
                break
        if archive is None:
            raise ValueError('Cargo.lock checksum mismatch: ' + filename)
        notices, links, vcs = [], [], None
        prefix = name + '-' + version
        with tarfile.open(archive, 'r:gz') as tar:
            for member in tar.getmembers():
                path = PurePosixPath(member.name)
                if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0] != prefix:
                    raise ValueError('Unsafe/nonmatching archive path: ' + member.name)
                relative = '/'.join(path.parts[1:])
                if relative == '.cargo_vcs_info.json' and member.isfile() and member.size <= 1_000_000:
                    vcs = json.loads(tar.extractfile(member).read())
                if not notice_path(relative):
                    continue
                if member.issym() or member.islnk():
                    links.append(relative)
                elif member.isfile():
                    if member.size > 2_000_000:
                        raise ValueError('Oversized notice requires review: ' + relative)
                    body = tar.extractfile(member).read()
                    try:
                        body.decode('utf-8')
                    except UnicodeDecodeError as error:
                        raise ValueError('Non-UTF-8 notice requires review: ' + relative) from error
                    digest = sha(body)
                    texts[digest] = body
                    notices.append({'path': relative, 'bytes': len(body), 'sha256': digest})
        records.append({'name': name, 'version': version, 'source': source,
                        'archive': filename, 'archive_sha256': locked[key]['checksum'],
                        'archive_bytes': archive.stat().st_size,
                        'source_archive_url': 'https://crates.io/api/v1/crates/' + quote(name, safe='') + '/' + quote(version, safe='') + '/download',
                        'repository': package.get('repository'), 'declared_license': package.get('license'),
                        'declared_license_file': Path(package['license_file']).name if package.get('license_file') else None,
                        'vcs': vcs, 'notices': sorted(notices, key=lambda n: n['path']),
                        'unresolved_notice_links': sorted(links)})
    gaps = [{'name': p['name'], 'version': p['version'], 'declared_license': p['declared_license']}
            for p in records if not p['notices'] or p['unresolved_notice_links']]
    report = {'schema': 1, 'source_commit': source_commit, 'lock_sha256': sha(raw_lock),
              'metadata_packages': len(packages), 'verified_registry_archives': len(records),
              'notice_files': sum(len(p['notices']) for p in records), 'unique_notice_texts': len(texts),
              'archive_bytes': sum(p['archive_bytes'] for p in records),
              'all_archive_checksums_verified': True, 'notice_file_inventory_complete': not gaps,
              'public_release_approved': False,
              'status': 'notice-source-review-required' if gaps else 'archive-notice-inventory-complete; legal/source-offer review still required',
              'notice_gaps': gaps, 'packages': records,
              'limits': ['A missing archived notice file is not a finding that a crate is unlicensed.',
                         'SPDX labels are recorded verbatim; no license alternative is selected automatically.',
                         'The unmodified source archive/checksum is authoritative; VCS metadata can describe a dirty source tree.',
                         'The cross-platform lock includes target-specific and build-only crates; the inventory does not claim that every dependency is linked into every binary.',
                         'MPL/source-offer applicability and pinned upstream notices require separate distribution review.',
                         'No Scripture corpus, application store or network is read or modified.']}
    return report, texts

def write_report(report, texts, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'DEPENDENCY-RIGHTS.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with (out / 'ARCHIVED-NOTICES.txt').open('wb') as bundle:
        bundle.write(b'Archived dependency notice texts, byte-preserved and deduplicated by SHA-256.\nSee DEPENDENCY-RIGHTS.json for package/source identities and unresolved gaps.\nThis is an audit sidecar, not legal clearance or a declaration of license choices.\n')
        for digest, body in sorted(texts.items()):
            bundle.write(('\n===== SHA-256 ' + digest + ' =====\n').encode())
            bundle.write(body)
            bundle.write(b'\n')
    paths = ['DEPENDENCY-RIGHTS.json', 'ARCHIVED-NOTICES.txt']
    (out / 'SHA256SUMS').write_text(''.join(sha((out / p).read_bytes()) + '  ' + p + '\n' for p in paths), encoding='utf-8')

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--metadata', required=True)
    p.add_argument('--lock', required=True)
    p.add_argument('--cache', required=True)
    p.add_argument('--source-commit', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--require-notices', action='store_true')
    args = p.parse_args()
    report, texts = audit(args.metadata, args.lock, args.cache, args.source_commit)
    write_report(report, texts, args.out)
    print(json.dumps({k: v for k, v in report.items() if k not in {'packages', 'limits', 'notice_gaps'}}))
    print('Notice-source follow-up cases:', len(report['notice_gaps']))
    return 2 if args.require_notices and not report['notice_file_inventory_complete'] else 0

if __name__ == '__main__':
    raise SystemExit(main())
