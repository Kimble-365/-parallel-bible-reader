# Parallel Bible Reader 1.28 — development

Nondeploying project-branch increment over 1.27 r2; preserves all 84 editions, source bytes, device stores and M1 discovery.

Completed: six device-font settings with script fallback, preview, persistence and failure feedback; verse-specific Copy, Copy to Notes, Bookmark, Share and four persistent highlight colors/removal, with native text selection and no left-gutter icons.

Completed: Verse image generates an attributed PNG locally using current theme/device fonts, without uploading text. Bounded Unicode wrapping and image size provide a Copy fallback for unsupported/oversized passages. Compare shows already-selected translations and their own references with an explicit label-only alignment warning; empty slots remain empty. Offline actions require saved Bible texts.

Verified at code 66ecf3273dcd96ffc8b4b63ae475e12cdcb4596a in Actions 42319320612 with actual Chromium at 320/390/1280px, Unicode/RTL PNG generation, downloads, offline use, empty slots and inherited font/catalog/verse-action/reading checks. Physical Safari/Edge and exhaustive linguistic/glyph review remain separate.

Pending: introduction/theology/salvation/prayer resources and Pray, final packaging and production promotion. Production remains unchanged on 1.27 r2. Incoming 1.29 material must be inspected and integrated without overwriting these improvements. No merge or deployment is authorized by this development package.
