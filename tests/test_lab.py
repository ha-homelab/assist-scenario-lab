import copy
import io
import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock
from contextlib import redirect_stderr, redirect_stdout
from xml.etree import ElementTree as ET

from assist_scenario_lab.core import (
    InputError,
    evaluate,
    import_ha,
    load_json,
    MAX_BYTES,
)
from assist_scenario_lab.cli import LANGUAGES, catalog, main, render_html, render_junit

ROOT = Path(__file__).resolve().parents[1]


def sample():
    return json.loads((ROOT / "examples/synthetic-pass.json").read_text())


class EvaluationTests(unittest.TestCase):
    def test_pass(self):
        result = evaluate(sample())
        self.assertEqual(result["status"], "pass")
        self.assertFalse(result["evidence_verified"])
        self.assertIsNone(result["groups"][0]["p95_audible_ms"])

    def test_protocol_is_not_audibility(self):
        result = evaluate(load_json(ROOT / "examples/synthetic-incomplete.json"))
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["sessions"][0]["protocol"], "pass")
        self.assertIn("audible", result["sessions"][0]["pending"])

    def test_error_dominates_other_success(self):
        data = sample()
        data["sessions"][0]["events"].append(
            {"stage": "error", "origin": "pipeline", "at_ms": 2000}
        )
        self.assertEqual(evaluate(data)["status"], "fail")

    def test_required_action_failure(self):
        self.assertEqual(
            evaluate(load_json(ROOT / "examples/synthetic-fail.json"))["status"], "fail"
        )

    def test_oversized_latency_fails(self):
        data = sample()
        data["requirements"]["max_audible_ms"] = 1000
        self.assertEqual(evaluate(data)["status"], "fail")

    def test_percentiles_and_evidence_are_separate(self):
        data = sample()
        base = data["sessions"][0]
        data["sessions"] = []
        for i in range(20):
            row = copy.deepcopy(base)
            row["id"] = "sample_" + str(i)
            row["events"][-1]["at_ms"] = 1000 + i * 10
            data["sessions"].append(row)
        group = evaluate(data)["groups"][0]
        self.assertEqual(group["p50_audible_ms"], 1090)
        self.assertEqual(group["p95_audible_ms"], 1180)
        data["sessions"][-1]["events"][-1]["origin"] = "operator"
        groups = evaluate(data)["groups"]
        self.assertEqual(len(groups), 2)
        self.assertTrue(all(g["p95_audible_ms"] is None for g in groups))

    def test_reject_invalid_numbers_and_types(self):
        for value in [True, -1, float("nan"), float("inf"), 10**1000, [], {}]:
            data = sample()
            data["sessions"][0]["events"][0]["at_ms"] = value
            with (
                self.subTest(value=type(value).__name__),
                self.assertRaises(InputError),
            ):
                evaluate(data)

    def test_method_invalid_type(self):
        data = sample()
        data["sessions"][0]["checks"]["audible"]["method"] = []
        with self.assertRaises(InputError):
            evaluate(data)

    def test_duplicate_stage_time_origin_request(self):
        for variant in ["duplicate", "order", "origin", "start"]:
            data = sample()
            events = data["sessions"][0]["events"]
            if variant == "duplicate":
                events.append(copy.deepcopy(events[-1]))
            if variant == "order":
                events[-1]["at_ms"] = 1
            if variant == "origin":
                events[-1]["origin"] = "pipeline"
            if variant == "start":
                events[0]["at_ms"] = 1
            with self.subTest(variant=variant), self.assertRaises(InputError):
                evaluate(data)

    def test_conflicting_audible_evidence(self):
        data = sample()
        data["sessions"][0]["checks"]["audible"] = {
            "result": "fail",
            "method": "operator",
        }
        with self.assertRaises(InputError):
            evaluate(data)

    def test_unknown_fields_rejected(self):
        data = sample()
        data["sessions"][0]["ip_address"] = "discard-me"
        with self.assertRaises(InputError):
            evaluate(data)

    def test_duplicate_session(self):
        data = sample()
        data["sessions"][1]["id"] = data["sessions"][0]["id"]
        with self.assertRaises(InputError):
            evaluate(data)


class InputTests(unittest.TestCase):
    def test_missing_or_empty_open_flags_rejected_before_open(self):
        with tempfile.TemporaryDirectory() as folder:
            regular = Path(folder) / "input.json"
            regular.write_text("{}")
            for flag in ("O_NOFOLLOW", "O_NONBLOCK"):
                for missing in (True, False):
                    file_os = SimpleNamespace(**vars(os))
                    file_os.open = mock.Mock(wraps=os.open)
                    if missing:
                        delattr(file_os, flag)
                    else:
                        setattr(file_os, flag, 0)
                    with (
                        self.subTest(flag=flag, missing=missing),
                        mock.patch("assist_scenario_lab.core.os", file_os),
                    ):
                        with self.assertRaises(InputError) as caught:
                            load_json(regular)
                        self.assertEqual(caught.exception.code, "unsupported_platform")
                        file_os.open.assert_not_called()

    def test_invalid_json_and_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "input.json"
            for raw in ['{"a":1,"a":2}', '{"a":NaN}', "[", "\x00", "[" * 2000]:
                p.write_text(raw)
                with self.subTest(raw=raw[:10]), self.assertRaises(InputError):
                    load_json(p)

    def test_symlink_fifo_size_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            regular = root / "x"
            regular.write_text("{}")
            link = root / "link"
            link.symlink_to(regular)
            fifo = root / "fifo"
            os.mkfifo(fifo)
            big = root / "big"
            big.write_bytes(b" " * (MAX_BYTES + 1))
            for p in [link, fifo, big, root, root / "missing"]:
                with self.subTest(path=p.name), self.assertRaises(InputError):
                    load_json(p)


