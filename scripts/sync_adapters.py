#!/usr/bin/env python3
"""Generate the shipped Codex/Gemini instruction editions from SKILL.md."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def render(text):
    _, frontmatter, body = text.split("---", 2)
    description = next(line.split(":", 1)[1].strip().strip('"')
                       for line in frontmatter.splitlines() if line.startswith("description:"))
    body = body.strip() + "\n"
    return {
        "AGENTS.md": "<!-- Generated from SKILL.md by scripts/sync_adapters.py. -->\n\n" + body,
        "GEMINI.md": "<!-- Generated from SKILL.md by scripts/sync_adapters.py. -->\n\n"
                     + "When to use: " + description + "\n\n" + body,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    drift = []
    for name, expected in render((ROOT / "SKILL.md").read_text(encoding="utf-8")).items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                drift.append(name)
        else:
            with path.open("w", encoding="utf-8", newline="\n") as output:
                output.write(expected)
    if drift:
        print("Adapters out of sync: " + ", ".join(drift))
        return 1
    print("Adapters in sync." if args.check else "Generated AGENTS.md and GEMINI.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
