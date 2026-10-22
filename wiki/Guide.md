# Recorded voice scenario evaluation

<!-- language-navigation:start -->
<p dir="ltr">
<a href="Guide.md" lang="en" dir="ltr">English</a> ·
<a href="Guide-ar.md" lang="ar" dir="rtl">العربية</a> ·
<a href="Guide-bn.md" lang="bn" dir="ltr">বাংলা</a> ·
<a href="Guide-cs.md" lang="cs" dir="ltr">Čeština</a> ·
<a href="Guide-de.md" lang="de" dir="ltr">Deutsch</a> ·
<a href="Guide-es.md" lang="es" dir="ltr">Español</a> ·
<a href="Guide-fa.md" lang="fa" dir="rtl">فارسی</a> ·
<a href="Guide-fr.md" lang="fr" dir="ltr">Français</a> ·
<a href="Guide-he.md" lang="he" dir="rtl">עברית</a> ·
<a href="Guide-hi.md" lang="hi" dir="ltr">हिन्दी</a> ·
<a href="Guide-id.md" lang="id" dir="ltr">Bahasa Indonesia</a> ·
<a href="Guide-it.md" lang="it" dir="ltr">Italiano</a> ·
<a href="Guide-ja.md" lang="ja" dir="ltr">日本語</a> ·
<a href="Guide-ko.md" lang="ko" dir="ltr">한국어</a> ·
<a href="Guide-nl.md" lang="nl" dir="ltr">Nederlands</a> ·
<a href="Guide-pl.md" lang="pl" dir="ltr">Polski</a> ·
<a href="Guide-pt.md" lang="pt" dir="ltr">Português</a> ·
<a href="Guide-RU.md" lang="ru" dir="ltr">Русский</a> ·
<a href="Guide-th.md" lang="th" dir="ltr">ไทย</a> ·
<a href="Guide-tr.md" lang="tr" dir="ltr">Türkçe</a> ·
<a href="Guide-uk.md" lang="uk" dir="ltr">Українська</a> ·
<a href="Guide-vi.md" lang="vi" dir="ltr">Tiếng Việt</a> ·
<a href="Guide-zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> ·
<a href="Guide-zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

## Installation and boundaries

Install from a checkout with `python3 -m pip install .` in a virtual environment. Python 3.11+ is supported. There are no runtime dependencies beyond Python. `assist-lab --help --lang en` lists commands; `ru`, `de` and `es` also work. The module entry point is `python3 -m assist_scenario_lab`.

File loading requires the OS flags `O_NOFOLLOW` and `O_NONBLOCK`, available on Linux and macOS. Without either, the CLI returns exit 2 with `unsupported_platform` before opening input. The in-memory Python evaluation and import APIs do not require these flags.

This is an offline evaluator, not a satellite firmware, acoustic detector, live collector, HA integration or complete benchmark. Run actual product UAT with the appropriate firmware tools. Supply the resulting bounded evidence to this tool only after reviewing privacy.

## Canonical input

Start from `examples/synthetic-pass.json`. The root requires `schema: assist-scenario-lab/v1`, boolean `synthetic`, a `requirements` object and 1–500 `sessions`. Unknown fields are rejected. A session has a unique `id`, `platform`, `scenario`, `clock`, `events` and `checks`. IDs are 1–64 ASCII letters, digits, underscores or hyphens; start with a letter or digit. Use pseudonyms, not room names, addresses or device identifiers.

`clock` is `relative_monotonic` or `utc_derived`. Events contain `stage`, `at_ms`, `origin`. Times are finite, non-negative, at most 12 hours, ordered nondecreasing. The first event is `request` at zero. A stage occurs once. Supported stages: `request`, `wake_detected`, `stt_end`, `intent_end`, `tts_ready`, `protocol_end`, `playback_started`, `playback_finished`, `audible_start`, `error`. Different pipelines may stream; there is deliberately no fixed ordering between TTS and playback beyond chronological timestamps.

Origins are `pipeline`, `satellite`, `operator` and `acoustic`. Only `operator` or `acoustic` can originate `audible_start`. Every session must supply all three checks: `intent_correct`, `action_observed`, `audible`. Each has `result` (`pass`, `fail`, `unknown`) and `method`. Unknown requires `none`. Other valid methods are `operator`/`intent_assertion` for intent, `operator`/`ha_state` for action, `operator`/`acoustic` for audibility. An audible timestamp requires a passing audible check. The tool verifies consistency, not truth.

Requirements may enable any of the three checks and optionally `max_audible_ms`. Omitted/false checks are not required: an API-only policy can pass without physical evidence and must be labelled as such. The bundled examples require all checks. A pipeline error always fails. Missing `protocol_end` is incomplete. A required failure dominates unknown observations. Latency over the threshold fails; absent required latency is incomplete.

