# DavarQadosh source and license notices

Original reader and pipeline code in this repository is covered by the repository MIT license. This does not relicense third-party data.

## Hebrew / Biblical Aramaic source and morphology

Original work of the Open Scriptures Hebrew Bible available at https://github.com/openscriptures/morphhb — Creative Commons Attribution 4.0 International: https://creativecommons.org/licenses/by/4.0/ . Pinned revision: `3d15126fb1ef74867fc1434be1942e837932691f`. The project describes its underlying Westminster Leningrad Codex text as public domain. This is an OSHB WLC-derived transcription, not a new collation of the Leningrad manuscript. Source slash segmentation is hidden only in the reading projection; exact source XML, notes, source forms, and ketiv/qere alternatives remain in each SQLite shard. Source numbering remains explicit.

## Historical dictionary

Open Scriptures Hebrew Bible Project, https://github.com/openscriptures/HebrewLexicon, revision `21c9add13bc727d3a951361778e97e3ff7afd1ce`, `HebrewStrong.xml`. Digital files: CC BY 4.0. The repository describes the historical Strong and BDB dictionary texts as public domain. Only the Strong file is imported in this increment. General dictionary headwords, transliterations and explanations are not validated contextual senses. A numeric Strong link is broader than some OSHB augmented homograph identities; those identities remain separate.

## Parallel texts and inherited research

The build reuses existing reader 1.27 assets at revision `9554e05a170e2a44e3cfa7156b6d3ccbd421c197`. Full original edition metadata, attributions and licenses accompany the artifact as `COMPARISON-LICENSES.md` and in its discovery manifest. Derived comparison sidecars preserve selected source strings and their source labels; they do not establish cross-versification equivalence.

- World English Bible, eBible.org: public domain; World English Bible is a trademark of eBible.org. Existing source text is unchanged.
- Swete Greek: Open Greek and Latin / First1KGreek and nathans/lxx-swete, CC BY-SA 4.0. Greek comparison extracts/adaptations retain CC BY-SA 4.0. Known digital-source and versification limitations remain.
- Miqra according to the Masorah: Hebrew Wikisource, Seth (Avi) Kadish, Erel Segal-Halevi and Benjamin Denckla, CC BY-SA 4.0. Existing BHH reading projection is reused with its original limitations; it is not a new manuscript witness.
- Public LXXL source-report register: reused from reader 1.27 with source URLs, inherited evidence classes, reconstruction/damage details and review states intact. An edition report is not a new manuscript-image collation. Underlying sources retain their own rights. No new scholarly approval is inferred.

Private BHH/LXXL research imports are optional and stay in separately built private artifacts. Do not mix a private research build into the public artifact without reviewing the individual source terms. No Finnish translations, proprietary modern lexica or restricted apparatus texts are added to this research corpus.

## Reused libraries

`vendor/sqlite-reader.js` is copied byte-for-byte from the maintained reader 1.27 (MIT repository code). It reads ordinary SQLite tables without executing SQL and is reused instead of introducing a second SQLite engine. `vendor/pako_inflate.min.js` is the existing bundled Pako inflater; its MIT license is in `vendor/PAKO-LICENSE.txt`. No CDN or remote code execution is required.
