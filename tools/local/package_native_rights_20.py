"""Create a reproducible dependency source/notice review sidecar, never release approval."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tomllib
import zipfile
from verify_native_rights_review_20 import verify as verify_review

REGISTRY = 'registry+https://github.com/rust-lang/crates.io-index'
PROJECT_FILES = ('LICENSE', 'apps/native-20/src-tauri/Cargo.lock',
                 'apps/native-20/src-tauri/Cargo.toml', 'apps/native-20/src-tauri/build.rs',
                 'apps/native-20/src-tauri/src/lib.rs', 'apps/native-20/src-tauri/src/main.rs',
                 'apps/native-20/src-tauri/tauri.conf.json', 'apps/native-20/src-tauri/capabilities/main.json')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_name(name):
    p = PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or '\\' in name or str(p) != name:
        raise ValueError('Unsafe bundle path')
    return name


def read_inside(root, name):
    path = root / safe_name(name)
    if path.is_symlink() or not path.resolve().is_relative_to(root):
        raise ValueError('Source escapes supplied root')
    return path.read_bytes()


def build_inputs(root, audit, cache, source_commit):
    root, audit, cache = Path(root).resolve(), Path(audit).resolve(), Path(cache).resolve()
    inventory_path = audit / 'DEPENDENCY-RIGHTS.json'
    verify_review(root, inventory_path)
    inventory = json.loads(inventory_path.read_text(encoding='utf-8'))
    lock_bytes = read_inside(root, 'apps/native-20/src-tauri/Cargo.lock')
    lock = tomllib.loads(lock_bytes.decode('utf-8'))
    locked = {(p['name'], p['version']): p for p in lock['package'] if p.get('source')}
    packages = {(p['name'], p['version']): p for p in inventory['packages']}
    if len(packages) != len(inventory['packages']) or packages.keys() != locked.keys():
        raise ValueError('Archive inventory differs from the complete external lock')
    if inventory['source_commit'] != source_commit or inventory['lock_sha256'] != digest(lock_bytes):
        raise ValueError('Stale source/lock identity')
    targets = json.loads(read_inside(audit, 'target-graphs/TARGET-RIGHTS.json'))
    if targets['source_commit'] != source_commit or targets['lock_sha256'] != digest(lock_bytes):
        raise ValueError('Target graph source/lock identity differs')
    files = {}
    for (name, version), p in sorted(packages.items()):
        safe_name(name); safe_name(version)
        if '/' in name or '/' in version or locked[(name, version)]['source'] != REGISTRY:
            raise ValueError('Unsupported crate identity/source')
        checksum = locked[(name, version)]['checksum']
        if p['archive_sha256'] != checksum:
            raise ValueError('Inventory archive checksum differs from lock')
        filename = name + '-' + version + '.crate'
        candidates = sorted(cache.glob('*/' + filename))
        body = None
        for path in candidates:
            if path.is_symlink() or not path.resolve().is_relative_to(cache):
                raise ValueError('Archive escapes cache')
            data = path.read_bytes()
            if digest(data) == checksum:
                body = data; break
        if body is None:
            raise ValueError('Missing or altered original archive: ' + filename)
        files['crates/' + filename] = body
    for name in ('DEPENDENCY-RIGHTS.json', 'ARCHIVED-NOTICES.txt', 'SHA256SUMS'):
        files['audit/' + name] = read_inside(audit, name)
    for path in sorted((audit / 'target-graphs').iterdir()):
        if path.is_file():
            files['audit/target-graphs/' + path.name] = read_inside(audit, 'target-graphs/' + path.name)
    review_path = 'editor-notes/research/native-notice-review-20.json'
    review = json.loads(read_inside(root, review_path))
    files[review_path] = read_inside(root, review_path)
    for source in review['sources']:
        files[source['path']] = read_inside(root, source['path'])
    for path in PROJECT_FILES:
        files['project/' + path] = read_inside(root, path)
    files['README.txt'] = (
        'Parallel Bible Reader 2.0 dependency source/notice REVIEW sidecar\n'
        'Source commit: ' + source_commit + '\n\n'
        'All external Cargo.lock crate archives are included verbatim, including target/build-only crates.\n'
        'Archived notices, exact-revision upstream evidence, graph identities and selected native host source are retained.\n'
        'Original crate archives, not edited extractions, identify unmodified upstream dependency source.\n'
        'No licence alternative or copyright holder is invented. See the original per-package terms and open cases.\n'
        'This is not a complete application/build-tool/SDK/font/Scripture source distribution or a signed installer.\n'
        'The complete project revision is https://github.com/Kimble-365/-parallel-bible-reader/tree/' + source_commit + '\n'
        'No product notice integration, native shipped-file/link assessment, SDK clearance or public release approval is implied.\n'
        'All 36 original conventional-notice cases and applicable source-availability requirements remain reviewable.\n'
        'A temporary CI artifact does not establish durable public source availability. Preserve/rehost a reviewed bundle\n'
        'alongside any future authorized distribution and verify its applicability to the actual shipped components.\n'
    ).encode('utf-8')
    return files, {'source_commit': source_commit, 'lock_sha256': digest(lock_bytes),
                   'external_archives': len(packages), 'original_notice_cases': len(inventory['notice_gaps']),
                   'public_release_approved': False, 'actual_shipped_file_assessment_complete': False}


def write_bundle(files, identity, output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if 'BUNDLE-MANIFEST.json' in files:
        raise ValueError('Reserved manifest path')
    manifest = {**identity, 'files': [{'path': safe_name(name), 'bytes': len(body), 'sha256': digest(body)}
                                    for name, body in sorted(files.items())]}
    contents = {**files, 'BUNDLE-MANIFEST.json': (json.dumps(manifest, indent=2)+'\n').encode('utf-8')}
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_STORED) as z:
        for name, body in sorted(contents.items()):
            info = zipfile.ZipInfo(safe_name(name), date_time=(2020, 1, 1, 0, 0, 0))
            info.create_system = 3; info.external_attr = 0o100644 << 16
            z.writestr(info, body)
    verify_bundle(output)
    return {'source_commit': identity['source_commit'], 'archive_bytes': output.stat().st_size,
            'sha256': digest(output.read_bytes()), 'files': len(contents),
            'external_archives': identity['external_archives'], 'public_release_approved': False}


def verify_bundle(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate bundle member')
        for name in names: safe_name(name)
        manifest = json.loads(z.read('BUNDLE-MANIFEST.json'))
        expected = {p['path']: p for p in manifest['files']}
        if len(expected) != len(manifest['files']) or set(names) != set(expected) | {'BUNDLE-MANIFEST.json'}:
            raise ValueError('Bundle inventory differs')
        if manifest['public_release_approved'] is not False or manifest['actual_shipped_file_assessment_complete'] is not False:
            raise ValueError('Review bundle cannot grant release clearance')
        for name, p in expected.items():
            body = z.read(name)
            if len(body) != p['bytes'] or digest(body) != p['sha256']:
                raise ValueError('Bundle member checksum differs')
        return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    files, identity = build_inputs(args.root, args.audit, args.cache, args.source_commit)
    print(json.dumps(write_bundle(files, identity, args.out)))
