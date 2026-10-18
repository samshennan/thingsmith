# namesmith — install on another machine

> **What:** the naming skill (`/namesmith`): brief → namescape → territories → generate →
> screen → score → verify → stage, with real RDAP/WHOIS domain and handle checks.
> **Why this file:** the skill lives once, in `_SHARED/skills/namesmith`. Each machine links
> to it instead of keeping a copy, so a fix made anywhere reaches everywhere.
> **What you do:** pull `_SHARED`, link the folder, install `dnspython`, run the smoke test.

## Windows (PowerShell)

```powershell
$src = "C:\AI_LAB\_SHARED\skills\namesmith"
$dst = "$HOME\.claude\skills\namesmith"
git -C C:\AI_LAB\_SHARED pull --ff-only
if (-not (Test-Path $dst)) { New-Item -ItemType Junction -Path $dst -Target $src | Out-Null }
(Get-Item $dst -Force).LinkType   # "Junction". Blank = an old real copy is in the way: move it aside, re-run.
python -m pip install dnspython
python "$dst\scripts\check_domains.py" --names google zqxvbrnemt --tlds com pl
```

## macOS / Linux

```bash
SRC=~/AI_LAB/_SHARED/skills/namesmith          # wherever _SHARED is cloned
git -C "$SRC/../.." pull --ff-only
[ -e ~/.claude/skills/namesmith ] || ln -s "$SRC" ~/.claude/skills/namesmith
python3 -m pip install --user dnspython
python3 ~/.claude/skills/namesmith/scripts/check_domains.py --names google zqxvbrnemt --tlds com pl
```

## Smoke test — what passing looks like

`google.com` and `google.pl` report **taken**, `zqxvbrnemt.com` and `zqxvbrnemt.pl` report
**FREE**, and the exit code is 0. `UNVERIFIED` on `.pl` means outbound port 43 (WHOIS) is
blocked on that network — that is a network problem, not a free domain. Try another network.

## Other agents

`AGENTS.md` (Codex) and `GEMINI.md` (Gemini) are generated from `SKILL.md` by
`_SHARED/scripts/skill-adapt.py`. Re-run it after editing `SKILL.md`, or they drift.

## Do not

- Copy the folder onto a machine instead of linking it. Copies fork.
- Junction it into a folder a git repo tracks. A checkout there writes old files back through
  the link into `_SHARED` (see `_SHARED/.planning/handoffs/2026-08-20-skill-library-unification.md`).
- Commit `scripts/.rdap-bootstrap.json` or `scripts/.whois-servers.json`. They are per-machine
  caches and are gitignored.
