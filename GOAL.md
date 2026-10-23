# GOAL — Multilingual Parallel Bible Reader

Project instruction and acceptance contract. Updated 2026-10-23.

## Mission

Develop an approachable, English-interface Bible reader that helps people in India and worldwide read and hear Scripture in their own language and discover other translations. It must work without a ChatGPT account, on Safari, Chrome and Edge, on phones and computers. Keep ordinary reading simple; put cataloguing and technical details behind optional controls.

Treat this document as the continuing development brief. Complete work in reviewable, tested, numbered increments. Preserve source text and report what is installed, experimental, unavailable, or still under investigation accurately. Do not describe this roadmap as functionality already delivered.

## Baseline and release policy

The production application is the repository root: https://kimble-365.github.io/-parallel-bible-reader/ . The current catalog contains 27 text editions, including separate Arabic-script and Devanagari Urdu editions. The current reader supports three displayed editions, mechanical Latin forms and independent external audio links. A SQLite source database already exists in the authoring workspace; the published reader uses static per-book JavaScript data.

The first separate development release is **1.1**, the John 3 Hindi/SAB pilot under `sab-hindi-pilot/v1.1/`. It was built and locally tested; do not claim a public deployment until GitHub Pages delivery has been checked. The next development release starts at **1.2**, then 1.3, 1.4, etc. Record a version in the UI, metadata, source notes, changelog and ZIP filename. Tool versions, such as SAB 14.7, are different from application versions.

Keep each release in its own directory and retain its URL. Isolate experiments from production until validated. Preserve the current production reader and offline ZIP. Publish only reader material; exclude Biblical Encyclopedia material. Use the existing GitHub repository. Maintain a version history, deployment status and rollback path. Do not silently replace an earlier numbered release with a substantially different implementation.

## Retain earlier requirements

- Original text, Latin transliteration and combined reading; Finnish KR33/38 and English WEB comparisons, subject to documented distribution rights.
- All existing Indian editions, book/chapter navigation, edition-aware sharing, remembered location, bookmarks, text size, quiet reading mode, short book guides and the seven-reading beginner path.
- Papyrus Yellow, Blue and Brown, each with Light and Dark options.
- Account-free public access and an extract-and-open offline ZIP where technically feasible. Preserve file-based operation with a static fallback if a richer browser backend requires HTTPS.
- Bible.is listening choices and source/edition information. Hindi Revised Version availability remains an edition-specific research task; do not silently substitute Hindi IRV or infer an exact recording match from language alone.
- USFM source export and a documented e-Sword import/export path where the target module format and text rights allow it. Do not label generic text as an installable e-Sword module.
- Scripture App Builder remains a companion experiment. Compare actual native/web capabilities with the existing reader; SAB's current browser template does not implement parallel text layouts. The custom pilot preview must be identified separately.

## Four independent reading slots

Implement numbered slots 1–4 with an edition selector and an explicit `None` choice in **every** slot. Slot order is stable: disabling slot 2 must not rename or replace slot 3. No automatic filling after a user clears a slot.

Allow any subset, including all slots empty. If all are empty, render no Scripture panes or stale results, stop text-driven navigation/search work and show a brief `Choose a translation to start` message. The catalog remains reachable. If slot 1 is empty, an enabled slot can provide passage availability without being moved into slot 1. Keep the passage reference separately from the chosen editions.

Acceptance examples: `[A,B,C,D]` shows four; `[A,None,C,None]` shows slots 1 and 3; `[None,None,C,None]` shows only slot 3; `[None,None,None,None]` shows no passage. Never assume an always-present primary edition in rendering, bookmarking, search, sharing or restoring preferences.

A cleared slot contributes no hidden column, search result, download or audio match. Distinguish a disabled slot from an enabled edition that lacks a verse or book. Keep verse ranges, omissions, differing numbering and canon differences explicit; never invent alignment by row position. Shared URLs and saved state must round-trip all four slots, their display forms and intentional empty choices. Migrate existing three-selector preferences without losing data.

## Text forms and universal transliteration architecture

Keep three concepts separate:

1. **Original**: the edition's actual source script and exact wording.
2. **Text transliteration**: a named, versioned mapping of written forms to another script. Explain ambiguity and information loss. Transliteration is not translation.
3. **Pronunciation / spoken form**: a language-, dialect- and pronunciation-tradition-specific phonemic or phonetic rendering. Offer IPA and, where validated, a practical readable Latin representation. Identify whether it is phonemic `/.../` or phonetic `[...]` and document the convention.

