# Contributing

Report bugs with the command, Python/OS version, sanitised input, observed result and expected observation. Don't post private naming briefs, credentials or respondent details.

Parser changes need offline fixtures for positive records, negative observations, malformed responses and ambiguity. Never introduce a rule that turns rate limits, hidden accounts or unknown HTML into claimability. Live checks are optional, can change, and should respect provider restrictions.

Run `python -B -m unittest discover -s tests -v`. Edit `SKILL.md` as the canonical instructions, then run `python -B scripts/sync_adapters.py`; `--check` detects drift. Keep the README, stage references and report template consistent. Use `python3` where necessary. CI runs the same offline checks.

External agency methods are credited in `references/09-sources.md`; don't copy third-party guides or imply endorsement. Keep generated illustrations consistent with `assets/STYLE.md` and add useful alt text when embedding them.
