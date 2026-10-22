# namesmith

**A naming agency's method, packaged as an agent skill.** Give it what you are naming and
who it is for. It runs the process professional naming houses use: brief, competitor map,
territories, four competing generation teams, trap screening, a scorecard, and then
availability checks built never to report something as free unless they have proof. It
stages the decision with the evidence underneath. It never chooses for you.

> Working name. `namesmith` collides with an existing AI name generator at namesmith.app,
> so the skill's own rules kill it as a public brand. It gets a new name before any public
> release.

Built for Claude Code. `AGENTS.md` (Codex) and `GEMINI.md` (Gemini CLI) carry the same
skill for those agents.

---

## What you get

- A **naming document**: the brief, the competitor map, territories, candidates with
  their derivations, a scorecard, verification evidence, and a **KILLED list** that gives
  the specific reason each name was dropped.
- A **names-in-context sheet**: one HTML page showing every finalist, plus competitors
  for scale, in nine identical real-world scenes.
- **Domain and handle sweeps** with proof for every result. Anything unresolved prints
  `UNVERIFIED`.
- A **pronunciation screen**: per-language cold readings plus a machine radio test.
- A **native-speaker form**, ready to send to real people in each market.

---

## Install

### 1. Put the skill where your agent looks

**Claude Code.** Clone the repo straight into your skills folder:

```bash
# macOS / Linux
git clone https://github.com/samshennan/namesmith.git ~/.claude/skills/namesmith
```

```powershell
# Windows (PowerShell)
git clone https://github.com/samshennan/namesmith.git "$HOME\.claude\skills\namesmith"
```

If you keep the clone somewhere else, link it instead of copying it, so updates reach the
skill:
- macOS / Linux: `ln -s <clone> ~/.claude/skills/namesmith`
- Windows: `New-Item -ItemType Junction`

**Codex / Gemini CLI.** Point the agent at `AGENTS.md` or `GEMINI.md` in the clone. The
scripts run the same way.

### 2. Install the dependencies

Every dependency is optional, and each one unlocks one capability. Without it, the
matching check prints `UNSUPPORTED` rather than pretending it passed.

| Install | Unlocks | Without it |
|---|---|---|
| Python 3.9+ | All scripts (standard library only at the core) | Nothing runs |
| `pip install dnspython` | Fast DNS rung for domain checks (proof that a domain is taken) | Goes straight to RDAP; slower, still correct |
| `pip install certifi` | Up-to-date certificate store for handle checks | Docker Hub and others can fail TLS on older Pythons, so they show `UNVERIFIED` |
| [eSpeak NG](https://github.com/espeak-ng/espeak-ng/releases) (Windows: `winget install eSpeak-NG.eSpeak-NG`; macOS: `brew install espeak-ng`; Linux: `apt install espeak-ng`) | Per-language cold readings (IPA) and fallback text-to-speech | Readings `UNSUPPORTED` |
| `pip install faster-whisper` | Machine radio test (the model downloads once, ~500 MB for `small`) | Radio test `UNSUPPORTED` |
| A text-to-speech voice per test language | Radio test in that language. Windows uses installed SAPI voices (Settings → Time & language → Speech); everywhere else uses eSpeak NG | That language `UNSUPPORTED` |

### 3. Smoke test

```bash
python scripts/check_domains.py --names google zqxvbrnemt --tlds com pl
python scripts/check_handles.py --names google zqxvbrnemt
python scripts/say_it.py --names karbia --langs en
```

**What passing looks like:**
- `google` shows **taken** everywhere and `zqxvbrnemt` shows **FREE**.
- `UNVERIFIED` on `.pl` means outbound port 43 (WHOIS) is blocked on your network. That
  tells you about the network, not about the domain.
- Reddit often blocks scripts. Seeing `UNVERIFIED` there, with exit code 1, is the honest
  result.

---

## Part 1: finding a name

Start it in Claude Code with:

```
/namesmith a tender-discovery tool for XR studios, selling in the UK and Poland
```

You can also just say "help me name this" or "is this name available?". The skill
triggers on either.

The order is fixed. **Do not check domains first.** Checking early is how people fall in
love with names they cannot have.

> **brief → namescape → territories → generate → screen → score → verify → stage**

| # | Stage | What happens | Gate before moving on |
|---|---|---|---|
| 0 | **Brief** | About fifteen questions: what the name must do, for whom, in which markets, and what it must never sound like. The agent asks; you answer | The name's job fits in **one sentence** |
| 1 | **Namescape** | Every competitor's name plotted by type and tone, to find the empty corner of the category | Empty quadrant named |
| 2 | **Territories** | Four or more metaphor fields to name from, including a **Forge pass** (distant analogy, inversion, collision, impossible-first). One bold territory is kept on purpose | 4+ territories |
| 3 | **Generate** | **Four isolated teams** that never see each other's work: **A** has the real brief; **B** has a decoy brief, the same job disguised as another company or category (Lexicon's Zune method); **C** has only the Forge territories; **D** gets one line and nothing else. Every candidate is tagged with its team, mechanic and source word | **150+** raw candidates, all four name types |
| 4 | **Screen** | Form rules, readings in four languages, the trap register (slang, slurs, medical meanings, false friends, famous people, existing packages), and the radio test | **40+** survivors, with a KILLED list giving the reason for each cut |
| 5 | **Score** | A 90-point scorecard, run on every survivor | **8–15** survive |
| 6 | **Verify** | Domains, handles, trademark knockout, collision search, all with evidence | Every result proven or marked `UNVERIFIED` |
| 7 | **Stage** | The naming document plus the in-context sheet. The skill presents the evidence and stops | You choose |

