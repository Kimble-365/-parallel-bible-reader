# Parallel Bible Reader 1.28 — development

Nondeploying project-branch increment over 1.27 r2. Preserves all 84 Bible editions, source bytes, device stores and catalog discovery work.

Implemented and browser-verified:

- Six device-font choices with script fallback, preview, persistence and storage-failure feedback.
- Verse-specific Copy, Copy to Notes, Bookmark, Share, four persistent highlight colors/removal and native text selection; left-gutter icons removed.
- Local attributed PNG verse images and selected-slot Compare; empty slots stay empty. Offline actions require saved Bible texts.
- Optional Bible/theology/salvation introductions and 11 prayers (eight original, three short attributed historic selections), available from Settings and selected-verse Pray. English editorial resources are separate from Scripture. See PRAYER-SOURCES.md for wording/source attribution.

Complete checks passed at code 7a37fadfc29f766f0369b8575061b9c26cb50015 in Actions 42324819651: actual Chromium 320/390/1280px, Unicode/RTL PNG, clipboard/Notes/highlights, empty slots, resource navigation, offline use and inherited catalog/font/reading tests. Physical Safari/Edge and theological/scholarly/linguistic review remain separate.

Pending: reproducible final release packaging/size/rights audit and promotion review. Production remains unchanged on 1.27 r2. Incoming 1.29 material must be inspected and integrated without overwriting these improvements. No merge, GitHub Release publication or deployment is authorized by this development package.
