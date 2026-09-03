#!/usr/bin/env python3
"""Regenerates the profile SVG panels in the Saku palette.

Palette is the same one extracted from the desktop wallpaper
(~/.local/share/color-schemes/Saku.colors), so the profile and the
desktop read as one system.
"""
import json, os, subprocess, datetime

BG, LINE, TEXT, MUTED, ACCENT = "#1F2933", "#2C3644", "#C2BEC3", "#8A93A0", "#84A8CD"
SANS = "system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
HERE = os.path.dirname(os.path.abspath(__file__))

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def frame(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img">'
            f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="6" '
            f'fill="{BG}" stroke="{LINE}"/>'
            f'<rect x="24" y="22" width="1" height="{h-44}" fill="{ACCENT}" opacity="0.45"/>'
            f'{body}</svg>')

def label(x, y, s):
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="11" '
            f'letter-spacing="1.6" fill="{MUTED}">{esc(s.upper())}</text>')

def value(x, y, s, size=15, fill=TEXT):
    return (f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="{size}" '
            f'fill="{fill}">{esc(s)}</text>')

# ---- stack panel -----------------------------------------------------------
STACK = [("Warehouse", "Snowflake · PostgreSQL"), ("Transform", "dbt · SQL · Python"),
         ("Orchestration", "Dagster"), ("Ingestion", "Airbyte"),
         ("BI", "Lightdash"), ("Runtime", "Docker · Linux")]

def stack_panel(path):
    w, h, cols = 860, 224, 2
    colw, x0, y0 = 400, 56, 62
    parts = [label(x0, 36, "stack")]
    for i, (k, v) in enumerate(STACK):
        x = x0 + (i % cols) * colw
        y = y0 + (i // cols) * 54
        parts.append(label(x, y, k))
        parts.append(value(x, y + 22, v))
    open(path, "w").write(frame(w, h, "".join(parts)))

# ---- repository cards ------------------------------------------------------
LANG_DOT = {"Python": "#8AA9C9", "SQL": "#9EB3A6", "PLpgSQL": "#9EB3A6"}

def gh(*args):
    return json.loads(subprocess.check_output(["gh", "api", *args], text=True))

def repo_card(repo, blurb, path):
    d = gh(f"repos/Seinokojii/{repo}")
    langs = gh(f"repos/Seinokojii/{repo}/languages")
    lang = max(langs, key=langs.get) if langs else "—"
    when = datetime.datetime.strptime(d["pushed_at"], "%Y-%m-%dT%H:%M:%SZ")
    w, h = 420, 150
    dot = LANG_DOT.get(lang, MUTED)
    body = (label(56, 36, "repository")
            + value(56, 68, repo, size=17)
            + value(56, 92, blurb, size=13, fill=MUTED)
            + f'<circle cx="61" cy="{h-30}" r="4" fill="{dot}"/>'
            + f'<text x="74" y="{h-26}" font-family="{MONO}" font-size="11" '
              f'letter-spacing="1.2" fill="{MUTED}">{esc(lang.upper())}'
              f'<tspan fill="{LINE}">  ·  </tspan>'
              f'{when.strftime("%b %Y").upper()}</text>')
    open(path, "w").write(frame(w, h, body))

if __name__ == "__main__":
    stack_panel(os.path.join(HERE, "stack.svg"))
    repo_card("analytics-engineer-roadmap", "Full AE stack, built day by day",
              os.path.join(HERE, "repo-roadmap.svg"))
    repo_card("37BOT", "Telegram bot", os.path.join(HERE, "repo-37bot.svg"))
    print("panels rebuilt")
