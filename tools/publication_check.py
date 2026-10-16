#!/usr/bin/env python3
"""Audit the Git index without printing content; complementary to Gitleaks."""

from pathlib import PurePosixPath
import re
import subprocess
import sys

DENIED = {
    ".venv",
    ".terraform",
    ".storage",
    ".esphome",
    "__pycache__",
    "private",
    "backups",
    "recordings",
    "node_modules",
}
SUFFIXES = (
    ".pem",
    ".key",
    ".pfx",
    ".p12",
    ".bin",
    ".elf",
    ".uf2",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".log",
    ".wav",
    ".mp3",
    ".mp4",
    ".heic",
    ".tfstate",
    ".tfplan",
)


def violations(name, data):
    p = PurePosixPath(name.lower())
    result = []
    if (
        any(part in DENIED for part in p.parts)
        or p.name in {"secrets.yaml", "secrets.yml", ".env"}
        or p.name.endswith(SUFFIXES)
        or ".private." in p.name
        or p.name.startswith("credentials.")
        or (p.name.startswith(".env.") and p.name != ".env.example")
    ):
        result.append("private/runtime artifact")
    if len(data) > 2 * 1024 * 1024:
        result.append("file over 2 MiB; review separately")
    text = data.decode("utf-8", errors="replace")
    # A public source tree has no need to carry real private-network targets.
    if re.search(
        r"(?<![\d.])(?:192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(?![\d.])",
        text,
    ):
        result.append("private network address")
    if re.search(r"(?i)(?:https?|mqtts?)://[^\s/<>]+:[^\s/<>]+@", text):
        result.append("credential-bearing URL")
    return result


def main():
    failed = False
    raw = subprocess.check_output(["git", "ls-files", "--stage", "-z"])
    for entry in filter(None, raw.split(b"\0")):
        metadata, path = entry.split(b"\t", 1)
        mode, oid, stage = metadata.decode().split()
        name = path.decode("utf-8")
        # Never dereference symlinks or include embedded repositories in a release.
        if mode not in {"100644", "100755"} or stage != "0":
            print("BLOCKED index entry type:", repr(name))
            failed = True
            continue
        data = subprocess.check_output(["git", "cat-file", "blob", oid])
        for reason in violations(name, data):
            print("BLOCKED", repr(name) + ":", reason)
            failed = True
    if not failed:
        print("PASS: public source index policy (not a complete secret guarantee).")
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
