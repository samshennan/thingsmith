# Stage 4 — Screening

**Gate: 40+ candidates through form, four-language, trap register and the say-it tests.**

Screening is subtractive and cheap. Run it before the scorecard, because scoring a name that
a slang check would have killed is wasted effort, and run it before any domain lookup,
because that is what stops people falling in love.

Four screens, in this order. Each is a **kill**, not a deduction.

---

## Screen 1 — Form

From `04-generation.md`, applied strictly now:

- Plain ASCII, no diacritics
- 2–3 syllables, 4–10 characters
- No consonant cluster the second market will not attempt (`szcz`, `trz`, initial `zd`)
- One obvious spelling from the sound, one obvious sound from the spelling
- Reads as the category it is entering

---

## Screen 2 — The four-language test

For each candidate, write the reading in each target language and **check they match**. A
name pronounced differently in each market is two brands wearing one spelling.

| Test | Ask |
|---|---|
| **Reading** | How does each market say it on sight, with no help? Write it phonetically. |
| **Convergence** | Are those readings the same? If not, kill it. This is a veto, not a deduction. |
| **Slang** | Anything crude or comic in EN, PL, DE, FR, ES, IT — **and the target market's own slang**? |
| **Person-vs-product** | Does it read as somebody's first name? If so, search results are permanently swamped. |

Default language set: English, Polish, German, French, Spanish, Italian. Add any language
spoken in a market the brief names, and any language with a large diaspora in those markets.

**Run the machine reading first.** `scripts/say_it.py --readings-only` prints each
language's cold reading as IPA (eSpeak NG applies that language's spelling rules) and flags
`DIVERGENT` when two markets read the spelling as different words. It is a fast, honest
first cut across all 40+ survivors; do the slang and false-friend columns yourself.

```bash
python "${CLAUDE_SKILL_DIR}/scripts/say_it.py" --names karbia zyla --langs en pl de --readings-only
```

**On the limits of doing this yourself:** professional houses use three native speakers
*resident in the target country* per language — Catchword's standard, and the reason they
catch things a dictionary does not. A model check is a screen, not a clearance. If the name
is going to carry real money, say in the report that a native-speaker check is the next step
and has not been done — and hand the principal `assets/native-speaker-check.md`, filled in
with the shortlist, so the next step is a message they can send today.

---

## Screen 3 — The trap register

These are real kills. Check every one explicitly — they do not surface on their own, and
each one below cost somebody a shortlist.

| Trap | Example that died | Why |
|---|---|---|
| **Local slang in the target market** | `troppo` | Australian for "gone crazy" |
| **Slur or insult in a third language** | `zorra` | A strong insult for a woman in Spanish |
| **Medical / clinical meaning** | `rhabdo` | Gym and medical shorthand for rhabdomyolysis |
| **Divergent pronunciation** | `dowsa` | Bogan in Australia, "dovsa" in Polish |
| **A large local company owns it** | `rokita` | PCC Rokita SA, WSE-listed, holds the `.pl` |
| **A famous person shares it** | `rokita` | A nationally known politician too |
| **A well-known package or library** | `boruta` | A feature-selection algorithm every data scientist knows |
| **A competitor already has it** | `tendrix` | An AI tender-discovery platform — found while naming |
| **The metaphor is claimed in-market** | `fossick` | An Australian recruiter, same gold-rush metaphor |
| **A common given name** | `ritika` | Reads as a person; SEO permanently swamped |
| **False-friend meaning** | `mina` | "Landmine" in Polish; only Romance languages give it "mine shaft" |
| **Too close to the incumbent** | `minra` | Sits on top of `Mimira`, the competitor being displaced |
| **Reads as an existing global brand** | — | One letter from a giant is a lawsuit, not a shortcut |
| **Unfortunate substring** | — | Read the name as one lowercase string and look for words inside it |
| **Bad in the URL** | — | `therapistfinder.com`. Concatenate and read again. |
| **Already a ticker or a token** | — | Crypto tickers and listed symbols swamp search too |
| **Pharma stem collision** | — | WHO INN stems (`-mab`, `-tinib`, `-prazole`) are reserved; never coin into them |

**Additions since v1** — the last five rows. The substring and URL checks in particular take
ten seconds and have the highest embarrassment-per-second ratio of anything in this file.

---

## Screen 4 — The human tests

Cheap, fast, and they catch what analysis does not. Run at least the first two on every
surviving candidate; run all four on the shortlist.

**The radio test.** Say the name aloud, once, with no spelling. Could the listener find the
website afterwards? If not, the name leaks a customer at every verbal handoff. Misspelled
coinages fail here almost every time, which is the honest cost of mechanic 13.

**The spelling-back test.** Say it to five people who have not seen it written. Ask them to
write it down. **Fewer than four correct out of five is a fail**, not a caution.

**The recall test.** Say the name, talk about something else for twenty minutes, then ask
what it was. Under 7 in 10 correct signals a retention problem.

**The read-aloud test.** Have people read the name off a page. Multiple pronunciations means
confusion, and confusion means they will search wrong and spell wrong.

**The machine radio test** — run it on every survivor, before the humans. `say_it.py`
speaks each name inside a carrier sentence ("The company is called ___", "Firma nazywa
się ___") with a text-to-speech voice per language, then has Whisper transcribe it with no
hint of the spelling. A `FAIL` prints the spelling it heard, which is the spelling customers
will type into a search box.

```bash
python "${CLAUDE_SKILL_DIR}/scripts/say_it.py" --names karbia zyla --langs en pl
#   karbia  radio en  FAIL  heard 'Carbia'   <- the K/C leak, every verbal handoff
#   zyla    radio pl  FAIL  heard 'Żyła'     <- Polish for "vein": a trap-register kill
```

Synthetic voices are clearer than a phone line and Whisper is more attentive than a
distracted listener, so read the result asymmetrically: **a machine FAIL is strong
evidence; a machine PASS is weak evidence.** It never replaces the five-person tests on the
shortlist.

When there is no one to test on, say so in the output — "radio and spelling tests not run,
five-person test recommended before purchase" — rather than quietly skipping them. A machine
radio pass does not change that sentence.

---

## SCRATCH — the deal-breaker checklist

Alexandra Watkins' seven, useful as a final sweep because they are memorable and catch
different things from the trap register:

| | Deal-breaker | Check |
|---|---|---|
| **S** | Spelling-challenged | Does it look like a typo? |
| **C** | Copycat | Does it look like a competitor's name? |
| **R** | Restrictive | Does it box in the roadmap, the geography, the category? |
| **A** | Annoying | Forced, contrived, or trying too hard? |
| **T** | Tame | Flat, vague, uninspired — the most common failure and the least noticed |
| **C** | Curse of knowledge | Does it only make sense to insiders? |
| **H** | Hard to pronounce | Covered by screen 2, confirmed here |

And the positive counterpart, **SMILE**, which is really the scorecard in mnemonic form:
**S**uggestive of the brand · **M**emorable · **I**magery · **L**egs (extends into a theme) ·
**E**motional.

"Legs" is the one people forget and the one that matters in eighteen months: can the name
generate a family — product names, feature names, a visual world, a vocabulary the company
speaks in? Igor calls the same property a *deep well*. A name with no legs has to be
re-solved every time the company ships something new.

---

## Output of this stage

Two lists, both carried into the final document:

1. **Survivors** — with the four-language reading table.
2. **KILLED** — every dropped name with the specific reason. This is the most re-read
   section of the report. "It didn't feel right" is not a reason; "reads as a first name in
   both markets, SEO permanently swamped" is.
