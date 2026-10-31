---
title: "Thingsmith: a little forge for naming your next big thing"
section: tech
status: draft
thumbnail: ../assets/marketing/tech-thumbnail-forge.png
---

# Thingsmith: a little forge for naming your next big thing

![Thingsmith: a little forge for naming your next big thing](../assets/images/hero.png)

I keep making things that need names.

The naming is fun for about twenty minutes. Then I start checking domains. The name I like is taken. The next one sounds awkward in Polish. Another belongs to a software package I've never heard of.

I'm naming more things now, often for more than one country. I wanted a way to do the checks without rebuilding the process every time.

So I built Thingsmith: a free, open-source AI naming skill for Claude Code, Codex and Gemini CLI. It develops names and gathers domain, handle and language observations behind a shortlist.

## The space between a prompt and an agency

You can ask ChatGPT for fifty names. I've done that. It gets you moving, but a list doesn't tell you which names survive contact with the world.

You can also hire a specialist naming agency. Lexicon, whose work includes Pentium and Swiffer, publishes an average project fee of **US$75,000–$150,000**. That covers a professional engagement with research and human expertise. [Lexicon's process and pricing](https://www.lexiconbranding.com/brand-naming-process/).

I wanted something between those options. A repeatable process I could run myself, with the tedious checks attached and a clear account of what remained unknown.

Thingsmith is free to use under the MIT licence. Running it can still cost model tokens, and buying a domain costs whatever the domain costs.

## Start with the name's job

Thingsmith begins with what you're naming, who it's for and where it needs to work.

That matters because “I like it” is a difficult brief. “A name for a tender-discovery tool that small studios in the UK and Poland can say and remember” gives you something to test.

The full workflow maps competitor names, explores different naming territories and generates candidates from differently briefed teams. One gets the real brief. Another gets a disguised version of the same problem. A cold team gets very little context.

That's a way to introduce different starting points. It still needs evaluation; four agents aren't automatically four good ideas.

The candidates then go through screening and comparison. The output includes a rejection log. I like that part because it stops the next naming conversation from walking straight back into an idea we've already ruled out.

## “Available” is the difficult word

![A naming check with evidence and open questions](../assets/images/evidence-checks.png)

The most interesting engineering problem turned out to be deciding what a check actually proves.

A domain that doesn't resolve might still be registered. A missing profile might belong to a private account. A platform can return an error because it blocked your request.

Thingsmith uses registry RDAP and WHOIS lookups for domains, with DNS as supporting evidence that a name is already taken. Separate probes inspect handles and package registries.

Reviewing the implementation exposed places where the output was more confident than the evidence. Telegram and GitLab checks could print `FREE` while their own notes admitted that a hidden account or group might hold the name. A controlled RDAP fixture also showed why searching response text for “404” is weaker than parsing the response structure.

That's the standard I want the tool to meet: tell me what you observed, then tell me what it means. If all you know is that no public record was found, say that. Leave the next check visible.

Those findings led to concrete changes. The scripts now use `NO_RECORD_FOUND` for negative lookups. Hidden-holder cases remain `UNVERIFIED`, and offline regression tests cover the parser mistakes. The result is still an observation, not a promise that you can register or claim something.

## We make it say the names, too

![People trying names aloud in a welcoming workshop](../assets/images/say-it-together.png)

Thingsmith can read candidates using different language voices, then send the speech through transcription without supplying the spelling.

It's an inexpensive way to surface possible trouble. If the transcript comes back with a different word, that's worth investigating.

It isn't a room full of native speakers. A machine can get something wrong that a person understands immediately. People also pronounce international brands differently without losing track of the brand.

The useful question is whether the difference causes a problem in your market. Thingsmith includes a form for getting that feedback from real people.

## Put the shortlist somewhere real

A bare word is easy to dislike.

Thingsmith generates a context sheet showing finalists in everyday situations, including a homepage and an email. It uses the same styling for each candidate and includes competitors for comparison.

That makes the discussion more practical. Can I imagine introducing this? Does it work next to the names already in the market? What would I have to explain every time I said it?

The skill leaves you with a shortlist and the evidence behind it. Trademark clearance and human language checks remain separate work.

## It even had to rename itself

The earlier name was Namesmith. A collision with an existing AI naming tool helped rule that out.

Thingsmith is the working name that followed. Its trademark and native-speaker checks are still open, which feels like a fair place to leave the example: even the naming tool has unfinished checks.

A blacksmith makes things. Thingsmith makes names for things.

The [Thingsmith repository](https://github.com/samshennan/thingsmith) contains the skill and its scripts. Give it your next naming brief, inspect the evidence, and use the shortlist to decide what deserves the next round of checks.

## Questions before you try it

### Can AI check whether a business name is available?

It can gather evidence from domain registries and supported public platforms. That doesn't settle every reservation, hidden account or trademark conflict. Thingsmith separates what a lookup found from what you can actually register.

### Is Thingsmith free, and do I need API keys?

The skill is free under MIT, and its core Python checkers require no API keys. Your agent host may charge for model use. Domain purchases and professional checks are separate costs.

### Can I use it to name something for different countries?

Yes. State the markets and languages in your brief. The tool can investigate meanings and synthetic readings, then prepare questions for native speakers. Ordinary local pronunciation differences need human judgement rather than an automatic rejection.

### How do I start in Claude Code, Codex or Gemini CLI?

Clone the repository and follow its installation instructions. In Claude Code, try `/thingsmith name a product that …` with its audience and markets. For Codex and Gemini CLI, load the included instruction edition from the clone. You can also run the Python checks on names you already have.

### Does it replace a trademark lawyer or a naming agency?

It helps you build and investigate a shortlist. It doesn't provide professional trademark clearance or a human language panel. A bigger agency engagement may include expert research and stakeholder work that a self-run skill doesn't deliver.
