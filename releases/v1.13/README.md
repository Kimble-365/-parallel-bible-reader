# Reader 1.13 — more languages and personal study notes

51 public editions. Includes all search improvements from 1.12 and five additional 66-book editions:

| Edition | Source units | License |
|---|---:|---|
| Portuguese — Biblica Open Nova Bíblia Viva 2007 | 31,105 | CC BY-SA 4.0 |
| Czech — Bible Kralická 1613 | 31,172 | Public Domain |
| Korean — historical Korean Revised | 31,103 | Public Domain |
| Tagalog — Ang Biblia 1905 | 31,088 | Public Domain |
| Nepali — Biblica Open Contemporary Version 2024 | 31,094 | CC BY-SA 4.0 |

Portuguese is a Brazilian edition, also discoverable through the Portuguese language in Europe; it is not labeled as a European-Portuguese translation. Nepali is an alternative to the existing Unlocked Literal Bible. Korean retains Hangul with an ICU written Latin conversion. Nepali retains Devanagari with an ICU written Latin conversion. Neither is reconstructed speech or a pronunciation guide. Older Czech, Korean and Tagalog sources can use historical language. No matching new audio has been verified; existing audio choices remain independent.

The directory includes native-name aliases, language families and countries. These are project browsing groups with ISO language identity, not claimed United Bible Societies identifiers. Source reference panels preserve the edition's own numbering; matching labels do not prove equivalent passages.

## Notes

Open **Notes** in the reading toolbar. A new note automatically copies the selected verse from **Text 1**. Add a reference such as `JHN 3:16-18` or `John 3:16`, the current verse or a whole chapter. The original source text is inserted with its reference and translation name; it is not generated or translated by AI. A displayed Latin/phonetic form does not replace the source quotation. If Text 1 is empty or lacks that passage, the reader never substitutes another column.

Your writing is separate from quotations. Changing the reading translation leaves previous quotations unchanged. Notes save only in the current browser; they do not sync or upload. Clearing browser data or browser eviction can remove them. Download an individual note as UTF-8 text or back up all notes as JSON. Restore adds new copies without replacing existing notes. The notebook supports up to 100 notes and 2 MB of stored note data. Exporting private Bible quotations does not grant redistribution rights to their underlying translation.

Already stored quotations remain available offline. Inserting a different passage offline requires its text to be saved first. **Save selected texts** downloads original scripts and available transliterations; source ZIPs, external resources and audio require internet. Storage errors are shown, and closing an unsaved draft through the notebook's Back button is prevented. Keep a backup: the browser or operating system can still close a tab.

## Sources and compatibility

Original archives, rights declarations, exact-source checksums and derived UTF-8 USFM are under `sources/`; counts are in `sources/europe-asia-import.json`. Portuguese USX extraction omits headings/notes without changing verse spelling. Nepali USFM extraction omits headings/notes. Czech/Korean/Tagalog source JSON arrays retain their original chapter/verse positions and are mapped by verified book abbreviations. Original JSON blobs were checked against their Git object hashes. CC adaptations retain the same CC BY-SA 4.0 terms and identify the changes; no publisher endorsement is implied.

Existing text payloads remain shared from 1.8, 1.10 and 1.11. The 1.10 text storage schema/source keys are unchanged, preserving previously permitted private imports in the same browser. Notes use a separate local-storage key. Clearing the search index does not remove notes or saved texts. The 1.13 app shell has a separate service worker scope/cache, including the notebook assets. The original root reader and ZIP, and earlier numbered versions, remain available. The 1.8 ZIP remains the separate file-open reader; there is no new 1.13 standalone ZIP.

## Verification

Real Chromium checks cover all five new editions loading/searching, Korean/Nepali Latin display, automatic Text 1 quotations and ranges, note editing/reload, JSON export/additive restoration, original quotation attribution after changing translations, offline notes/reload and an empty Text 1 without fallback. Existing regression suites cover all 16 text-slot combinations, all six themes, mobile overflow, blocked storage, pronunciation, language-directory navigation, indexed search, stopping, incomplete searches, result paging and PWA behavior. Every new source unit, raw archive checksum, derived USFM and search fingerprint is checked separately. Model/UI tests also cover storage failure and draft retention. Safari/Edge and physical phone installation have not been tested.
