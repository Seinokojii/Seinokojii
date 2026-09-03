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
import sys
from datetime import datetime

USER = "Seinokojii"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

BG, LINE, TEXT, MUTED, ACCENT = "#1F2933", "#2C3644", "#C2BEC3", "#8A93A0", "#84A8CD"
HERO = "#1B2531"   # the hero panel sits one step deeper than the rest
EMPTY = "#242B37"
RAMP = ["#33465A", "#4A6D8F", "#6B93BC", "#84A8CD"]
SANS = "system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
W = 860


RIGHT_EDGE = W - 64


def fits(x, string, size, family=None, where=""):
    """Warns when a string would run past the panel's right margin.

    An SVG has no layout engine, so overflow is invisible until the page is
    rendered. These ratios are measured from the system stacks below and are
    deliberately pessimistic.
    """
    ratio = 0.60 if family == "mono" else 0.55
    end = x + len(string) * size * ratio
    if end > RIGHT_EDGE:
        print(f"  overflow: {where or string!r} ends near {end:.0f}px, "
              f"margin is {RIGHT_EDGE}px", file=sys.stderr)
    return string


def centred(cx, string, size, family=None, where=""):
    """Same guard as fits(), for text that grows from its own centre."""
    ratio = 0.60 if family == "mono" else 0.55
    half = len(string) * size * ratio / 2
    if cx - half < W - RIGHT_EDGE or cx + half > RIGHT_EDGE:
        print(f"  overflow: centred {where or string!r} spans "
              f"{cx - half:.0f}..{cx + half:.0f}px", file=sys.stderr)
    return string


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def gh(*args):
    return json.loads(subprocess.check_output(["gh", "api", *args], text=True))


def graphql(query):
    out = subprocess.check_output(["gh", "api", "graphql", "-f", f"query={query}"], text=True)
    return json.loads(out)["data"]


def panel(height, body, hairline=False, fill=BG):
    """A card in the Saku palette.

    The accent hairline is reserved for the hero panel. Repeating it on every
    card turned the page into five identical slabs; the other panels carry
    their own accent already — ramp bars, timeline dots, heatmap cells.
    """
    edge = (f'<rect x="28" y="28" width="2" height="{height-56}" fill="{ACCENT}" '
            f'opacity="0.4"/>') if hairline else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
            f'viewBox="0 0 {W} {height}" role="img">'
            f'<rect x="0.5" y="0.5" width="{W-1}" height="{height-1}" rx="8" '
            f'fill="{fill}" stroke="{LINE}"/>'
            f'{edge}{body}</svg>')


def eyebrow(x, y, s):
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="15" '
            f'letter-spacing="2.4" fill="{MUTED}">{esc(s.upper())}</text>')


def text(x, y, s, size=26, fill=TEXT, family=SANS, weight=400, extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}"{extra}>{esc(s)}</text>')


# --------------------------------------------------------------------- panels
STACK = [
    ("Warehouse", "Snowflake · DuckDB · PostgreSQL"),
    ("Transform", "dbt — models, macros, snapshots, contracts"),
    ("Orchestration", "Dagster — assets, partitions, sensors"),
    ("Ingestion", "Airbyte, self-hosted"),
    ("Quality", "dbt-expectations · Elementary · pytest"),
    ("Semantics & BI", "dbt Semantic Layer · MetricFlow · Lightdash"),
    ("Interfaces", "FastAPI · SQLAlchemy"),
    ("Runtime", "Docker · Linux · GitHub Actions"),
]


def stack_panel():
    """One column with a fixed label gutter: the two-column version clipped
    'dbt Semantic Layer, MetricFlow, Lightdash' at the panel edge."""
    x0, gutter, rowh, y0 = 64, 176, 54, 116
    parts = [eyebrow(x0, 62, "stack")]
    for i, (k, v) in enumerate(STACK):
        y = y0 + i * rowh
        parts.append(f'<text x="{x0}" y="{y}" font-family="{MONO}" font-size="15" '
                     f'letter-spacing="1.4" fill="{MUTED}">{esc(k.upper())}</text>')
        fits(x0 + gutter, v, 21, where=f"stack/{k}")
        parts.append(text(x0 + gutter, y, v, size=21))
    return panel(y0 + (len(STACK) - 1) * rowh + 48, "".join(parts))


