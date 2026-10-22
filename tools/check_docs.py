#!/usr/bin/env python3
"""Check documentation languages, relative links and original SVG syntax."""

from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote
from xml.etree import ElementTree as ET

from sync_wiki_guides import render_wiki_guides

root = Path(__file__).resolve().parents[1]
paths = [
    root / p
    for p in subprocess.check_output(["git", "ls-files", "-z"]).decode().split("\0")
    if p
]
errors = []
for name in (
    "README.md",
    "README.ru.md",
    "README.de.md",
    "README.es.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "wiki/Home.md",
    "wiki/_Sidebar.md",
):
    if not (root / name).is_file():
        errors.append("Missing " + name)
for path in paths:
    if path.suffix == ".svg":
        try:
            ET.parse(path)
        except ET.ParseError:
            errors.append("Invalid SVG " + str(path.relative_to(root)))
    if path.suffix != ".md":
        continue
    body = path.read_text(encoding="utf-8")
    links = re.findall(r'!?\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)', body)
    links += re.findall(r'href="([^"]+)"', body)
    for link in links:
        if link.startswith(("http:", "https:", "mailto:", "#")):
            continue
        dest = unquote(link.split("#")[0]).strip("<>")
        if not dest:
            continue
        target = path.parent / dest
        if "wiki" in path.relative_to(root).parts and not target.suffix:
            target = target.with_suffix(".md")
        if not target.exists():
            errors.append(
                str(path.relative_to(root)) + ": broken relative link " + dest
            )
# Full guide coverage is independent of the four runtime/README languages.
NAV = re.compile(
    r"\n*<!-- language-navigation:start -->.*?<!-- language-navigation:end -->\n*", re.S
)
FENCE = re.compile(r"^```[^\n]*\n.*?^```", re.M | re.S)
LINK = re.compile(r"!?\[[^\]]*\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)")
EXPECTED = set(
    "en ar bn cs de es fa fr he hi id it ja ko nl pl pt ru th tr uk vi zh-Hans zh-Hant".split()
)


def content(text):
    """Ignore navigation formatting without altering executable example bytes."""
    return NAV.sub("\n\n", text).strip()


def structure(text):
    prose = FENCE.sub("", text)
    return (
        re.findall(r"^(#{1,6}) ", prose, re.M),
        len(re.findall(r"^[-*] ", prose, re.M)),
    )


manifest = json.loads((root / "docs/translations.json").read_text(encoding="utf-8"))
catalog = json.loads((root / manifest["languages"]).read_text(encoding="utf-8"))
codes = [item["code"] for item in catalog]
if len(codes) != 24 or set(codes) != EXPECTED or manifest.get("version") != 1:
    errors.append("Invalid guide manifest or 24-language catalog")
original = content((root / manifest["source"]).read_text(encoding="utf-8"))
if hashlib.sha256(original.encode()).hexdigest() != manifest["source_sha256"]:
    errors.append(
        "English guide changed; review all translations and update source digest"
    )
for item in catalog:
    code = item["code"]
    expected_direction = "rtl" if code in {"ar", "fa", "he"} else "ltr"
    if item.get("dir", "ltr") != expected_direction or not item.get("label"):
        errors.append("Invalid language direction or label: " + code)
    path = root / "docs" / code / "guide.md"
    if not path.is_file():
        errors.append("Missing guide: " + code)
        continue
    text = path.read_text(encoding="utf-8")
    expected_links = [
        '<a href="../'
        + other["code"]
        + '/guide.md" lang="'
        + other["code"]
        + '" dir="'
        + other.get("dir", "ltr")
        + '">'
        + other["label"]
        + "</a>"
        for other in catalog
    ]
    navs = NAV.findall(text)
    if len(navs) != 1 or re.findall(r"<a\b[^>]*>.*?</a>", navs[0]) != expected_links:
        errors.append(code + ": incomplete guide language navigation")
    translated = content(text)
    if FENCE.findall(translated) != FENCE.findall(original):
        errors.append(code + ": fenced code differs from English")
    if Counter(re.findall(r"`([^`\n]+)`", translated)) != Counter(
        re.findall(r"`([^`\n]+)`", original)
    ):
        errors.append(code + ": inline code differs from English")
    if Counter(LINK.findall(translated)) != Counter(LINK.findall(original)):
        errors.append(code + ": link destinations differ from English")
    if structure(translated) != structure(original):
        errors.append(code + ": heading or list structure differs from English")
    if re.search(r"@@BLOCK\d+@@", translated):
        errors.append(code + ": unresolved authoring placeholder")
    if code in {"ar", "fa", "he"}:
        if f'<div dir="rtl" lang="{code}">\n\n' not in text:
            errors.append(code + ": missing RTL prose container")
        for block in FENCE.findall(translated):
            if '<div dir="ltr">\n\n' + block + "\n\n</div>" not in text:
                errors.append(code + ": missing LTR code container")
if all((root / "docs" / code / "guide.md").is_file() for code in codes):
    for relative, expected in render_wiki_guides(root).items():
        path = root / relative
        if not path.is_file() or path.read_text(encoding="utf-8") != expected:
            errors.append("Stale wiki guide: " + relative.as_posix())

if errors:
    raise SystemExit("\n".join(errors))
print("PASS: 24 complete guides, exact wiki mirrors, source digest, links and SVG XML.")
