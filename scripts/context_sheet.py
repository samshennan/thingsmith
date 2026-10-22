#!/usr/bin/env python3
"""In-context presentation sheet for the namesmith skill.

Agencies never present a name as a word on a white slide. Siegel+Gale's rule
is to show it where it will live -- on the packaging, inside a press release
-- because a bare name invites objections that disappear in context.
Catchword built a visualiser that puts candidates into six real-world
scenarios for the same reason.

This script renders every finalist into the same set of scenes, in one
neutral typeface, so the comparison is between names and not between logo
treatments (Fabrik's warning: a styled mockup lets the font choose the name).
Optionally, competitor names are rendered in the identical scenes, so the
shortlist is judged against the field it will actually spar with.

Output is one self-contained HTML file. No network, no dependencies.

Usage:
    python context_sheet.py --names karbia ritka --descriptor "tender discovery for XR studios"
    python context_sheet.py --names karbia ritka --descriptor "..." \
        --competitors Mimira Tendrix --shuffle --out shortlist.html
"""

import argparse
import html
import random
import sys

CSS = """
:root{--bg:#f4f2ee;--card:#fff;--ink:#16161a;--mute:#6b6b74;--line:#dedad3;--accent:#2d5bff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{padding:28px 20px 8px;max-width:1200px;margin:auto}
header h1{font-size:18px;margin:0 0 4px}header p{margin:0;color:var(--mute)}
section.name{max-width:1200px;margin:24px auto;padding:0 20px}
section.name>h2{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--mute);
margin:0 0 10px;border-top:1px solid var(--line);padding-top:16px}
section.name.comp>h2::after{content:" · competitor, for scale";color:var(--accent)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.scene{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;min-height:120px}
.lbl{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--mute);margin-bottom:8px}
.url{font:13px ui-monospace,Menlo,Consolas,monospace;background:#f0f0f3;border-radius:6px;padding:6px 10px}
.hero{font-size:30px;font-weight:650;letter-spacing:-.01em;margin:10px 0 2px}
.sub{color:var(--mute)}
.icon{width:62px;height:62px;border-radius:15px;background:var(--ink);color:#fff;display:flex;
align-items:center;justify-content:center;font-size:28px;font-weight:650;margin:4px auto 6px}
.iconlbl{text-align:center;font-size:12px;width:76px;margin:auto;overflow:hidden;
white-space:nowrap;text-overflow:ellipsis}
.mail .from{font-weight:600}.mail .sig{margin-top:10px;border-top:1px solid var(--line);
padding-top:8px;font-size:13px;color:var(--mute)}
.say p{margin:4px 0;font-size:17px}.say em{color:var(--mute);font-style:normal;font-size:12px}
.news .src{font-size:11px;color:#b23}.news .hl{font:600 19px/1.25 Georgia,serif;margin-top:4px}
.serp .t{color:#1a0dab;font-size:17px}.serp .u{color:#1e6b34;font-size:13px}
.serp .d{font-size:13px;color:var(--mute)}
.card{border:1px solid var(--line);border-radius:6px;padding:14px;aspect-ratio:1.75}
.card b{font-size:20px;display:block}.card small{color:var(--mute)}
.note{background:#1e1e24;color:#fff;border-radius:12px;padding:10px 12px;font-size:13px}
.note b{display:block}.mono{font:13px ui-monospace,Menlo,Consolas,monospace;line-height:1.9}
footer{max-width:1200px;margin:30px auto;padding:0 20px 40px;color:var(--mute);font-size:13px}
@media print{.scene{break-inside:avoid}section.name{break-inside:avoid}}
"""


def scenes(name, descriptor, field, sender):
    n = html.escape(name)
    who = html.escape(sender)
    first = html.escape(sender.split()[0])
    low = html.escape(name.lower())
    d = html.escape(descriptor)
    rival = html.escape(field[0]) if field else "the incumbent"
    return f"""
<div class="scene"><div class="lbl">Homepage</div>
  <div class="url">https://{low}.com</div>
  <div class="hero">{n}</div><div class="sub">{d}</div></div>
<div class="scene"><div class="lbl">Phone home screen</div>
  <div class="icon">{html.escape(name[:1].upper())}</div><div class="iconlbl">{n}</div></div>
<div class="scene mail"><div class="lbl">Inbox</div>
  <div class="from">{first} at {n}</div><div>Your first report is ready</div>
  <div class="sig">{who} · {n}<br>{low}.com</div></div>
<div class="scene say"><div class="lbl">Said aloud (read these out)</div>
  <p>“Hi, I'm calling from {n}.”</p><p>“Have you tried {n}?”</p>
  <p>“Just {n} it.”</p><em>the verb test — fine if it fails, telling if it works</em></div>
<div class="scene news"><div class="lbl">Press</div><div class="src">TECH NEWS</div>
  <div class="hl">{n} raises seed round to take on {rival}</div></div>
<div class="scene serp"><div class="lbl">Search result</div>
  <div class="u">{low}.com</div><div class="t">{n} — {d}</div>
  <div class="d">{n} helps teams … Sign up free.</div></div>
<div class="scene"><div class="lbl">Business card</div>
  <div class="card"><b>{n}</b><small>{who}<br>hello@{low}.com</small></div></div>
<div class="scene"><div class="lbl">Notification</div>
  <div class="note"><b>{n}</b>3 new matches since yesterday</div></div>
<div class="scene"><div class="lbl">Every lowercase form — read for hidden words</div>
  <div class="mono">{low}.com<br>@{low}<br>github.com/{low}<br>hello@{low}.com<br>#{low}</div></div>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--names", nargs="+", required=True, help="finalists, 3-5 is right")
    ap.add_argument("--descriptor", required=True,
                    help="the plain line that sits under the name, e.g. 'tender discovery for XR studios'")
    ap.add_argument("--competitors", nargs="*", default=[],
                    help="names from the stage-1 grid, rendered identically for scale")
    ap.add_argument("--shuffle", action="store_true",
                    help="random finalist order -- use when the presenter has a favourite")
    ap.add_argument("--sender", default="Alex Morgan", help="person shown in the inbox and card scenes")
    ap.add_argument("--out", default="context-sheet.html")
    a = ap.parse_args()

    names = list(a.names)
    if a.shuffle:
        random.shuffle(names)
    if len(names) > 5:
        print("note: more than five finalists dilutes the comparison", file=sys.stderr)

    body = []
    for n in names:
        body.append(f'<section class="name"><h2>{html.escape(n)}</h2>'
                    f'<div class="grid">{scenes(n, a.descriptor, a.competitors, a.sender)}</div></section>')
    for c in a.competitors:
        body.append(f'<section class="name comp"><h2>{html.escape(c)}</h2>'
                    f'<div class="grid">{scenes(c, a.descriptor, names, a.sender)}</div></section>')

    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Names in context</title><style>{CSS}</style></head><body>
<header><h1>Names in context</h1>
<p>{html.escape(a.descriptor)} · {len(names)} finalists{', shown in random order' if a.shuffle else ''}.
Ask “which of these <em>work</em>, and why?” — not “which do you like?”</p></header>
{''.join(body)}
<footer>Same typeface, same scenes for every name, on purpose: judge the name, not the styling.
Read the “said aloud” lines out loud. Concept presentation only; no name here is cleared.</footer>
</body></html>"""
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"wrote {a.out}  ({len(names)} finalists, {len(a.competitors)} competitors)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
