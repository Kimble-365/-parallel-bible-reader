# Architecture and language acquisition assessment

Research date: 2026-10-23. This is a feasibility assessment and acquisition queue, not a list of newly installed translations. Main instructions: [GOAL.md](../../GOAL.md).

## Findings and decisions

| Topic | Finding | Development decision |
| --- | --- | --- |
| USFM | UBS-origin USFM documentation defines Scripture structure; its encoding marker supports UTF-8. | Retain structured UTF-8 USFM, including Indian scripts, Hebrew, Greek and Urdu. Font shaping/RTL handling remain separate browser requirements. |
| SQLite | FTS5 provides indexed full-text search; SQLite has an official browser WASM distribution. | Reuse the existing authoring SQLite database. Benchmark browser WASM against static indexed shards before replacing delivery. |
| Universal transliteration | Aksharamukha documents Urdu, Devanagari, Hebrew and many other script mappings and named romanization schemes. | Reuse script engines behind a language-aware adapter interface; advertised script coverage is not proof of accurate Urdu vowels or speech. |
| Pronunciation | Letters, phonemes, surface sounds and colloquial wording are different representations. | Keep orthographic transliteration, reviewed pronunciation and colloquial translations distinct. Unsupported pronunciation stays unavailable. |
| Audio | Bible Brain is the provider's API offering; public catalog/listening access is distinct from redistribution rights. | Track exact edition and coverage; keep external links until access and rights are established. |
| UBS classification | USFM provides book structure identifiers; these are not a language-family classification. | Store verified UBS/provider IDs separately from ISO language codes and a separately sourced genealogical classification. |
| Existing source system | Production has 27 editions and static per-book payloads; authoring already uses SQLite. | Extend a working pipeline rather than replacing it solely to adopt a database. |

## Why one universal pronunciation converter will not suffice

A shared interface is feasible. A single language-independent rule set promising correct pronunciation is not. Urdu vowels omitted in Perso-Arabic writing require lexical/contextual information. Hindi schwa deletion differs from a direct character map. Tamil graphemes may realize different sounds by context. Greek and Hebrew reading traditions differ, and Chinese characters can have multiple contextual readings. Dialects add another axis.

Start with deterministic written conversion and reviewed samples. For spoken forms, require a specified variety, scheme, dictionary/model version, uncertainty policy and independent speaker review. A system may produce IPA characters without producing accurate phonetic transcription. Maintain word/span alignment, and never replace canonical text with a guessed pronunciation.

## Suggested normalized data model

Keep these entities separate, with migration scripts and foreign keys:

- `languages`: stable ID, ISO 639-3, English/native names, aliases and source-supported identity.
- `language_varieties`: language, dialect/variety, BCP 47, family mapping and geographic associations.
- `classifications`: provider/source, identifier, parent mapping, version and retrieval date; allow multiple sourced views.
- `editions`: language variety, script, title, canon, source version, rights, direction and versification.
- `source_documents`: edition/book, original USFM, checksum, import timestamp and validation report.
- `verse_units`: edition/book/source reference, bridge/range, structured text/span references; preserve multiple source units where necessary.
- `derived_forms`: source unit/checksum, orthographic or pronunciation type, target script/scheme, dialect/tradition, adapter version, text, alignment and review status.
- `audio_resources`: source edition/variety, provider ID, human/synthetic identity, coverage, URLs, rights and timings.
- `geographies` plus join tables: continent, country, state/territory; multiple regions per language.
- Search indexes partitioned by edition, form and tokenizer policy, with a source manifest and deterministic invalidation.

Reading slots refer to edition/form IDs; they do not define edition identity. Browser bookmarks and reading state remain local user data, separate from distributed corpus databases. Do not put every user's notes into the source database or require accounts.

## Acquisition queue by region

Every row below is a **candidate research scope**. Edition IDs, source USFM, present coverage, rights and audio must be checked individually before import. These examples are not a claim of a usable Bible or recording for every language. Scripture Earth and Bible Brain are discovery sources; provider catalog presence alone is not an import license.

