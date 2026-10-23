# Development versions

The production reader remains at the repository root. Each development release has a separate numbered directory and retains its own URL. First release: **1.1**. Future releases: 1.2, 1.3, etc. The Scripture App Builder tool version (14.7) is separate from the application release number.

## 1.1 — Hindi pilot

- `v1.1/`: English landing page, source notices and project download.
- `v1.1/parallel.html`: 36 paired Hindi/Latin verses in John 3; text selector, font size and dark mode.
- `v1.1/app/`: actual Scripture App Builder 14.7 modern PWA; Hindi and Latin text collections. Its browser template does not yet implement parallel layouts; use the preview to read both together.
- `v1.1/hindi-pilot-1.1.zip`: portable SAB project, USFM, generated PWA data and build notes. No SAB installation, node_modules or credentials are included.

Audio is an external Bible.is link. No recordings or timings are bundled; the linked recording may be a different Hindi edition. Transliteration is mechanical and needs native-speaker review.

Hindi IRV 2019 © 2017, 2018, 2019 Bridge Connectivity Solutions, CC BY-SA 4.0. The original text is unchanged; Latin is an adaptation. Source: https://ebible.org/Scriptures/details.php?id=hin2017 . SAB modern PWA template: MIT, see v1.1/PWA-LICENSE.txt. No endorsement is implied.

Validation: actual production PWA build succeeded; Chromium loaded John 3 with no runtime errors; preview verified for all 36 pairs, text switching, dark mode and 390px mobile width; ZIP integrity, project version and USFM counts checked. Safari and Edge were not directly tested.
