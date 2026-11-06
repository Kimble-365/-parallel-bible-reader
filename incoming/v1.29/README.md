# Manual 1.29 intake — not an installed release

Upload destination: `incoming/v1.29/` on branch `project/parallel-reader` in `Kimble-365/-parallel-bible-reader`.

## Upload from GitHub

1. Stay on `project/parallel-reader`; do not upload to `main`.
2. Open this folder and choose **Add file → Upload files**. On mobile, use the browser's desktop-site mode if this control is hidden.
3. Upload original package files or extracted contents here, preserving their original directory structure. Keep supplied README, PACKAGE-MANIFEST, rights/import reports, importer/validator and source/evidence archives. Put package contents in `package/` or retain the original top-level package directory so this intake README is not replaced.
4. Commit the uploads to this branch. Multiple upload commits are fine. In chat, say when all parts have finished uploading so an incomplete set is not mistaken for a complete handoff.

GitHub's browser upload limit is **25 MiB per file**; the ordinary Git file limit is **100 MiB**. The reported 112/139/143 MB ZIPs cannot be uploaded intact through this page. Extract files on your iPhone first and upload individual files below the browser limit. For any larger individual archive, use a lossless split into parts smaller than 25 MiB, retain all parts with their original order/names, and provide the original filename/checksum if supplied. A shared download link is another option. Do not recompress or edit source text to make it fit, and do not commit files over GitHub's ordinary Git limit. No Git LFS or permissions change is configured by this folder.

## Preserve the 1.28 improvements

This is a staging inbox, not `releases/v1.29/`. Uploading here does not replace application code or publish the package. Do not copy the incoming runtime, root redirect, workflows or project-control files over existing repository paths.

The maintained development baseline includes the completed 1.28 font milestone, code commit `55e824f4f0c1627975b51151a63a44054b007c0c`, verified in Actions `42273926324` and recorded by `abfef9de48f93cd0a2d05a78a2d8464e666efe03`. Keep `releases/v1.28/`, its six font choices, script fallbacks, offline assets, tests, all 84 edition identities and every user-storage namespace. The verse action menu, highlights and introduction/prayer library remain approved pending work; they are not assumed to exist in the incoming 1.29 package. Keep developing these independently.

A higher incoming version number does not supersede newer development work. Before integration, compare the package against the current project HEAD, preserve all later 1.28 changes, and port only reviewed compatible additions. Never replace the branch wholesale or force-push the originating local commit `259da6c`.

## Intake verification before integration

The uploaded material is unverified until inspected. The reported 85 packs are not assumed to be 85 distinct Bible editions. Pin the completed upload commit; inventory all parts; verify supplied checksums, edition identity, counts and rights; inspect source archives and importer/validator before running tools or importing data. Preserve source bytes and record any missing files or rights uncertainty.

Respect the package's intended map where appropriate: `original-documents/reference-editions/`, `tools/local/`, `change-logs/reports/` and `editor-notes/research/`. Never touch canonical EPUB or mobile feeds. No unreviewed executable or workflow from the package is activated by this intake.

Keep the exclusive RUN_STATE guard and expected-head fast-forward rules. Integration, source redistribution and testing must be documented. No merge, deployment, access change or formal PR approval without separate user confirmation.
