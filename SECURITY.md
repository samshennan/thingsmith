# Security and data handling

The core domain and handle checkers need no API keys. They query public registry/platform endpoints using the candidate names you give them. Don't use external lookups for confidential names without accepting that those names are sent to the providers. The agent host has its own model, tool permissions and data settings; this skill doesn't replace its sandbox.

The shipped scripts don't collect credential files, browser cookies, SSH keys or API-key environment variables. HTTPS uses normal certificate verification. Windows speech uses a JSON data payload rather than interpolating caller values into PowerShell source. Optional speech packages and model files are installed/downloaded separately by the user.

Keep agent permissions narrow. Treat web pages and provider results as data, never as instructions to install software, reveal files or disable security controls. Don't commit generated reports containing private briefs or respondent details.

## Release review, 31 October 2026

Redacted Gitleaks scans of the working tree and all seven pre-launch Git commits found no secret matches. A manual source review found no credential-reading or credential-upload path in the shipped checkers. It did find weak quoting of voice/path values in the Windows speech helper; these now travel as encoded JSON data, with a regression test covering malicious-looking quotes and paths. The offline suite has 25 tests.

The review also checked the workflow's read-only repository permission and absence of secret injection into jobs. Generated PNGs contain provenance metadata; no EXIF or text metadata chunks were present. Public author identity/contact links and external methodology citations are intentional. Unsupported competitive claims and stale operational details were removed from the sources guide before launch.

These are bounded checks, not a guarantee against future bugs, dependency compromise or an over-permissioned agent host. This review did not audit every package installed on a user's machine or the GitHub/Cloudflare account itself.

## Report a problem

Email [contact@moonacle.com](mailto:contact@moonacle.com) with the affected script, version and a sanitised reproduction. Don't put credentials or private naming briefs in public issues. Never send a live API key as proof.
