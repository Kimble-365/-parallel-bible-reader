"""Download only missing pinned, licensed source objects; verify before replace."""
from pathlib import Path
import argparse, hashlib, json, urllib.request

ROOT = Path(__file__).resolve().parents[1]


def acquire(destination):
    lock = json.loads((ROOT / 'releases/v1.23/sources/syriac-lock.json').read_text())
    downloaded = 0
    for item in lock['files']:
        path = destination / item['repo'] / item['path']
        if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']:
            continue
        with urllib.request.urlopen(item['url'], timeout=60) as response:
            data = response.read(16 * 1024 * 1024 + 1)
        assert len(data) <= 16 * 1024 * 1024
        assert hashlib.sha256(data).hexdigest() == item['sha256'], item['path']
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + '.tmp')
        temporary.write_bytes(data)
        temporary.replace(path)
        downloaded += 1
    print('Verified pinned source objects:', len(lock['files']), 'downloaded:', downloaded)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=Path('/workspace/syriac-input'))
    acquire(parser.parse_args().source)
