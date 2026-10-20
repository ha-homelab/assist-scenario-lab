# Security policy

The current 0.1 series accepts local JSON and does not implement network access, recording or actuator control. Inputs are limited to regular files of at most 2 MiB, with strict keys, finite numbers and session limits. Final file symlinks/FIFOs are rejected; this is input hardening, not a hostile-code sandbox.

File loading requires nonzero `O_NOFOLLOW` and `O_NONBLOCK` flags from the operating system. If either is unavailable, `load_json` raises `InputError("unsupported_platform")` before opening the input, and the CLI exits with code 2. Linux and macOS provide these capabilities; other platforms are not assumed to. Pure in-memory evaluation and event import remain independent of file-loading capabilities.

The HA adapter discards event payloads. User-supplied pseudonyms and timestamps may still reveal information; inspect exported reports. Real data belongs outside the public checkout. Do not submit credentials, recordings, private traces, entity inventories or private network identifiers in issues.

Report vulnerabilities using [GitHub private vulnerability reporting](https://github.com/ha-homelab/assist-scenario-lab/security/advisories/new). If unavailable, open an issue requesting a private contact without disclosing exploit data or secrets. Supported version: latest 0.1.x. Secret and publication checks complement review; they cannot prove the absence of all sensitive information.


## Private reports and handling

Use [the private vulnerability form](https://github.com/ha-homelab/assist-scenario-lab/security/advisories/new)
or email **alvit.work@gmail.com**. Include the affected revision, impact and a
minimal synthetic reproduction. Never send live credentials or household data.
The latest source on the 0.1 maintenance line receives fixes; update to the latest
reviewed revision before filing a report when possible.

The maintainer aims to acknowledge reports within 14 days, assess severity and
reproduce them privately, agree on disclosure timing with the reporter, and test
the fix before release. Confirmed critical issues are addressed immediately;
other medium-or-higher issues should be fixed within 60 days. Release notes list
available CVE/GHSA identifiers and upgrade instructions. Reporters receive credit
unless they request anonymity. If the first contact receives no response, retry
the other private channel. There is currently no independent security team or
backup maintainer; [governance](GOVERNANCE.md) records that limitation.
