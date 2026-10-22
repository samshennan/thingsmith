# Sources

What this skill is built on, and which claim each source supports. Cite this when a
principal or client asks "says who". Researched 2026-08-22.

---

## Methodology — the naming houses

**Igor Naming Agency — "Building the Perfect Beast: The Igor Naming Guide"** (v6.4, 2011,
free PDF, ~120pp).
`igorinternational.com/guide` · mirror: `efektyvusdizainas.lt/uploads/igor-naming-guide.pdf`
The most substantial free naming methodology in circulation. Source for: the six-step
process (competitive analysis → positioning → name development → trademark prescreen →
creative/testing → name and tagline); the four name approaches (functional, invented,
experiential, evocative) with their documented upsides and downsides; the nine-dimension,
90-point name evaluation chart (appearance, distinctive, depth, energy, humanity,
positioning, sound, "33", trademark); the name taxonomy chart format; the twenty-eight
undifferentiated naming-company names used to demonstrate descriptive brand fade-out; and
the documented committee objections to Virgin, Oracle, The Gap, Caterpillar, Banana Republic,
Yahoo!, Stingray and Fannie Mae. Founded 2002 by Jurisich and Manning, who left A Hundred
Monkeys.

**Catchword — "6 Steps to Create a Great Brand Name"**
`catchwordbranding.com/catchthis/create-the-perfect-brand-name/`
Source for: ~2,000 candidates generated per project and a 10% shortlist rate; the 15-question
creative brief; the three creative phases (project vocabulary → blue sky → review/refine/
repeat); the availability-screening sequence; "the more you like a name, the less likely it
is to be available". Their linguistic-analysis practice
(`catchwordbranding.com/naming/linguistics-cultural-analysis/`) is the source for the
three-native-speakers-resident-in-country standard.

**Lexicon Branding / David Placek** — 3,500+ names over 40 years: Swiffer, Febreze, Pentium,
BlackBerry, Sonos, Dasani, Subaru Outback, Impossible Foods, Azure, Vercel.
`lennysnewsletter.com/p/how-to-find-the-perfect-name` · `lennysnewsletter.com/p/naming-expert-david-placek`
· `digiday.com/media-buying/lexicons-david-placek-on-ai-nomenclature-and-what-makes-a-good-name/`
Source for: the four strategic questions (what does winning look like / what do we have to
win / what do we need to win / what do we need to say); 1,000+ ideas narrowed to 50–100;
prefix×suffix matrices (one project: 55 × 102); small two-person teams with deliberately
misleading briefs rather than large brainstorms; >$3M invested in sound-symbolism research;
the letter findings (`v` alive, `b` reliable, `z` attention, `x` innovation); a linguist
network across 76 countries; 5.5M+ live US trademarks across 45 classes.

**Lexicon / Zune, the parallel-teams example** — `wtop.com/business-finance/2019/09/swiffer-blackberry-dasani-meet-the-man-who-named-your-favorite-products/`
Source for: three teams on Microsoft's 2006 player, one on the real brief, one on a
hypothetical Sony player, one for a different client; Placek declined to say which produced
*Zune*. Lenny's podcast summary (above) describes the same "small, diversely briefed teams".
Basis for the four-team method in `04-generation.md`.

**Siegel+Gale — "Keeping names alive" (Jason Hall)** — `siegelgale.com/brand-building-creative-naming-lead-jason-hall-keeping-names-alive-final-presentation/`
Source for: present names in real context (packaging, press release) because irrelevant
associations fall away in context; ask "which names work and why", not "which do you like".
Basis for `context_sheet.py` and the stage-7 rule.

**Catchword — Name Visualizer** and "Now you see it: do you like it?" — `catchwordbranding.com/catchthis/now-you-see-it-do-you-like-it`
Source for: showing candidates in six real-world marketing scenarios, business card to
billboard.

**Fabrik — brand naming presentation** — `fabrikbrands.com/branding-matters/brand-naming/how-to-create-a-brand-naming-presentation/`
Source for: name in a large neutral font so logo styling does not drive the decision; say the
name aloud. Basis for the single typeface in `context_sheet.py`.

**Zinzin** — `zinzin.com/process/`
Source for: the competitive namescape and search-engine namescape as distinct first steps;
"naming the positioning, not the company"; the same four-category name taxonomy.

**Alexandra Watkins, *Hello, My Name Is Awesome*** (Eat My Words).
Source for: **SMILE** (Suggestive, Memorable, Imagery, Legs, Emotional) and **SCRATCH**
(Spelling-challenged, Copycat, Restrictive, Annoying, Tame, Curse of knowledge, Hard to
pronounce). "Legs" is her term for what Igor calls a deep well.

**How Brands Are Built — "Every type of brand name in one simple chart"**
`howbrandsarebuilt.com/types-of-brand-names/`
Source for: the two-axis approach × construct grid (descriptive → suggestive → abstract
against real-word / compound / coined) and the construct vocabulary — lexical, metaphorical,
arbitrary, fanciful, empty-vessel, alphanumeric.

---

## Linguistics

**Lowrey, T. M. & Shrum, L. J. (2007), "Phonetic Symbolism and Brand Name Preference",
*Journal of Consumer Research*.** Phonetic symbolism measurably shifts brand-name preference
even when consumers are unaware of it.

**Yorkston, E. & Menon, G. (2004), *Journal of Consumer Research*.** Phonetic symbolism
operates as a relatively automatic process that consumers can correct for only when they
recognise it as non-diagnostic.

