# Parallel Reader project progress

Working branch: `project/parallel-reader`. Development target: **1.28**, reading-font milestone verified against maintained reader 1.27 r2. Nothing is merged or deployed. Baseline main: `89afb00cfa94b7630bf8e48419d95d73bd5f5181` (84 editions). All source corpora, metadata, source IDs and user-storage namespaces are retained.

## Work rules

Read GOAL.md, this file and RUN_STATE.json every run. Skip a running owner; elapsed time is not proof of completion. Acquire ownership through an expected-head fast-forward lease, reread before mutation and release only your own guard. Existing GitHub workflows were inspected: the new reader-development workflow runs checks on this project branch only, with contents:read and no deployment steps. Never write main, merge, deploy, alter access or formally approve PRs without separate confirmation.

## M1 — translation discovery (completed and verified)

Add a separate name-search engine to the existing directory. Rank exact ISO/edition IDs before exact language names, aliases and prefixes; accept multiword edition-name queries. Fold Latin accents for catalog names only; preserve non-Latin marks and every Scripture byte. Offer bounded, explicit spelling suggestions only when the current filters yield no direct result; never select a translation automatically. Return links must preserve all four slots, intentional empty choices, text forms and reference. Cache the new engine for offline directory reading.

Local model verification passed against all 84 existing editions, including Finnish ISO, Urdu/Tamil native names, Swedish 1917 multiword lookup, transposition suggestions, filter isolation, query limits and unchanged metadata. Chromium browser and static checks passed at code commit `a79bb2c8d7b07f1252b0f3d2f4446a8a1bc05a43`, [Actions 41505810695](https://github.com/Kimble-365/-parallel-bible-reader/actions/runs/41505810695). Actual 320/390/1280px checks cover explicit suggestion click/keyboard activation and focus return, filter isolation, native queries, all four slot/empty/reference return parameters, plain-text rendering and offline reload. Static validation covers 151 cached assets and unchanged text/note stores. A measured 329px Norwegian edition title in a 288px column is now wrapped; source spelling is unchanged. Mixed Latin/Indic and Latin/Hebrew mark-preservation regressions also pass. Physical Safari/Edge review remains separate. No new Bible text, audio or scholarly evidence is acquired.

## Deferred backlog — M2 discovery-state navigation

The current directory keeps search/filter state only in the document; URL/back-forward restoration is not implemented. After M1 verification, preserve the directory query and combined filters in the directory URL, restore them on reload/back/forward and keep all four reading-slot/form/reference parameters intact. Whitelist filter values from installed metadata; never persist Bible text or private notes in URLs. Verify native queries, invalid filters, history navigation, reset and slot-return links at mobile/desktop widths and offline.

## Separate owners and later decisions

DavarQadosh and whole-WLC integration already have project branches/PRs and another automation. LXXL, Syriac and other source research are separately managed. Do not duplicate or mutate those projects. Broader source acquisition, SQLite/WASM delivery benchmarks, updated offline ZIP and scholarly review remain governed by GOAL.md and current source/rights evidence; do not claim completion from this catalog work. Final promotion/version packaging requires separate user confirmation and a check of the repository's published-site size.


Latest completed run: 2026-11-02T19:01:09Z. M2 is next. Production `main` remains `89afb00cfa94b7630bf8e48419d95d73bd5f5181`. No merge, deployment, repository-access change or formal PR approval was performed.


## 1.28 interaction work authorized; write blocker cleared (6 November 2026)

GitHub connector writes now succeed: tree creation, commit creation and an expected-head non-forced fast-forward acquired the exclusive guard. Direct native Git remains unavailable because the workspace proxy cannot be reached. This run records the newly approved 1.28 scope in GOAL.md and releases only its own guard. No application changes or feature/browser verification are claimed. Next: implement the 1.28 font/verse-action/prayer-library milestone. M2 navigation remains pending and must not be reported complete. The unavailable 1.29 source package remains separate; do not rebuild it. Keep main and deployed reader unchanged.


## 1.28 reading fonts — completed and verified (6 November 2026)

Code `55e824f4f0c1627975b51151a63a44054b007c0c` passed [Actions 42273926324](https://github.com/Kimble-365/-parallel-bible-reader/actions/runs/42273926324). New isolated `releases/v1.28/` reuses all 92 inherited 1.27 files; only README, VERSION, boot, shell, app manifest, reader version/share route and service worker differ, with two new font files. Catalog bytes and all 84 editions remain unchanged. Six choices: Reader default, system sans, Georgia book serif, Palatino classic serif, Trebuchet humanist sans and monospace. Uses device fonts with Unicode and script fallbacks; no external font service or universal glyph-coverage claim. Separate font preference preserves every prior storage key. Default retains earlier appearance.

Local model and manifest checks passed. Actual Chromium passed 320/390/1280px Settings interactions, exact source-text preservation, Hebrew/Syriac/Arabic/Japanese CSS fallback fixtures, reload persistence, corrupt-value rejection, cross-tab updates, quota feedback and offline settings. All 153 shell assets exist. Inherited 84-edition discovery/offline tests, four-column alignment, mobile grouping, independent mode, Finnish quotes, gzip fallback, Japanese ruby/Latin/copy, tracker and offline source/aid saving passed without page errors. Physical Safari/Edge and exhaustive glyph/linguistic review remain separate.

The first browser attempt exposed a test expression that returned and invoked its throwing quota function; the second exposed an omitted nested translation-directory page during packaging. Both are corrected. The complete inherited directory page is now byte-identical, and the browser test uses a bounded controller wait. Project-only CI now cancels superseded test runs and bounds the new verification step; no deployment workflow was changed.

## Next concrete milestone — 1.28 verse action menu

Replace left-gutter action icons with an accessible verse-activated menu. Reuse existing edition-aware copy/share/bookmark and Notes paths; add persistent color highlights/removal, verse-image export, Compare and Pray. Preserve exact source references, all four slots including intentional empties, native text selection, keyboard/focus and offline/user-store behavior. Then complete the separately recorded introduction/theology/salvation and original/rights-verified historic prayer library. These features and a final 1.28 package are pending, not delivered by the font milestone.

The user explicitly lifted the 1.29 waiting restriction. The existing hourly automation prompt was updated accordingly without changing its cadence. Do not reconstruct the unavailable 1.29 package or touch canonical EPUB/mobile feeds. Production remains unchanged; no merge, deployment, access change or formal PR approval. This final progress commit releases only this run's guard.


## Manual 1.29 upload inbox (6 November 2026)

Created `incoming/v1.29/README.md` on the nondeploying project branch at the user's request. It explains browser upload limits and lossless intake, and requires preserving all 1.28 improvements and subsequent work. Incoming runtime/workflow/control files must remain staged under this folder; do not overwrite releases or activate uploaded code. The package remains unreceived/unverified. Validate complete upload parts, checksums, rights, identities and counts before any integration; 85 packs is not an edition count. Continue `1.28-verse-action-menu` independently. No application/source/store/workflow changes, merge or deployment. This setup releases only its own run guard.
