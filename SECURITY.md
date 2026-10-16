# Security policy

The current 0.1 series accepts local JSON and does not implement network access, recording or actuator control. Inputs are limited to regular files of at most 2 MiB, with strict keys, finite numbers and session limits. Final file symlinks/FIFOs are rejected; this is input hardening, not a hostile-code sandbox.

The HA adapter discards event payloads. User-supplied pseudonyms and timestamps may still reveal information; inspect exported reports. Real data belongs outside the public checkout. Do not submit credentials, recordings, private traces, entity inventories or private network identifiers in issues.

Report vulnerabilities using [GitHub private vulnerability reporting](https://github.com/ha-homelab/assist-scenario-lab/security/advisories/new). If unavailable, open an issue requesting a private contact without disclosing exploit data or secrets. Supported version: latest 0.1.x. Secret and publication checks complement review; they cannot prove the absence of all sensitive information.
