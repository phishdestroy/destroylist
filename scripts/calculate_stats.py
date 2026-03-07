#!/usr/bin/env python3
"""Calculate domain addition statistics using git history."""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Set

from utils import PROJECT_ROOT, make_badge, save_json, log

DNS_DIR = PROJECT_ROOT / "dns"
ARCHIVES_DIR = PROJECT_ROOT / "archives"

LIST_FILE = "list.json"
COMMUNITY_FILE = "community/blocklist.json"

OUTPUT_FILES = {
    "today_added": DNS_DIR / "today_added.json",
    "week_added": DNS_DIR / "week_added.json",
    "month_added": DNS_DIR / "month_added.json",
    "today_community": DNS_DIR / "today_community.json",
    "week_community": DNS_DIR / "week_community.json",
    "month_community": DNS_DIR / "month_community.json",
}


def run_git(cmd: list) -> str:
    try:
        result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return ""


def get_domains_from_json(content: str) -> Set[str]:
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return {d.lower().strip() for d in data if isinstance(d, str)}
        elif isinstance(data, dict) and "domains" in data:
            return {d.lower().strip() for d in data["domains"] if isinstance(d, str)}
    except Exception as e:
        log(f"Failed to parse JSON content: {e}", "warn")
    return set()


def load_current_domains(file_path: str) -> Set[str]:
    try:
        return get_domains_from_json((PROJECT_ROOT / file_path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return set()


def get_domains_added_since(file_path: str, since_date: str) -> int:
    current = load_current_domains(file_path)
    if not current:
        return 0

    commits = run_git(["git", "log", f"--since={since_date}", "--reverse", "--format=%H", "--", file_path]).strip().split("\n")
    if not commits or not commits[0]:
        return 0

    parent = run_git(["git", "rev-parse", f"{commits[0]}^"]).strip()
    if not parent:
        return len(current)

    old_content = run_git(["git", "show", f"{parent}:{file_path}"])
    if not old_content:
        return len(current)

    return len(current - get_domains_from_json(old_content))


def save_archive():
    now = datetime.now(timezone.utc)

    primary = load_current_domains(LIST_FILE)
    community = load_current_domains(COMMUNITY_FILE)

    archive_data = {
        "date": now.strftime("%Y-%m-%d"),
        "primary_count": len(primary),
        "community_count": len(community),
        "primary_domains": sorted(primary),
        "community_domains": sorted(community),
    }

    if now.weekday() == 0:
        weekly_dir = ARCHIVES_DIR / "weekly"
        weekly_dir.mkdir(parents=True, exist_ok=True)
        week_file = weekly_dir / f"{now.strftime('%G-W%V')}.json"
        week_file.write_text(json.dumps(archive_data, indent=2), encoding="utf-8")
        log(f"Weekly archive: {week_file.name}", "ok")

    if now.day == 1:
        monthly_dir = ARCHIVES_DIR / "monthly"
        monthly_dir.mkdir(parents=True, exist_ok=True)
        month_file = monthly_dir / f"{now.strftime('%Y-%m')}.json"
        month_file.write_text(json.dumps(archive_data, indent=2), encoding="utf-8")
        log(f"Monthly archive: {month_file.name}", "ok")


def main():
    log("Calculate statistics", "step")
    DNS_DIR.mkdir(exist_ok=True)

    stats = {
        "today_added": get_domains_added_since(LIST_FILE, "1 day ago"),
        "week_added": get_domains_added_since(LIST_FILE, "1 week ago"),
        "month_added": get_domains_added_since(LIST_FILE, "1 month ago"),
        "today_community": get_domains_added_since(COMMUNITY_FILE, "1 day ago"),
        "week_community": get_domains_added_since(COMMUNITY_FILE, "1 week ago"),
        "month_community": get_domains_added_since(COMMUNITY_FILE, "1 month ago"),
    }

    log(f"Primary  — today: +{stats['today_added']:,}, week: +{stats['week_added']:,}, month: +{stats['month_added']:,}")
    log(f"Community — today: +{stats['today_community']:,}, week: +{stats['week_community']:,}, month: +{stats['month_community']:,}")

    badges = {
        "today_added": make_badge("added today", f"+{stats['today_added']:,}", "success"),
        "week_added": make_badge("added this week", f"+{stats['week_added']:,}", "success"),
        "month_added": make_badge("added this month", f"+{stats['month_added']:,}", "success"),
        "today_community": make_badge("community today", f"+{stats['today_community']:,}", "blue"),
        "week_community": make_badge("community this week", f"+{stats['week_community']:,}", "blue"),
        "month_community": make_badge("community this month", f"+{stats['month_community']:,}", "blue"),
    }

    for key, data in badges.items():
        save_json(OUTPUT_FILES[key], data)

    save_archive()
    log("Done", "ok")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"FATAL: {e}", "error")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)
