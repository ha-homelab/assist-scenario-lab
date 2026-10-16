#!/usr/bin/env python3
"""Rebuild original diagrams and the HTML screenshot source from synthetic fixtures."""

from pathlib import Path
import sys
from html import escape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from assist_scenario_lab import evaluate, load_json  # noqa: E402
from assist_scenario_lab.cli import render_html, catalog  # noqa: E402


def svg(title, subtitle, boxes, filename):
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="350" viewBox="0 0 1100 350" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(subtitle)}</desc><rect width="1100" height="350" fill="#f4f6f2"/><g font-family="sans-serif" fill="#15261e"><text x="40" y="55" font-size="27">{escape(title)}</text><text x="40" y="88" font-size="16">{escape(subtitle)}</text>'
    ]
    for i, (header, lines) in enumerate(boxes):
        x = 40 + i * 350
        parts.append(
            f'<rect x="{x}" y="125" width="320" height="175" rx="14" fill="#fff" stroke="#276c50" stroke-width="2"/><text x="{x + 18}" y="159" font-size="20">{escape(header)}</text>'
        )
        for j, line in enumerate(lines):
            parts.append(
                f'<text x="{x + 18}" y="{194 + j * 26}" font-size="15">{escape(line)}</text>'
            )
        if i < 2:
            parts.append(f'<text x="{x + 327}" y="222" font-size="22">→</text>')
    parts.append("</g></svg>")
    (ROOT / "assets" / filename).write_text("".join(parts) + "\n")


svg(
    "Three different evidence layers",
    "A completed pipeline cannot prove what a person heard.",
    [
        (
            "Protocol",
            [
                "run-start → run-end",
                "TTS ready is an API milestone",
                "No audio completion inference",
            ],
        ),
        (
            "Observed action",
            [
                "Expected intent checked",
                "HA state or operator observation",
                "State is not physical proof",
            ],
        ),
        (
            "Audible response",
            [
                "Operator or acoustic observation",
                "Explicit request-to-audible timing",
                "Unknown remains incomplete",
            ],
        ),
    ],
    "evidence-layers.svg",
)
svg(
    "Offline data flow",
    "No microphone capture, network client or device control is included.",
    [
        (
            "Private input",
            [
                "Single-run HA event array",
                "or canonical session manifest",
                "Keep raw data outside Git",
            ],
        ),
        (
            "Bounded validation",
            [
                "Strip every HA event payload",
                "Separate clock + evidence methods",
                "Reject malformed / mixed inputs",
            ],
        ),
        (
            "Reviewable output",
            [
                "JSON, HTML and JUnit",
                "Stable failure / pending codes",
                "Synthetic label stays visible",
            ],
        ),
    ],
    "architecture.svg",
)
report = evaluate(load_json(ROOT / "examples/synthetic-pass.json"))
page = render_html(report, catalog("en"))
(ROOT / "assets/synthetic-report.html").write_text(page)
chart = page[page.index("<svg") : page.index("</svg>") + 6]
chart = chart.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
(ROOT / "assets/synthetic-latency.svg").write_text(chart + "\n")
print("Rebuilt two architecture diagrams and synthetic latency report.")
