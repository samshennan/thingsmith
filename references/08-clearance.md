# Stage 6 — Verification and clearance

**Gate: every shortlisted name has a domain picture, a handle picture, a knockout result and
a collision result — each with evidence, and each unresolved item named as unresolved.**

This is the stage that kills names, and the stage where a sloppy answer costs the most. The
governing rule: **"no collision found" means *you did not find one*. Say it that way.**

Four checks. Run them in this order — trademark first, because it is the only one that can
end the project, and it is free.

---

## 1. Trademark knockout

### What a knockout is and is not

A **knockout** is a quick screen for identical and near-identical marks in the relevant
classes. It answers "is this obviously dead?" — nothing more.

A **full clearance** covers federal, national, common-law, domain and international sources,
applies a likelihood-of-confusion analysis, weighs coexistence and seniority, and ends in a
written opinion from someone qualified to give one.

**This skill performs knockouts.** It never performs clearance, and every output must carry
the sentence:

> This is a knockout screen, not legal clearance. It does not cover similar-sounding or
> visually similar marks, unregistered common-law rights, or state and regional registers.
> A trademark attorney must clear the final candidate before launch.

Skipping that sentence is how a knockout gets quoted back as "we checked and it's fine".

### The registers, in order

Free, no account needed, all of them:

| Register | URL | Covers |
|---|---|---|
| **TMview** | tmdn.org/tmview | 70+ offices in one search — start here, it is the highest-yield single query |
| **EUIPO eSearch plus** | euipo.europa.eu/eSearch | EU trade marks and designs |
| **WIPO Global Brand Database** | branddb.wipo.int | Madrid international registrations |
| **USPTO Trademark Search** | tmsearch.uspto.gov | US federal (replaced TESS) |
| **UPRP** (Poland) | ewyszukiwarka.pue.uprp.gov.pl | Polish national register |
| **IP Australia** | search.ipaustralia.gov.au/trademarks | Australian register |
| **UK IPO** | trademarks.ipo.gov.uk/ipo-tmtext | UK register |

Search **TMview plus the national register of every market in the brief.** TMview is broad
but not exhaustive per office, so the national search is not redundant.

### Which classes

The Nice Classification has 45 classes, and the same mark can legitimately coexist across
unrelated ones. Search the classes the thing actually trades in:

| Class | Scope |
|---|---|
| **9** | Software, downloadable apps, recorded data, hardware |
| **35** | Business services, advertising, data processing, retail |
| **38** | Telecommunications, streaming, transmission |
| **41** | Education, training, entertainment — **any VR/simulation training offer** |
| **42** | SaaS, PaaS, software design and development, hosting, R&D |
| **45** | Security services, legal, personal and social services |

A software product sold to enterprise typically needs **9 and 42**, plus **35** if it touches
business process and **41** if it teaches anything. Use TMclass (`euipo.europa.eu/ec2`) to
confirm rather than guessing.

### How to search

For each shortlisted name, in each register:

1. **Exact string.** If it is registered in your class, the name is dead — score 0.
2. **Wildcard the ending** (`karbi*`) — catches the near-identicals that matter most.
3. **Phonetic neighbours.** Swap the vowels, drop a doubled consonant, try the obvious
   misspelling. `Minra` against `Mimira` is the case worth remembering: not identical, close
   enough to be a problem, and specifically close to the incumbent being displaced — which is
   the worst possible direction to be similar in.
4. **Record what you searched.** Register, class, query string, date, hit count. A knockout
   with no record cannot be re-run or defended.

### Reading a result

| Finding | Score | Action |
|---|---|---|
| Identical mark, same/related class, live | 0 | Dead. Remove. |
| Identical mark, unrelated class only | 5 | Viable; flag for the attorney |
| Near-identical, related class | 0–5 | Usually dead; attorney call |
| Expired or abandoned mark | 5–10 | Note it — abandonment can be contested and the owner may still hold common-law rights |
| Nothing found | 10 | "Nothing found in the registers searched", never "clear" |

### The pharma exception

If the thing is anything medical or pharmaceutical, WHO INN stems (`-mab`, `-tinib`,
`-prazole`, `-vir`, and hundreds more) are reserved and coining into them causes a rejection
regardless of trademark status. Check the INN stem list before coining in that space.

---

## 2. Domains

```bash
python "${CLAUDE_SKILL_DIR}/scripts/check_domains.py" \
  --names ritka karbia zyla --tlds com pl io ai --csv domains.csv --json domains.json
```

### How the script decides, and why

Ladder per domain: **DNS NS proof → registry RDAP → port-43 WHOIS → UNVERIFIED.**

- **DNS is a one-way TAKEN proof only.** NS records present ⇒ registered, definitively, for
  free, with no rate limit — which settles most of a sweep before an RDAP call is spent.
  Absence of NS proves nothing and is never reported as free.
- **RDAP, never bare DNS, for availability.** A registered-but-unhosted domain returns
  NXDOMAIN and would misreport as free. This single mistake invalidates a whole sweep.
