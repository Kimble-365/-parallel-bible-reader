# Reader 1.10 verification — 2026-10-24

Chromium, actual local static site with service worker and IndexedDB:

- `python tests/finnish_110.py`: real Biblia 1776 beside KR33/38; user-provided LLL ZIP imported into Text 3; known Genesis/John 3:16/Revelation samples with 66-book fixed-line mapping; local edition hydration into the directory; offline reload and chapter search; plain ONT parsing and wrong-edition rejection; synthetic (explicitly non-scripture) KR92/RK format paths; no POST text upload. Complete 78-book Biblia save and Wisdom offline are included in this test.
- `READER_VERSION=1.10 python tests/reader_v12.py`: all 16 optional-slot states, reading-state migration and storage errors, coverage union/search, sharing/bookmarks, themes and mobile, genuine Hindi/Finnish/English/Urdu.
- `READER_VERSION=1.10 python tests/pwa_offline.py`: actual English/Hebrew offline persistence, directory/pronunciation assets, no stale missing-text content, bookmark-safe deletion, cancellation/resume, full 66-book English save and Revelation offline, worker scope/cache and blocked-IndexedDB online fallback.
- `READER_VERSION=1.10 python tests/catalog_directory.py`: aliases, favorites, filters and independent slot/reference return.
- Node syntax checks and Python compilation; whitespace check; no production root or 1.8/1.9 source changes.

Import issue found and fixed: LLL contains nested TS headings. A non-greedy single regular expression left closing tags behind; the parser now tracks heading nesting and rejects unbalanced/cross-line headings. Unmarked source text is retained; no guessed scripture corrections.

Rights/access evidence: FinBiblia declares Public Domain; 78 nonempty source books and 35,445 numbered units imported, with SHA-256 and raw archive. KR92/RK official terms require permission for public redistribution. LLL publisher permits personal downloading/storage but a public redistribution license was not verified. LLL.zip was supplied by the user for private transformation/testing and is not committed to the public app. The reader has 44 public editions; additional local private editions exist only after import on that device. Real KR92/RK protected files were not acquired or tested; their importer branches use synthetic fixtures.

Physical Safari/Edge/phone installation is not tested. Only standard 31,102-position UTF-8 theWord ONT (or one-file ZIP) is supported by private import; PDF/e-Sword/SWORD import is not claimed. Private data is version-local browser storage, can be evicted and is not transferred by a shared URL. Retain your original personal file. Public deployment checks follow publication; local tests alone do not prove deployment.