def pipeline_panel():
    """The shape of the pipeline the roadmap repository builds up to.

    Drawn by hand rather than with mermaid: GitHub renders mermaid in its own
    colours, which would leave one element on the page fighting the palette.
    Stages sit on a rail rather than in boxes — five boxes across 732px left
    the labels wider than the boxes holding them.
    """
    name = "analytics-engineer-roadmap"
    d = gh(f"repos/{USER}/{name}")
    when = datetime.strptime(d["pushed_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%b %Y")

    stages = [("SOURCE", "gh_events"), ("RAW", "json payload"),
              ("STAGING", "flatten · dedupe"), ("MARTS", "incremental"),
              ("SERVING", "Lightdash · API")]
    x0 = 64
    # the rail is inset from the panel margin by half of the widest end label,
    # otherwise "SOURCE" runs into the accent hairline and "Lightdash · API"
    # runs off the right edge
    inset = 72
    first, last = x0 + inset, W - x0 - inset
    step = (last - first) / (len(stages) - 1)
    rail = 268

    parts = [eyebrow(x0, 62, "current work"),
             text(x0, 108, name, size=30),
             text(x0, 142, "One pipeline, reproducible from a clean checkout: ingest, model, "
                           "test, orchestrate.", size=20, fill=MUTED)]

    # orchestration bracket over the whole rail
    parts.append(f'<path d="M{x0} {rail - 46} v-12 H{W - x0} v12" fill="none" '
                 f'stroke="{LINE}" stroke-width="1.5"/>')
    parts.append(f'<text x="{W / 2}" y="{rail - 68}" text-anchor="middle" '
                 f'font-family="{MONO}" font-size="15" letter-spacing="1.8" fill="{MUTED}">'
                 f'DAGSTER · PARTITIONED BY DAY · IDEMPOTENT BACKFILL</text>')

    parts.append(f'<path d="M{first} {rail} H{last}" stroke="{LINE}" stroke-width="1.5"/>')
    for i, (label, sub) in enumerate(stages):
        cx = first + i * step
        centred(cx, label, 17, "mono", f"pipeline/{label}")
        centred(cx, sub, 16, where=f"pipeline/{label} caption")
        parts.append(f'<circle cx="{cx:.1f}" cy="{rail}" r="6" fill="{BG}" '
                     f'stroke="{ACCENT}" stroke-width="2"/>')
        parts.append(f'<text x="{cx:.1f}" y="{rail - 22}" text-anchor="middle" '
                     f'font-family="{MONO}" font-size="17" letter-spacing="1.4" '
                     f'fill="{TEXT}">{esc(label)}</text>')
        parts.append(f'<text x="{cx:.1f}" y="{rail + 32}" text-anchor="middle" '
                     f'font-family="{SANS}" font-size="16" fill="{MUTED}">{esc(sub)}</text>')
        if i < len(stages) - 1:
            mx = cx + step / 2
            parts.append(f'<path d="M{mx - 4:.1f} {rail - 5} l6 5 -6 5" fill="none" '
                         f'stroke="{ACCENT}" stroke-width="1.6" stroke-linejoin="round" '
                         f'stroke-linecap="round"/>')

    qy = rail + 66
    parts.append(f'<path d="M{x0} {qy} v12 H{W - x0} v-12" fill="none" stroke="{LINE}" '
                 f'stroke-width="1.5" stroke-dasharray="3 5"/>')
    parts.append(f'<text x="{W / 2}" y="{qy + 38}" text-anchor="middle" font-family="{MONO}" '
                 f'font-size="15" letter-spacing="1.8" fill="{MUTED}">'
                 f'30 TESTS IN THREE LAYERS · CI ON EVERY PULL REQUEST</text>')

    foot = qy + 78
    parts.append(f'<circle cx="{x0 + 6}" cy="{foot - 5}" r="6" fill="{ACCENT}"/>')
    line = f"Python · DuckDB locally, Snowflake by changing a target · pushed {when}"
    fits(x0 + 24, line, 17, where="pipeline/footer")
    parts.append(text(x0 + 24, foot, line, size=17, fill=MUTED))
    return panel(foot + 34, "".join(parts), hairline=True, fill=HERO)


QUALITY = [
    ("dbt core tests", "Is this row valid?", "unique, not_null, accepted_values"),
    ("dbt-expectations", "Is this value plausible?", "row counts, payload size in range"),
    ("Elementary", "Does today look like yesterday?", "volume drops, mean shift, null spikes"),
    ("Dagster asset checks", "Should downstream run at all?", "raw not empty, source fresh"),
]


def quality_panel():
    x0, y0, rowh = 64, 120, 78
    parts = [eyebrow(x0, 62, "how the data is checked"),
             text(x0, 96, "Four layers, each catching what the others miss.", size=20, fill=MUTED)]
    for i, (layer, question, example) in enumerate(QUALITY):
        y = y0 + 40 + i * rowh
        parts.append(f'<rect x="{x0}" y="{y - 26}" width="4" height="42" rx="2" '
                     f'fill="{RAMP[i]}"/>')
        fits(x0 + 22, question, 22, where=f"quality/{layer}")
        parts.append(text(x0 + 22, y, question, size=22))
        parts.append(f'<text x="{x0 + 22}" y="{y + 24}" font-family="{MONO}" font-size="15" '
                     f'letter-spacing="1.2" fill="{MUTED}">{esc(layer.upper())}'
                     f'<tspan fill="{LINE}">  ·  </tspan>{esc(example)}</text>')
    return panel(y0 + 40 + len(QUALITY) * rowh + 6, "".join(parts))


JOURNEY = [
    ("done", "Foundations", "SQL to window functions and EXPLAIN, Python to Polars and Pydantic"),
    ("done", "dbt, end to end", "Models, macros, snapshots, data contracts, CI on pull requests"),
    ("done", "Orchestration and cloud", "Dagster assets and partitions, Snowflake, self-hosted Airbyte"),
    ("now", "Snowflake architecture", "Time travel, zero-copy clone, streams and tasks"),
    ("next", "Semantics and BI", "MetricFlow, Lightdash, a data API, portfolio projects"),
]


def journey_panel():
    x0, y0, rowh = 64, 116, 76
    parts = [eyebrow(x0, 62, "the way through")]
    last = len(JOURNEY) - 1
    for i, (state, title, detail) in enumerate(JOURNEY):
        y = y0 + i * rowh
        cx, cy = x0 + 7, y - 6
        if i != last:
            parts.append(f'<path d="M{cx} {cy + 12} V{cy + rowh - 12}" stroke="{LINE}" '
                         f'stroke-width="1.5"/>')
        if state == "done":
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{ACCENT}" opacity="0.55"/>')
        elif state == "now":
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{BG}" stroke="{ACCENT}" '
                         f'stroke-width="2.5"/>')
        else:
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="none" stroke="{LINE}" '
                         f'stroke-width="1.5"/>')
        fill = TEXT if state != "next" else MUTED
        parts.append(text(x0 + 32, y, title, size=23, fill=fill))
        if state == "now":
            parts.append(f'<text x="{x0 + 32 + 11.5 * len(title)}" y="{y}" '
                         f'font-family="{MONO}" font-size="15" letter-spacing="1.6" '
                         f'fill="{ACCENT}">   NOW</text>')
        fits(x0 + 32, detail, 18, where=f"journey/{title}")
        parts.append(f'<text x="{x0 + 32}" y="{y + 26}" font-family="{SANS}" font-size="18" '
                     f'fill="{MUTED}">{esc(detail)}</text>')
    return panel(y0 + last * rowh + 62, "".join(parts))


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


