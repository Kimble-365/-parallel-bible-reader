# Reader 1.12 — indexed search

Numbered search release; its changes are also included in reader 1.13.

The reader retains the 46 public editions from 1.11 and references the existing text payloads without duplicating them. Personal Bible imports remain private and are not bundled.

Search defaults to all available books for the selected texts. Choose whole words (all terms in the same displayed verse form), a phrase, or a substring. Use Contains for Finnish word endings; automatic stemming is not provided. Search accepts short words. Original Finnish, Hungarian and Indic spelling distinctions are retained. Optional exact marks control Hebrew, Arabic, Greek and Latin transliteration matching; written forms are not pronunciation reconstructions.

Public text search indexes are stored separately in IndexedDB and checked against a per-book content fingerprint manifest (46 editions, 2,253 book/edition pairs). Personal imports use memory-only search indexes. The first search may download and index books. Saved books scope searches saved texts without fetching missing books. Clearing the search index leaves saved texts and bookmarks intact.

Search reports complete, incomplete or stopped coverage, keeps available results when a book is unavailable, combines matching slots for the same edition/verse, and offers additional results in batches of 100. Results include the full matching verse. A stop control cancels an ongoing search.

The text storage schema remains compatible with 1.10 and 1.11. Earlier releases and their source/license records remain unchanged. Audio links and source downloads require internet.

Verified in Chromium: real-word/short searches, results beyond 100, persistent and warm public indexes without text-payload rereads, incomplete offline searches, saved-only scope, Greek exact marks, duplicate-slot merging, stopping requests, result opening and available-text rendering when a comparison fails. Node normalization tests also pass. The earlier extra-loader-call report was a Playwright instrumentation error: evaluating a function assignment invoked that function with undefined arguments. The test now avoids returning a callable. Safari and Edge have not been tested.
