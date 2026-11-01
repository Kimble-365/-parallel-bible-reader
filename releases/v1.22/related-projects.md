# Related English comparison texts

OET Literal and Readers (66 books each) are drafts intended to be used together. POB (66 canonical books) is AI-assisted; its model reviews are not independent expert approval. OEB contains only 44 published release books, with an incomplete OT. Nonempty verse counts differ between sources and do not prove aligned versification or completeness. Missing/blank verses remain absent.

The loader downloads only the requested book, supports existing offline saving, and verifies decompressed sizes and SHA-256. Source cleaned USFM or POB translation records (with notes) are retained once, compressed, under sources/related/. POB’s third-party Hebrew/Greek source texts and lexicon quotations are excluded. Per-file identities, rights and counts: [import report](sources/related-import.json); [licenses](LICENSES.md).

OET: https://github.com/Freely-Given-org/OpenEnglishTranslation--OET
POB: https://github.com/zackseyun/peoples-open-bible
OEB: https://github.com/openenglishbible/Open-English-Bible
Greek Room: https://github.com/BibleNLP/greek-room (checking tools, no Bible text)
Open Bibles: https://github.com/seven1m/open-bibles (existing WEB reused)
Swarm: https://github.com/ryderwishart/swarm (English paraphrase; conflicting README/license data notices, import pending clarification)
TWV: https://github.com/Wayback-Project/thewaytranslations (full-text/derivative redistribution permission required)
AI Scribes: https://github.com/aiScribesProject/ai-bible-translation (no verified content license)

No absent permission is inferred from public GitHub visibility. No source draft is labelled expert-approved. UI display conversion preserves inline-word spacing, excludes notes and section headings from verses, and retains note data in compressed sources.

Measured added text/source bytes: 14,679,745 (about 14.0 MiB), with 66 requested-book gzip packs. Reproduction: run `python3 tools/acquire_related_english.py` (network, PyYAML), then `python3 tools/import_related_english.py`. Acquisition invokes no model or paid generation service. Empty source verses are excluded; verse bridges retain their source endpoint.
