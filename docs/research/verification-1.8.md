# Reader 1.8 verification — 2026-10-23

Validated in headless Chromium on the local static site. Safari/WebKit and Edge were not available for execution; no claim of a test run on them is made.

- `READER_VERSION=1.8 python tests/reader_v12.py`: all 16 optional-slot combinations, empty-state network behavior, state migration, union navigation, visible-form search, share/bookmarks, themes, mobile, storage failures, genuine Hindi/Finnish/English/Urdu.
- `READER_VERSION=1.8 python tests/catalog_directory.py`: favorites, aliases, filter combinations and independent return to the correct slot.
- `READER_VERSION=1.8 python tests/pronunciation_browser.py`: opt-in data loading, independent spoken estimate and source, IPA search, sharing and source restoration.
- `python tests/source_references.py`: native LXX chapter selection and shared state; suffixed verse keys and bookmarks; Esther prologue; Wisdom extra-book loading; Hebrew RTL and Latin; Vamvas Greek OT; Theodotion, Church Slavonic and Thomson; opaque SQLite source keys and complete new source-unit FTS.
- `READER_VERSION=1.8 python tests/offline_package.py`: actual extracted release artifact, all external network blocked, original scripts/Latin/phoneme resources and new French/Greek/Hebrew text assets. Older 1.3 and 1.7 actual artifacts also checked with this test.
- Node syntax checks for reader/catalog/directory; Python compilation of acquisition/import/tests; `git diff --check`.
- Production `index.html`, `reader.js`, `catalog.js`, `reader-guides.js`, `data/` and root offline ZIP are identical to baseline `9d72a1d11b30992f209ebda28d58e45a4208c225`.

New import report lists eight editions and 159,764 source units. Original and adapted text are separate. Raw source archives and Wikisource revision attribution retained as separate online source-library downloads. The final published offline ZIP is reader-only, with display data and licenses. Alphabetic/compound references remain opaque keys, not coerced integers. Derived USFM exports normalize exceptional numeric references with explicit source-key remarks; consult raw sources for exact original structures.

Known limits: no verified cross-versification verse map; Swete corpus lacks Ecclesiastes; Delitzsch source numbering defects are disclosed; historical Delitzsch is not the latest modern Hebrew NT; modern Hebrew rights/revision and clean Brenton structured import remain open. No new verified edition-matched audio recordings. Written Latin is not pronunciation, and English phoneme estimates are not contextual spoken language. Uralic expansion beyond Finnish remains pending. Pages built commit 082ec12 successfully and public HTML/catalog/Wisdom data matched local checksums. Release-asset upload was rejected with HTTP 401; the latest reader-only ZIP uses the Pages download path. Final package and deployment checks follow this packaging adjustment.
