# MASTER RESEARCH PROMPT — Whole-WLC Hebrew Lexical and Textual-Critical Corpus

**Version:** 3.0  
**Prompt language:** English  
**Research and reader interface language:** English  
**Source corpus:** Westminster Leningrad Codex (WLC), all canonical Hebrew Bible books, chapters, verses and tokens  
**Target repository:** `Kimble-365/-parallel-bible-reader`  
**Goal:** Build a verifiable, book-sharded SQLite lexical research corpus, packed delivery format, browser-compatible reader, and per-Hebrew-word lookup integrated with the existing WLC Bible edition.

## RESEARCH INPUT — AUTOMATIC COMPLETE-CORPUS MODE

Do **not** request a single Hebrew lemma or verse from the operator. Enumerate the entire WLC Hebrew Bible in its published source order. For **every book → chapter → verse → Hebrew/Aramaic word token**, perform the detailed lexical and textual-critical research specified below. Create **one SQLite database per biblical book**, preserving each token's identity and its link to shared lemma and sense records. Never treat Hebrew spelling alone as a unique lexical identity; resolve homographs, morphology, clitics, ketiv/qere, and Hebrew versus Biblical Aramaic.

Process books incrementally with resumable checkpoints, explicit completeness status, and source verification. Full scholarly research may be unavailable for some tokens; store an honest `pending`/`unverified` state rather than invent results.

**Requested deliverables:**
1. A source-preserving WLC import and token identification pipeline.
2. Per-book `.sqlite` databases covering **every** word occurrence.
3. A documented deterministic `.wlexpack` format plus manifest, integrity hashes, indexes, and pack/unpack tools.
4. A reusable JavaScript/TypeScript **Lexical Pack Reader** capable of reading the packed format in browser and offline contexts.
5. A WLC-specific click/tap action **“Study this Hebrew word”** integrated with the existing word-study interface, opening contextual research with lemma, meaning, Qumran and ancient version evidence, translations, and sources.
6. Automated import, integrity, size, compression, performance, navigation, text-accuracy, and UI regression tests.
7. Per-book completion manifests and research audit reports.

## 1. REPOSITORY FIRST

Inspect the current architecture and newest maintained release of `Kimble-365/-parallel-bible-reader` before coding. Reuse existing book IDs, WLC edition IDs, versification, source apparatus, word study, study packs, offline storage, and licensing records. Do not overwrite or fork features without a documented compatibility reason. Target the maintained release path and its build pipeline; do not edit archived releases as the source of truth.

Implement on a feature branch with reviewable commits and a pull request. Preserve existing Bible functionality and all supported editions.

## 2. WLC INGESTION AND CANONICAL TOKEN IDENTITY

Record the precise WLC edition/source URL, revision, license, provenance, SHA-256 hash and import timestamp. Preserve the exact Unicode text including consonants, niqqud, cantillation, maqaf, punctuation, ketiv/qere, book/chapter/verse numbering and exceptional verse segmentation.

For each word, generate a deterministic occurrence ID based on `source_version + book + chapter + verse_key + token_position + subtoken_position`; retain source token offsets and logical displayed word boundaries. Support one-to-many relationships between displayed words and morphological segments. Treat ketiv/qere as aligned separate attestations, never silently replace one with the other. Store Biblical Aramaic language tagging and perform appropriate Aramaic research where required.

Verify full round-trip reconstruction of each verse against its WLC input; report every difference. Keep cross-versification mappings explicit and provenance-backed.

## 3. LEXICAL RESEARCH FOR EVERY WORD

For each lemma and its individual occurrence, research:

- Consonantal lemma, vocalized form, transliteration, root (where defensible), part of speech, inflection, morphology, homographs, affixes and clitics.
- Full semantic range, primary/secondary senses, polysemy versus homonymy, syntactic and literary context, collocations, parallelism, historical and theological nuances.
- Exact contextual sense of **this specific occurrence**, with competing interpretations and evidence-based confidence.
- Lemma-wide concordance and sense counts across all WLC books (using a separate shared index generated from book shards).
- Relevant comparative Semitic data, avoiding the etymological/root fallacy.

Use accessible academically established lexica such as BDB, HALOT, DCH, TDOT and other published scholarship; identify inaccessible sources and do not pretend to have read them.

