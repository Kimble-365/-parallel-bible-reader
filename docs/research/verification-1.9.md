# Reader 1.9 verification — 2026-10-24

Chromium with real service worker and IndexedDB, served on localhost:

- `python tests/pwa_offline.py`: actual UI saving of real English/Hebrew John, persistence after network-offline reload, RTL/Latin and source numbering, chapter search, offline directory and pronunciation dictionary, missing-text feedback, removal without deleting bookmarks, cancellation after a committed book and resume, full English 66-book save followed by Revelation 22 offline, no corpus bundles in the shell cache, version-specific worker URL, and blocked IndexedDB with online reading still available.
- `READER_VERSION=1.9 python tests/reader_v12.py`: all 16 optional-slot states including no text download when empty, storage migration/failures, mixed coverage and search, sharing/bookmarks, themes, mobile and genuine Hindi/Finnish/English/Urdu.
- `READER_VERSION=1.9 python tests/catalog_directory.py`: favorites, native aliases, filters and independent slot/reference return.
- `READER_VERSION=1.9 python tests/pronunciation_browser.py`: opt-in dictionary, per-slot source/phoneme forms, search, share/state and source restoration.
- Node syntax checks for worker, library, UI and reader; whitespace check.

The 1.9 app adds under 1 MB of static assets and references existing licensed corpus bundles. It saves selected edition/book rows and their completion metadata in one IndexedDB transaction, not the whole bundle. Source fetches use no-store. The service worker scope is only releases/v1.9. Production root and earlier releases are not changed.

Not verified on a physical phone, Safari/WebKit or Edge. Browser installation prompts and persistent-storage grants cannot be guaranteed by the app. Audio and source archives are online-only. All-book offline search needs all corresponding books saved. An installation or save does not guarantee the browser will never evict storage; test reopening before travel. Public deployment is verified after push rather than inferred from local tests.
