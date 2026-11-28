"""Verify pinned notice-review evidence without interpreting licences as approval."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import tomllib


def verify(root, inventory=None):
    root = Path(root).resolve()
    review = json.loads((root / 'editor-notes/research/native-notice-review-20.json').read_text(encoding='utf-8'))
    lock = (root / 'apps/native-20/src-tauri/Cargo.lock').read_bytes()
    if hashlib.sha256(lock).hexdigest() != review['lock_sha256']:
        raise ValueError('Review lock identity is stale')
    locked = {(p['name'], p['version']): p for p in tomllib.loads(lock.decode('utf-8'))['package']}
    cases = review['cases']
    if review['public_release_approved'] is not False or any(p['distribution_clearance'] is not False for p in cases):
        raise ValueError('Evidence triage cannot grant distribution clearance')
    identities = {(p['name'], p['version']) for p in cases}
    if len(identities) != len(cases):
        raise ValueError('Duplicate review case')
    for s in review['sources']:
        rel = PurePosixPath(s['path'])
        if rel.is_absolute() or '..' in rel.parts or not s['path'].startswith('editor-notes/research/native-notice-evidence/'):
            raise ValueError('Unsafe evidence path')
        path = root / s['path']
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError('Evidence escapes root')
        b = path.read_bytes()
        git_blob = hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()
        if len(b) != s['bytes'] or hashlib.sha256(b).hexdigest() != s['sha256'] or git_blob != s['git_blob']:
            raise ValueError('Pinned evidence bytes differ')
        if not re.fullmatch('[0-9a-f]{40}', s['revision']):
            raise ValueError('Unpinned upstream revision')
        expected = s['repository'].replace('https://github.com/', 'https://raw.githubusercontent.com/') + '/' + s['revision'] + '/' + s['upstream_path']
        if s['url'] != expected:
            raise ValueError('Upstream URL differs from pinned revision')
    for p in cases:
        if locked.get((p['name'], p['version']), {}).get('checksum') != p['archive_sha256']:
            raise ValueError('Case archive identity differs from lock')
        if not p['status'] or not p['next_action']:
            raise ValueError('Missing disposition')
        for index in p['source_ids']:
            s = review['sources'][index]
            if s['repository'] != p['repository'] or s['revision'] != p['vcs']['git']['sha1']:
                raise ValueError('Notice revision differs from archived VCS provenance')
    if inventory is not None:
        actual = json.loads(Path(inventory).read_text(encoding='utf-8'))
        gaps = {(p['name'], p['version']) for p in actual['notice_gaps']}
        if identities != gaps or actual['lock_sha256'] != review['lock_sha256']:
            raise ValueError('Review cases differ from fresh archive gaps')
        records = {(p['name'], p['version']): p for p in actual['packages']}
        for p in cases:
            a = records[(p['name'], p['version'])]
            for key in ('archive_sha256', 'repository', 'declared_license', 'vcs'):
                if p[key] != a[key]:
                    raise ValueError('Review provenance differs from fresh archive: ' + key)
    return {'cases': len(cases), 'upstream_urls': len(review['sources']),
            'unique_snapshots': len({s['path'] for s in review['sources']}),
            'public_release_approved': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--inventory', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.root, args.inventory)))