## 4. TEXTUAL CRITICISM — PASSAGE-LEVEL EVIDENCE

For every occurrence, identify relevant evidence from:

- Masoretic witnesses including WLC, Aleppo where preserved, Masoretic notes and accessible BHS/BHQ apparatus.
- Dead Sea Scrolls and Judean Desert biblical manuscripts (DJD, DSS electronic collections and scholarly editions): manuscript identifier, fragment, column/line, actual surviving letters, orthographic vs substantive variation, reconstruction and damage.
- Samaritan Pentateuch for Pentateuch passages.
- Septuagint/Old Greek using critical editions (Göttingen where available, Rahlfs–Hanhart as appropriate); record Greek lemma/form and distinguish translation technique from putative alternative Hebrew Vorlage.
- Targums, Peshitta, Vulgate, Vetus Latina, Hexaplaric witnesses (Aquila, Symmachus, Theodotion), Ben Sira, and other relevant ancient evidence.

Model manuscript claims with an explicit status: `directly_attested`, `partial`, `editorially_reconstructed`, `not_preserved`, `not_checked`; and an evidence grade `high`, `moderate`, `low`, or `speculative`. Record the concrete manuscript/source reference. Do not invent Qumran readings. Store manuscript variants separately from ancient translation renderings and conjectural emendations.

## 5. ENGLISH AND MAJOR EUROPEAN TRANSLATIONS

Compare source-verified renderings and notes, where lawful and available:

- **English:** KJV, ASV, NASB 1995, ESV, NRSVue, NIV, NET, NKJV, WEB, JPS 1917, NJPS.
- **German:** Lutherbibel, Elberfelder, Einheitsübersetzung, Zürcher.
- **French:** Louis Segond, Nouvelle Bible Segond, Bible de Jérusalem, TOB.
- **Spanish:** Reina-Valera, Biblia de Jerusalén, NVI.
- **Italian:** Diodati, Nuova Riveduta, CEI.
- **Dutch:** Statenvertaling, NBV21.
- **Portuguese:** Almeida, Nova Almeida Atualizada, Bíblia de Jerusalém.
- **Additional significant European traditions:** Swedish, Norwegian, Danish, Polish, Czech, modern Greek, Russian and Ukrainian as relevant.

Every translation record needs exact edition/year, language, verse mapping, lexical equivalent or short justified phrase, source/license and alignment confidence. Store analysis of literal, contextual, idiomatic, interpretive, and text-critically motivated translation decisions. Never equate agreement among historically dependent translations with independent evidence. Do not include Finnish translations.

Respect licenses: do not bulk-ingest or redistribute copyrighted texts or proprietary apparatus without rights. Store metadata, short legally usable equivalents where appropriate, and external references otherwise.

## 6. DATABASE SCHEMA

Use SQLite with UTF-8 and a versioned schema migration strategy. Suggested normalized entities:

`metadata`, `books`, `verses`, `tokens`, `token_segments`, `lemmas`, `lemma_senses`, `occurrence_senses`, `morphology`, `manuscripts`, `witness_readings`, `variants`, `ancient_equivalents`, `translation_editions`, `translation_equivalents`, `sources`, `claims`, `verification_events`, `research_progress`.

Each book database must be independently readable. A separate derived cross-book lemma index may deduplicate shared data but must never be required to resolve an occurrence in its own book. Include foreign keys, constraints, lookup indexes, FTS5 only if beneficial, and migration tests.

Separate **source facts**, **scholarly interpretations**, and **machine-generated suggestions**. Each substantive claim must link to a source and verification state. Unknown data must be NULL or explicitly marked pending, not fabricated.

## 7. PACKED FORMAT AND READER

Define `.wlexpack` as a **versioned manifest + compressed SQLite payload** per book. First implementation may use deterministic ZIP with DEFLATE and a JSON manifest; assess Brotli/Zstandard based on cross-platform compatibility, browser availability and measured compression. Document the exact format, byte layout, schema/version compatibility, canonical book code, source SHA-256, SQLite SHA-256, packed SHA-256, packed/unpacked lengths, allowed compression codecs, data license, build fingerprint and content status.

