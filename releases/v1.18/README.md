# Reader 1.18 — Nordic texts, private imports and reading aids

Numbered release promoted after browser verification. Builds on 1.17's history, daily plan, presentation and combined Contents menu, while retaining 1.16's compact verses and clean copying.

## Texts

62 public editions. Adds Swedish Bibeln 1917 (66 books; 31,069 units), Norwegian Bokmål 1930 (66; 31,101), Norwegian Nynorsk 1921 (66; 31,060), Icelandic Open Living New Testament and Psalms (28; 9,421) and Estonian Open Contemporary New Testament 2022 (27; 7,956). Swedish/Norwegian are Public Domain; the Icelandic/Estonian texts are CC BY-SA 4.0 with original attribution retained. Source archives, exact source Git/SHA256 checksums and derived UTF-8 USFM are in sources/.

The existing five-book Piibel Kõigile edition remains separate. A 27-book Estonian NT does not complete its Old Testament or turn it into a 66-book Bible. A complete matching licensed edition remains pending. Nordic source spellings and published reference positions are retained; source-array positions for Icelandic/Estonian are not asserted to prove equivalent cross-translation verses.

Gzip JSON packs avoid duplicate Latin-script payloads. The loader verifies expanded length, SHA256 and source book identity before showing text. Current Safari/Chrome/Edge gzip support is needed. All selected texts can be saved in the existing offline store. The measured working tree remains below the 1 GB Pages limit; further large additions require separate storage.

## Imports

Settings → Import a text, or Languages → Import your own text. Preview one or more files (32 MB total) and explicitly install a private copy in any of the four text slots. Supported: USFM, USX, container/milestone OSIS, Zefania XML, explicit verse JSON, quoted CSV/TSV, referenced text/VPL, CrossWire IMP and unencrypted e-Sword SQLite Bible tables. e-Sword plain text/HTML and ordinary RTF content is converted to text. SQLite internal and overflow pages and UTF-8/UTF-16BE are covered by real SQLite-created fixtures. Duplicate or unknown references are rejected; numbering is not guessed. Source introductions, headings and front-matter prefaces from supported USFM/USX are retained for Contents.

Provider-specific help covers **CrossWire, Crossway, e-Sword, Bible Hub, Bible.is, YouVersion, STEP Bible, Davar** and other exports. A provider selector is not an authenticated API connection. Crossway numbered single-chapter JSON responses are supported, retaining a supplied copyright notice. CrossWire native/packed/encrypted binaries need mod2imp/mod2osis export. STEP morphology/lexicon tables need a verse-text export, not a guessed reconstruction. Protected provider pages/app packages are not scraped. ZIPs must be extracted first. No file or API key is uploaded or publicly committed. The existing Finnish .ont importer remains available.

## Japanese and guides

Japanese has an additional optional **dictionary reading — experimental** form, covering all 31,099 original source rows. It uses pinned PyKakasi dictionary output, including kanji, and preserves unresolved source characters in brackets. Historical/contextual/proper-name readings may be wrong. It is not a recording transcript or a verified phonetic/spoken version. The original kana-only written conversion remains available. Reading packs are bound to original row hashes; Save selected texts also saves all dictionary reading packs when that form is selected. The GPL build engine is not shipped as browser runtime code; provenance and its license are retained.

Contents collects source material and editorial guides. In addition to English, there are 396 **draft** introductions across Finnish, Swedish, Norwegian Bokmål/Nynorsk, Icelandic and Estonian, with native labels and outlines for nine books. These short editorial summaries are not publisher prefaces or Scripture. Linguistic review is pending. Other language translations remain pending and use an explicitly labeled English fallback; no all-language completion is claimed.

Source/model/parser/checksum tests and actual Chromium XML/import/install/offline/menu tests passed in [GitHub Actions 40627493177](https://github.com/Kimble-365/-parallel-bible-reader/actions/runs/40627493177), commit eabaff33aac466165cb1c46d27d4a41ccdd8ac1a. The suite also passed compact native-reference copying, all 16 text-slot combinations, notes and Office exports, search/index/directory/pronunciation/PWA regressions, and full Japanese/Swedish offline saving with dictionary reading packs. A previous run stopped on an outdated test assumption that Esperanto was in the short popular list; the test now uses Swedish for this release. No app fix was required for that test failure. Physical Safari/Edge testing and linguistic review remain pending. The root is promoted to 1.18; live Pages bytes are checked separately after deployment.
