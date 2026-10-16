"""Four-language CLI; machine formats retain locale-independent keys and codes."""

from __future__ import annotations

import html
from importlib.resources import files
import json
import sys
from xml.etree import ElementTree as ET

from .core import InputError, evaluate, import_ha, load_json

LANGUAGES = ("en", "ru", "de", "es")


def catalog(lang: str) -> dict:
    return json.loads(
        files("assist_scenario_lab")
        .joinpath("locales", lang + ".json")
        .read_text(encoding="utf-8")
    )


def policy_text(report: dict, t: dict) -> str:
    required = report["requirements"]
    items = [
        t["label_" + k]
        for k in ("intent_correct", "action_observed", "audible")
        if required.get(k)
    ]
    if "max_audible_ms" in required:
        items.append(
            t["label_max_audible_ms"] + ": " + str(required["max_audible_ms"]) + " ms"
        )
    return "; ".join(items) or t["protocol_only"]


def details_text(session: dict, t: dict) -> str:
    return (
        "; ".join(t["reason_" + k] for k in session["failures"] + session["pending"])
        or t["clear"]
    )


def render_html(report: dict, t: dict) -> str:
    esc = html.escape
    rows = []
    for s in report["sessions"]:
        rows.append(
            "<tr>"
            + "".join(
                "<td>" + esc(str(v)) + "</td>"
                for v in [
                    s["id"],
                    s["platform"],
                    s["clock"] + " / " + (s["audible_timing_method"] or "none"),
                    t[s["status"]],
                    details_text(s, t),
                    s["request_to_tts_ready_ms"]
                    if s["request_to_tts_ready_ms"] is not None
                    else t["unknown"],
                    s["request_to_audible_ms"]
                    if s["request_to_audible_ms"] is not None
                    else t["unknown"],
                ]
            )
            + "</tr>"
        )
    bars = []
    with_audio = [
        s for s in report["sessions"] if s["request_to_audible_ms"] is not None
    ]
    maximum = max((s["request_to_audible_ms"] for s in with_audio), default=1) or 1
    for i, s in enumerate(with_audio[:50]):
        value = s["request_to_audible_ms"]
        y = 60 + i * 40
        width = value / maximum * 420
        bars.append(
            f'<text x="4" y="{y + 15}">{esc(s["id"][:18])}</text><rect x="185" y="{y}" width="{width:.1f}" height="20" fill="#16734e"/><text x="{195 + width:.1f}" y="{y + 15}">{value:g}</text>'
        )
    height = 90 + len(with_audio[:50]) * 40
    graph = (
        f'<h2>{esc(t["chart"])}</h2><p>{esc(t["chart_note"])}</p><svg viewBox="0 0 750 {height}" role="img" aria-label="{esc(t["chart"])}"><text x="4" y="20">{esc(t["synthetic"] if report["synthetic"] else t["declared"])}</text><text x="185" y="45">{esc(t["milliseconds"])}</text>'
        + "".join(bars)
        + "</svg>"
        if with_audio
        else ""
    )
    return f'''<!doctype html><html lang="{esc(t["lang"])}"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{esc(t["title"])}</title><style>body{{font:16px/1.6 system-ui;max-width:1000px;margin:40px auto;padding:0 20px;color:#202820}}table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;border-bottom:1px solid #ccc;padding:10px}}.scroll{{overflow:auto}}svg{{width:100%;min-width:500px}}svg text{{font:13px system-ui}}h1{{font-size:25px}}.note{{border-left:3px solid #16734e;padding:12px}}@media(prefers-color-scheme:dark){{body{{background:#161b16;color:#eee}}svg text{{fill:#eee}}}}</style><h1>{esc(t["title"])}</h1><p>{esc(t["synthetic"] if report["synthetic"] else t["declared"])}</p><p class="note">{esc(t["evidence_note"])}</p><p>{esc(t["status"])}: <strong>{esc(t[report["status"]])}</strong></p><p><strong>{esc(t["requirements"])}</strong>: {esc(policy_text(report, t))}</p><div class="scroll"><table><thead><tr>{"".join("<th>" + esc(t[k]) + "</th>" for k in ["session", "platform", "method", "status", "details", "tts_ms", "audio_ms"])}</tr></thead><tbody>{"".join(rows)}</tbody></table></div><div class="scroll">{graph}</div><p>{esc(t["percentile_note"])}</p></html>'''