Important: store the manifest externally as `manifest.json` for pack discovery; embedded manifest cannot include a self-referential hash. Verify payload hashes before opening. Provide decompression and read-only SQLite through a licensed browser WASM SQLite engine or an existing compatible repository reader, loaded on demand. Avoid downloading all books: fetch only the selected book pack, cache subject to available offline storage, and cap decompressed memory. Handle corrupt packs and migrations gracefully.

Provide CLI: `import-wlc`, `build-book`, `pack-book`, `verify-pack`, `audit-corpus`. Make commands deterministic and restartable.

## 8. WLC READER INTEGRATION

Within the existing WLC Bible version only:

1. Render exact Hebrew source text with word click/tap targets without changing underlying text, diacritics or directionality.
2. On click, show a contextual action **Study this Hebrew word** (keyboard accessible and usable on touch screens).
3. Resolve the clicked occurrence via a stable token mapping, not visual position guessed by splitting whitespace.
4. Lazy-load the relevant book's lexical pack using the shared Lexical Pack Reader.
5. Show current word, transliteration, lemma, morphology, contextual sense, alternatives, occurrence concordance, Qumran variants, LXX and other ancient witnesses, English and European translation equivalents, source references and evidence confidence.
6. Provide tabs/sections, links to other occurrences, previous/next occurrence navigation, copyable citations, and visible **pending research** status where material is not verified.
7. Allow viewing verified base lexical data when a scholarly layer remains incomplete, and never misrepresent a generic dictionary gloss as a validated contextual sense.
8. Preserve existing offline mode, accessibility, RTL behavior, selection/copying, reading navigation, notes and apparatus interactions.

## 9. EXECUTION PLAN AND GATES

- **Phase 0:** Audit repo architecture, WLC source/license, existing study/SQLite pack paths; write compatibility plan.
- **Phase 1:** Deliver schema, import pipeline, deterministic token IDs, one-book SQLite prototype (Genesis), exact text round-trip and tests.
- **Phase 2:** Deliver packing tools, manifest, integrity verification, browser pack reader, offline on-demand caching.
- **Phase 3:** Integrate WLC word click → study action using the existing study UI; verify real token identity.
- **Phase 4:** Scale raw WLC token coverage to all books; check verse and token completeness against source.
- **Phase 5:** Enrich lemma/occurrence records using licensed, verified sources and ancient witnesses; continue per-book with checkpointed progress and claim-level audits.
- **Phase 6:** Complete English/European comparison, quality audit, compression/performance optimization and release documentation.

**Never call Phase 4 token coverage “complete lexical research.”** Publish independent counters for `ingested`, `morphologically_analyzed`, `semantically_reviewed`, `manuscript_checked`, `translations_checked`, and `fully_verified`.

## 10. VALIDATION / ACCEPTANCE CRITERIA

- Every WLC source book, chapter, verse and token is accounted for (including exceptional verse labels and Aramaic passages).
- Unicode WLC reconstruction is byte/normalization-equivalent to the declared source under an explicitly documented comparison rule.
- Book databases pass SQLite `integrity_check`, `foreign_key_check`, migration checks and representative query tests.
- Packed book files round-trip to identical SQLite payload hashes.
- WLC word click selects the intended token in Genesis, Psalms, Isaiah and an Aramaic passage; keyboard/touch/RTL tested.
- Broken packs/network failures show non-destructive, actionable UI messages.
- No invented manuscript readings, unlicensed bulk translations, fabricated footnotes, or unverified claims marked verified.
- UI regression tests confirm existing reader editions, navigation, study tools and offline functionality remain intact.
- Per-book manifest clearly states coverage and evidence gaps.

## 11. REPORTING AND OPERATING RULES

Work book by book, chapter by chapter, verse by verse; deduplicate lemma research and reuse source-verified scholarship, but review each occurrence context independently. Preserve logs, checkpoints and research provenance. Report completed artifacts and test results, not merely plans. If access to a protected scholarly edition is missing, mark the gap and continue independent work. Use small, reviewable commits and never push generated multi-gigabyte databases into Git history by default; use release assets or an established repository artifact channel.

**Begin with a repository and WLC corpus audit, followed by a functioning Genesis prototype with packed SQLite and clickable Hebrew token lookup. Then expand to the whole WLC in measurable stages.**
