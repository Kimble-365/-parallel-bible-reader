# Reader 2.0 — verified review builds

8 November 2026. These are **development review artifacts**, not a production deployment or a signed public release. Version 1.29 remains reserved. The native applications use a Rust/Tauri host and the platform webview.

| Platform | Actual build | Download |
| --- | --- | --- |
| Windows PC x64 | Unsigned NSIS installer | [Windows review artifact](https://github.com/Kimble-365/-parallel-bible-reader/actions/runs/42504060531/artifacts/13626264319) |
| Apple Silicon Mac | Unsigned `.app` in a tar.gz preserving permissions/symlinks | [Apple Silicon review artifact](https://github.com/Kimble-365/-parallel-bible-reader/actions/runs/42504060531/artifacts/13627371340) |
| Intel Mac | Unsigned `.app` in a tar.gz preserving permissions/symlinks | [Intel Mac review artifact](https://github.com/Kimble-365/-parallel-bible-reader/actions/runs/42504060531/artifacts/13626399196) |
| Android ARM64 | Debug APK, not a Play Store release | [Android review artifact](https://github.com/Kimble-365/-parallel-bible-reader/actions/runs/42504608301/artifacts/13626224843) |
| iOS | ARM64 simulator application; **not an installable physical iPad IPA** | [iOS simulator artifact](https://github.com/Kimble-365/-parallel-bible-reader/actions/runs/42504060531/artifacts/13627670181) |
| Web/offline reader and reading volumes | Reproducible reader ZIP, reports, twelve complete UTF-8 volume exports | [Web and reading-volume review artifact](https://github.com/Kimble-365/-parallel-bible-reader/actions/runs/42504060531/artifacts/13626628980) |

GitHub artifact downloads may require signing in. Artifacts are retained until **22 November 2026**. The downloaded artifact ZIP is a container: locate the installer, Mac tar.gz, Android APK, simulator tar.gz or reader ZIP inside it. Artifact ZIP sizes/digests and exact source/run identities are recorded in [native-20-build-audit.json](native-20-build-audit.json). The source is retained independently of artifact expiry.

The native application code is commit `620a78efd3507f28f757d773c1b920ce1f5b42a1`. The Android workflow correction is `ce499a4e04cd5d7f3df87dcd5664c2acdd0bb801`; it changes SDK setup/check selection and progress, not application/source bytes. Successful desktop/iOS/browser/tool jobs are in [run 42504060531](https://github.com/Kimble-365/-parallel-bible-reader/actions/runs/42504060531); its obsolete failed Android setup is superseded by the successful Android job in [run 42504608301](https://github.com/Kimble-365/-parallel-bible-reader/actions/runs/42504608301). The complete inherited suite also passed in [run 42504608237](https://github.com/Kimble-365/-parallel-bible-reader/actions/runs/42504608237).

## What was verified

All five target builds completed. Rustfmt and Clippy passed; Rust URL/export-name tests passed on Windows and Apple Silicon. PowerShell **7.6.9** executed the tool-inspection script on Windows and Mac. Rust/Cargo 1.92.0, Node/Python, Java/SDK/NDK, Xcode, SQLite/Unicode tooling, Playwright Chromium/Firefox/WebKit, npm audit and Cargo audit are active in CI. Cargo audit returned success with five documented warnings from Linux-only dependencies; each warning crate is absent from all five requested target trees. No advisory ignore configuration was added.

The actual 2.0 reader passed Chromium, Firefox and WebKit startup/Shema/mobile/store checks. The extracted reader ZIP passed all 84 representative edition loads, exact file/source hashes, font/Notes/highlight/PNG/Pray and offline/gzip checks. Two ZIP builds were byte-identical: **174,764,530 bytes**, 2,258 files, SHA-256 `a701b268f15ba22e3a3189ab3d804bd657227d6a8de4cffc1a5f5e821142f3c3`.

The twelve source/Latin reading volumes contain 29,322,134 bytes and preserve each source's actual row coverage. Hebrew uses current Israeli reading estimates and Greek uses Modern Greek estimates; these are UTF-8 reading files, **not human audio recordings or linguistically approved phonetic editions**. Delitzsch and Salkinson originals remain separately identified. ABP remains external because redistribution/adaptation rights were not established. All 84 main edition identities, original corpus bytes, 1.28 files, incoming 1.29 and user-store keys remain preserved.

## Remaining verification and release decisions

Compiler success and mocked bridge tests do not verify native GUI behavior on physical devices. Next work is native runtime smoke testing, mobile export/share usability, explicit backup/import behavior and the native distribution notices/source-offer audit. Pronunciation estimates still need linguistic review. Browser and native profiles are separate; there is no automatic migration or deletion of browser notes/bookmarks/private imports.

Unsigned review apps are not notarized/signed public desktop releases. Physical iPad signing/provisioning, Android production signing, store publication and production hosting are separate decisions. No merge, deployment, public GitHub Release, access change or formal PR approval was performed. Production remains `89afb00cfa94b7630bf8e48419d95d73bd5f5181`.

For PowerShell 7, the repository includes `tools/local/reader_native_20.ps1`: `-Task Tools`, `-Task Check`, or `-Task Build`. Build compiles an unsigned host app; it does not install or publish it.
