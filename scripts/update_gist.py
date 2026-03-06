#!/usr/bin/env python3
"""Update a GitHub Gist with current blocklist statistics."""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_badge(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main():
    token = os.environ.get("GIST_TOKEN", "").strip()
    gist_id = os.environ.get("GIST_ID", "").strip()

    if not token:
        print("GIST_TOKEN not set, skipping gist update")
        return

    if not gist_id:
        print("GIST_ID not set, skipping gist update")
        return

    badge_files = {
        "primary": PROJECT_ROOT / "count.json",
        "primary_dns": PROJECT_ROOT / "dns" / "active_count.json",
        "community": PROJECT_ROOT / "community" / "count.json",
        "community_dns": PROJECT_ROOT / "community" / "live_count.json",
        "today_added": PROJECT_ROOT / "dns" / "today_added.json",
        "week_added": PROJECT_ROOT / "dns" / "week_added.json",
        "month_added": PROJECT_ROOT / "dns" / "month_added.json",
    }

    stats = {}
    for name, path in badge_files.items():
        badge = load_badge(path)
        stats[name] = badge.get("message", "0")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    content = (
        f"# Destroylist Statistics\n"
        f"Updated: {now}\n\n"
        f"| Metric | Count |\n"
        f"|--------|-------|\n"
        f"| Primary Domains | {stats.get('primary', '0')} |\n"
        f"| Primary Active (DNS) | {stats.get('primary_dns', '0')} |\n"
        f"| Community Domains | {stats.get('community', '0')} |\n"
        f"| Community Active (DNS) | {stats.get('community_dns', '0')} |\n"
        f"| Added Today | {stats.get('today_added', '0')} |\n"
        f"| Added This Week | {stats.get('week_added', '0')} |\n"
        f"| Added This Month | {stats.get('month_added', '0')} |\n"
    )

    payload = json.dumps({
        "files": {
            "destroylist-stats.md": {"content": content}
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        f"https://api.github.com/gists/{gist_id}",
        method="PATCH",
        data=payload,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            print(f"Gist updated: {result.get('html_url', gist_id)}")
    except Exception as e:
        print(f"Warning: could not update gist: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
