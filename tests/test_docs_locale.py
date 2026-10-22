"""Documentation commands work when Python's default text encoding is ASCII."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DocumentationLocaleTests(unittest.TestCase):
    def run_ascii(self, script, *args, cwd=ROOT):
        env = os.environ.copy()
        env.update(LC_ALL="C", PYTHONUTF8="0", PYTHONCOERCECLOCALE="0")
        result = subprocess.run(
            [sys.executable, str(script), *args],
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_documentation_checks_in_ascii_locale(self):
        self.run_ascii(ROOT / "tools/check_docs.py")
        self.run_ascii(ROOT / "tools/sync_wiki_guides.py", "--check")

    def test_wiki_generation_preserves_utf8_bytes_in_ascii_locale(self):
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory)
            shutil.copytree(ROOT / "docs", checkout / "docs")
            (checkout / "tools").mkdir()
            (checkout / "wiki").mkdir()
            script = checkout / "tools/sync_wiki_guides.py"
            shutil.copyfile(ROOT / "tools/sync_wiki_guides.py", script)
            self.run_ascii(script, cwd=checkout)
            generated = list((checkout / "wiki").glob("Guide*.md"))
            self.assertEqual(len(generated), 24)
            for page in generated:
                with self.subTest(page=page.name):
                    self.assertEqual(
                        page.read_bytes(), (ROOT / "wiki" / page.name).read_bytes()
                    )
            self.run_ascii(script, "--check", cwd=checkout)
