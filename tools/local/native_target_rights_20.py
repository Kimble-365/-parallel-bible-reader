"""Measure target dependency graphs; graph presence is not binary inclusion or clearance."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

TARGETS = ('x86_64-pc-windows-msvc', 'aarch64-apple-darwin',
           'x86_64-apple-darwin', 'aarch64-linux-android', 'aarch64-apple-ios-sim')
WARNINGS = {'chrono': 'RUSTSEC-2026-0543', 'proc-macro-error': 'RUSTSEC-2024-0370',
            'zbus_names': 'RUSTSEC-2026-0371', 'zvariant': 'RUSTSEC-2026-0370',
            'zvariant_derive': 'RUSTSEC-2026-0372', 'glib': 'RUSTSEC-2024-0429'}
PROJECT = ('parallel-bible-reader', '2.0.0')


def parse_tree(text):
    packages = set()
    for line in text.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r'([A-Za-z0-9_-]+) v([^\s]+)(?: \([^\n]*\))?(?: \(\*\))?', line)
        if not match:
            raise ValueError('Unrecognized cargo tree line: ' + line)
        packages.add(match.groups())
    if PROJECT not in packages:
        raise ValueError('Cargo graph does not contain the expected project')
    return packages


def classify(normal, all_edges, records, gaps):
    if not normal.issubset(all_edges):
        raise ValueError('Normal graph is not a subset of normal/build graph')
    if any(p != PROJECT and p not in records for p in all_edges):
        raise ValueError('Cargo graph contains an unverified package identity')
    def rows(ids):
        return [{'name': n, 'version': v, 'archive_sha256': records[(n, v)]['archive_sha256'],
                 'source_archive_url': records[(n, v)]['source_archive_url'],
                 'declared_license': records[(n, v)]['declared_license']}
                for n, v in sorted(ids) if (n, v) != PROJECT]
    def location(p):
        return 'normal_graph' if p in normal else 'build_graph_only' if p in all_edges else 'absent'
    return {'normal_graph': rows(normal), 'build_graph_only': rows(all_edges - normal),
            'notice_cases': [{'name': n, 'version': v, 'location': location((n, v))} for n, v in sorted(gaps)],
            'mpl_cases': [{'name': n, 'version': v, 'location': location((n, v))}
                          for (n, v), r in sorted(records.items()) if 'MPL' in (r['declared_license'] or '')],
            'warning_cases': [{'name': n, 'version': v, 'advisory': WARNINGS[n], 'location': location((n, v))}
                              for n, v in sorted(records) if n in WARNINGS]}


def collect(root, inventory_path, out, source_commit, run=subprocess.run):
    root, out = Path(root).resolve(), Path(out)
    inventory = json.loads(Path(inventory_path).read_text(encoding='utf-8'))
    lock = root / 'apps/native-20/src-tauri/Cargo.lock'
    if hashlib.sha256(lock.read_bytes()).hexdigest() != inventory['lock_sha256'] or not inventory['all_archive_checksums_verified']:
        raise ValueError('Archive inventory does not verify the current lock')
    records = {(p['name'], p['version']): p for p in inventory['packages']}
    if len(records) != len(inventory['packages']):
        raise ValueError('Ambiguous archive identities')
    gaps = {(p['name'], p['version']) for p in inventory['notice_gaps']}
    report = {'schema_version': 1, 'source_commit': source_commit, 'lock_sha256': inventory['lock_sha256'],
              'features': ['custom-protocol'], 'public_release_approved': False, 'targets': {},
              'limits': ['Cargo graphs are conservative dependency reachability, not linked-binary or shipped-file analysis.',
                         'Normal edges can include procedural macros; build_graph_only means reachable only when build edges are included, not proof that no generated code is shipped.',
                         'Default features plus custom-protocol are requested explicitly; no dev edges are included.',
                         'Absent packages are absent only from these exact target/feature graphs; this does not dismiss advisories for other targets or future changes.',
                         'Native/system/SDK/npm/toolchain/font/Scripture obligations require separate distribution inventory.']}
    out.mkdir(parents=True, exist_ok=True)
    for target in TARGETS:
        graphs = []
        for edges in ('normal', 'normal,build'):
            command = ['cargo', 'tree', '--locked', '--manifest-path', 'apps/native-20/src-tauri/Cargo.toml',
                       '--target', target, '--features', 'custom-protocol', '--edges', edges,
                       '--prefix', 'none', '--format', '{p}']
            result = run(command, cwd=root, env={**os.environ, 'CARGO_TERM_COLOR': 'never'},
                         capture_output=True, text=True, check=True)
            suffix = 'normal' if edges == 'normal' else 'normal-build'
            raw = result.stdout.encode('utf-8')
            (out / (target + '-' + suffix + '.txt')).write_bytes(raw)
            graphs.append(parse_tree(result.stdout))
        report['targets'][target] = classify(*graphs, records, gaps)
        print(json.dumps({'target': target, 'normal': len(graphs[0])-1,
                          'build_only': len(graphs[1]-graphs[0]),
                          'notice_cases': report['targets'][target]['notice_cases'],
                          'mpl_cases': report['targets'][target]['mpl_cases'],
                          'warning_cases': report['targets'][target]['warning_cases']}))
    (out / 'TARGET-RIGHTS.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    files = sorted(p for p in out.iterdir() if p.name == 'TARGET-RIGHTS.json' or p.suffix == '.txt')
    (out / 'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--inventory', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    args = parser.parse_args()
    collect(args.root, args.inventory, args.out, args.source_commit)
