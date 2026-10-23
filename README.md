# Parallel Bible Reader

[Open the reader](https://kimble-365.github.io/-parallel-bible-reader/) · [Download ZIP](https://kimble-365.github.io/-parallel-bible-reader/parallel-bible-reader.zip)

A standalone English-interface Bible reader with original scripts, Latin transliterations, Finnish KR33/38 and World English Bible comparisons. No ChatGPT account is required. This distribution contains only the Bible reader.

## Latest development reader

[Open version 1.8](https://kimble-365.github.io/-parallel-bible-reader/releases/v1.8/) · [Offline ZIP 1.8](https://github.com/Kimble-365/-parallel-bible-reader/releases/download/v1.8/parallel-bible-reader-1.8.zip) · [Version history](releases/)

The separate development reader has four independently optional text slots, favorites and a language directory, experimental Urdu script mapping, written Latin for Hebrew/Greek and other scripts, opt-in English phoneme estimates, and 43 editions. Septuagint sources retain their own reference keys and independent chapter selectors. Historical Hebrew NT is installed; the latest modern Hebrew NT remains an external reading link pending rights and revision verification. Brenton is linked externally; French Giguet and historical Church Slavonic are installed. See [1.8 details and limits](releases/v1.8/README.md). Production remains the 27-edition reader below.

## Development brief

See [GOAL.md](GOAL.md) for the continuing project instructions and numbered roadmap, and [the architecture and language assessment](docs/research/architecture-and-language-plan.md) for the initial research. Planned features are not installed features.

## Use online or offline

Open the GitHub Pages site, or download `parallel-bible-reader.zip`, extract the entire archive and open `index.html` in Safari, Chrome or Edge. Keep `data/`, `catalog.js` and `reader.js` beside it. Texts load as local scripts, without a server or fetch/CORS dependency. The download link is for obtaining the package online; it need not be used again from an extracted package.

Installed text editions and verified Bible.is listening choices are available in their respective selectors. Use audio for reading language selects a verified recording in the reading language when one is available; the recording may use a different translation. Some text editions cover only the New Testament. The eight Telugu, Tamil, Kannada, Marathi, Malayalam, Bengali, Odia and Gujarati texts are full Bibles; their verified audio recordings cover the New Testament. Audio needs internet and is not included offline. Audio selection is independent of the displayed text. For editions whose Old Testament chapter coverage has not been verified, the link explicitly opens Matthew 1.

Choose Papyrus Yellow, Blue or Brown under Color theme, and Light or Dark under Display mode. Preferences are saved locally when browser storage is available. Direct links also accept `?theme=blue&mode=dark` (or `papyrus-yellow` / `brown`, `light` / `dark`).

Search selected languages in the current book or all available books. Search loads additional book files as needed. Text alignment follows source verse numbering; source verse ranges appear once. Mechanical transliteration is not pronunciation guidance. See the reader's sources section and LICENSES.md for attribution, adaptation notices and edition-specific licenses.

## Reading tools

The reader remembers the primary and comparison editions, last chapter and verse, text display, text size and audio choice in this browser. A shared passage link overrides the saved reading location and identifies its primary edition. Use Original, Latin or Both under Reading appearance; Latin-script texts are shown once. A− / A+ adjust reading size, and Reading mode hides surrounding controls until you exit it (Escape also exits).

Use ☆ beside a verse to bookmark it. Bookmarks and the seven-reading Start here path are saved on this device only. Each Bible book has a short About guide, clearly separate from scripture. The ↗ button opens verse sharing: copy text, copy an edition-aware link, or use device sharing where supported. If clipboard access is blocked, the text stays available for manual copying. Offline ZIP links can point to the public reader. No account is needed; clearing browser data removes saved progress and bookmarks.

## GitHub Pages

Publish the `main` branch from `/ (root)`. `.nojekyll` ensures static assets are served unchanged. No build, backend or credentials are required. All assets use relative paths and work under a repository subpath.

Coverage: 27 installed text editions and 30 verified audio choices. Recent additions: Chambeali, Gaddi, Kulvi, Kulvi Outer Seraji, Pahari Mahasui, Nepali ULB, Arabic-script Urdu OUCV, and full Telugu, Tamil, Kannada, Marathi, Malayalam, Bengali, Odia and Gujarati IRV Bibles. Urdu OUCV includes ICU orthographic Latin conversion; unwritten vowels are not reconstructed.

## Installed editions

| Edition | Coverage | Original script | Latin conversion |
| --- | --- | --- | --- |
| Hindi — IRV 2019 | Full Bible | Devanagari | Mechanical transliteration |
| Punjabi | Full Bible | Gurmukhi | Mechanical transliteration |
| Haryanvi | New Testament | Devanagari | Mechanical transliteration |
| Urdu (Devanagari) | Full Bible | Devanagari | Mechanical transliteration |
| Dogri | New Testament | Devanagari | Mechanical transliteration |
| Kangri | New Testament | Devanagari | Mechanical transliteration |
| Bilaspuri | New Testament | Devanagari | Mechanical transliteration |
| Mandeali | New Testament | Devanagari | Mechanical transliteration |
| Mahasu pahari — Baghlayani | New Testament | Devanagari | Mechanical transliteration |
| Bhadrawahi | New Testament | Devanagari | Mechanical transliteration |
| KR33/38 — Finnish | Full Bible | Latin | Original Latin text |
| WEB — English | Full Bible | Latin | Original Latin text |
| Bengali — IRV 2019 | Full Bible | Bengali | Mechanical transliteration |
| Pahari Mahasui | New Testament | Devanagari | Mechanical transliteration |
| Chambeali | New Testament | Devanagari | Mechanical transliteration |
| Gaddi | New Testament | Devanagari | Mechanical transliteration |
| Gujarati — IRV 2019 | Full Bible | Gujarati | Mechanical transliteration |
| Kannada — IRV 2019 | Full Bible | Kannada | Mechanical transliteration |
| Kulvi | New Testament | Devanagari | Mechanical transliteration |
| Kulvi — Outer Seraji | New Testament | Devanagari | Mechanical transliteration |
| Malayalam — IRV 2019 | Full Bible | Malayalam | Mechanical transliteration |
| Marathi — IRV 2019 | Full Bible | Devanagari | Mechanical transliteration |
| Nepali — Unlocked Literal Bible | Full Bible | Devanagari | Mechanical transliteration |
| Odia — IRV | Full Bible | Oriya | Mechanical transliteration |
| Tamil — IRV 2019 | Full Bible | Tamil | Mechanical transliteration |
| Telugu — IRV 2019 | Full Bible | Telugu | Mechanical transliteration |
| Urdu — Open Contemporary Version (Arabic script) | Full Bible | Arabic | ICU orthographic; unwritten vowels not reconstructed |

## Listening links

Recordings are streamed from Bible.is and are not bundled in the ZIP. Text and audio may use different translations.

- [Hindi — Indian Revised Version](https://live.bible.is/bible/HINDPI/GEN/1)
- [Awadhi - Easy-to-Read Version](https://live.bible.is/bible/AWAWTC/MAT/1)
- [Awadhi - New India Bible Version (Pavithar Bible)](https://live.bible.is/bible/AWAIBS/MAT/1)
- [बाइबल भोजपुरी पुराना संस्करण](https://live.bible.is/bible/BHOROV/MAT/1)
- [Braj Bhasha - New Life Computer Institute](https://live.bible.is/bible/BRADPI/MAT/1)
- [Marwari - New Life Computer Institute](https://live.bible.is/bible/RWRDPI/MAT/1)
- [New Life Computer Institute](https://live.bible.is/bible/MTRNLC/MAT/1)
- [Wycliffe Bible Tranlsators, Inc.](https://live.bible.is/bible/MAIWBT/MAT/1)
- [2014 Asian Sahyogi Sanstha India Gorakhpur, (U.P.)](https://live.bible.is/bible/MAGSSI/MAT/1)
- [Garhwali Bible (गढ़वाली बाइबिल)](https://live.bible.is/bible/GBMDPI/MAT/1)
- [Soriyali Bible](https://live.bible.is/bible/KFYDPI/MAT/1)
- [Wycliffe Bible Translators, Inc.](https://live.bible.is/bible/LBJWBT/MAT/1)
- [Chambeali — Chambeali Bible (चम्बयाळी बाइबिल)](https://live.bible.is/bible/CDHDPI/MAT/1)
- [Gaddi — DPI Version](https://live.bible.is/bible/GBKDPI/MAT/1)
- [Kulvi — Kulvi Bible (कुल्वी बाइबिल)](https://live.bible.is/bible/KFXDPI/MAT/1)
- [Kulvi — Outer Seraji — Kulvi Outer Seraji Bible](https://live.bible.is/bible/KFXKOS/MAT/1)
- [Pahari Mahasui — Pahari, Mahasu - The Love Fellowship](https://live.bible.is/bible/BFZDPI/MAT/1)
- [Nepali — New Revised Version — New Revised Version](https://live.bible.is/bible/NPINRV/MAT/1)
- [Nepali — DPI — Nepali Unlocked Literal Bible (ULB)](https://live.bible.is/bible/NPIDPI/MAT/1)
- [Kashmiri — BSI — Kashmiri - Bible Society of India](https://live.bible.is/bible/KASBSI/MAT/1)
- [Urdu — Indian Revised Version — Indian Revised Version](https://live.bible.is/bible/URDIRV/MAT/1)
- [Urdu — Easy-to-Read Version — پڑھنے کے لئے آسان](https://live.bible.is/bible/URDWTC/MAT/1)
- [Telugu — Indian Revised Version — Indian Revised Version](https://live.bible.is/bible/TELDPI/MAT/1)
- [Tamil — Indian Revised Version — Indian Revised Version (Davar Audio)](https://live.bible.is/bible/TAMDPI/MAT/1)
- [Kannada — Indian Revised Version — Indian Revised Version](https://live.bible.is/bible/KANDPI/MAT/1)
- [Marathi — Indian Revised Version — Indian Revised Version](https://live.bible.is/bible/MARDPI/MAT/1)
- [Malayalam — Indian Revised Version — Indian Revised Version](https://live.bible.is/bible/MALDPI/MAT/1)
- [Bengali — Indian Revised Version — Indian Revised Version](https://live.bible.is/bible/BENDPI/MAT/1)
- [Odia — Indian Revised Version — Indian Revised Version (Davar Audio)](https://live.bible.is/bible/ORYDPI/MAT/1)
- [Gujarati — Indian Revised Version — Indian Revised Version](https://live.bible.is/bible/GUJDPI/MAT/1)

## Source rights

Edition-specific copyright and attribution notices are in LICENSES.md and in the reader. The reader code MIT license does not replace the scripture licenses.
