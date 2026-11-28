# Native dependency archive and notice inventory

This audit covers the exact Cargo.lock for Reader 2.0. It is an inventory sidecar for distribution review, not release approval or a complete product notice bundle.

Run `cargo metadata --locked --format-version 1 --manifest-path apps/native-20/src-tauri/Cargo.toml`, save its JSON, then run `tools/local/audit_native_rights_20.py` with `--metadata`, `--lock`, `--cache` (Cargo registry/cache), `--source-commit` and `--out`. Original archives are never extracted into the repository. Each registry archive must match the locked checksum, and metadata identities must match the complete lock. The tool reads no user store or Scripture corpus and uses no network; Cargo obtains the original archives separately.

Outputs are DEPENDENCY-RIGHTS.json, ARCHIVED-NOTICES.txt and SHA256SUMS. Package/version, declared SPDX expression, repository, archive download URL/checksum, original VCS metadata and conventional archived notice paths/checksums are retained. Notice text bytes, including CRLF and Unicode, are preserved and deduplicated by SHA-256. Unsafe paths, changed/missing archives, metadata mismatch and unreadable notices fail. Notice symlinks are recorded unresolved without dereferencing.

The seven fixture tests exercise byte preservation/repeatability, tampering, stale metadata, traversal, notice links, nested LICENSES directories and missing-notice gate behavior. The contents-read-only native-rights-20.yml workflow runs them and repeats the full audit twice against freshly obtained locked archives, requiring byte-identical outputs. Its review artifact retains complete package mappings and original notice texts. The final progress report pins actual source/run/artifact identities and measured results.

## Limits and next review

A conventional notice-file inventory does not read all source headers, recover missing files from upstream repositories or choose license alternatives. A missing conventional notice is not a declaration that a package is unlicensed. A declared license-file outside its crate archive requires separate source review. VCS metadata can describe a dirty checkout; the original crate checksum is authoritative.

Determine which target/runtime/build components are distributed and fulfill applicable attribution/source-availability requirements, including MPL-2.0 components. Preserve notices from pinned upstream sources where they are absent from the archive. `--require-notices` exits 2 for unresolved conventional-notice cases; even a passing presence gate does not establish legal clearance or publication authority.

Rust/toolchain, native/system libraries, npm/build components, fonts and Scripture licenses need their own review. These Cargo sidecars are not automatically incorporated into desktop/Android/iOS packages. Native GUI/device execution, signing and public distribution remain distinct unfinished tasks. Do not treat review artifact creation as publishing a release.
