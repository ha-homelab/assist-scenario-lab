# Changelog

## Unreleased

No pending changes.

## 0.1.1b2 — 2026-10-20

- Refuse file input before opening it when the OS lacks `O_NOFOLLOW` or `O_NONBLOCK`, preserving the documented symlink/FIFO protections. Report `unsupported_platform` with CLI exit 2, and document the capability requirement in all supported languages.

## 0.1.1b1 — 2026-10-20

- Publish the first GitHub beta packages with matching source/package versions and SHA-256 checksums.
- Document the prerelease process and use the pinned build configuration as the source of truth.

- Update CI to pytest 9.0.3 (GHSA-6w46-j5rx-g56g) and the build backend to setuptools 83.0.0 (upstream fix for GHSA-h35f-9h28-mq5c).
- Document private reporting, review/release responsibilities, contribution rules and the current continuity limitation; include these policies in source distributions.

## 0.1.0 — 2026-10-15

Initial offline evaluator: strict canonical sessions, HA event-array import, separate protocol/action/audibility evidence, grouped latency summaries, text/JSON/HTML/JUnit, four-language CLI and README, English/Russian reference and wiki, synthetic examples and reproducible SVGs. No live collector or independently verified hardware measurements.
