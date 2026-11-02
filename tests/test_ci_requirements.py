"""The CI environment must follow reviewed tool inputs, not a stale lock."""

from importlib.metadata import version
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CIRequirementsTests(unittest.TestCase):
    def test_reviewed_tool_versions_are_locked_and_installed(self):
        lock = (ROOT / "requirements-ci.txt").read_text(encoding="utf-8")
        inputs = (ROOT / "requirements-ci.in").read_text(encoding="utf-8")
        requirements = [line.strip() for line in inputs.splitlines()
                        if line.strip() and not line.lstrip().startswith("#")]
        self.assertTrue(requirements, "CI tool inputs must not be empty")
        for requirement in requirements:
            with self.subTest(requirement=requirement):
                self.assertRegex(requirement, r"^[A-Za-z0-9_.-]+==[^ ;]+$")
                name, expected = requirement.split("==")
                self.assertRegex(lock, rf"(?m)^{re.escape(name)}=={re.escape(expected)}(?:\s|;|$)")
                self.assertEqual(version(name), expected,
                                 "Regenerate the hash lock and reinstall reviewed CI requirements")
