"""Adds TWmod (.twmod) import support to a built reader release.

The CI rebuild copies the app files unchanged from the base release, so this
script patches the built release afterwards:

  <release>/twmod-import.js        copied from tools/twmod_web/
  <release>/index.html             loads twmod-import.js before bible-import.js
  <release>/bible-import.js        routes .twmod files to ReaderTwmod
  <release>/import-ui.js           accepts .twmod in the file picker
  <release>/import-sources.js      documents the TWmod source option

Idempotent: already-patched files are skipped. A missing patch anchor is an
error (exit 1) — the base release changed and this script needs updating.

Usage: python tools/apply_twmod_web.py [--release releases/v1.29]
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "twmod_web" / "twmod-import.js"


def patch(path: Path, anchor: str, replacement: str, marker: str) -> str:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return "skip"
    if anchor not in text:
        raise SystemExit(f"ANCHOR MISSING in {path.name}: {anchor[:70]}...")
    path.write_text(text.replace(anchor, replacement, 1), encoding="utf-8")
    return "patched"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", type=Path, default=ROOT / "releases" / "v1.29")
    args = ap.parse_args()
    rel = args.release
    version = rel.name.lstrip("v")  # v1.29 -> 1.29

    if not SOURCE.is_file():
        raise SystemExit(f"missing {SOURCE}")
    if not (rel / "index.html").is_file():
        raise SystemExit(f"not a built release directory: {rel}")

    results = {}

    target = rel / "twmod-import.js"
    if target.is_file() and target.read_bytes() == SOURCE.read_bytes():
        results["twmod-import.js"] = "skip"
    else:
        target.write_bytes(SOURCE.read_bytes())
        results["twmod-import.js"] = "copied"

    results["index.html"] = patch(
        rel / "index.html",
        f'<script src="bible-import.js?v={version}"></script>',
        f'<script src="twmod-import.js?v={version}"></script>'
        f'<script src="bible-import.js?v={version}"></script>',
        "twmod-import.js",
    )

    results["bible-import.js"] = patch(
        rel / "bible-import.js",
        "if(/\\.(bblx|bbli|sqlite|sqlite3|db)$/.test(name)){esword(bytes,c);continue}",
        "if(/\\.twmod$/i.test(name)){await ReaderTwmod.add(bytes,c);continue}"
        "if(/\\.(bblx|bbli|sqlite|sqlite3|db)$/.test(name)){esword(bytes,c);continue}",
        "ReaderTwmod",
    )

    results["import-ui.js"] = patch(
        rel / "import-ui.js",
        ".bblx,.bbli,.sqlite,.sqlite3,.db'",
        ".bblx,.bbli,.sqlite,.sqlite3,.db,.twmod'",
        ".twmod",
    )
    results["import-ui.js label"] = patch(
        rel / "import-ui.js",
        "field('Text / XML / SQLite file(s), up to 32 MB total','import-files')",
        "field('Text / XML / SQLite / TWmod file(s), up to 32 MB total','import-files')",
        "TWmod file(s)",
    )

    results["import-sources.js"] = patch(
        rel / "import-sources.js",
        "\n];",
        ",\n {id:'twmod',name:'TWmod module',url:'',"
        "formats:'Packed (ZIP) or plain SQLite .twmod Bible modules',"
        "note:'Select a .twmod module. Packed modules are unpacked in memory"
        " only — no temporary files are written to the device.'}\n];",
        "'twmod'",
    )

    for name, state in results.items():
        print(f"{state:8} {name}")
    print("twmod web support OK ->", rel)


if __name__ == "__main__":
    sys.exit(main())
