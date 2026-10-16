# Quality and security evidence

The [Check workflow](../.github/workflows/check.yml) runs on every pull request
and main-branch push. It installs the package, runs Ruff E4/E7/E9/F diagnostics,
runs the automated tests, checks relative documentation links and SVG syntax,
builds an sdist and wheel, and scans the full Git history using Gitleaks with
redacted output. Failures must be investigated before release; green checks are
bounded evidence, not proof that every defect is absent.

The tests exercise this offline voice-scenario evidence evaluator with synthetic inputs and negative cases.
See [the interface guide](../docs/en/guide.md) and [security policy](../SECURITY.md) for
boundaries. No whole-repository coverage percentage, fuzzing campaign, complete
secure-design assurance case, signed release or independent continuity is claimed.
English, Russian, German and Spanish CLI catalogs and README entry points are
maintained with parity checks; detailed translations have their documented scope.

## Dependency review on 2026-10-16

CI now uses pytest 9.0.3, which fixes local temporary-directory handling in
[GHSA-6w46-j5rx-g56g](https://github.com/advisories/GHSA-6w46-j5rx-g56g).
This concerns test tooling on a shared UNIX host, not a demonstrated remote flaw
in the offline application. Build metadata requires setuptools 83.0.0, which
contains the upstream Unicode MANIFEST pattern normalization
[fix](https://github.com/pypa/setuptools/commit/dd9f436a36486b4cb8a4c70a2321548b0be09b8f)
for [GHSA-h35f-9h28-mq5c](https://github.com/advisories/GHSA-h35f-9h28-mq5c).
The advisory's fixed-version field may lag the released upstream fix. Source
builds must still be checked for unwanted files; version changes alone do not
validate artifact contents.

The primary maintainer has personally confirmed familiarity with secure-design
principles and common Python/network-application vulnerabilities. The maintainer
also confirms no bug, enhancement or vulnerability reports outside GitHub in the
preceding 12 months. These are maintainer attestations, not automated test results.
The public issue history and current security findings must also be checked when
refreshing the badge assessment.
