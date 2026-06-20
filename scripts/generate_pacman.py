#!/usr/bin/env python3
"""Generate a Pac-Man contribution graph SVG using GitHub GraphQL API."""
import json
import math
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

TOKEN = os.environ.get("GITHUB_TOKEN", "")
USER = os.environ.get("GITHUB_USER", "phishdestroy")
OUT_DIR = Path(os.environ.get("OUTPUT_DIR", "dist"))

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

# Layout
CELL = 11
GAP = 3
STEP = CELL + GAP
MARGIN_LEFT = 20
MARGIN_TOP = 30
MARGIN_BOTTOM = 20
LABEL_H = 18

COLORS_LIGHT = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
COLORS_DARK  = ["#161b22", "#0d4429", "#006d32", "#26a641", "#39d353"]
PAC_COLOR = "#FFD700"
BG_LIGHT = "#ffffff"
BG_DARK  = "#0d1117"


def fetch_contributions():
    if not TOKEN:
        print("GITHUB_TOKEN not set — using dummy data", file=sys.stderr)
        return _dummy_weeks()

    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "pacman-generator",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
    except urllib.error.URLError as e:
        print(f"API error: {e}", file=sys.stderr)
        return _dummy_weeks()

    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [[d["contributionCount"] for d in w["contributionDays"]] for w in weeks]


def _dummy_weeks():
    import random
    random.seed(42)
    weeks = []
    for _ in range(52):
        week = [random.choices([0,0,0,1,2,3,4], k=7)[i] for i in range(7)]
        weeks.append(week)
    return weeks


def count_to_level(c):
    if c == 0: return 0
    if c <= 2: return 1
    if c <= 5: return 2
    if c <= 9: return 3
    return 4


def build_svg(weeks, dark=False):
    colors = COLORS_DARK if dark else COLORS_LIGHT
    bg = BG_DARK if dark else BG_LIGHT
    text_color = "#8b949e" if dark else "#57606a"

    n_weeks = len(weeks)
    n_days = max(len(w) for w in weeks)

    w = MARGIN_LEFT + n_weeks * STEP + 20
    h = MARGIN_TOP + LABEL_H + n_days * STEP + MARGIN_BOTTOM

    # Build a flat list of all dots: (svg_x, svg_y, level, col, row)
    dots = []
    for col, week in enumerate(weeks):
        for row, count in enumerate(week):
            x = MARGIN_LEFT + col * STEP
            y = MARGIN_TOP + LABEL_H + row * STEP
            dots.append((x, y, count_to_level(count), col, row))

    # Pac-Man path: snake through rows left-to-right, right-to-left alternating
    path_points = []  # (x_center, y_center) in order Pac-Man travels
    for row in range(n_days):
        row_dots = sorted([d for d in dots if d[3+1] == row], key=lambda d: d[0])
        if row % 2 == 0:
            pass  # left to right
        else:
            row_dots = list(reversed(row_dots))
        for d in row_dots:
            path_points.append((d[0] + CELL//2, d[1] + CELL//2))
        # Turn between rows: add midpoint
        if row < n_days - 1:
            if row_dots:
                last = row_dots[-1]
                turn_x = last[0] + CELL//2
                next_y = MARGIN_TOP + LABEL_H + (row+1) * STEP + CELL//2
                path_points.append((turn_x, next_y))

    total_pts = len(path_points)
    dur = max(10, total_pts * 0.06)  # seconds for full traversal

    # Build SVG path string for animateMotion
    if path_points:
        path_d = "M " + " L ".join(f"{x},{y}" for x, y in path_points)
    else:
        path_d = "M 0,0"

    # Dot rectangles with fade animation
    dot_rects = []
    for idx, (x, y, level, col, row) in enumerate(dots):
        color = colors[level]
        # Each dot fades when Pac-Man reaches it
        # Find when this dot appears in path traversal (approximate)
        begin_offset = (idx / max(1, len(dots))) * dur

        dot_rects.append(
            f'  <rect id="d{idx}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
            f'rx="2" ry="2" fill="{color}">'
            f'<animate attributeName="opacity" values="1;1;0;0" '
            f'keyTimes="0;{begin_offset/dur:.3f};{min(begin_offset/dur+0.02, 1):.3f};1" '
            f'dur="{dur:.1f}s" repeatCount="indefinite"/>'
            f'</rect>'
        )

    # Month labels
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    month_labels = []
    prev_month = -1
    for col, week in enumerate(weeks):
        if not week:
            continue
        # Get first day of week to determine month — approximate
        pass  # skip for simplicity, just use position

    # Day labels
    day_labels = []
    day_names = ["","Mon","","Wed","","Fri",""]
    for i, name in enumerate(day_names):
        if name:
            y = MARGIN_TOP + LABEL_H + i * STEP + CELL - 1
            day_labels.append(
                f'  <text x="{MARGIN_LEFT - 5}" y="{y}" '
                f'font-size="9" fill="{text_color}" text-anchor="end" '
                f'font-family="monospace">{name}</text>'
            )

    # Pac-Man character (circle with animated mouth wedge clipped)
    # Mouth: open angle oscillates 0..45 degrees
    pac_size = CELL + 2
    pac_r = pac_size // 2

    pac_svg = f"""
  <g id="pacman">
    <animateMotion dur="{dur:.1f}s" repeatCount="indefinite" rotate="auto">
      <mpath href="#pacpath"/>
    </animateMotion>
    <!-- Body -->
    <circle cx="0" cy="0" r="{pac_r}" fill="{PAC_COLOR}"/>
    <!-- Mouth wedge (black triangle) -->
    <path fill="{bg}" opacity="0.95">
      <animate attributeName="d"
        values="M0,0 L{pac_r},0 A{pac_r},{pac_r} 0 0,0 {pac_r},0 Z;
                M0,0 L{pac_r},-{int(pac_r*0.7)} A{pac_r},{pac_r} 0 0,0 {pac_r},{int(pac_r*0.7)} Z;
                M0,0 L{pac_r},0 A{pac_r},{pac_r} 0 0,0 {pac_r},0 Z"
        keyTimes="0;0.5;1"
        dur="0.3s" repeatCount="indefinite"/>
    </path>
    <!-- Eye -->
    <circle cx="{max(2, pac_r//3)}" cy="{-max(2, pac_r//3)}" r="1.5" fill="{bg}"/>
  </g>"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <rect width="{w}" height="{h}" rx="6" fill="{bg}"/>

  <!-- Dot grid -->
{''.join(dot_rects)}

  <!-- Day labels -->
{''.join(day_labels)}

  <!-- Pac-Man motion path (invisible) -->
  <path id="pacpath" d="{path_d}" fill="none" stroke="none"/>

  <!-- Pac-Man -->
{pac_svg}
</svg>"""

    return svg


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Fetching contributions for @{USER}...", file=sys.stderr)
    weeks = fetch_contributions()
    print(f"Got {len(weeks)} weeks", file=sys.stderr)

    light_svg = build_svg(weeks, dark=False)
    dark_svg  = build_svg(weeks, dark=True)

    out_light = OUT_DIR / "github-snake.svg"
    out_dark  = OUT_DIR / "github-snake-dark.svg"

    out_light.write_text(light_svg, encoding="utf-8")
    out_dark.write_text(dark_svg, encoding="utf-8")

    print(f"Written: {out_light}", file=sys.stderr)
    print(f"Written: {out_dark}", file=sys.stderr)


if __name__ == "__main__":
    main()
