# Assist Scenario Lab

[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/15565/badge)](https://www.bestpractices.dev/projects/15565)

[English](README.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Español](README.es.md)

Evaluate recorded Home Assistant voice sessions without mistaking a completed API call for a correct action or an audible response. The CLI reads local JSON and writes reviewable text, JSON, HTML or JUnit. It does not connect to Home Assistant or control devices.

**Status: initial tested release, 0.1.0. All bundled timings are synthetic.** No satellite has been physically benchmarked by this release. Recorded observations are declarations; `evidence_verified` is always false.

![Three layers of evidence](assets/evidence-layers.svg)

## Install and run

Requires Python 3.11 or newer. From this checkout:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install .
assist-lab evaluate examples/synthetic-pass.json
assist-lab evaluate examples/synthetic-pass.json --format html > /tmp/assist-report.html
assist-lab evaluate examples/synthetic-incomplete.json --lang en
```

The last command intentionally exits **3**: the API finished, but audibility is unknown. Exit **0** means recorded requirements pass, **1** a requirement failed, and **2** invalid input. Nothing turns unknown physical evidence into success.

## What is implemented

- Strict bounded input, explicit evidence methods, error dominance and latency thresholds.
- An offline adapter for one exported HA Assist event array. All event payloads are discarded, including transcripts and generated-audio tokens.
- Separate summaries by platform, scenario, clock and audible observation method. Nearest-rank p95 is withheld below 20 observations; 20 is a display threshold, not proof of statistical confidence.
- Four-language CLI/help/reports; stable machine-readable codes in every locale.
- Synthetic pass, fail and incomplete fixtures, malformed-input tests and reproducible SVGs.

![Synthetic latency example, not a hardware benchmark](assets/synthetic-latency.svg)

[Rendered HTML preview](assets/report-preview.png) (generated from the synthetic example, not a live HA screenshot).

These example values describe fictitious `satellite_a` and `satellite_b`. They do not compare real products.

## Documentation

- [English guide](docs/en/guide.md): input contract, HA adapter, interpretation and troubleshooting.
- [Русское руководство](docs/ru/guide.md).
- [Wiki source](wiki/Home.md) and [published wiki](https://github.com/ha-homelab/assist-scenario-lab/wiki).
- [Contributing and translations](CONTRIBUTING.md), [security](SECURITY.md), [changelog](CHANGELOG.md).

## Development

```sh
python3 -m pip install -e .
python3 -m unittest discover -s tests -v
python3 tools/render_docs.py
```

MIT licensed. Not an official Home Assistant project. Build a live collector separately with explicit recording consent; this package only evaluates supplied data.

## Project maintenance

See [Contributing](CONTRIBUTING.md), [Security](SECURITY.md),
[Governance](GOVERNANCE.md), [Code of Conduct](CODE_OF_CONDUCT.md),
[Roadmap](ROADMAP.md), [Source releases](RELEASING.md), and
[Quality evidence](docs/quality.md).
