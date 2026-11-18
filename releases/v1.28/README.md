# Parallel Bible Reader 1.28

TSK and Finnish reader notes can now be selected in any Text slot like a Bible, with clickable passage links, independent source chapters, search, sharing and selected-text offline saving. The Finnish v005 Bible is also installed as a separate edition. All 84 existing editions and existing storage revisions are retained: 85 Bible editions plus two commentary companions.

[Open Finnish Bible, notes and TSK](./?edition=fin-study-v005&compare1=fin-study-notes-v005&compare2=tsk-crosswire&compare3=&layout=source#GEN.1.1) · [TSK only](./?edition=tsk-crosswire&compare1=&compare2=&compare3=&layout=source#GEN.1.1) · [Sources and checks](reference-guide.html)

Source: CrossWire TSK 1.4, 2001-12-15, Public Domain. The original ZIP, module configuration and source ThML articles are retained under `sources/tsk/`. This is not the later Enhanced TSK or OpenBible's community-voted dataset. TSK source wording remains English and follows KJV numbering. It is not silently renumbered onto the Finnish Bible.

The build parses 31,090 source articles and preserves 85,312 scripRef tags. Every one of the 387,161 linked target ranges has valid KJV book/chapter/verse endpoints. Thirty-six malformed, out-of-bound or context-ambiguous source notations remain readable but unlinked; see `sources/tsk/reference-issues.json`. The original is unchanged. This verifies the source export and link structure, not the theological merit of every connection.

Finnish Bible wording remains exact across all 31,170 verses. All 24,531 edited notes and 110 editorial cross-reference links are preserved as a separate companion. Their `unreviewed` editorial status is unchanged. No new translation review was performed.

`tests/references_128.py` independently compares every retained source-reference tag, every linked range endpoint, all original Finnish verse words and note definitions, and the unchanged 84-edition catalog/storage baseline. `tests/references_browser_128.py` checks actual Chromium at 390/1280 pixels, reference navigation, independent and aligned layouts, empty slots, complete 198 book-edition offline saving/reopening, and rejection of a tampered data pack. This increment does not claim a new full regression run of every older feature or physical Safari/Edge testing.

Rebuild with Python and `pysword==0.2.8`:

```text
python tools/build_tsk_128.py /path/to/unpacked/modules/comments/zcom/tsk /path/to/TSK.zip
python tools/wire_references_128.py
python tests/references_128.py
```

The zCom source uses SWORD's compressed verse storage layout, decoded through pysword's zText block reader; original ThML is retained before parsing. Per-book packs are hash-checked before use. Earlier numbered releases remain untouched.
