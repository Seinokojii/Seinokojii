#!/usr/bin/env python3
"""Regenerates every graphic on the profile and rewrites README.md.

Design notes
------------
* Palette is the one extracted from the desktop wallpaper, so the profile and
  the desktop read as one system: see ~/.local/share/color-schemes/Saku.colors.
* GitHub proxies images through camo, which does not load web fonts, so every
  SVG uses system font stacks only.
* camo also caches by path, so file names carry a content hash. A changed panel
  gets a new name, which is the only reliable way to make the proxy refetch it.
* Panels are read at 860px on desktop and ~400px on a phone, so type is sized
  for the phone: nothing below 15px at native size.
"""
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime

USER = "Seinokojii"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

BG, LINE, TEXT, MUTED, ACCENT = "#1F2933", "#2C3644", "#C2BEC3", "#8A93A0", "#84A8CD"
EMPTY = "#242B37"
RAMP = ["#33465A", "#4A6D8F", "#6B93BC", "#84A8CD"]
SANS = "system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
W = 860


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def gh(*args):
    return json.loads(subprocess.check_output(["gh", "api", *args], text=True))


def graphql(query):
    out = subprocess.check_output(["gh", "api", "graphql", "-f", f"query={query}"], text=True)
    return json.loads(out)["data"]


def panel(height, body):
    """A card in the Saku palette with the accent hairline down its left edge."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
            f'viewBox="0 0 {W} {height}" role="img">'
            f'<rect x="0.5" y="0.5" width="{W-1}" height="{height-1}" rx="8" '
            f'fill="{BG}" stroke="{LINE}"/>'
            f'<rect x="28" y="28" width="2" height="{height-56}" fill="{ACCENT}" opacity="0.4"/>'
            f'{body}</svg>')


def eyebrow(x, y, s):
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="15" '
            f'letter-spacing="2.4" fill="{MUTED}">{esc(s.upper())}</text>')


def text(x, y, s, size=26, fill=TEXT, family=SANS, weight=400, extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}"{extra}>{esc(s)}</text>')


# --------------------------------------------------------------------- panels
STACK = [("Warehouse", "Snowflake · PostgreSQL"), ("Transform", "dbt · SQL · Python"),
         ("Orchestration", "Dagster"), ("Ingestion", "Airbyte"),
         ("BI", "Lightdash"), ("Runtime", "Docker · Linux")]


def stack_panel():
    x0, colw, rowh, y0 = 64, 400, 78, 116
    parts = [eyebrow(x0, 62, "stack")]
    for i, (k, v) in enumerate(STACK):
        x, y = x0 + (i % 2) * colw, y0 + (i // 2) * rowh
        parts.append(f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="15" '
                     f'letter-spacing="1.6" fill="{MUTED}">{esc(k.upper())}</text>')
        parts.append(text(x, y + 32, v, size=25))
    return panel(y0 + 2 * rowh + 44, "".join(parts))


def activity_panel():
    d = graphql('{ user(login: "%s") { contributionsCollection {'
                ' contributionCalendar { totalContributions'
                ' weeks { contributionDays { date contributionCount weekday } } } } } }' % USER)
    cal = d["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    counts = [day["contributionCount"] for w in weeks for day in w["contributionDays"]]
    top = max(counts) or 1

    grid_x, grid_y = 64, 132
    gap = 3
    cell = (W - 2 * grid_x - (len(weeks) - 1) * gap) / len(weeks)
    parts = [eyebrow(grid_x, 62, "contribution activity"),
             text(grid_x, 100, f'{cal["totalContributions"]} contributions in the last year',
                  size=22, fill=MUTED)]

    months = []
    for wi, week in enumerate(weeks):
        for day in week["contributionDays"]:
            n = day["contributionCount"]
            if n == 0:
                fill = EMPTY
            else:
                fill = RAMP[min(3, int((n - 1) / max(1, top / 4)))]
            x = grid_x + wi * (cell + gap)
            y = grid_y + day["weekday"] * (cell + gap)
            parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{cell:.2f}" height="{cell:.2f}" rx="2.5" fill="{fill}"/>')
        first = week["contributionDays"][0]["date"]
        m = datetime.strptime(first, "%Y-%m-%d")
        if m.day <= 7:
            months.append((grid_x + wi * (cell + gap), m.strftime("%b")))

    label_y = grid_y - 12
    for x, m in months:
        parts.append(f'<text x="{x}" y="{label_y}" font-family="{MONO}" font-size="13" '
                     f'letter-spacing="1" fill="{MUTED}" opacity="0.75">{m}</text>')

    legend_y = grid_y + 7 * (cell + gap) + 34
    parts.append(f'<text x="{grid_x}" y="{legend_y}" font-family="{MONO}" font-size="14" '
                 f'letter-spacing="1.4" fill="{MUTED}">QUIET</text>')
    lx = grid_x + 72
    for fill in [EMPTY] + RAMP:
        parts.append(f'<rect x="{lx:.2f}" y="{legend_y - 12}" width="{cell:.2f}" height="{cell:.2f}" rx="2.5" fill="{fill}"/>')
        lx += cell + gap
    parts.append(f'<text x="{lx + 8}" y="{legend_y}" font-family="{MONO}" font-size="14" '
                 f'letter-spacing="1.4" fill="{MUTED}">BUSY</text>')
    return panel(legend_y + 34, "".join(parts))


def repo_panel():
    name = "analytics-engineer-roadmap"
    d = gh(f"repos/{USER}/{name}")
    langs = gh(f"repos/{USER}/{name}/languages")
    lang = max(langs, key=langs.get) if langs else "—"
    when = datetime.strptime(d["pushed_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%b %Y").upper()
    body = (eyebrow(64, 62, "current work")
            + text(64, 110, name, size=30)
            + text(64, 146, "Snowflake, dbt, Dagster, Airbyte and Lightdash, wired up day by day",
                   size=20, fill=MUTED)
            + f'<circle cx="70" cy="184" r="6" fill="{ACCENT}"/>'
            + f'<text x="88" y="190" font-family="{MONO}" font-size="15" letter-spacing="1.6" '
              f'fill="{MUTED}">{esc(lang.upper())}<tspan fill="{LINE}">  ·  </tspan>'
              f'LAST PUSH {when}</text>')
    return panel(224, body)


# ------------------------------------------------------------------- plumbing
def emit(prefix, svg):
    """Writes assets/<prefix>.<hash>.svg and drops older builds of that panel."""
    digest = hashlib.sha1(svg.encode()).hexdigest()[:8]
    name = f"{prefix}.{digest}.svg"
    for old in os.listdir(HERE):
        if old.startswith(prefix + ".") and old.endswith(".svg") and old != name:
            os.remove(os.path.join(HERE, old))
    with open(os.path.join(HERE, name), "w") as f:
        f.write(svg)
    return f"./assets/{name}"


def render_readme(paths):
    tmpl = open(os.path.join(HERE, "README.tmpl.md")).read()
    for key, path in paths.items():
        tmpl = tmpl.replace("{{%s}}" % key, path)
    open(os.path.join(ROOT, "README.md"), "w").write(tmpl)


if __name__ == "__main__":
    paths = {
        "stack": emit("stack", stack_panel()),
        "activity": emit("activity", activity_panel()),
        "repo": emit("repo", repo_panel()),
    }
    render_readme(paths)
    print("\n".join(f"{k:10} {v}" for k, v in paths.items()))