Formal versus colloquial vocabulary and grammar are not merely pronunciation differences. A colloquial rewording is a separately identified translation/adaptation with its own editorial review and rights, never a silently generated Scripture form.

Each edition exposes only forms supported for that specific language/script/variant. Allow written transliteration and/or pronunciation independently, beside the original. Preserve an optional unreviewed experimental mode with a clear label; do not default readers into speculative pronunciations.

Build a common conversion interface with language-specific adapters, rather than promising one accurate character map for all languages. Adapters declare source language/script, target script, scheme, dialect, vowel policy, normalization, reversibility limits, engine/rule version and quality status. Cache conversions by source checksum and adapter configuration. Transform text nodes only: never USFM markers, verse identifiers, references, metadata or unrelated-language quotations. Maintain mapping back to source spans for search highlighting.

Evaluate ICU, Aksharamukha and indic-transliteration for written-script conversion, with pinned versions and compatible distribution licenses. Evaluate pronunciation dictionaries, language-specific grapheme-to-phoneme tools, validated lexicons and recorded native speech for pronunciation. A TTS phoneme stream or automatic speech recognition transcript is an estimate, not proof of a correct spoken form. Assess language support and licenses separately for each engine/model/dataset. Do not make online AI APIs a requirement for ordinary reading.

### Urdu priority

Support the **Perso-Arabic Urdu script** (`Arab`, RTL) and **Devanagari Urdu** (`Deva`, LTR), with explicit choices to:

- Keep each edition's original script.
- Convert the *same edition* to the other script, where an adapter exists.
- Produce orthographic Latin transliteration from either script, identifying the source.
- Offer a pronunciation form only when language-specific reconstruction/review supports it.

Do not describe an already Arabic-script Urdu text as a translation into the Arabic language. Do not claim that the existing two Urdu editions are identical editions in different scripts. Record edition provenance and compare only genuinely paired source material when assessing conversion quality.

Perso-Arabic Urdu often omits short vowels. Arabic-to-Devanagari, Latin and IPA output cannot reliably recover them from letters alone. Preserve uncertainty and use a reviewed dictionary/context layer when available. Devanagari spelling is also not a complete phonetic transcript. Test Urdu-specific consonants, aspirates, retroflexes, hamza, nasalization, izafat, vowel signs, punctuation, Arabic/Persian letter variants and mixed RTL/LTR text. Use Unicode bidi isolation, not manual string reversal.

### Hebrew and Greek

Investigate and import a licensed Biblical Hebrew Old Testament and Koine Greek New Testament. Preserve source orthography, vowels/diacritics, Hebrew cantillation where provided and Greek accents/breathings. Record editorial text tradition and versification. Do not label a modern-language translation as an original-language edition.

Provide named orthographic Latin schemes. A spoken option requires an explicit tradition, such as Modern Israeli versus a specified reconstructed Hebrew tradition, or a specified historical Koine reconstruction versus Modern Greek reading. Do not present competing reconstructions as a single certain pronunciation. Preserve original pointing/accents independently from simplified search forms.

## Catalog and language discovery

Keep the reading dropdowns compact: a curated **Popular translations** list plus user favorites/recent choices, clearly distinguished from usage statistics. Include a prominent `Browse all translations` action for each slot.

Create a dedicated translation directory (`translations/` as a user-facing route or static directory; catalog metadata may live separately from book payloads). Support combined filters for language family/group, language, dialect/variety, script, country, continent/region and Indian state/territory. A language or dialect may belong to multiple geographic areas. Russia, China and India are country/region filters, not language families; Russia spans Europe and Asia. Preserve self-identification and alternative names without treating disputed language/dialect labels as settled facts.

Search English names, native names, aliases, transliterated names, ISO codes and dialect names. Rank exact language/code matches first, then aliases/prefixes, then optional typo-tolerant results. Provide keyboard access, meaningful screen-reader labels, visible counts, reset filters and a clear empty state. A chosen entry returns to the requested slot, without changing other slots.

Use Bible.is as a reference for discovering languages and recordings, with an independently designed interface that improves aliases, script/dialect distinctions and geography filters. Do not copy its branding or infer catalog coverage from a screenshot.

### Identity, classification and metadata

