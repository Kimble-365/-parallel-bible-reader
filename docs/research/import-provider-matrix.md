# Provider import status (prepared 1.18)

These are implemented **private file adapters**, not claims of authenticated connections or blanket rights to a provider's inventory. Choose a permitted export and preview it; local files are not uploaded.

| Source | Implemented readable input | Remaining limit | Primary documentation |
|---|---|---|---|
| CrossWire / SWORD | IMP from mod2imp, OSIS from mod2osis; USFM exports | Raw/zipped/encrypted SWORD engine binaries need an official readable export; module license is per .conf | https://wiki.crosswire.org/DevTools:Modules |
| e-Sword | Unencrypted SQLite .bblx/.bbli Bible tables, plain text/HTML/ordinary RTF | Compressed/encrypted cells and legacy Access are not decoded | https://www.e-sword.net/faq.html |
| Crossway / ESV | Saved passage/text JSON with explicit single-chapter passage_meta and verse markers; attribution retained | No embedded API key, authenticated live request or bulk/full-ESV permission is supplied | https://api.esv.org/docs/passage-text/ |
| Bible Hub / Berean | Explicit verse text, CSV/TSV/JSON and supported publisher XML | BSB's public-domain status does not license other Bible Hub material; arbitrary website HTML is not parsed as a Bible | https://berean.bible/licensing.htm |
| Bible.is / Bible Brain | Authorized USFM/USX/OSIS/verse JSON exports | Edition-specific credentials and offline/redistribution rights; no audio download connection | https://www.faithcomesbyhearing.com/audio-bible-resources/bible-brain |
| YouVersion / Bible.com | Authorized publisher USFM/USX/JSON exports | Protected web/app content is not scraped; developer access does not confer all Bible rights | https://developers.youversion.com/ |
| STEP Bible | Verse TSV/CSV with explicit reference/text fields, OSIS/USFM/IMP exports | Morphology, lexicons and alignment tables are not guessed into verse text | https://stepbible.github.io/STEPBible-Data/ |
| Davar | Referenced UTF-8 text, verse CSV/TSV and supported XML exports | Proprietary/encrypted module containers require a readable export | https://www.davar3.net/about.html |
| Other publishers/tools | USFM, USX, OSIS, Zefania XML, explicit JSON, CSV/TSV, referenced VPL | Unknown verse maps and encodings are rejected, not silently normalized | https://docs.usfm.bible/ |

ZIP files must be extracted first; multiple book files can be selected together. Total input limit is 32 MB. Private import metadata records language, script, source attribution, source files and a content fingerprint. Imported texts participate in the existing reading/search/offline UI; their verse positions are not asserted to be aligned with other translations.

Public Nordic additions use original Latin-script spelling without a redundant Latin duplicate. Icelandic has 28 supplied books; the additional Estonian edition has 27. Unknown-license historical Estonian sources are excluded. The PyKakasi Japanese form is explicitly an unreviewed dictionary reading, not a spoken transcript. Guide translations are editorial drafts and must not be presented as original Bible prefaces or a completed all-language translation project.
