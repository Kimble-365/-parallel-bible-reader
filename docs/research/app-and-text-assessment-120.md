# Bible app and text-source assessment — 2026-10-28

Research checked 2026-10-28 using provider pages and documentation. These are design ideas and text-source candidates, not claims that all features/texts are installed. Actual provider playback/account flows were not exercised. The reader stays account-free and keeps the main screen simple.

## App ideas

### PRS

Kana above kanji, reading plans with several passages, manual whole-Bible tracking. 1.19 adds experimental kana and tracking; 1.20 adds three original multi-passage paths. Modern PRS editions stay external.

Source: https://prsi.org/en/app

### YouVersion

Easy verse actions, highlights, notes, reading plans and parallel versions. Keep the clean reading view; a later small verse-action sheet and optional highlight colors could reuse our local notes. Its library is not a bulk-export license.

Source: https://www.youversion.com/bible-app

### AndBible

Synchronized split windows, pinned documents, workspaces and offline study pads. Shared verse rows are implemented. Saved reading sets/workspaces are a useful next small feature; do not add a large technical dashboard.

Source: https://andbible.org/

### STEPBible

Word-level original-language lookup, morphology and linked lexical datasets. A tap-to-explain word panel is feasible with versioned licensed word alignments. Not implemented by plain transliteration or a generic search index.

Source: https://github.com/STEPBible/STEPBible-Data

### Bible Gateway

Parallel reading, notes, audio and reading plans. Comparison and plans fit this reader. Publisher text/audio permissions remain separate from website access.

Source: https://www.biblegateway.com/app/

### Bible.is

Multilingual listening plans and changing the plan’s reading language. Plan progress in 1.20 follows the plan across translations. Direct audio queues/verse sync still need permitted streams and verified timing metadata.

Source: https://bibleis.freshdesk.com/support/solutions/articles/47000399221-plans-on-bible-is

### BibleProject

Book-context videos, thematic collections and progress through content. Link context resources from Contents. Current original guides remain separate from Scripture; no videos/artwork are copied.

Source: https://bibleproject.com/app/

### Logos

Passage-centered resources, notes, comparison and original-language guides. A small passage context panel may be useful later. Licensed resources and commercial guides are not exported into this app.

Source: https://www.logos.com/faq

### e-Sword

Modular Bible library, linked study tools and personal notes. 1.18+ supports permitted unencrypted Bible SQLite exports; commentaries/dictionaries are not falsely imported as verse texts.

Source: https://www.e-sword.net/

### Blue Letter Bible

Interlinear, Hebrew/Greek lexicon and cross-reference tools. A simple word/cross-reference popover could use separately licensed datasets. Do not copy the hosted study library.

Source: https://blb.sc/

## Text candidates

### Japanese Kougo-yaku 1954/1955

CrossWire module JapKougo labels this historical colloquial edition Public Domain. High-priority Japanese candidate. Acquire the exact module/readable export, verify coverage/source numbering, then create separate kana/Latin aids. Not Shinkaiyaku 2017; not installed by this research.

Source: https://www.crosswire.org/sword/modules/ModInfo.jsp?modName=JapKougo

### Berean Bible / Berean Standard Bible

Publisher dedicates Berean and Majority Bible texts to the public domain from 30 April 2023. High-priority modern English candidate; pin a source download and validate any verse annotations. Text dedication does not automatically prove every recording is reusable.

Source: https://berean.bible/licensing.htm

### unfoldingWord ULT/UST and language projects

Publisher describes the listed resources as CC BY-SA 4.0. Possible literal/simplified text pairs, plus new regional languages through Door43. Verify the exact language project, release, canon and attribution before acquisition. OBS is a retelling, not a Bible translation.

Source: https://unfoldingword.org/for-translators/content/

### STEPBible original-language datasets

Repository states CC BY 4.0; individual files/resources need attribution checks. Tagged Hebrew/Greek, lexicons and word-level data can support optional word study. Do not silently replace the installed source editions or claim all external texts share this license.

Source: https://github.com/STEPBible/STEPBible-Data

### eBible.org and Open.Bible

Edition-specific Public Domain/Creative Commons notices; coverage varies. Strong sources for licensed Asian, African, European and minority-language USFM. Deduplicate installed 62 editions and check actual source coverage instead of treating catalog descriptions as complete Bibles.

Source: https://www.open.bible/bibles

### Free Use Bible API

Catalog provides each translation’s license URL and book counts; structured and simplified formats. Useful acquisition/index adapter candidate with explicit edition metadata. Review source/license per translation, preserve source hashes, headings, notes and unusual numbering. No blanket permission is inferred.

Source: https://bible.helloao.org/docs/reference/translations/

### API.Bible / Digital Bible Library

Open and protected versions have separate agreements and access terms. Possible later approved integration. Not a permission to scrape protected texts, expose an API key or republish every translation.

Source: https://care.api.bible/article/369-understanding-api-bible-licensing