class ImportTests(unittest.TestCase):
    def events(self):
        return load_json(ROOT / "examples/ha-events.synthetic.json")

    def test_discards_payload_and_infers_no_physical_success(self):
        events = self.events()
        events[-1]["data"] = None
        marker = "private-transcript-DO-NOT-EXPORT"
        events[1]["data"] = {"text": marker, "token": marker, "url": marker}
        result = import_ha(events, session="test", platform="test", synthetic=True)
        self.assertNotIn(marker, json.dumps(result))
        report = evaluate(result)
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["sessions"][0]["protocol"], "pass")
        self.assertIsNone(report["sessions"][0]["request_to_audible_ms"])

    def test_reject_missing_timezone_and_out_of_order(self):
        for stamp in ["2026-01-01T00:00:00", "2025-01-01T00:00:00Z", "bad"]:
            events = self.events()
            events[-1]["timestamp"] = stamp
            with self.subTest(stamp=stamp), self.assertRaises(InputError):
                import_ha(events, session="test", platform="test")

    def test_reject_two_runs(self):
        events = self.events()
        events.append(copy.deepcopy(events[-1]))
        with self.assertRaises(InputError):
            import_ha(events, session="test", platform="test")


class CliTests(unittest.TestCase):
    def invoke(self, args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(args)
        return code, out.getvalue(), err.getvalue()

    def test_exit_codes(self):
        for name, code in [("pass", 0), ("fail", 1), ("incomplete", 3)]:
            self.assertEqual(
                self.invoke(
                    [
                        "evaluate",
                        str(ROOT / f"examples/synthetic-{name}.json"),
                        "--format",
                        "json",
                    ]
                )[0],
                code,
            )
        self.assertEqual(self.invoke(["evaluate", "does-not-exist"])[0], 2)

    def test_unsupported_platform_reports_error_without_output(self):
        file_os = SimpleNamespace(**vars(os))
        file_os.O_NOFOLLOW = 0
        with mock.patch("assist_scenario_lab.core.os", file_os):
            for args in (
                ["evaluate", str(ROOT / "examples/synthetic-pass.json")],
                [
                    "import-ha", str(ROOT / "examples/ha-events.synthetic.json"),
                    "--session", "test", "--platform", "test",
                ],
            ):
                with self.subTest(command=args[0]):
                    code, out, err = self.invoke(args)
                    self.assertEqual(code, 2)
                    self.assertEqual(out, "")
                    self.assertIn("[unsupported_platform]", err)
                    self.assertNotIn(args[1], err)
            self.assertEqual(self.invoke(["--help"])[0], 0)

    def test_locales_keys_and_commands(self):
        for lang in LANGUAGES:
            self.assertEqual(set(catalog(lang)), set(catalog("en")))
            result = self.invoke(["--help", "--lang", lang])
            self.assertEqual(result[0], 0)
            self.assertIn("assist-lab", result[1])

    def test_machine_output_locale_independent(self):
        args = [
            "evaluate",
            str(ROOT / "examples/synthetic-pass.json"),
            "--format",
            "json",
        ]
        self.assertEqual(self.invoke(args)[1], self.invoke(args + ["--lang", "ru"])[1])

    def test_invalid_arguments(self):
        for args in [
            ["--bad"],
            ["--lang", "xx"],
            ["--lang"],
            ["--lang", "en", "--lang", "ru"],
            ["evaluate", "x", "--synthetic"],
        ]:
            self.assertEqual(self.invoke(args)[0], 2)

    def test_html_and_junit(self):
        report = evaluate(sample())
        page = render_html(report, catalog("ru"))
        self.assertIn("<svg", page)
        self.assertIn('lang="ru"', page)
        self.assertEqual(ET.fromstring(render_junit(report)).attrib["tests"], "2")
        report["sessions"][0]["id"] = "<script>alert(1)</script>"
        self.assertNotIn("<script>", render_html(report, catalog("en")))
        self.assertIn("&lt;script&gt;", render_html(report, catalog("en")))

    def test_report_exposes_api_only_policy_and_missing_evidence(self):
        data = sample()
        data["requirements"] = {}
        page = render_html(evaluate(data), catalog("en"))
        self.assertIn("Protocol completion only", page)
        report = evaluate(load_json(ROOT / "examples/synthetic-incomplete.json"))
        page = render_html(report, catalog("en"))
        self.assertIn("Audible timing missing", page)
        self.assertIn("Response audible", page)

    def test_no_path_or_content_in_error(self):
        result = self.invoke(["evaluate", "private-super-secret-file"])
        self.assertNotIn("private-super-secret", result[2])
        self.assertEqual(result[1], "")


if __name__ == "__main__":
    unittest.main()