If a stage comes up short (say, 60 candidates rather than 150), the report says so instead
of pretending the full process ran.

### Running the tools yourself

The agent calls these scripts during the run. You can also use them on their own to check a
name you already have.

```bash
# Domains: DNS proof of "taken" → registry RDAP → port-43 WHOIS → UNVERIFIED
python scripts/check_domains.py --names ritka karbia --tlds com io ai co pl --csv domains.csv
python scripts/check_domains.py --tld-report --tlds com io co eu   # which TLDs are answerable

# Handles: 12 platforms automated, the rest listed as manual (never as clear)
python scripts/check_handles.py --names ritka karbia --json handles.json
python scripts/check_handles.py --list

# Pronunciation: cold readings per language + machine radio test
python scripts/say_it.py --names karbia zyla --langs en pl de --readings-only
python scripts/say_it.py --names karbia zyla --langs en pl

# Names in context: nine scenes, one neutral font, competitors for scale
python scripts/context_sheet.py --names karbia ritka namira \
  --descriptor "tender discovery for XR studios" --competitors Mimira --shuffle \
  --sender "Your Name" --out shortlist.html
```

Every script exits non-zero if anything is unresolved, so a partial sweep can't be passed
off as a clean one.

### How to read the results

- **A machine FAIL is strong evidence; a machine PASS is weak evidence.** If a synthetic voice
  and Whisper can't get the spelling across, people on a phone line won't either. A pass
  still needs humans. Real catches from the radio test:
  - `karbia` was heard as "Carbia", so every verbal handoff leaks the spelling.
  - `zyla` was heard as "Żyła", which is Polish for "vein".
- **Native speakers are the clearance.** Send `assets/native-speaker-check.md` to three
  speakers per language, each living in that country now. One credible bad-meaning report
  kills a name; don't average it away.
- **Judge in context.** On the context sheet, ask "which of these *work*, and why?", not
  "which do you like?"
- **A trademark knockout is not legal clearance.** It finds obvious conflicts cheaply,
  before you pay a lawyer to find subtle ones.
- **Live with it for a week.** Say it, type it, sign emails with it, before buying anything.

### What it can't do for you

It can't do the human steps: native-speaker panels, an association test with people who
have never seen the brief, a trademark lawyer's opinion, or quietly buying a domain someone
else owns. The report names each of these as an open step. It never marks one as done.

---

## Part 2: pulling the trigger

Once you've chosen, the clock starts. Domains, handles and trademark priority all go to
whoever moves first.

1. **Re-check on the day you buy.** A two-week-old sweep proves nothing.
2. **Domains.** Register the main domain and a few typo or variant domains chosen from
   evidence, such as the spellings the radio test actually heard. Redirect them all
   permanently (301) to the main site. Turn on WHOIS privacy, registrar lock and auto-renew.
   **Confirm the registrant email within 15 days**, or the registrar suspends the domain.
3. **Lock down the parked domains.** Every domain that won't send email gets a null MX
   record, an SPF record of `v=spf1 -all`, and DMARC set to `p=reject`. Typo domains are a
   phishing tool, aimed at your own customers.
4. **Handles.** Claim them by hand, using the manual list from `check_handles.py --list`.
   Bot sign-ups break the rules on X, Instagram and TikTok, and are an easy way to lose the
   handle. Don't publish placeholder packages to reserve names; npm and PyPI treat that as
   squatting.
5. **Trademark.** Give a lawyer the mark, the Nice classes, the goods description, the
   jurisdictions and your knockout evidence. They file it.
6. **Watch.** Set up alerts for newly registered look-alike domains and new trademark
   filings.

### Or have it done for you

[**Moonacle**](https://moonacle.com) runs this process as a done-for-you service. That
covers:
- the human checks: a native-speaker panel and an association test;
- the trademark brief for your lawyer;
- buying the domains quietly and setting up DNS and email lockdown;
- securing the handles.

Every purchase and filing waits for your sign-off. Email
**[contact@moonacle.com](mailto:contact@moonacle.com)** with what you're naming and where it
will sell.

---

## Layout

```
SKILL.md                     the skill: stages, rules, commands (Claude Code)
AGENTS.md / GEMINI.md        same skill for Codex / Gemini (generated from SKILL.md)
references/01-09             one file per stage; the agent loads each when it reaches that stage
assets/report-template.md    the naming document
assets/native-speaker-check.md   send-ready form for native speakers
scripts/check_domains.py     RDAP/WHOIS domain checker
scripts/check_handles.py     handle checker, 12 platforms + a manual list
scripts/say_it.py            cold readings + machine radio test
scripts/context_sheet.py     names-in-context HTML sheet
```

`references/09-sources.md` lists the research the method rests on (Catchword, Lexicon, Igor,
Siegel+Gale and others), with the specific claim each source supports.

## Optional companions

`SKILL.md` mentions `veles-forge` (generating territories), `polonize` (Polish-language
checks) and a brand skill (identity work once a name is chosen). They aren't in this repo.
Without them, the skill runs the Forge moves itself and skips the rest.

## Maintenance

- After editing `SKILL.md`, regenerate `AGENTS.md` and `GEMINI.md` (`python _SHARED/scripts/skill-adapt.py
  skills/namesmith` in the source workspace), or they drift out of sync.
- Don't commit `scripts/.rdap-bootstrap.json` or `scripts/.whois-servers.json`. They are
  per-machine caches, and they're gitignored.
