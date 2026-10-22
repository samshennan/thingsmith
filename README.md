# Thingsmith

**A little forge for naming your next big thing.**

![Thingsmith: a welcoming naming workshop with letterpress blocks and a small coral anvil.](assets/images/hero.png)

Finding a name you like is one job. Finding out whether you can use it is another.

Thingsmith is a free agent skill for naming products, brands and companies across markets. It develops candidates and gathers domain, handle and language observations behind a usable shortlist. You get the reasoning, the rejection log and the checks that still need a human.

I built it because I kept needing international names and getting stuck in the same loop: a promising idea, a taken domain, another idea, an awkward meaning somewhere else.

## Try it

In Claude Code:

```text
/thingsmith a tool that helps small studios find public tenders, for the UK and Poland
```

Already have a name? Ask directly:

```text
/thingsmith check thingsmith: .com and .io, GitHub and npm; markets UK and Poland
```

That goes straight to investigation. A naming request starts with a brief and develops candidates. A comparison request can work with your existing shortlist.

The skill is free under [MIT](LICENSE). Your agent's model usage, domain purchases and professional checks may cost money.

## What comes back

![A maker sorts a tray of wooden blocks into a small considered shortlist.](assets/images/naming-workflow.png)

A report records the brief and candidate derivations, with creative comparisons and a rejection log. A neutral HTML sheet shows finalists in the same everyday situations, alongside competitors. You choose what to pursue.

The process is: brief → competitor map → territories → generate → screen → compare → investigate → present.

Compact scope targets 40–60 distinct ideas. Full scope targets 150+ using differently briefed generators where supported. These are effort budgets, not quality guarantees. The report states what actually ran, including models, isolation and skipped checks.

## Check the evidence

![A maker investigates a name with evidence cards for a conflict, an unknown and a documented observation.](assets/images/evidence-checks.png)

The scripts inspect registration and public-platform records. They distinguish what was observed from whether you can claim something:

| Result | Meaning |
|---|---|
| `taken` | A registration or public record was found |
| `NO_RECORD_FOUND` | This lookup found no record; registration or claiming remains unconfirmed |
| `UNVERIFIED` | Ambiguous response, hidden-holder possibility, blocked request or failed lookup |
| `UNSUPPORTED` | This tool cannot perform the check |
| `INVALID` | Input doesn't fit a supported platform rule |
| `MANUAL` | A human/provider check remains open |

A missing DNS record never proves a domain can be registered. A missing public profile never guarantees a handle can be claimed. Reservations, premium pricing and eligibility still matter. Evidence exports record timestamps and sources; old results need re-checking.

Exit 0 means the requested automated checks completed. It doesn't mean the name is suitable or available. Manual work remains listed separately. Exit 1 means requested observations are unresolved, unsupported or invalid; exit 2 means a CLI usage error. Pronunciation tools use exit 0 for completed machine checks even when a transcript differs.

## Say it in the markets that matter

![Three people try names aloud and listen for different readings around a workshop table.](assets/images/say-it-together.png)

An optional speech tool reads candidates using language-specific voices, then transcribes the speech without supplying the spelling. It flags possible spelling or pronunciation trouble. A machine mismatch is a reason to investigate; ordinary local accents don't have to sound identical.

The included [native-speaker form](assets/native-speaker-check.md) helps you get real feedback. A machine PASS isn't human validation. Preliminary trademark research also leaves professional clearance outstanding.

## Between a brainstorm and a naming agency

Asking ChatGPT for names is a useful start. Thingsmith adds a repeatable process, scripts for investigating the shortlist and a record of what remains unknown.

At the other end, Lexicon publishes an average project fee of **US$75,000–$150,000** for its professional naming engagement. That's a price anchor, not a claim that this skill provides equivalent work. [Lexicon's process and pricing](https://www.lexiconbranding.com/brand-naming-process/) (checked 22 October 2026).

Thingsmith is for the work between those options: moving beyond suggestions without buying a full agency engagement.

## Install

Requires Python 3.9+ and an agent that can read instructions and run local scripts. No API key is required by the core checkers. They make outbound requests to public registries and platforms; your agent host has its own model/data settings. Don't put private naming briefs in public issues.

**Claude Code — Windows PowerShell:**

```powershell
git clone https://github.com/samshennan/thingsmith.git "$HOME\.claude\skills\thingsmith"
```

**Claude Code — macOS/Linux:**

```sh
git clone https://github.com/samshennan/thingsmith.git ~/.claude/skills/thingsmith
```

If the repository is private, cloning requires authorised GitHub access. If that destination already exists, update the existing clone rather than cloning over it.

**Codex / Gemini CLI:** clone to a location of your choice and explicitly load its `AGENTS.md` / `GEMINI.md` as task instructions. These are generated editions of the same skill, not a claim of automatic discovery by every host. Keep your host's permissions and approval settings.

Optional dependencies unlock additional capabilities:

| Install | Capability |
|---|---|
| `python -m pip install dnspython` | Fast DNS evidence that a domain is taken |
| `python -m pip install certifi` | Certificate bundle for handle requests |
| [eSpeak NG](https://github.com/espeak-ng/espeak-ng/releases) | Language-specific IPA and fallback speech |
| `python -m pip install faster-whisper` | Synthetic speech-to-text test; downloads a model on first use |

Windows SAPI voices are used when available; eSpeak is the fallback. Missing voices/backends remain explicit. Use `python3` where your system requires it.

## Run the scripts yourself

From the clone:

```text
python scripts/check_domains.py --names thingsmith --tlds com io --json domains.json
python scripts/check_handles.py --names thingsmith --only github npm pypi --json handles.json
python scripts/check_handles.py --list
python scripts/say_it.py --names thingsmith --langs en pl --readings-only
python scripts/context_sheet.py --names exampleone exampletwo --descriptor "your product description" --competitors Example --shuffle --sender "Your Name" --out shortlist.html
```

These are commands to investigate, not assertions about current availability. Check only the namespaces your project needs. Respect provider restrictions and rate limits; unsupported endpoints can change over time.

## Project status and contributing

Early release. Thingsmith itself remains a working name; its trademark and native-speaker checks are open. Historical domain/handle checks don't settle current availability.

The method lives in [SKILL.md](SKILL.md), stage guidance in `references/`, tools in `scripts/`, and templates in `assets/`. External methods are credited in [sources](references/09-sources.md); the agencies haven't endorsed this project.

Run offline checks with:

```text
python -B -m unittest discover -s tests -v
python -B scripts/sync_adapters.py --check
```

See [contributing](CONTRIBUTING.md), the [media kit](docs/media-kit.md) and the [tech post draft](docs/tech-post.md). Edit `SKILL.md`, then regenerate the shipped adapters with `python -B scripts/sync_adapters.py`.

## Want help finishing?

[Moonacle](https://moonacle.com) offers a done-for-you route. Contact [contact@moonacle.com](mailto:contact@moonacle.com) with what you're naming and where it will sell to discuss scope.
