# Parallel Bible Reader

[Open the reader](https://kimble-365.github.io/-parallel-bible-reader/) · [Download ZIP](https://kimble-365.github.io/-parallel-bible-reader/parallel-bible-reader.zip)

A standalone English-interface Bible reader with original scripts, Latin transliterations, Finnish KR33/38 and World English Bible comparisons. No ChatGPT account is required. This distribution contains only the Bible reader.

## Use online or offline

Open the GitHub Pages site, or download `parallel-bible-reader.zip`, extract the entire archive and open `index.html` in Safari, Chrome or Edge. Keep `data/`, `catalog.js` and `reader.js` beside it. Texts load as local scripts, without a server or fetch/CORS dependency. The download link is for obtaining the package online; it need not be used again from an extracted package.

12 installed text editions and 12 Bible.is listening choices are available. Some text editions cover only the New Testament. Audio needs internet and is not included offline. Audio selection is independent of the displayed text. For editions whose Old Testament chapter coverage has not been verified, the link explicitly opens Matthew 1.

Choose Papyrus Yellow, Blue or Brown under Color theme, and Light or Dark under Display mode. Preferences are saved locally when browser storage is available. Direct links also accept `?theme=blue&mode=dark` (or `papyrus-yellow` / `brown`, `light` / `dark`).

Search selected languages in the current book or all available books. Search loads additional book files as needed. Text alignment follows source verse numbering; source verse ranges appear once. Mechanical transliteration is not pronunciation guidance. See the reader's sources section and LICENSES.md for attribution, adaptation notices and edition-specific licenses.

## GitHub Pages

For a branch deployment, publish the `main` branch from `/ (root)`. `.nojekyll` ensures static assets are served unchanged. No build, backend or credentials are required. All assets use relative paths and work under a repository subpath.
