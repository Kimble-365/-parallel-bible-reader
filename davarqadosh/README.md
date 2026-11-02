# DavarQadosh parallel lexical reader

Independent development entry point: `davarqadosh/index.html`. The existing reader and numbered releases remain intact. TheWay research home: `Kimble-365/TheWay/DavarQadosh`.

The generated reader opens one verified, compressed SQLite book at a time and renders source-defined Hebrew/Aramaic token buttons. The study pane shows occurrence identity, source morphology, segments, historical dictionary explanations, inherited research reports and honest pending contextual research. Parallel WEB, Swete and MAM text follows each edition's own source labels. No word alignment or manuscript agreement is inferred from matching verse labels.

## Build the complete reader

Use Python 3.11+ (stdlib only), this repository at revision `9554e05a170e2a44e3cfa7156b6d3ccbd421c197` plus this change, and pinned source checkouts:

```sh
git clone https://github.com/openscriptures/morphhb.git /tmp/dq-oshb
git -C /tmp/dq-oshb checkout 3d15126fb1ef74867fc1434be1942e837932691f
git clone https://github.com/openscriptures/HebrewLexicon.git /tmp/dq-lexicon
git -C /tmp/dq-lexicon checkout 21c9add13bc727d3a951361778e97e3ff7afd1ce
python tools/davarqadosh/build_site.py --source /tmp/dq-oshb/wlc --lexicon /tmp/dq-lexicon/HebrewStrong.xml --book all --work /tmp/dq-work --out /tmp/dq-site
python -m http.server --directory /tmp/dq-site 8000
```

Open `http://localhost:8000/`. A secure origin (localhost or HTTPS) is required for SHA-256 and offline storage. Opening `index.html` via `file://` is not supported. The page explains how to import a locally built pack and external manifest if discovery files are unavailable.

`--book Gen` builds only the Genesis prototype. Repeating a build verifies and resumes unchanged book checkpoints. `--research PATH` adds pinned private BHH/LXXL records to a separate private build; public CI does not use this option. Keep generated SQLite databases and packs outside Git history. The workflow uploads the self-contained reader with its packs as a downloadable artifact.

```sh
python tools/davarqadosh/corpus.py audit-corpus /tmp/dq-work
python tools/davarqadosh/corpus.py verify-pack /tmp/dq-site/packs/GEN.wlexpack --manifest /tmp/dq-site/packs/GEN.manifest.json
python tools/davarqadosh/corpus.py unpack-book /tmp/dq-site/packs/GEN.wlexpack --manifest /tmp/dq-site/packs/GEN.manifest.json --out /tmp/GEN.sqlite
OSHB_SOURCE=/tmp/dq-oshb/wlc OSHB_LEXICON=/tmp/dq-lexicon/HebrewStrong.xml python tests/davarqadosh/test_corpus.py
python tests/davarqadosh/browser.py --site /tmp/dq-site
```

The UI saves only the selected book and its comparison sidecar when requested. Its caches are separate from existing reader stores. The book-pack cache has a 64 MiB budget; a book payload has a 128 MiB limit and a packed input a 32 MiB limit. One open book is retained in memory; browser objects require additional memory beyond the SQLite payload. Physical mobile device memory testing remains outstanding.

See [format specification](../docs/research/davarqadosh-format.md), [compatibility and discovery audit](../docs/research/davarqadosh-audit.md), [notices](NOTICE.md), and generated `coverage.json`. Source annotation coverage does not mean completed lexical research.
