# Reader 1.26 — saved apparatus and filtered UTF-8 export

Prepared increment; browser verification and publication are pending.

Study → Textual apparatus → Saved apparatus lists downloaded source books and private imports separately, and opens either directly. Downloaded books use saved bytes only; missing or outdated list entries never trigger a source download. After a missing-cache error, an explicit Load can retrieve the source. Current supported source pins are recognized by namespace/commit/book; older pins remain visible with an explanation and a remove option. Independent storage failures do not hide the other library.

Export filtered entries TXT saves every matching entry as UTF-8, including matches beyond the first 100 displayed. Source credits/terms, sigla, hands/status, qualifiers and original records/XML remain in the file. JSON remains a complete package export. First reference makes navigation available from All source entries.

Existing 84 editions, BHH/NTGL/LXXL resources, notes, vocabulary, pages and offline stores remain available with unchanged storage keys. Large BHH payloads are reused from 1.23; Syriac reading/index/lexicon packs are reused from 1.25. This integration preserves that concurrently published Syriac release. The apparatus sources and scope remain as in 1.24: SBLGNT printed-edition comparisons and OSHB qere/ketiv loaders, plus private permitted Greek NT/LXX/Hebrew/Syriac JSON/JSONL/TEI imports. No new corpus or scholarly reconstruction is introduced. Physical Safari/Edge script-font and interaction review remains open.

See [formats, sources and saved-library guide](apparatus-guide.html).

## Retained Syriac scope


Full combined browser verification passed in [Actions 40855411166](https://github.com/Kimble-365/-parallel-bible-reader/actions/runs/40855411166) at preview commit a595018e7a45195748ced4dc16434a2d0b349273. Existing 1.21 texts, notes, plans, imports, pages and study resources are retained with the same device storage keys.

Study → Saved vocabulary & backups opens a searchable list of saved Hebrew/Greek words. Search original spelling, transliteration, gloss, word code or reference; remove individual words or start saved-word flashcards. The same screen remains available from empty practice and from Word study.

Export vocabulary as attributed UTF-8 JSON for backup/restore, or UTF-8 CSV with a BOM for spreadsheet use. CSV quotes delimiters/newlines and prefixes potential spreadsheet formula cells. Use JSON, not CSV, to restore. A backup file is read on this device; nothing is uploaded.

Import shows added/duplicate/final counts before saving. Confirm explicitly to merge; existing words are preserved, and repeated original/code/gloss combinations are skipped. If the stored list changes after preview, preview again. Malformed/oversized files, unsupported versions, invalid fields, full lists (500 words / 1.8 MB compact storage) and storage failures are reported without replacing saved data. Imported personal backup content is not independently verified against the source corpus. This is a vocabulary backup, not a backup of notes or all offline Bible/study packs.

Word study now has Previous verse / Next verse buttons that follow the pinned source book's numeric verse order, crossing chapter boundaries within that book. Buttons stop at the source book edges. Moving clears the in-verse filter and loads the next source verse; missing offline packs show an error rather than displaying the previous verse's words. Source numbering may differ from Text 1, and these controls do not change the reading translation/reference. No automatic next-book or mass source download is introduced.

The 1.21 library still has 60 entries and eight in-app sources; the public Bible catalog remains 62 editions. No new corpus or publisher-protected content is silently installed. Full NET notes/modern commentary texts remain provider-hosted. Hebrew/Greek source credits and CC BY 4.0 terms are retained in source readers and word backups. Physical iPhone/Safari animation quality and full linguistic review remain open.

## Related English texts — 31 October 2026

Added OET Literal/Readers drafts, POB canonical AI-assisted draft and the 44-book OEB US published release. Catalog now contains 66 editions. [Coverage, provenance and permission limits](related-projects.md). Use OET’s pair together. Existing text IDs, storage keys and earlier releases are retained.

## Current baseline

This release extends the published 1.24 reader and preserves its 80 BHH/NTGL/LXXL editions and textual-apparatus features. Four Syriac additions bring the selectable catalog to 84. Number 1.25 avoids replacing the independently published BHH 1.23 release. Existing large packs remain referenced from their original release paths.

## Publication evidence

Merged PR: https://github.com/Kimble-365/-parallel-bible-reader/pull/1. Exact-head preview checks: Syriac/apparatus/BHH/browser suite [41358011540](https://github.com/Kimble-365/-parallel-bible-reader/actions/runs/41358011540) and full historical suite [41358011441](https://github.com/Kimble-365/-parallel-bible-reader/actions/runs/41358011441), both successful. Main publication additionally checks Pages delivery, public file hashes and real live Syriac reading/lexical lookup. Source and scholarly limitations above remain in force.
