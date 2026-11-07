# Parallel Bible Reader 1.28 — review and rollback

This final preparation does not merge, publish a GitHub Release, change access or deploy. Review artifacts come from the nondeploying `project/parallel-reader` check run. Core 1.28 application features passed Actions 42324819651 at `7a37fadfc29f766f0369b8575061b9c26cb50015`; the package run separately verifies the exact packaging commit.

## Scope and artifact

The final review archive is `parallel-bible-reader-1.28.zip`, accompanied by `.sha256`, `PACKAGE-REPORT.json` and `VERIFICATION-REPORT.json`. The artifact is retained for 30 days; it is not a permanent public download. `tools/package_reader_128.py` builds it from an exact 40-character source commit. Two builds with the same inputs and Python/zlib environment must be byte-identical. Every manifest-listed file is size/hash verified; repository runtime/text files remain verbatim and keep their original paths. Generated launch/docs files are explicitly identified.

Retain all current font, verse action, highlight, Notes, PNG, Compare and prayer changes. Retain all 84 catalog editions with their actual source coverage. A pack/edition count does not mean a complete 66-book Bible. Incoming 1.29 material remains separate and cannot overwrite these improvements.

## Scope of the ZIP

The reader-only ZIP includes local Bible delivery families, shell assets, Japanese aids, local BHH/Syriac data, interlinear indexes and license/provenance metadata. It excludes original ZIP source archives, the encyclopedia, old app shells, Git history, private user data and the unavailable 1.29 package. Audio/video, publisher links, raw source archives and some pinned source-hosted study/apparatus resources still need Internet or a previously saved supported source. Do not claim full offline availability of all linked websites.

The original generic `tools/package_release.py` is retained for older versions; use the version-specific packager for 1.28 so shared paths are not broken. Direct `file://` is not a full supported delivery mode for this fetch-based reader. The generated HTML explains the limitation instead of silently presenting an empty reader. Use the standard-library local launcher on desktop or an approved HTTPS/PWA deployment for iPhone/iPad. The local launcher uses stable `127.0.0.1:8765`; changing browser/host/port changes the storage origin. Export supported backups before moving from the hosted site; do not clear browser data.

## Promotion plan — requires separate confirmation

1. Review the immutable successful package run, ZIP hashes, source/rights inventory, test reports and documented browser/linguistic limits. Inspect the PR/diff against the current `main`, preserving any intervening production changes and all separately owned source projects.
2. Recheck the repository/site size. Its tracked tree already exceeds one billion bytes before packaging; do not add this large ZIP to the Pages tree blindly. Choose an explicitly approved artifact/download hosting strategy. A GitHub Release publication also requires confirmation.
3. After explicit authorization, merge only the reviewed compatible changes and update the production redirect/reader version, with the existing release retained. Do not force-push a branch or overwrite prior release directories.
4. Verify the exact Pages deployment, public file hashes, sources, mobile reading, all empty-slot combinations and persistence. Do not describe the code as publicly installed before these checks pass.

## Rollback plan — requires separate confirmation if deployed

Retain 1.27 r2 and every user-store key. If the deployment fails, restore the production redirect to the then-verified previous release in a normal reviewed commit; do not delete 1.28 or clear user stores/caches indiscriminately. Validate the rollback deployment and public bytes. Never reset `main` or force a ref. Current packaging does not change the production redirect.

Broader GOAL acquisition, M2 navigation, storage benchmarks and scholarly/physical browser review remain open; this is final preparation of the specifically requested 1.28 feature set, not completion of the global roadmap.


## Verified final review artifact (7 November 2026)

Code `70ae0eabdd950f5c4cffabca747a9dbe7130e323`, [Actions 42330023025](https://github.com/Kimble-365/-parallel-bible-reader/actions/runs/42330023025), all checks successful including the KR33/38 Matthew 6:13 escaped-formatting repair. All Scripture words and original corpus bytes are retained; only known FO/Fo delimiters are omitted from display/search/new quotations. Existing stored notes are not rewritten.

[Review ZIP and reports](https://github.com/Kimble-365/-parallel-bible-reader/actions/runs/42330023025/artifacts/13556588392), available until 7 December 2026. Inner reader ZIP: **174,304,492 bytes**, **2,223 files**, **84 editions**; SHA-256 `ba9fcca82f5c0a2b9a349abfbbead1b369a3035573b81ea29f92275d2fb2dd0b`. Two builds matched byte-for-byte; all manifest/verbatim hashes and the extracted 84-edition local-reader browser checks passed. This supersedes the earlier e102064 artifact. Full measurements: `../../docs/research/reader-128-package-audit.json`. This review artifact has not been merged, published as a Release or deployed.
