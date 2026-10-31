# Reader 1.23 — source-aware textual apparatus

Prepared increment; full browser verification and publication remain pending.

Study → Textual apparatus opens a separate source reader for Greek NT, Greek OT/LXX, Hebrew and Syriac. Search loaded readings/notes/status, filter source references and exact witness sigla, navigate previous/next recorded references and export an attributed JSON package. Right-to-left and mixed-script readings use Unicode direction isolation; no NFC/phonetic reconstruction or manuscript-identity guessing is applied.

Optional live loaders: SBLGNT apparatus XML for 27 NT books (printed-edition comparison, not the NA28/UBS manuscript apparatus) and OSHB WLC qere/ketiv/variant notes for 39 Hebrew books (not full BHS/BHQ). Immutable source manifests specify commit, size and Git blob checksum. Save a source book separately for offline use. No source downloads run merely by opening the reader. Exact open Philemon/Ruth fixtures verify byte identity and parsing.

Private JSON/JSONL and restricted TEI apparatus import supports all four traditions, including research records using reference/address/locus, display_tokens/supports, source_siglum and evidence arrays. Original objects and XML are retained for inspection. Printed edition comparisons, manuscript hands, source/version evidence, statuses and unapproved proposals remain distinct. TEI preserves witness definitions and header/rights, and rejects nested/grouped/stand-off apparatus that needs explicit conversion. This is a reader, not a scholarly collation or full generic TEI engine.

Preview then explicitly save to a separate device-only IndexedDB library (up to 10 imports / 24 MiB). Input and expanded text are bounded at 4 MiB; gzip uses the existing local fallback. Private imports are never uploaded, copied into the public repository or fetched from private GitHub by browser code. Export JSON before removing an import or changing device. Unsupported/corrupt files do not replace earlier imports. No private source records are used in public tests; format fixtures are synthetic and clearly labeled.

LXX and Syriac apparatus display is ready for permitted imports; no full modern Göttingen/Cambridge/Leiden corpus is bundled. Open base texts are not mislabeled as critical apparatus. Empty results do not imply agreement. Source numbering is retained, with no automatic equivalence claim for Text 1. All prior texts, pages, notes, vocabulary, plans and imports retain their storage keys.

See [formats, provenance and limitations](apparatus-guide.html). Physical Safari/Edge script-font and interaction review remains open; no claim of exhaustive textual-critical validation is made.
