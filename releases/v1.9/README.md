# Reader 1.9 — installable app and selected-text offline reading

Keeps the 43 editions, four independent optional slots, source references, directory, themes, bookmarks and search from 1.8. No new Bible texts or audio matches are claimed.

Open the HTTPS reader. Use **Install & read offline**. Chrome/Edge may offer **Install reader** or a browser-menu installation command. On iPhone/iPad, use Safari’s Share → Add to Home Screen. Save texts from inside the installed reader where possible, since browser and installed-app storage may differ. Actual installation prompts are controlled by the browser.

Choose texts in the reading slots and press **Save selected texts**. The reader stores only those editions’ original text and existing Latin conversion in IndexedDB. It downloads one book at a time and commits its texts and completion metadata atomically. Stop or a network/storage failure retains completed books; saving again resumes. The list distinguishes incomplete versus ready editions, reports book counts and approximate text size, and can remove one saved edition without changing bookmarks or reading progress. Clearing browser/site data can remove both.

The app shell, directory, book guides and small English pronunciation dictionary are cached by a service worker scoped to `/releases/v1.9/`. It does not take over production or earlier releases. Updates wait for the user’s **Update reader** action. Shell caching and offline setup failures are reported; saving is enabled only after the app shell is ready. Device storage persistence is requested when saving, but a browser may refuse or later evict data. Test a fresh reopening in airplane mode before travel.

Text downloads reuse the verified 1.8/root book bundles: a network transfer can contain other editions, but only selected text rows are saved. Bundle requests use no-store, source code is parsed as JSON rather than evaluated, and no new bulk corpus is duplicated on Pages. The displayed data is checked for the expected book and chapters before being marked saved. Source licensing is included locally; raw USFM/source archives remain separate online links. Shared URL overrides and opaque source keys still work.

Audio and external source websites require internet. An unsaved text/book cannot be promised offline. Search works over saved books; an all-book search requires the corresponding selected editions’ full coverage to be saved. The PWA requires HTTPS or localhost; file-open users can still download the separate 1.8 ZIP. There is no new 1.9 ZIP; installation and selected-text storage are this version’s experiment.

Verified with actual Chromium service worker and IndexedDB, including English/Hebrew offline reload, RTL/Latin, directory, search, phoneme assets, missing-text feedback, cancellation/resume, full 66-book English save and Revelation offline, and bookmark-preserving deletion. Safari/WebKit, Edge and physical phone installation are not yet device-tested.
