# Source builds and releases

The public Git repository is the source of truth. Clone it over GitHub HTTPS and
record `git rev-parse HEAD` with test results. Package version `0.1.0` identifies
the initial source series; a full 40-character Git commit identifies a unique
development snapshot within that series. Entries under `Unreleased` in
CHANGELOG.md describe development changes, not an additional published release.
Existing initial release notes remain available in that file.

Use the Python version in [the Check workflow](.github/workflows/check.yml) and
follow [CONTRIBUTING.md](CONTRIBUTING.md) to install the source and its test tools.
Build with `python -m pip install build==1.3.0` then
`python -m build --outdir dist`. Setuptools 83.0.0 is the reviewed build backend.
The standard build creates an sdist and a wheel from that sdist. Source archives
include the license, interface guides, tests and contribution/security policies.
No private files, credentials or real household exports belong in an artifact.

Before publishing a new release, the maintainer must run the complete Check
workflow, inspect its test/build/static-analysis/secret-scan results and review
all open findings. For a numbered release, update the package, source `__version__`
and root `version` consistently, move the relevant changelog entries into a
versioned section, and create a new immutable `vX.Y.Z` tag. Never reuse a release
tag. Security releases include available advisory identifiers and upgrade notes.
Use semantic versioning; breaking public report/schema behavior requires an
explicit compatibility decision and documented migration instructions.

Downloads and documentation are served through authenticated GitHub HTTPS.
Do not disable certificate checks. GitHub source archives can be requested for
the recorded commit; verify the intended repository and revision before use.
There is no claim of a separately signed release artifact or a signed-tag policy.
Reinstall a reviewed newer source revision in a fresh virtual environment to
update, and rerun synthetic tests. Read the changelog before accepting changed
output semantics. No PyPI publication, live device acceptance, Docker validation
or deployment is implied by a successful source build.
