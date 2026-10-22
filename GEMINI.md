# Skill: thingsmith

**When to use:** Name a public-facing product, brand or company for an international market and clear it: brief, namescape, four territories, generation, four-language trap screen, 90-point scorecard, then real RDAP/WHOIS domain, handle, trademark and collision checks. Triggers: 'name this', 'what should we call it', 'is that name available', 'check this domain', /thingsmith.

## Thingsmith

Naming fails in three ways, and none of them is running out of ideas.

**It fails at the brief.** Nobody decided what the name has to *do*, so the debate becomes
taste. Every professional house starts here — Igor calls it positioning, Lexicon asks "what
does winning look like", Catchword writes fifteen questions down before a single candidate
exists. A name cannot be judged against nothing.

**It fails at the metaphor.** Someone picks a word they like, then discovers it means
nothing in the second market. The fix is not a better word — it is finding a territory
*both* markets already own, then naming from inside it.

**It fails at the check.** Someone falls in love, checks DNS, sees NXDOMAIN, and buys a
story that a squatter already owns. Or never runs a collision search and ships a name a
competitor holds. Every name this skill has killed died at the check, not the idea.

So the order is fixed and it does not bend:

> **brief → namescape → territories → generate → screen → score → verify → stage**

Never check domains before the territories are settled. Checking early is what makes people
fall in love with names they cannot have, and it caps generation at whatever survived a
premature filter.

---

### The eight stages

Load the reference for a stage when you reach it. Do not front-load them all.

| # | Stage | Load | Gate to pass |
|---|---|---|---|
| 0 | **Brief** | `references/01-brief.md` | The name's job is written down in one sentence |
| 1 | **Namescape** | `references/02-namescape.md` | Every competitor plotted; the empty quadrant named |
| 2 | **Territories** | `references/03-name-types.md` | 4+ territories incl. a Forge pass; one bold option kept |
| 3 | **Generate** | `references/04-generation.md`, `references/05-sound-symbolism.md` | 150+ raw from four isolated teams, all four name types |
| 4 | **Screen** | `references/06-screening.md` | Form, machine readings + radio test, trap register, human tests |
| 5 | **Score** | `references/07-scorecard.md` | 90-point card run; 8–15 survive |
| 6 | **Verify** | `references/08-clearance.md` | Domains, handles, knockout, collision — all with evidence |
| 7 | **Stage** | `assets/report-template.md`, `scripts/context_sheet.py` | Document + names-in-context sheet. Choose nothing. |

`references/09-sources.md` holds the research this skill is built on, with the specific
claim each source supports. Cite it when a client or principal asks "says who".

---

### Stage rules that override everything

#### Volume is not optional (stage 3)
Catchword generates ~2,000 candidates per project and shortlists 10%. Lexicon targets 1,000+
ideas before narrowing to 50–100. A twenty-candidate list is not a naming project, it is a
brainstorm, and it will be beaten by whatever the founder already had in their head.

**Minimums for this skill: 150 raw candidates, 40 surviving form screen, 8–15 scored.**
Below that, say so in the output rather than pretending the funnel ran.

#### Generate across all four types, not just coinages (stage 3)
The four types — **functional, experiential, evocative, invented** — have different
strengths and different trademark odds. A set that is all invented coinages has no
comparison class, and the principal cannot tell whether the winner is good or merely the
least bad of one flavour. Generate all four. Kill types at the *scorecard*, not before.

Real words are mostly gone — across ~250 RDAP lookups on one project, every evocative real
word was registered and only 6 of ~38 short coined `.com` were free. That is an argument for
weighting coinages, not for generating nothing else.

#### Four teams, four briefs, no peeking (stages 2–3)
One generator in one context is one point of view, however many names it writes. Run four
isolated teams — straight, decoy brief, Forge territories, cold — and merge only at the end
(`04-generation.md`). Lexicon has done this for decades with people; agents make it nearly
free. Tag every candidate with its team. Record which models actually ran.

#### The second market is a veto, never a tiebreak (stages 4, 6)
A name pronounced differently in each market is two brands wearing one spelling. Divergent
readings kill; they do not deduct points.

#### Nothing unverified is ever reported as clear (stage 6)
A 429, a timeout, a TLD with no RDAP service, a register you could not search — each is
`UNVERIFIED` or `UNSUPPORTED`, printed as itself. "Probably free" is a banned phrase.
`check_domains.py` exits non-zero when anything is unresolved, precisely so a partial sweep
cannot be handed over as a clean one.

#### Never present a name on a blank page (stage 7)
A bare word on white invites objections that disappear once the name sits in a homepage, an
inbox, a headline, a sentence said aloud. Render every finalist — and two or three
competitors, for scale — into the same scenes with `context_sheet.py`, in one neutral
typeface so the font cannot choose the name. Ask the principal which names *work* and why,
not which they like.