## Importing an HA run

The adapter consumes one **array of event objects**, not a full WebSocket log or a diagnostics ZIP. Extract each event body locally. Objects have exactly `type`, `timestamp`, `data`; data may be an object or null. Timestamps must be timezone-aware ISO 8601. Start with `run-start`, preserve chronological order and do not mix runs. Repeated mapped stages are rejected.

```sh
assist-lab import-ha examples/ha-events.synthetic.json --session demo --platform demo --synthetic > /tmp/imported.json
assist-lab evaluate /tmp/imported.json --format json
```

The second command intentionally returns 3. `run-end` maps to `protocol_end`, not physical success. `tts-end` maps to `tts_ready`, not audible sound. All `data` is discarded, including transcripts, input text, errors, TTS URLs/tokens and pipeline metadata. Start/progress/VAD events are recognized but not retained. Converted times use `utc_derived`: wall-clock subtraction is not a monotonic latency measurement and can be affected by clock adjustment. All three physical/semantic checks remain unknown.

## Reports and comparison

`--format text|json|html|junit` chooses the report. Shell redirection writes the result to a chosen local path. The CLI never overwrites an input itself. Exit 0: recorded requirements passed; 1: failed; 2: invalid input/arguments; 3: incomplete. JUnit represents incomplete sessions as skipped; CI must still honor exit 3.

JSON groups use platform + scenario + clock + audible timing method. Never compare separate clocks or human and acoustic observations as interchangeable measurements. p50/p95 use nearest rank. p95 is null below 20 samples; 20 is a reporting threshold, not evidence of statistical confidence. Failed sessions with observed audio remain in the latency sample population and their failure count remains visible. Do not cherry-pick only passing trials. No raw audio or transcript is exported. IDs can still disclose information, so review them.

The HTML lists all sessions and charts the first 50 audible observations, using a shared scale. Read each row's platform/method; the overview is not a statistical ranking. `evidence_verified: false` is always present. `synthetic: false` means the author did not mark the run synthetic, not that hardware was independently validated.

## Collecting meaningful evidence

Define an expected intent and target before running a trial. Specify the start event consistently: pipeline request is not necessarily the beginning of the spoken phrase. Keep an external trial record with software versions, language, network conditions, microphone and speaker placement, observer method and trial count. Use an appropriate acoustic measurement for precise audible timing; do not substitute the first network chunk. Record failures, timeouts and missing evidence. This package does not perform acoustic synchronization or consent management.

## Troubleshooting

- `object_fields`: compare keys with the canonical fixture; a full diagnostics dump is not accepted.
- `ha_timestamp` / `time_order`: export one run, include timezones, inspect clock corrections. Do not reorder events to manufacture latency.
- `stage`: a stage is unknown or duplicated; check whether two runs were concatenated.
- `audible_origin` / `conflicting_audible`: playback metadata cannot stand in for hearing sound.
- Exit 3 after a successful API: expected until required observations are recorded.
- `unsupported_platform`: the OS lacks `O_NOFOLLOW` or `O_NONBLOCK`; use an environment that provides both (Linux or macOS). Input is refused before opening it, rather than weakening symlink or FIFO checks.
- `file_size_type`: regular UTF-8 JSON only, at most 2 MiB. Directories, FIFOs and final-component symlinks are rejected. Parent directory symlinks are not a sandbox boundary.
- `number`: no negative, non-finite, boolean or over-12-hour timestamps.

Errors print a translated summary and stable code, not source contents or local paths. The public examples are entirely synthetic. Keep exports outside this checkout, preferably in a private temporary directory.

## Architecture, translations and sources

![Offline flow](https://raw.githubusercontent.com/ha-homelab/assist-scenario-lab/main/assets/architecture.svg)

`core.py` handles pure validation/import/evaluation; `cli.py` renders formats; `locales/*.json` contains four catalogs. Tests require catalog key parity. Machine keys and diagnostic codes are not translated. Full guides cover the 24 ha-homelab documentation languages; CLI and README coverage remains English, Russian, German and Spanish. Contribute additional reference translations with parity tests and reviewed examples.

Protocol mapping checked against [Home Assistant Assist documentation](https://developers.home-assistant.io/docs/voice/pipelines/) and [HA 2026.10.0 event models](https://github.com/home-assistant/core/blob/2026.10.0/homeassistant/components/assist_pipeline/models.py). Satellite lifecycle is documented in [the official entity guide](https://developers.home-assistant.io/docs/core/entity/assist-satellite/). These upstream APIs do not promise acoustic verification; separating it here is a design decision.
