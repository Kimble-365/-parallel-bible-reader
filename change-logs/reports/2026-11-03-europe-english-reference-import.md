# 2026-11-03 — Europe and English reference-edition import (Parallel Bible Reader 1.29)

## What changed

116 redistributable English and European Bible editions were imported into the
Parallel Bible Reader as release 1.29, data group `europe-english-1.29`. The 84
pre-existing editions are preserved unchanged. The reader now offers 200
editions with 85 deterministic book packs (111,501,632 packed bytes,
2,431,331 imported verse rows across 5,394 source books).

This directory receives the material as **reference editions for consultation
alongside The Way Version**. It is not a The Way Version release. Nothing under
`current-form-documents/` and nothing in the mobile reader feed is modified by
this package.

## Source and selection

- Source catalogue: eBible.org Scriptures catalogue, retrieved 2026-11-03
  (1,552 rows; 1,295 marked redistributable).
- 133 English/European candidate editions reviewed page by page.
- 116 imported; 13 skipped as duplicates of editions already in the reader;
  4 excluded for unclear or incompatible redistribution terms (see the JSON
  report and the rights review for the specific reasons).

## Nordic target languages

Already present and preserved: `fin-kr1938`, `fin-biblia1776`, `swe-1917`,
`nob-1930`, `nno-1921`, `dan-1819`, `isl-olo1995`.

Newly added:

| id       | edition                                   | books | licence          |
|----------|-------------------------------------------|-------|------------------|
| `fin`    | Finnish Open Living News NT               | 27    | CC BY-SA 4.0     |
| `swe`    | Swedish Kärnbibeln / Swedish NT+          | 66    | CC BY-NC-ND 4.0  |
| `noblb`  | Norwegian Living NT                       | 27    | CC BY-SA 4.0     |
| `dan1931`| Danish Bible 1931                         | 66    | Public Domain      |
| `isl316` | Icelandic 316-biblían (Mark at snapshot)  | 1     | CC BY-SA 4.0     |

## Rights handling

- Every imported edition carries attribution text, licence name, licence URL,
  source URL, retrieval date and the SHA-256 of the downloaded USFM archive in
  `sources/<id>-source.zip` (`PROVENANCE.json`, `RIGHTS.txt`, `DETAILS.html`).
- CC BY-ND / CC BY-NC-ND editions received format conversion only; translated
  words and punctuation are unchanged. Headings, footnotes, cross references
  and publication-only matter are omitted from display but remain in the
  source archives.
- `dan1931` was re-checked on 2026-11-04 and is labelled **Public Domain**: the
  Danish Bible Society's official copyright page claims rights only to the 1992
  and 2020 translations, and the society has confirmed the 1931 OT is public
  domain; the historical © 1907, 1931 notice stays in the source archive.
- Reader code licensing stays separate from source text licensing; the
  third-party texts remain under their own licences.

## Verification

- `tools/local/audit_2026_11_03_europe_english_reader.py`: ALL CHECKS PASSED —
  200 catalog editions, 116 in the new group, all 85 pack checksums, all 232
  source/display archives intact, provenance licences consistent, all 84
  baseline editions preserved.
- Headless Chromium runtime check: all 116 new editions load through the
  reader's own pack loader; preserved editions `swe-1917` and `fin-kr1938`
  load; search builds and matches for new (`dan1931`) and old (`swe-1917`)
  editions; offline save path verified for `isl316`.

## Revisions

- Reader baseline (main): `89afb00cfa94b7630bf8e48419d95d73bd5f5181`
- Reader 1.28 development head (avoided): `96762dea788802570f833fbc26eed293f6f8e66e`
- The Way base revision for this package map: `827dd32a00036886fada82f5b43bd7041f9c8906`
  (committer date 2026-10-27T17:35:29Z)
