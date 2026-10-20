# Source builds and releases

The public Git repository is the source of truth. Clone it over GitHub HTTPS and
record `git rev-parse HEAD` with test results. The package version in
`pyproject.toml`, source `__version__` and root `version` must agree. A full
40-character Git commit identifies a unique development snapshot. Entries under
`Unreleased` in CHANGELOG.md describe development changes, not another published
release. Existing release notes remain available in that file.

Use the Python version in [the Check workflow](.github/workflows/check.yml) and
follow [CONTRIBUTING.md](CONTRIBUTING.md) to install the source and its test tools.
Build with `python -m pip install build==1.3.0` then
`python -m build --outdir dist`. The reviewed build backend is pinned in
`pyproject.toml` under `build-system.requires`; use that pin rather than a separate
version in documentation.
The standard build creates an sdist and a wheel from that sdist. Source archives
include the license, interface guides, tests and contribution/security policies.
No private files, credentials or real household exports belong in an artifact.

Before publishing a new release, the maintainer must run the complete Check
workflow, inspect its test/build/static-analysis/secret-scan results and review
all open findings. For a numbered release, update the package, source `__version__`
and root `version` consistently, move the relevant changelog entries into a
versioned section, and create a new immutable `v<package-version>` tag. Never
reuse a release tag. Stable versions use `X.Y.Z`; betas use the Python prerelease
form `X.Y.ZbN` (for example, package `0.1.1b1` and tag `v0.1.1b1`). Mark beta
releases as GitHub prereleases, not the latest stable release. Security releases
include available advisory identifiers and upgrade notes.
Use semantic versioning; breaking public report/schema behavior requires an
explicit compatibility decision and documented migration instructions.

Publish the wheel and source archive produced by the same clean source revision,
plus `SHA256SUMS` containing their SHA-256 hashes. Inspect both archives, install
the wheel in a fresh environment and check the CLI version and synthetic examples
before uploading. Release notes must identify the source commit and successful
Check run. These checksums identify the files; they are not digital signatures.

Downloads and documentation are served through authenticated GitHub HTTPS.
Do not disable certificate checks. GitHub source archives can be requested for
the recorded commit; verify the intended repository and revision before use.
There is no claim of a separately signed release artifact or a signed-tag policy.
Reinstall a reviewed newer source revision in a fresh virtual environment to
update, and rerun synthetic tests. Read the changelog before accepting changed
output semantics. No PyPI publication, live device acceptance, Docker validation
or deployment is implied by a successful source build.