For every language/edition record store stable internal IDs, native/English names, ISO 639-3 where applicable, BCP 47 language tags, ISO 15924 script code, dialect/variety, text tradition, direction, source, rights, version, canon, coverage and verse system. Represent original-language/ancient codes and macrolanguages carefully; do not force every provider code into a modern ISO code.

Honor the user's request for **United Bible Societies (UBS) classification** by recording actual UBS/DBL identifiers and provider language labels when available, with source and retrieval date. USFM book identifiers are UBS-origin scripture structure identifiers, not a genealogy of languages. Do not invent a universal UBS language-family taxonomy. Keep ISO identifiers, provider IDs and genealogy separate. For language families use an explicitly cited classification source, such as a suitable Glottolog dataset, checking its license and version; flag uncertain mappings. Map providers rather than replacing their native identifiers.

## Global acquisition research

Build an evidence-backed inventory by region before importing. Include Europe, Africa, Asia, Russia, Australasia, China, South America and North America. Regions overlap deliberately; do not double-count an edition. Distinguish translation count from language count and from script/dialect variants.

Prioritize current Indian users and requested languages, then Biblical Hebrew/Greek and European/Uralic coverage, then expand globally. Audit North Indian gaps such as Awadhi, Bhojpuri, Braj, Maithili, Magahi, Kashmiri, Garhwali, Kumaoni, Ladakhi and Rajasthani varieties. Existing availability is not proof that every requested language is installed.

Explicitly cover European Germanic, Romance, Slavic, Celtic, Baltic, Greek, Albanian and Armenian branches of Indo-European; Uralic; Basque; Maltese/Semitic; European Turkic; and Caucasian language families where geographically relevant. Separate classification from residence or official status.

Give Uralic languages a dedicated browsing group and separate subgroups. Investigate Finnish, Estonian, Karelian, Veps, Livonian, Votic, Ingrian, Võro/Seto status and identifiers; individual Sámi languages; Erzya, Moksha, Meadow/Hill Mari, Komi varieties and Udmurt; Hungarian, Khanty and Mansi; and Samoyedic languages such as Nenets. Do not collapse these into Finnish dialects or equate all Uralic languages with the narrower Finnic branch. Include languages only at a source-supported granularity.

For each candidate record: region; language/variety/script; provider edition ID; source URL; checked date; OT/NT/books/chapters; USFM or convertible source; text rights; adaptation rights; audio rights; source-to-audio edition match; timings; download/API requirements; quality; and import status. Status values should distinguish `candidate`, `metadata verified`, `text verified`, `audio link verified`, `download permitted`, `imported` and `unavailable/unknown`. Never convert a candidate list into installed UI choices.

Investigate eBible, Scripture Earth, Bible.is/Bible Brain, Bible societies and other legitimate providers. Human recordings, text, video, timings and phonetic text are separate assets. Availability for listening does not imply download, redistribution or transliteration permission. Include a smaller correctly licensed inventory before pursuing an unsupported claim of global completeness.

## Audio and spoken text

For every edition track language/variety, script-independent audio identity, narrator/source, edition, canon/chapter coverage, streaming/download rights, format and timings. Link to verified listening options when embedding or redistribution is not allowed or credentials are absent. Never expose private Bible Brain credentials in static GitHub Pages assets.

Require an exact text/recording match plus verified timings before synchronized verse highlighting. If audio is another translation, state that clearly. Show NT-only and incomplete coverage before opening a link; never silently redirect an absent chapter as if it were available.

Record whether a spoken transcript or phonetic transcription actually exists. Audio alone is not a ready-made phonetic text. Separate native human recordings, synthesized demonstration speech, automatic transcripts and reviewed pronunciation resources. Allow phonetic reading and listening independently. Provide playback speed and passage links when the source supports them, without fabricated controls for an external player.

## Storage, USFM and search

Use **UTF-8 USFM** as an interoperable source/import/export format. Unicode supports Indian scripts, Urdu, Hebrew and Greek; correct display additionally requires suitable fonts, shaping and bidi handling. Preserve raw source bytes/checksums and full structured content, including notes, headings, poetry, verse bridges and milestones. A lossy plain-verse extraction is not a replacement for archival USFM.

Use **SQLite as the authoring/normalized catalog and text database**, with a repeatable import/export pipeline and FTS5 indexes where available. Reuse/migrate the existing source database rather than rebuilding blindly. Keep original text distinct from derived forms, pronunciation hypotheses and editorial prose. Store versioned transformations with provenance and alignments. SQLite UTF-8 can store these scripts, but database support alone does not ensure good tokenization or rendering.