| Region/filter | Candidate language groups and examples | First checks |
| --- | --- | --- |
| India / South Asia | Existing Indian languages; Awadhi, Bhojpuri, Braj, Maithili, Magahi, Kashmiri, Garhwali, Kumaoni, Ladakhi, Rajasthani varieties; Sanskrit, Assamese, Santali, Konkani, Sindhi | Distinct varieties/scripts; missing books; state associations; source-to-audio edition match. |
| Europe: Germanic | English, German, Dutch, Swedish, Danish, Norwegian varieties, Icelandic, Faroese, Frisian varieties | Open editions versus modern copyrighted editions; independent language/variety IDs. |
| Europe: Romance | French, Spanish, Portuguese, Italian, Romanian, Catalan, Galician, Occitan, Romansh, Sardinian | Rights and regional varieties; avoid treating every regional label as a separate licensed edition. |
| Europe: Slavic/Baltic | Russian, Ukrainian, Belarusian, Polish, Czech, Slovak, Slovenian, Croatian, Serbian scripts, Bosnian, Bulgarian, Macedonian; Lithuanian, Latvian | Cyrillic/Latin variants, edition equivalence, diacritics and canon. |
| Europe: other families/branches | Irish, Scottish Gaelic, Welsh, Breton; Greek, Albanian, Armenian; Basque, Maltese, Turkish; geographically relevant Caucasian families | Classify separate branches/families correctly; historical versus modern Greek. |
| Uralic: Finnic | Finnish, Estonian, Karelian, Veps, Livonian, Votic, Ingrian; investigate Võro and Seto source classifications | Actual translation coverage; language/variety status; rights; self-names and alternative names. |
| Uralic: Sámi | Northern, Inari, Skolt, Southern, Lule and other source-supported Sámi languages | Separate identifiers and resources; do not use a single undifferentiated Sámi record. |
| Uralic: other branches | Erzya, Moksha, Meadow/Hill Mari, Komi varieties, Udmurt, Hungarian, Khanty, Mansi, Nenets and other Samoyedic candidates | Branch-specific classification, dialect IDs and minority-language coverage. |
| Russia | Russian plus Uralic, Turkic (Tatar, Bashkir, Chuvash, Sakha), Mongolic (Buryat, Kalmyk), Tungusic (Evenki) and other regional languages | Cross-border geography, scripts, family identity, text/audio coverage and rights. |
| Africa | Swahili, Hausa, Yoruba, Igbo, Amharic, Oromo, Somali, Zulu, Xhosa, Shona, Kinyarwanda, Malagasy, African Arabic varieties | Diverse unrelated families; Ethiopic/Latin/Arabic scripts; dialect and audio identities. |
| Asia outside India/China | Arabic varieties, Persian, Dari, Pashto, Bengali across borders, Nepali, Sinhala, Thai, Vietnamese, Khmer, Burmese, Indonesian, Malay, Tagalog, Korean, Japanese, Mongolian | Multiple scripts, contextual pronunciation, segmentation and countries sharing languages. |
| China | Mandarin varieties, Cantonese/Yue, Min varieties, Hakka; Tibetan, Uyghur, Mongolian and distinct minority languages | Language versus writing system; Simplified/Traditional Chinese are script conventions, not different languages; tokenizer/reading tradition. |
| Australasia / Oceania | Aboriginal Australian languages, Torres Strait languages, Māori, Tok Pisin, Fijian, Samoan, Tongan, other Pacific and Papua New Guinean languages | Specific community/language identifiers, partial translations, local permissions and offline size. |
| South America | Spanish, Portuguese, Quechuan varieties, Aymara, Guarani varieties, Mapudungun and other Indigenous languages | Specific varieties, orthography, coverage, community/source rights and recordings. |
| North America | English/French/Spanish; Inuktitut varieties/scripts, Greenlandic, Cree varieties, Ojibwe, Navajo, Cherokee and other Indigenous languages | Latin/syllabic variants, dialect identity, community/source rights, partial canon. |
| Biblical original languages | Biblical Hebrew OT; Koine Greek NT | Exact edition, license, text tradition, pointing/diacritics, versification and named pronunciation traditions. |

## Source checks and limitations

Successfully opened during this assessment:

- [USFM 3 documentation](https://ubsicap.github.io/usfm/) and [identification/encoding markers](https://ubsicap.github.io/usfm/identification/index.html).
- [SQLite FTS5](https://www.sqlite.org/fts5.html) and [official SQLite WASM documentation](https://www.sqlite.org/wasm/doc/trunk/index.md).
- [Scripture Earth](https://www.scriptureearth.org/).
- [Bible Brain](https://www.faithcomesbyhearing.com/audio-bible-resources/bible-brain).
- [Aksharamukha Python repository](https://github.com/virtualvinodh/aksharamukha-python) and [README](https://raw.githubusercontent.com/virtualvinodh/aksharamukha-python/main/README.md), which advertises Urdu, Devanagari and Hebrew support. This is an engine capability claim, not a validated pronunciation result.
- [indic-transliteration Python repository](https://github.com/indic-transliteration/indic_transliteration_py).

The eBible index and UBS homepage returned HTTP 403 in this environment. Two attempted raw unfoldingWord license URLs returned 404; those addresses do not verify Hebrew/Greek edition rights. These failures are not evidence that the texts do not exist. Discover current official edition pages and license files before selecting/importing them. The initial `docs.usfm.bible/usfm/3.0/` URL returned 404; the UBS ICAP documentation above was reachable.

A global language/edition/audio inventory has **not** been verified in this assessment. No new text, phonetic corpus or audio has been imported by writing this plan. The accompanying source-check JSON records successful and failed requests; revisit live catalogs during each acquisition release.
