# Parallel Bible Reader 2.0 — native development

New Rust/Tauri application line for Windows and Mac, with optional Android/iPad/iOS targets. 1.29 remains reserved for the separate unreceived improvement package. Prior 1.28 files are retained. No merge, public Release, installation or deployment is implied.

The app reuses the 84-edition main catalog and existing user-store keys, plus separate source/Latin reading volumes. Hebrew WLC typography is handled without changing original source bytes. Salkinson/Delitzsch and pronunciation methods/rights are documented in PRONUNCIATION-SOURCES.md. ABP remains external pending appropriate rights.

See NATIVE-2.0.md and apps/native-20 for build targets, storage boundaries, exports, platform detection and verification limits. Browser checks and actual native build results must be reported separately.
