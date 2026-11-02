# DavarQadosh compatibility and source discovery audit

Audit date: 2026-11-02. This is a bounded, source-backed discovery pass, not an exhaustive survey of GitHub or a completed scholarly collation.

## Repository placement and maintained reader

Research home: `Kimble-365/TheWay/DavarQadosh/`, initialized on branch `project/davarqadosh` (PR 4). New parallel reader: `Kimble-365/-parallel-bible-reader/davarqadosh/`. Python build tooling is under `tools/davarqadosh/`. The root redirect and README identify reader 1.27 as current at baseline `9554e05a170e2a44e3cfa7156b6d3ccbd421c197`; older versioned assets are reused only through that maintained release's established data references. No archived release is edited. Stable reader book codes and the `hbo-wlc`, `engwebp`, `grc-swete`, `hbo-mam` edition identities are reused.

The branch inventory also includes `feature/wlc-lexical-research-spec`, `preview/bhh-reader-1.23`, Syriac branches, and numbered release/preview branches. Existing BHH/LXXL work is already represented in main. TheWay main inspected at `d208ce9e0b537d4ba6c8bf222af8bad926721399`; its research directories include BHH, LXXL, NTGL and the versional projects SYR, ARC, LAT, COP, ARM and others. The book lists use the existing reader catalogue order; source-local chapter and verse labels remain unchanged.

The standalone entry is a compatibility decision: the new token identity and packed SQLite model can be tested without altering current reader selections, apparatus, notes, interlinear vocabulary, or offline databases. The generated reader links back to the maintained reader with edition and source reference. This increment has its own accessible word action and occurrence mappings. Injecting actions into the existing 1.27 study menu remains a later reviewed integration, rather than silently mapping old whitespace-based displays to new tokens. Existing `ReaderSQLite` and Pako are reused byte-for-byte and credited. A fresh browser regression check is required before publication.

## Reusable materials actually inspected

| Source | Evidence inspected | Adoption in this increment / limitation |
| --- | --- | --- |
| TheWay/BHH | README, reader-integration.json, related-projects.json, third-party notices, 50 alignment records and four variant records | Private Genesis pack imports the records as inherited verse-level drafts. No old ordinal token ID is guessed into a new occurrence mapping. Public BHH source library is linked from the reader. |
| TheWay/LXXL | README, lexical-entry and passage-link specs, eight unit-evidence records | Public reader 1.27 source register is reused with its full evidence distinctions; private source records remain source-labelled. Phrase correspondences do not establish a Hebrew Vorlage. |
| TheWay/SYR | README and data inventory | Historical OCR/catalogue and pending lexical links are discovery leads. They are not imported as verified biblical Syriac evidence. |
| openscriptures/morphhb | Current repository metadata, immutable source checkout, WLC XML and LICENSE.md | All 39 OSHB source books imported; Unicode, notes and alternatives preserved. CC BY 4.0 annotations, underlying WLC described as public domain. Genesis SHA-256 equals the BHH cached source hash, establishing same source ancestry, not an extra witness. |
| openscriptures/HebrewLexicon | readme.md, HebrewStrong.xml, augmented and lexical index samples | Licensed historical dictionary headwords/transliteration/general glosses. Homographs remain separate; no complete contemporary lexicon or contextual semantic review is claimed. |
| STEPBible/STEPBible-Data | Live root directory plus BHH TAHOT source-library registration | Candidate tagged ancient-version/lexical expansion; source alternatives and retroversions require explicit handling. Not imported into occurrence semantics in this increment. |
| ETCBC/dss | Live repository metadata and BHH acquisition/rights reports | Reuse via existing physical-locus/damage-aware library, CC BY-NC 4.0. No reconstructed letters are promoted to direct attestations. New occurrence-specific collation remains pending. |
| DT-UCPH/sp | Live repository metadata and BHH source/rights reports | Existing Samaritan source lineage retained; primary noncommercial terms prevail over conflicting derivative license summaries. Not a second witness merely because copied by another project. |
| evenderekh/THB | Live metadata, BHH prior evidence and existing public source-lexicon registrations | Candidate versification and lexical adapters; mixed source terms require path-level checking. No wholesale rights inference from its MIT code license. |
| bdenckla/MAM-basics | Live metadata, BHH source and rights reports | Existing licensed MAM display projection reused for parallel text. Structured notes and layout are distinct from main running text and from independent manuscript collation. |

External live metadata alone does not verify a dataset's contents or license. Concrete imported bytes have immutable revisions/hashes and specific notices. Prior-project discovery records are labelled inherited; their previous inspection is not represented as a fresh complete audit. Protected HALOT/DCH/TDOT/BHS/BHQ material was not acquired or consulted.

## Acceptance and remaining work

All imported source words are eligible for lookup, including Biblical Aramaic and separate qere. Technical source coverage and imported morphology are counted independently from semantic review, manuscript checking, translation checking and full verification. Those scholarly counters begin at zero. Private research import preserves draft status and does not increment them. Historical dictionary material also does not increment semantic review.

The build emits per-book manifests and a global coverage report; generated databases/packs are artifacts, not Git-history payloads. The full raw corpus has been processed, but this does not claim complete lexical research, full ancient-version coverage, verified sense counts, or exhaustive European translation comparison. Physical Safari/Edge/mobile devices and future schema migrations remain outside this initial verification.
