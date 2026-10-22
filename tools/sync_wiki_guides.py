#!/usr/bin/env python3
"""Generate wiki guides from the translated documentation source pages."""

import argparse
import json
from pathlib import Path


def wiki_path(code):
    suffix = "" if code == "en" else "-" + ("RU" if code == "ru" else code)
    return Path("wiki") / ("Guide" + suffix + ".md")


def render_wiki_guides(root):
    catalog = json.loads((root / "docs/languages.json").read_text())
    pages = {}
    for item in catalog:
        code = item["code"]
        text = (root / "docs" / code / "guide.md").read_text()
        for language in catalog:
            text = text.replace(
                'href="../' + language["code"] + '/guide.md"',
                'href="' + wiki_path(language["code"]).name + '"',
            )
        text = text.replace(
            "../../assets/architecture.svg",
            "https://raw.githubusercontent.com/ha-homelab/assist-scenario-lab/main/assets/architecture.svg",
        )
        pages[wiki_path(code)] = text
    return pages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Report stale mirrors without writing"
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    stale = []
    for relative, expected in render_wiki_guides(root).items():
        path = root / relative
        if args.check:
            if not path.is_file() or path.read_text() != expected:
                stale.append(relative.as_posix())
        else:
            path.write_text(expected)
    if stale:
        raise SystemExit(
            "Stale wiki guides; run tools/sync_wiki_guides.py: " + ", ".join(stale)
        )
    print("PASS: 24 wiki guide mirrors " + ("verified" if args.check else "generated"))


if __name__ == "__main__":
    main()
