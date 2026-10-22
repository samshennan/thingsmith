# Release preparation

Prepared 22 October 2026. Repository visibility is deliberately private.

## Included

- Owner-selected MIT licence, contributor guidance, cache ignores and line-ending rules.
- Illustrated README with a quick start, precise result semantics, limitations and a sourced agency price anchor.
- Three concept scenes, revised hero, two /tech thumbnails and a palette/style guide.
- Canonical skill plus generated Codex/Gemini editions; standalone regeneration helper.
- Direct name-check mode, market-specific constraints and /80 creative comparison separated from evidence.
- Structured RDAP parsing, conservative WHOIS negatives, unresolved hidden-handle cases and partial-result evidence.
- Offline regression tests and Windows/Linux Python 3.9/3.13 CI configuration.
- A complete /tech post draft and media kit. No blog site has been published or edited.

## Compatibility note

Negative lookup output changed from `FREE` to `NO_RECORD_FOUND`. Update any consumer that checks the old string. The result is an observation; script output leaves claimability `UNCONFIRMED`. Domain JSON remains a list and handle JSON remains keyed by candidate; both now include extra evidence fields. Handle entries also include `_summary` alongside `_manual`.

Exit 0 indicates completed requested automated checks, not a claimable name. Manual checks are still open. Exit 1 indicates unresolved, unsupported or invalid requested checks; CLI usage errors use 2. Speech output uses REVIEW/SIMILAR/NOT_COMPARED/UNSUPPORTED for reading comparisons; radio PASS/FAIL remains a synthetic result.

## Validation

Local Windows Python 3.10.6: 24 offline tests pass; adapter sync and relative Markdown links pass; `git diff --check` passes. Gitleaks 8.30.1 redacted scans found no matches in the working files or the repository's three pre-change historical commits. These checks don't establish live availability or replace human language/legal work. Hosted CI results are recorded on the review branch/PR.

## Owner actions later

Review/merge the release branch and choose when to change repository visibility. Publication is intentionally deferred. Use `assets/marketing/tech-thumbnail-forge.png` for the launch blog card and the evidence thumbnail for an availability-focused angle. Set the blog draft's publication metadata in the actual site when publishing.

Thingsmith itself is still a working name; its own native-speaker and trademark work remains disclosed. Don't turn historical name checks into current availability claims.