**Pathak, Calvert et al., "The connotative meanings of sound symbolism in brand names: a
conceptual framework"**, *Journal of Business Research* (2022).
`sciencedirect.com/science/article/abs/pii/S0148296322005458`
Source for the frequency-code mapping: higher-frequency sounds (front vowels, fricatives,
voiceless consonants) → higher evaluation, lower potency; lower-frequency sounds (back
vowels, stops, voiced consonants) → lower evaluation, higher potency. The front/back vowel
attribute table in `05-sound-symbolism.md` comes from this literature.

---

## Pronunciation tooling

**eSpeak NG** — `github.com/espeak-ng/espeak-ng`. Rule-based text-to-phoneme for 100+
languages; `--ipa` prints a language's reading of a spelling. Used for the cold-reading
convergence check. It models spelling rules, not a native speaker's instinct, and is weak on
loanwords and brand-like coinages that native readers often anglicise.

**faster-whisper** — `github.com/SYSTRAN/faster-whisper`. CTranslate2 Whisper, CPU int8. Used
with no initial prompt for the machine radio test, so the spelling is never leaked.

---

## Legal

**USPTO spectrum of distinctiveness** — generic → descriptive → suggestive → arbitrary →
fanciful. Fanciful, arbitrary and suggestive marks are inherently distinctive and registrable
on the Principal Register; descriptive marks need acquired secondary meaning; generic terms
never register. `bitlaw.com/trademark/degrees.html`

**Knockout vs full clearance** — a knockout screens identical and near-identical marks with
no likelihood-of-confusion analysis, and does not detect sound-alikes, common-law rights, or
state/international marks. A full clearance adds DuPont-style analysis, risk grading and a
written opinion. `perspireip.com/blog/trademark-knockout-search-vs-full-clearance-search/`

**Nice Classification** — 45 classes; the same mark can coexist across unrelated ones.
TMclass at `euipo.europa.eu/ec2`.

**Free registers** — TMview (`tmdn.org/tmview`, 70+ offices), EUIPO eSearch plus, WIPO Global
Brand Database (`branddb.wipo.int`), USPTO Trademark Search (`tmsearch.uspto.gov`, replaced
TESS), UPRP Poland (`ewyszukiwarka.pue.uprp.gov.pl`), IP Australia
(`search.ipaustralia.gov.au/trademarks`), UK IPO (`trademarks.ipo.gov.uk/ipo-tmtext`). All
free, no account required.

---

## Domains and infrastructure

**RFC 9224 / IANA RDAP bootstrap** — `data.iana.org/rdap/dns.json` maps TLDs to authoritative
registry RDAP base URLs. ICANN's own guidance is that persistent 429s from rdap.org mean you
should be consuming the bootstrap registries directly. Availability is determined by HTTP
status: 4xx = not registered, 200 = registered. `iana.org/help/rdap-requirements`

**Verified directly during this build (2026-08-22), not taken from documentation:**
- IANA bootstrap covers 590 service entries but **omits `.io`, `.co`, `.eu`, `.me`, `.sh`** —
  ccTLDs are not obliged to register RDAP with IANA.
- `rdap.org` returns a **bare, bodyless 404** for `github.io` and `google.co` — both plainly
  registered — because it has no service mapping for those TLDs. The 404 is byte-identical
  to a genuine "not found". This is the false-FREE bug that v1 of `check_domains.py` shipped.
- `rdap.identitydigital.services/rdap` correctly serves `.io`, `.ai`, `.me`, `.sh`
  (github.io → 200, free → 404).
- `rdap.dns.pl` returns **429 on the first request** from a non-registrar IP, on every
  User-Agent tried. `.pl` is effectively unanswerable over RDAP from here.
- **Port-43 WHOIS answers cleanly where RDAP does not**: `whois.dns.pl` ("No information
  available about domain name…"), `whois.registry.co` ("DOMAIN NOT FOUND"), `whois.eu`
  ("Status: AVAILABLE"). `whois.iana.org` reliably discovers the right server per TLD.
- `rdap.cctld.au/rdap` serves `.au` and `.com.au` correctly in both directions.

**TLD facts** — `.ai` carries a registry-mandated 2-year minimum registration (Anguilla),
roughly doubling the up-front cost. `.com.au` requires an Australian entity or ABN. `.io` is
the BIOT ccTLD; the Chagos sovereignty transfer has been repeatedly proposed and stalled, and
as of 2026 `.io` remains fully delegated with any change expected to be a multi-year phased
transition. `domainincite.com/tag/chagos`

---

## Market context

The commercial naming market this skill is competing with, as of August 2026:

| Tier | Examples | Price |
|---|---|---|
| Free AI generators | Namelix, Namify, NameBot, namemyapp, namesmith.app | Free; generation + a domain check, no strategy |
| Crowdsourced contests | Atom (formerly Squadhelp) | $299 / $599 / $1,099 / $1,999 tiers, ~7 days |
| Brandable marketplaces | Atom, BrandBucket, Brandpa | $300 – $25,000+ per name with the `.com` attached |
| Naming agencies | Catchword, Igor, Zinzin, Lexicon, Siegel+Gale, Namebase | Five to six figures |

**Note the collision:** `namesmith.app` is a live AI business-name generator — "blends
state-of-the-art language models with real-time domain search". This skill's own name is
therefore not clear for any public product. Kept as an internal skill name; flagged here
because the skill's own rules would kill it.

**What the free tier does not do**, and where this skill's value sits: no brief, no
competitive namescape, no territory strategy, no four-language screen, no trap register, no
scorecard, no trademark knockout across national registers, and — as verified above —
availability checking that quietly reports registered `.io` and `.co` domains as free.
