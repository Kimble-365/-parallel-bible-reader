# Reader 1.11 verification — 2026-10-24

Verified on the local static site with Chromium:

- `python tests/uralic_111.py`: 46 public editions; actual Hungarian/Estonian/Finnish John 3:16; Hungarian accented substring search; explicit missing Genesis in the five-book Estonian source; Uralic directory results; valid source ZIP download with the service worker controlling the page; saving all 66 Hungarian plus 5 Estonian books and reopening offline; actual permitted LLL ZIP imported in 1.10 and opened in 1.11 without reimport, also offline.
- `READER_VERSION=1.11 python tests/reader_v12.py`: all 16 optional-slot combinations, no text request when empty, migration/storage failures, union coverage/search, share/bookmarks, six themes/mobile, genuine Hindi/Finnish/English/Urdu.
- `READER_VERSION=1.11 python tests/catalog_directory.py`: popular/favorites, native aliases, directory filters and independent slot/reference return.
- Node syntax checks for worker/library/reader, Python compilation and whitespace check.
- Production root assets and releases 1.8–1.10 are unchanged. Site payload is approximately 781 MiB, below the Pages site-size limit. New bulk files cover only the new editions; existing corpus and Finnish 1776 files are reused.

Hungarian: HunKar public-domain declaration and module configuration retained. Source has 31,126 nonempty numbered units and 44 empty placeholders; no guessed replacement verses. Calvin numbering is preserved. Estonian: © 2023 Sihtasutus Piibel Kõigile, CC BY-SA 4.0, exact five-book USFM archive and copyright retained. Display extraction omits headings/notes, original source remains available. The unrelated Est module was excluded for unknown rights. No whole-Estonian-Bible or new matched-audio claim.

The new worker routes navigation fallback only for actual reader/directory pages; source files and other documents are not replaced with app HTML. The unchanged 1.10 IndexedDB schema and source keys are intentionally shared, retaining previous permitted private imports and saved texts on the same browser/origin. Source ZIP downloads still need internet. Original personal files should be retained because browser storage can be evicted.

No physical device installation, Safari/WebKit or Edge execution was tested. Written Latin text is not a spoken reconstruction. Broader Uralic coverage and audio matching remain open. Public Pages build and asset checks follow push; local verification does not by itself establish a live deployment.
