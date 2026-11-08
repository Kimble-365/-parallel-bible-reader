# Reader 2.0 native line

The user explicitly requested a new Rust-based Windows/Mac app and optional Android/iOS tablet apps on 8 November 2026. **2.0.0** is a new app line. **1.29 remains reserved** for the separately prepared, unreceived improvement package; it is not reconstructed, renumbered or overwritten. Prior 1.28 directories remain retained.

`apps/native-20` uses Tauri 2 with a Rust core and the existing reader frontend in a platform webview. `tools/local/prepare_native_20.py` prepares the actual shell and licensed text families without Git history, private data, raw archives, encyclopedia, canonical EPUB or mobile feed. A manifest records source/runtime hashes. Catalog dataset revision and all prior store keys remain unchanged. The 84-edition main catalog is retained; separately named Hebrew/Greek source and reading-aid volumes remain separate.

The native bridge supplies compile-target OS/architecture, plain-text clipboard writing, HTTP(S)-only external links and bounded exports to the application's own `exports` directory. Export file names cannot contain folders; existing files are never overwritten. Browser/PWA operation remains available, and browser platform recognition is explicitly a heuristic. The Rust target is authoritative only in the installed app. No device fingerprint or account is required.

## Build and review

Install Rust >=1.90 and the official platform prerequisites, then run `npm ci` in `apps/native-20`. Generate platform icons with `npm run tauri -- icon ../../releases/v2.0/icons/icon-512.png --output src-tauri/icons`, prepare assets, and run `npm run build`. Mobile projects are initialized using `npm run tauri -- android init --ci` or `npm run tauri -- ios init --ci` on a suitable host. These build actions do not install or publish the result.

Windows requires Microsoft C++ build tools/WebView2; macOS and iOS require Xcode, and mobile Android requires Android SDK/NDK/JDK. Official references: https://v2.tauri.app/start/prerequisites/ and https://v2.tauri.app/distribute/ . Dependencies are pinned at the app boundary, with generated lockfiles retained after resolution. Do not claim a platform build passed until its actual compiler result is inspected.

Desktop review installers may be unsigned; a macOS application build is not notarization. Android debug packages are development builds. An iOS simulator build is not an installable physical-device IPA, App Store or TestFlight publication. Signing credentials and distribution are separate decisions; none are inferred from the code request.

## Stores and parity limits

The native app has its own origin/container. It must not scrape or delete the browser profile or make a false promise of automatic data migration. Use explicit supported Notes/vocabulary backups. Browser bookmarks/private imports remain intact in their original browser. Do not clear user data during upgrade or uninstall testing.

Generated source/reading-volume text exports and PNGs can use the bounded native export bridge. File location is reported after the actual write. Mobile export/share experience, webview font shaping, audio/video, external study sources and physical-device behavior need explicit platform verification. Do not claim all platform parity from Chromium browser tests or Rust compilation alone.

## Source additions

WLC typography repair, the pinned public-domain eBible Salkinson–Ginsburg NT, historical Delitzsch source/written Latin and Hebrew/Modern Greek pronunciation estimates are described in `PRONUNCIATION-SOURCES.md`. Pronunciation aids are not speaker-reviewed phonetic editions. ABP remains external because no project redistribution/adaptation permission or expired ABP edition was located. The early printed LXX comparison note is research only and does not modify the separately owned LXXL project.

No merge, deployment, public Release, access change, store publication or formal PR approval is performed by this development line.
