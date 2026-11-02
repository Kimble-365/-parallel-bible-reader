# Parallel Reader project progress

Working branch: `project/parallel-reader`. Development target: **1.28-dev.M1**, staged against maintained reader 1.27 r2. Nothing is merged or deployed. Baseline main: `89afb00cfa94b7630bf8e48419d95d73bd5f5181` (84 editions). All source corpora, metadata, source IDs and user-storage namespaces are retained.

## Work rules

Read GOAL.md, this file and RUN_STATE.json every run. Skip a running owner; elapsed time is not proof of completion. Acquire ownership through an expected-head fast-forward lease, reread before mutation and release only your own guard. Existing GitHub workflows were inspected: the new reader-development workflow runs checks on this project branch only, with contents:read and no deployment steps. Never write main, merge, deploy, alter access or formally approve PRs without separate confirmation.

## M1 — translation discovery (implemented, browser verification pending)

Add a separate name-search engine to the existing directory. Rank exact ISO/edition IDs before exact language names, aliases and prefixes; accept multiword edition-name queries. Fold Latin accents for catalog names only; preserve non-Latin marks and every Scripture byte. Offer bounded, explicit spelling suggestions only when the current filters yield no direct result; never select a translation automatically. Return links must preserve all four slots, intentional empty choices, text forms and reference. Cache the new engine for offline directory reading.

Local model verification passed against all 84 existing editions, including Finnish ISO, Urdu/Tamil native names, Swedish 1917 multiword lookup, transposition suggestions, filter isolation, query limits and unchanged metadata. Remote browser/static checks pending. Physical Safari/Edge review remains separate. No new Bible text, audio or scholarly evidence is acquired.

## Next unfinished milestone — M2 discovery-state navigation

The current directory keeps search/filter state only in the document; URL/back-forward restoration is not implemented. After M1 verification, preserve the directory query and combined filters in the directory URL, restore them on reload/back/forward and keep all four reading-slot/form/reference parameters intact. Whitelist filter values from installed metadata; never persist Bible text or private notes in URLs. Verify native queries, invalid filters, history navigation, reset and slot-return links at mobile/desktop widths and offline.

## Separate owners and later decisions

DavarQadosh and whole-WLC integration already have project branches/PRs and another automation. LXXL, Syriac and other source research are separately managed. Do not duplicate or mutate those projects. Broader source acquisition, SQLite/WASM delivery benchmarks, updated offline ZIP and scholarly review remain governed by GOAL.md and current source/rights evidence; do not claim completion from this catalog work. Final promotion/version packaging requires separate user confirmation and a check of the repository's published-site size.
