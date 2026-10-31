# Reader 1.22 — vocabulary backups and continuous word study

Full combined browser verification passed in [Actions 40855411166](https://github.com/Kimble-365/-parallel-bible-reader/actions/runs/40855411166) at preview commit a595018e7a45195748ced4dc16434a2d0b349273. Existing 1.21 texts, notes, plans, imports, pages and study resources are retained with the same device storage keys.

Study → Saved vocabulary & backups opens a searchable list of saved Hebrew/Greek words. Search original spelling, transliteration, gloss, word code or reference; remove individual words or start saved-word flashcards. The same screen remains available from empty practice and from Word study.

Export vocabulary as attributed UTF-8 JSON for backup/restore, or UTF-8 CSV with a BOM for spreadsheet use. CSV quotes delimiters/newlines and prefixes potential spreadsheet formula cells. Use JSON, not CSV, to restore. A backup file is read on this device; nothing is uploaded.

Import shows added/duplicate/final counts before saving. Confirm explicitly to merge; existing words are preserved, and repeated original/code/gloss combinations are skipped. If the stored list changes after preview, preview again. Malformed/oversized files, unsupported versions, invalid fields, full lists (500 words / 1.8 MB compact storage) and storage failures are reported without replacing saved data. Imported personal backup content is not independently verified against the source corpus. This is a vocabulary backup, not a backup of notes or all offline Bible/study packs.

Word study now has Previous verse / Next verse buttons that follow the pinned source book's numeric verse order, crossing chapter boundaries within that book. Buttons stop at the source book edges. Moving clears the in-verse filter and loads the next source verse; missing offline packs show an error rather than displaying the previous verse's words. Source numbering may differ from Text 1, and these controls do not change the reading translation/reference. No automatic next-book or mass source download is introduced.

The 1.21 library still has 60 entries and eight in-app sources; the public Bible catalog remains 62 editions. No new corpus or publisher-protected content is silently installed. Full NET notes/modern commentary texts remain provider-hosted. Hebrew/Greek source credits and CC BY 4.0 terms are retained in source readers and word backups. Physical iPhone/Safari animation quality and full linguistic review remain open.

## Related English texts — 31 October 2026

Added OET Literal/Readers drafts, POB canonical AI-assisted draft and the 44-book OEB US published release. Catalog now contains 66 editions. [Coverage, provenance and permission limits](related-projects.md). Use OET’s pair together. Existing text IDs, storage keys and earlier releases are retained.



## Novum Testamentum Graece Aboensis — 31 October 2026

Added five complete 27-book digital Greek texts: Tischendorf 8 (version 2.8 printed-form/kethiv), Nestle 1904 digital base text, official SBLGNT v1.2, unaccented Westcott–Hort, and the unaccented OpenGNT Koine module. Sinaiticus original and ca-corrected views cover John 1:1–5 only. Matching source labels are not verified cross-edition alignment.

Tischendorf, Nestle base text and WH components declare public domain; SBLGNT is CC BY 4.0 (Society of Biblical Literature / Logos Bible Software, edited by Michael W. Holmes); OpenGNT main text is CC BY-SA 4.0 (Eliran Wong); Sinaiticus is CC BY-NC-SA 3.0 (Codex Sinaiticus Project / ITSEE). These source components retain their terms and are not relicensed under the app software license.

Study library → NTGL opens the complete 6,153-entry Abbott–Smith TEI-derived historical lexicon, declared public domain by its source project. GreekResources crosswalks are CC BY 4.0, credited to Open Scriptures Septuagint Project, and retain the upstream mismatch warning. The 61-word MorphGNT John sample uses CC BY-SA 3.0 annotation, credited to James Tauber/MorphGNT; it is a separately versioned source.

Edition revisions, source files and measured coverage are in `sources/ntgl-import.json`; source originals are stored once, compressed, under TheWay/NTGL/sources/reader-corpora. Mark’s unnumbered Nestle shorter-ending appendix is retained in `sources/ntgl-paratext.json`, not merged into Mark 16:20. The digital Tischendorf module has no printed apparatus.
