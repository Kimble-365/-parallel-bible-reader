# Europe and English Reference Editions — Parallel Bible Reader 1.29

Reference package for the The Way Translations repository, dated 2026-11-03.

## What this is

116 redistributable English and European Bible editions imported into the
Parallel Bible Reader as release 1.29 (200 editions total; the 84
pre-existing editions are preserved). This package maps the material onto
this repository's layout so it can be consulted alongside The Way Version.

## Where things go

| package path | contents |
|---|---|
| `original-documents/reference-editions/parallel-reader-1.29/` | complete reader 1.29 reference tree: catalog, manifests, 85 book packs (`europe-data/`), per-edition source and display archives with provenance (`sources/`), licences |
| `tools/local/import_2026_11_03_europe_english_reader.py` | the importer (runs against the reader repository; kept here for reproducibility) |
| `tools/local/audit_2026_11_03_europe_english_reader.py` | the audit tool (ran clean: ALL CHECKS PASSED) |
| `change-logs/reports/2026-11-03-europe-english-reference-import.json` / `.md` | import record: counts, revisions, licence distribution, duplicates, exclusions, verification |
| `editor-notes/research/EUROPEAN-REFERENCE-EDITIONS.txt` | scope, method, limitations, exclusions |
| `review/2026-11-03-europe-english-rights-review.md` | the complete rights decision record |

## Boundaries

- This is third-party reference material. It is not The Way Version text and
  implies no endorsement by The Way Partners LLC.
- Nothing in this package modifies `current-form-documents/` or the mobile
  reader feed. The Way Version text remains © 2026 The Way Partners LLC.
- Every imported edition stays under its own source licence; see
  `sources/<id>-source.zip` for the complete notices and
  `LICENSES.md` inside the reference tree for the per-edition summary.

## Provenance

- Reader baseline (main): `89afb00cfa94b7630bf8e48419d95d73bd5f5181`
- The Way base revision used for this map: `827dd32a00036886fada82f5b43bd7041f9c8906`
  (committer date 2026-10-27T17:35:29Z)
- Source catalogue: eBible.org Scriptures catalogue, retrieved 2026-11-03