- **The TLD must be resolved to a verified registry endpoint first.** `rdap.org` returns a
  bare, bodyless 404 *both* for "domain not found" and for "I have no server for `.io`" —
  indistinguishable. v1 of this script treated that as FREE, which would have cleared every
  `.io` and `.co` candidate it ever saw. The script now uses the IANA bootstrap
  (`data.iana.org/rdap/dns.json`, cached weekly) plus a hand-verified extras map, and reports
  `UNSUPPORTED` rather than guessing.
- **WHOIS on port 43 is the third rung and it is load-bearing in Europe.** `.pl` RDAP
  hard-429s from any non-registrar IP; `.co` and `.eu` publish no RDAP at all. All three
  answer WHOIS cleanly, with the server discovered from `whois.iana.org`.
- **`UNVERIFIED` and `UNSUPPORTED` print as themselves and the script exits non-zero.** A
  partial sweep cannot be handed over as a clean one.

Run `--tld-report` before a big sweep to see which TLDs are answerable at all.

### Which TLDs

- **`.com` and the home-market TLD for everything.** Non-negotiable.
- `.io`, `.ai`, `.dev`, `.app` only for survivors — they are a decision, not a default.

### TLD facts that change the decision

- **`.ai` requires a 2-year minimum registration.** The up-front cost is double the
  advertised annual price; budget ~$160–200 for the first commitment.
- **`.com.au` requires an Australian entity or ABN.** It cannot be bought from abroad. If
  Australia is in the brief, this is a corporate-structure question, not a domain question,
  and it needs raising early.
- **`.io` carries geopolitical tail risk.** It is the ccTLD of the British Indian Ocean
  Territory; the Chagos sovereignty transfer has been repeatedly proposed and repeatedly
  stalled. As of 2026 `.io` is fully operational with no change to its delegation, and any
  removal would be a multi-year phased transition rather than a switch-off. Treat it as a
  small, disclosed, long-horizon risk — not a reason to avoid it, and not something to leave
  unmentioned when the brief expects a domain to last a decade.
- **`.eu` requires an EU-resident registrant.** Fine for a Polish entity; not for a UK one
  post-Brexit.
- **A parked `.com` has a price.** Get it before writing the name off: check the aftermarket
  listing, look up the registrant via WHOIS/RDAP, and get an appraisal range. Coined names
  are cheaper than real words; short is dearer than long. A four-figure `.com` for the right
  name is usually the cheapest brand decision in the project.

### Price the bundle honestly

**First year *and* renewal**, from real registrar pages, for the set you would actually buy:
the `.com`, the home TLD, and any defensive registration that matters. Renewal is where
people get surprised — several TLDs are cheap to buy and expensive to keep.

---

## 3. Handles

```bash
python "${CLAUDE_SKILL_DIR}/scripts/check_handles.py" --names ritka karbia --json handles.json
python "${CLAUDE_SKILL_DIR}/scripts/check_handles.py" --list
```

**Automated:** GitHub · npm · PyPI · crates.io · Docker Hub · Hugging Face · YouTube ·
Telegram · Bluesky · GitLab · Reddit.

**Manual, and reported as manual:** X · Instagram · LinkedIn company slug · Product Hunt ·
TikTok · app-store developer name. These block anonymous lookups; the script reports
`BLOCKED`, never "free", and exits non-zero so the gap cannot pass silently.

Two that people underrate:

- **The package registries decide developer-facing SEO.** If `npm i <yourname>` already
  installs something else, that is permanent, and it is worse than a taken social handle.
- **PyPI normalises `-`, `_` and `.` to the same name.** `my-name`, `my_name` and `my.name`
  are one namespace.

---

## 4. Collision search — the check that kills

Run this on every candidate that survives the domain check. It has killed more good names
than availability has.

Search the name plus:

1. **The product's own category** — "karbia tender platform", "karbia VR training"
2. **Software packages and libraries** — npm, PyPI, GitHub, Hugging Face, and the phrase
   "<name> algorithm" / "<name> library". `boruta` died here: a feature-selection algorithm
   every data scientist already knows.
3. **Companies trading in each market**, including the national company register
4. **The metaphor, not just the word** — `fossick` was reported clean by one search; a second
   found an Australian recruiter using the identical gold-rush metaphor in the same market.
5. **Listed companies, tickers, tokens and public figures** in the home market. `rokita`
   collided with a WSE-listed chemical company *and* a nationally known politician.

**Two searches minimum, by different routes.** The single-search clean result has been wrong
often enough in this workspace to be treated as unreliable on its own.

---

## What goes in the report

Per shortlisted name:

```
NAME
  domains    .com FREE (rdap 404) | .pl FREE (whois) | .ai taken | .io UNSUPPORTED
  handles    free: github, npm, pypi, youtube | taken: telegram | BLOCKED: x, instagram, linkedin
  trademark  TMview 0 hits cl.9/42 (2026-08-22) | UPRP 0 hits | IP Australia 1 hit cl.41, unrelated
  collision  2 searches, nothing found. NOT a clearance.
  bundle     .com $12/yr + .pl PLN 60/yr + .ai $160/2yr = ~$XXX first year, ~$XXX renewal
  UNRESOLVED .io status, X and LinkedIn handles
```

The `UNRESOLVED` line is mandatory and appears even when empty. Its absence is how a partial
verification passes for a complete one.
