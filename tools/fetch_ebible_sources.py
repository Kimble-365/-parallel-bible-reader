"""Fetch pinned eBible.org inputs for the Reader 1.29 europe-english import.

Rebuilds the acquisition workspace expected by import_europe_english_129.py:

    <work>/rights-scan.json      (from the pins file)
    <work>/details/<id>.html     (details.php rights page per edition)
    <work>/sources/<id>_usfm.zip (USFM source archive per edition)

The pins file (tools/europe_129_pins.json) carries the rights-reviewed
selection as gzip+base64 JSON so the import is reproducible without the
original workstation. Downloads are retried and politely paced; existing
complete files are reused so reruns are cheap.
"""
from pathlib import Path
import argparse, base64, gzip, json, time, urllib.request, urllib.error

DETAILS = 'https://ebible.org/Scriptures/details.php?id='
UA = {'User-Agent': 'parallel-bible-reader-ci/1.29 (rights-reviewed import; contact via repository)'}


def fetch(url, dest, retries=4):
    if dest.exists() and dest.stat().st_size > 0:
        return 'cached'
    tmp = dest.with_suffix(dest.suffix + '.tmp')
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r, open(tmp, 'wb') as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
            if tmp.stat().st_size == 0:
                raise IOError('empty response')
            tmp.replace(dest)
            return 'ok'
        except (urllib.error.URLError, IOError, TimeoutError) as e:
            print(f'  retry {attempt}/{retries} {url}: {e}', flush=True)
            time.sleep(5 * attempt)
    raise SystemExit(f'FAILED to fetch {url}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--pins', type=Path, required=True)
    ap.add_argument('--delay', type=float, default=1.0)
    args = ap.parse_args()

    pins = json.loads(args.pins.read_text(encoding='utf-8'))
    scan = json.loads(gzip.decompress(base64.b64decode(pins['rights_scan_gz_b64'])).decode('utf-8'))
    work = args.work
    (work / 'details').mkdir(parents=True, exist_ok=True)
    (work / 'sources').mkdir(parents=True, exist_ok=True)
    (work / 'rights-scan.json').write_text(
        json.dumps(scan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    for i, spec in enumerate(scan, 1):
        sid = spec['id']
        r1 = fetch(DETAILS + sid, work / 'details' / (sid + '.html'))
        time.sleep(args.delay)
        r2 = fetch(spec['usfm'], work / 'sources' / (sid + '_usfm.zip'))
        print(f'{i:3}/{len(scan)} {sid:16} details={r1} usfm={r2}', flush=True)
        time.sleep(args.delay)
    print('FETCH COMPLETE:', len(scan), 'editions')


if __name__ == '__main__':
    main()