#### Choose nothing (stage 7)
Naming is the principal's decision. Stage it with the evidence under it. The most re-read
section of the output is always the KILLED list.

---

### Verification — the commands

The scripts sit in `scripts/` next to this file. In Claude Code that folder is
`${CLAUDE_SKILL_DIR}`; in any other agent, use the folder this file was loaded from. Python 3,
standard library only. `pip install dnspython` turns on the free DNS rung — without it the
script says so and goes straight to RDAP. Use `python3` on macOS/Linux.

**Domains.** Ladder: DNS NS proof → registry RDAP → port-43 WHOIS → `UNVERIFIED`.

```bash
python "${CLAUDE_SKILL_DIR}/scripts/check_domains.py" \
  --names ritka karbia zyla --tlds com pl io ai --csv domains.csv

## which TLDs are even answerable before you commit to a sweep
python "${CLAUDE_SKILL_DIR}/scripts/check_domains.py" --tld-report --tlds com pl io co eu
```

- **RDAP, not bare DNS.** A registered-but-unhosted domain returns NXDOMAIN and misreports
  as free. DNS is used here only as one-way *taken* proof: NS records present ⇒ registered.
- **A 404 from a resolver with no service for that TLD is not an answer.** `rdap.org` returns
  a bare bodyless 404 both for "not found" and for "I have no server for `.io`". The v1 of
  this script read that as FREE and would have cleared every `.io` and `.co` candidate.
  The script now resolves each TLD to a verified registry endpoint first.
- `.pl` RDAP hard-429s from outside a registrar; `.co` and `.eu` publish no RDAP at all. All
  three answer port-43 WHOIS, which is why that rung exists.

**Handles.** A domain alone is not a name.

```bash
python "${CLAUDE_SKILL_DIR}/scripts/check_handles.py" --names ritka karbia --json handles.json
python "${CLAUDE_SKILL_DIR}/scripts/check_handles.py" --list   # what is automatable vs manual
```

Automated: GitHub · npm · PyPI · crates · Docker Hub · Hugging Face · YouTube · Telegram ·
Bluesky · GitLab · Reddit. Manual, and named as manual in the report: X · Instagram ·
LinkedIn company slug · Product Hunt · TikTok · app-store developer name.

**Pronunciation.** Machine stand-ins for the four-language and radio tests. `--readings-only`
needs only eSpeak NG; the radio test also needs `pip install faster-whisper` (the model
downloads once) and a TTS voice per language (Windows SAPI voices are used when present,
eSpeak NG otherwise). Anything that cannot run prints `UNSUPPORTED` and exits non-zero.

```bash
python "${CLAUDE_SKILL_DIR}/scripts/say_it.py" --names karbia zyla --langs en pl de --readings-only
python "${CLAUDE_SKILL_DIR}/scripts/say_it.py" --names karbia zyla --langs en pl
```

A machine FAIL is strong evidence; a machine PASS is weak evidence. Native speakers are still
the clearance: send `assets/native-speaker-check.md`.

**Context sheet.** One self-contained HTML page, every finalist in nine identical scenes.

```bash
python "${CLAUDE_SKILL_DIR}/scripts/context_sheet.py" --names karbia ritka namira   --descriptor "tender discovery for XR studios" --competitors Mimira --shuffle
```

**Trademark knockout and collision search.** See `references/08-clearance.md` for the
register list, the Nice classes, and the sentence that must appear in every output about
what a knockout does not cover.

---

### Composes with

- **`veles-forge`** — run inside stage 2 (`03-name-types.md`, "The Forge pass") to find
  territories outside the category's vocabulary, and as team C in stage 3. If Forge shows the
  naming problem is really a positioning problem, stop and forge the concept first.
- **`polonize`** — for any Polish-market reading or register question.
- **`brand-guardian`** / **`veles-brand`** — once a name is chosen, for the wordmark and
  identity work.
- **Premortem, built in** — before anything is bought, write one paragraph on the leading
  candidate: "it is eighteen months from now and the name was a mistake — why?" Put it in the
  report next to the candidate.
- **Cold reader, built in** — hand the shortlist to a fresh agent or model with no context and
  ask what each name is and does. A name that needs its derivation explained to land is a
  name with a problem. Team D in stage 3 is the same idea, earlier.

### Hard rules

- Never check domains before the territories are settled.
- Never generate from a single territory. One bad metaphor must not be able to kill a project.
- Never report a 429, a timeout, an unsupported TLD, or an unsearchable register as
  "available" or "clear".
- Never present a name without its collision status and its scorecard row.
- Never call a knockout search legal clearance.
- Never present a finalist without its context sheet, or without competitors beside it.
- Never call a machine pronunciation pass a native-speaker check.
- Never choose. Stage the decision with the evidence under it.