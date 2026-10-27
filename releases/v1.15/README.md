# Reader 1.15 — simpler reading interface

The initial view has one Bible in its original script, a favorite/current Bible selector and book/chapter navigation. The top menu opens Settings, Search, Listen, Watch, Offline, Notes and Languages. Settings contains all four independent optional text slots, Original / Text + transliteration / Transliteration only, per-text forms, colors, light/dark mode and the existing study tools. Escape or Back to reading closes settings. Previous notes and saved texts remain in their existing device storage. On the first 1.15 visit comparisons start empty; explicit shared-passage choices take precedence. Later choices persist.

57 public editions: all 55 from 1.14 plus Danish New Testament 1819 (27 books, 7,953 source units) and Esperanto Londona Biblio (66 books, 31,102 units). Both use Latin script, preserving historical spelling and diacritics. Danish footnotes remain in the original USFM archive; the display contains verse text. Exact source Git blobs and corresponding Public Domain declarations are retained. No new matching audio recording is claimed.

Includes 1.14's UTF-8 TXT / DOCX / PPTX notebook export, manual Google Docs/Slides import instructions and official external film links. See [1.14 details and limits](../v1.14/README.md). Older text payloads are reused instead of duplicated. The original file-open ZIP remains 1.8; this release is the web/PWA edition.

Proposed future menu items: reading history, a daily reading plan and a presentation mode. These are proposals, not installed features. Keep the first view uncluttered.

Verification status: all new source units/archives/rights, source routes, search fingerprints, notes model/UI handlers, Office files all 35 PWA asset paths and actual menu handlers in a DOM fixture pass local checks; a full Chromium usability/offline rerun is required before promotion. Browser execution currently requires unavailable runtime approval. Do not label this release published or validated until that step and GitHub deployment complete.
