# Investigation and open checks

This stage gathers preliminary evidence. It does not issue legal clearance or guarantee registration.

## Domains

Run `scripts/check_domains.py`. DNS NS is one-way evidence of use. A matching RDAP domain object establishes a registration record; a structured registry no-record response establishes only NO_RECORD_FOUND. Query-specific WHOIS can be a fallback. Generic 404s, disclaimers, throttling and unsupported endpoints stay unresolved. Some registries cannot be interpreted by these parsers.

Re-check at a registrar for actual registration eligibility, reserved or premium names, acquisition price and renewal cost. Note exact-match requirements and acceptable alternatives. Do not infer that a taken domain can be bought at a guessed price. Record queried domain, endpoint, UTC time, source, parser version and decisive result. Claimability remains UNCONFIRMED in script output.

## Handles

Run `scripts/check_handles.py --list` for current coverage. Use `--only` for the namespaces the brief needs. NO_RECORD_FOUND means a negative public lookup. Telegram and GitLab can hide holders; ambiguous results stay UNVERIFIED. Package registries may prohibit a name even when no package record appears. PyPI normalises punctuation; keep the normalised query visible in the request URL.

Manual entries are listed, never completed by implication. Exit 0 means only the requested automated observations completed. JSON includes each request URL, final URL, HTTP status, timestamp and response digest. A digest permits comparison, not reconstruction of the response body. Don't claim that the tool saved a full response transcript.

## Preliminary conflict research

Search relevant category and local company collisions using distinct routes. For preliminary trademark work record exact queries, official databases used, date, jurisdictions and goods/classes. A no-hit result isn't legal clearance. Never invent a likelihood score or give jurisdiction-free priority rules. An appropriate professional must assess legal use before a consequential launch.

## Deliver

Use the report template. Separate completed observations, suitability decisions and outstanding work. Keep renewal/acquisition costs labelled known or unknown. Re-check current availability before purchase. No purchases, claims, filings or outreach happen without the user's instruction.