def render_junit(report: dict) -> str:
    root = ET.Element(
        "testsuite",
        name="assist-scenario-lab",
        tests=str(len(report["sessions"])),
        failures=str(sum(s["status"] == "fail" for s in report["sessions"])),
        skipped=str(sum(s["status"] == "incomplete" for s in report["sessions"])),
    )
    for s in report["sessions"]:
        case = ET.SubElement(
            root,
            "testcase",
            name=s["id"],
            classname=s["platform"] + "." + s["scenario"],
        )
        if s["status"] == "fail":
            ET.SubElement(case, "failure", message=",".join(s["failures"]))
        elif s["status"] == "incomplete":
            ET.SubElement(case, "skipped", message=",".join(s["pending"]))
    return ET.tostring(root, encoding="unicode", xml_declaration=True)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    lang = "en"
    for i, arg in enumerate(args):
        if arg == "--lang" and i + 1 < len(args) and args[i + 1] in LANGUAGES:
            lang = args[i + 1]
    t = catalog(lang)
    values, flags, positional = {}, set(), []
    try:
        i = 0
        while i < len(args):
            arg = args[i]
            if arg in ("--help", "--synthetic"):
                if arg in flags:
                    raise InputError("arguments")
                flags.add(arg)
            elif arg in ("--lang", "--format", "--platform", "--session"):
                if arg in values or i + 1 == len(args) or args[i + 1].startswith("--"):
                    raise InputError("arguments")
                values[arg] = args[i + 1]
                i += 1
            elif arg.startswith("--"):
                raise InputError("arguments")
            else:
                positional.append(arg)
            i += 1
        if values.get("--lang", "en") not in LANGUAGES:
            raise InputError("arguments")
        if "--help" in flags or not args:
            print(t["help"])
            return 0
        if len(positional) != 2:
            raise InputError("arguments")
        command, path = positional
        fmt = values.get("--format", "text")
        if command == "import-ha":
            if (
                fmt not in ("text", "json")
                or "--session" not in values
                or "--platform" not in values
            ):
                raise InputError("arguments")
            report = import_ha(
                load_json(path),
                session=values["--session"],
                platform=values["--platform"],
                synthetic="--synthetic" in flags,
            )
            print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
            return 0
        if (
            command != "evaluate"
            or fmt not in ("text", "json", "html", "junit")
            or flags
            or values.keys() - {"--lang", "--format"}
        ):
            raise InputError("arguments")
        report = evaluate(load_json(path))
        if fmt == "json":
            print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
        elif fmt == "html":
            print(render_html(report, t))
        elif fmt == "junit":
            print(render_junit(report))
        else:
            print(t["title"])
            print(t["synthetic"] if report["synthetic"] else t["declared"])
            print(t["evidence_note"])
            print(t["requirements"] + ": " + policy_text(report, t))
            for session in report["sessions"]:
                print(
                    session["id"]
                    + ": "
                    + t[session["status"]]
                    + " — "
                    + details_text(session, t)
                )
            print(t["status"] + ": " + t[report["status"]])
        return {"pass": 0, "fail": 1, "incomplete": 3}[report["status"]]
    except InputError as exc:
        # Never echo source content, paths supplied by users, or an upstream exception.
        print(
            t["error"]
            + ": "
            + t.get(exc.code, t["invalid_file"])
            + " ["
            + exc.code
            + "]",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