MONTHS = [
    ("Foundations", "Days 1-30",
     "SQL from joins to window functions, Python to pandas and Polars, "
     "first ETL patterns"),
    ("Advanced SQL, testing, dbt", "Days 31-60",
     "Recursive CTEs, QUALIFY, MERGE, EXPLAIN ANALYZE; dbt models, macros, "
     "snapshots, contracts; pytest and Great Expectations"),
    ("Orchestration and cloud", "Days 61-90",
     "Dagster software-defined assets, partitions and sensors; Snowflake "
     "architecture and loading; self-hosted Airbyte; the first end-to-end "
     "pipeline with tests, CI and docs"),
    ("Snowflake architecture", "Days 91-130",
     "Time travel, zero-copy clone, streams and tasks, Snowpipe; medallion "
     "layering; MetricFlow; FastAPI as a data API"),
    ("Semantics, BI and portfolio", "Days 131-165",
     "Lightdash on top of the semantic layer, then three portfolio builds"),
]


def recent_section():
    """The day-by-day log, taken from the roadmap's own feat: commits."""
    commits = gh("repos/%s/analytics-engineer-roadmap/commits?per_page=40" % USER)
    lines = []
    for c in commits:
        subject = c["commit"]["message"].split("\n")[0]
        if not subject.startswith("feat:"):
            continue
        title = subject[5:].strip().replace("->", "\u2192")
        when = datetime.strptime(c["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ")
        url = c["html_url"]
        lines.append(f'- [{title}]({url}) &nbsp;<sub>{when.strftime("%d %b %Y")}</sub>')
        if len(lines) == 5:
            break
    return "\n".join(lines)


def curriculum_section():
    rows = "\n".join(f"| **{name}** | {days} | {detail} |" for name, days, detail in MONTHS)
    return ("| Block | Days | Covered |\n|---|---|---|\n" + rows)


def render_readme(paths):
    tmpl = open(os.path.join(HERE, "README.tmpl.md")).read()
    for key, path in paths.items():
        tmpl = tmpl.replace("{{%s}}" % key, path)
    open(os.path.join(ROOT, "README.md"), "w").write(tmpl)


if __name__ == "__main__":
    paths = {
        "recent": recent_section(),
        "curriculum": curriculum_section(),
        "pipeline": emit("pipeline", pipeline_panel()),
        "stack": emit("stack", stack_panel()),
        "quality": emit("quality", quality_panel()),
        "journey": emit("journey", journey_panel()),
        "activity": emit("activity", activity_panel()),
    }
    render_readme(paths)
    print("\n".join(f"{k:10} {v}" for k, v in paths.items() if v.endswith(".svg")))
