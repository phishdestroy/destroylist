#!/usr/bin/env python3
"""Update a GitHub Gist with current blocklist statistics.

Requires environment variables:
  GIST_TOKEN  — GitHub personal access token with gist scope
  GIST_ID     — ID of the target gist
"""
import json
import os
import sys
from pathlib import Path

import requests

from utils import PROJECT_ROOT, log

GIST_TOKEN = os.getenv("GIST_TOKEN", "")
GIST_ID = os.getenv("GIST_ID", "")

STATS_FILES = {
    "primary": PROJECT_ROOT / "count.json",
    "primary_dns": PROJECT_ROOT / "dns" / "active_count.json",
    "community": PROJECT_ROOT / "community" / "count.json",
    "community_dns": PROJECT_ROOT / "community" / "live_count.json",
    "primary_content": PROJECT_ROOT / "dns" / "content_active_count.json",
    "community_content": PROJECT_ROOT / "community" / "content_active_count.json",
}


def collect_stats() -> dict:
    stats = {}
    for name, path in STATS_FILES.items():
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            stats[name] = data.get("message", "0")
        except Exception:
            pass
    return stats


def main():
    if not GIST_TOKEN or not GIST_ID:
        log("GIST_TOKEN or GIST_ID not set, skipping gist update", "warn")
        return

    stats = collect_stats()
    if not stats:
        log("No stats to push", "warn")
        return

    content = json.dumps(stats, indent=2)

    resp = requests.patch(
        f"https://api.github.com/gists/{GIST_ID}",
        headers={
            "Authorization": f"token {GIST_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
        json={"files": {"destroylist_stats.json": {"content": content}}},
        timeout=15,
    )
    resp.raise_for_status()
    log(f"Gist updated: {len(stats)} stats", "ok")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"Gist update failed: {e}", "warn")
        sys.exit(0)  # non-fatal, matches continue-on-error in workflow