For published GitHub Pages, benchmark a worker-based SQLite/WASM reader with per-language/edition downloads and caching against the existing per-book static delivery plus precomputed indexes. GitHub Pages cannot run a server-side SQLite service. Do not ship the whole world corpus on startup. Retain a static offline fallback for extracted ZIP use, since WASM, workers, service workers and persistent browser storage have different local-file restrictions. Choose based on measured size, startup time, search latency and supported browsers; record the decision.

Search **every currently visible slot and visible form**, across the union of their available books, with chapter/book/all-books scopes. Index original, orthographic transliteration and validated pronunciation separately; query only enabled views. Do not let the first edition's canon or book list exclude a book present in another visible slot.

Provide Unicode-aware exact search and optional forgiving matching. Preserve originals while maintaining normalized search keys. Handle combining marks, Indic matras/nukta/virama, Urdu/Persian letter variants, optional Hebrew pointing and Greek diacritics under language-specific policies. Do not strip all marks globally. Evaluate segmentation for Chinese, Japanese, Thai and other texts without whitespace; FTS5 unicode61 is not a universal word segmenter. Validate the tokenizer with real queries per language/script.

Each result identifies slot, edition, form and verse, and highlights the source span correctly. Group repeated hits without losing edition identity; cancel stale searches on view changes; paginate large results. Build and version indexes reproducibly; invalidate them when source or adapter changes. With all slots disabled, no hidden-edition search occurs.

## Delivery sequence

1. Finish and verify delivery of pilot **1.1**; retain its independent URL and accurate limitations.
2. **1.2:** four independent optional slots, empty-state behavior, shared/persisted state migration and search over the visible-book union. Measure and fix regressions before catalog expansion.
3. **1.3:** popular/favorites selectors, browse directory, language/variety/script/geography metadata and validated classification mappings.
4. **1.4:** Urdu script adapters and written Latin forms with ambiguity notices, small reviewed fixtures and source provenance. No unsupported pronunciation claims.
5. **1.5:** licensed Hebrew/Greek imports and named transliteration traditions; initial European/Uralic inventory and verified audio links.
6. **1.6:** pronunciation adapter pilot for a language with suitable reviewed resources, dialect selection and a clear unsupported state for other languages.
7. Later numbered releases: validated global imports, search/storage benchmarks, offline caching, optional e-Sword export and further audio synchronization only where permitted.

This sequence is a default implementation plan, not a statement that the features already exist. Adjust boundaries when evidence warrants it, recording the new release scope. Complete each release's actual committed scope before claiming it delivered.

## Acceptance and verification

- Test all 16 slot enable/disable combinations, including slot 1 absent and all absent; assert no stale panes, implicit replacement or hidden-edition searches. Test migration and URL restoration with empty values.
- Test same-script and mixed-script reading at phone/desktop widths, keyboard-only use, Arabic/Hebrew RTL with Latin/numbers, accessible controls and every retained theme.
- Use independently reviewed language fixtures, including Urdu vowel ambiguity and Indian combining sequences. Avoid validating transliteration only by round-tripping through the same engine.
- Test indexed queries against expected verses in every displayed form, including a book absent from slot 1, and removed slots producing no matches. Test verse bridges and differing canon/numbering.
- Validate USFM parsing/export, original text checksums, attribution and rights per asset. Verify book/chapter counts and avoid claiming a full Bible for an NT edition.
- Run appropriate build and browser checks. Test Chromium and, where available, Safari/WebKit and Edge; report actual coverage instead of claiming all three were tested.
- Check account-free HTTPS deployment and extracted offline ZIP independently, including absent internet, blocked storage and failed audio sources. Preserve progress/bookmarks where supported; explain local-only storage.
- Before publishing, verify the exact numbered artifact, source/license manifest, absence of secrets/encyclopedia payload and production rollback path. Verify the live URL after deployment. Report shipped features, remaining limits and links concisely.

## Immediate working instruction

Read this GOAL, repository instructions, current source and the release log. Start with the next incomplete numbered increment. Use available tools to create real, reviewable artifacts; do not stop at suggestions when implementation is requested. Ask only for decisions or credentials truly required, while continuing independent work. Keep the user informed in Finnish and keep the application interface in English. Never invent text, recordings, phonetic certainty, classification mappings, permissions or deployment success.
