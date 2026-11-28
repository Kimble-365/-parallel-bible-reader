# Actual native review-package inspection

The nondeploying native workflow now reads its actual output package bytes before upload. It records each package SHA-256 and size, hashes APK/tar member contents, checks ARM64 ELF headers and Apple bundle identity/Mach-O headers, records symbolic/hard links without dereferencing, and obtains a Windows NSIS technical payload listing using 7-Zip without launching the installer. Generated package-inspection JSON files are included beside the exact review package and lock in each artifact.

Windows installer stub architecture is not the application's architecture. The listing must contain the expected Cargo/product executable name; listing-only Windows mode does not create per-payload-file hashes and its summary member count is not a payload count. APK filenames such as universal-debug do not establish multi-ABI delivery: the actual library headers provide that evidence. Bundle identifiers and versions come from the actual Apple Info.plist files.

The inspector never executes or extracts an application. A failed archive/listing command, unexpected bundle identity, missing Android manifest, wrong Android machine, duplicate/traversal entry or absent expected executable fails the check. Seven unit fixtures exercise these conditions and byte/header distinctions. The job selector reruns affected native jobs if inspection tools change.

This is static package evidence, not GUI/device/signature testing or complete linked/generated-component/licence clearance. Tauri frontend data may be embedded/compressed in executables, so an empty list of loose notice paths is not proof that no embedded notices exist. Rust, Gradle/AndroidX, native/system/SDK, fonts and Scripture notices need separate applicable assessment.

The measured progress report pins source/run/job, outer artifact, inner native package and binary identities separately. The dependency-source review ZIP remains a separate sidecar; locally accessible native notice/source integration and durable corresponding source availability are still required before public readiness. No signed release, physical iPad delivery, deployment or merge is authorized by these checks.
