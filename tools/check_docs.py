#!/usr/bin/env python3
"""Check documentation languages, relative links and original SVG syntax."""

from pathlib import Path
import re
import subprocess
from urllib.parse import unquote
from xml.etree import ElementTree as ET

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
    body = path.read_text()
    for link in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)', body):
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
if errors:
    raise SystemExit("\n".join(errors))
print("PASS: language entry points, relative links and SVG XML.")
