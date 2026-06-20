#!/usr/bin/env python3
"""Calculate domain addition statistics using git history."""
import json
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Set, Optional

from utils import PROJECT_ROOT, make_badge, save_json, log

DNS_DIR = PROJECT_ROOT / "dns"
ARCHIVES_DIR = PROJECT_ROOT / "archives"
SNAPSHOT_FILE = DNS_DIR / "stats_snapshot.json"

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
    """Return count of domains added since since_date using git history.

    Returns 0 (not the full count) when history is unavailable,
    so callers get a conservative/safe result instead of a misleading spike.
    """
    current = load_current_domains(file_path)
    if not current:
        return 0

    commits = run_git(["git", "log", f"--since={since_date}", "--reverse", "--format=%H", "--", file_path]).strip().split("\n")
    if not commits or not commits[0]:
        return 0

    parent = run_git(["git", "rev-parse", f"{commits[0]}^"]).strip()
    if not parent:
        log(f"No parent commit accessible for {file_path} since {since_date} — returning 0", "warn")
        return 0

    old_content = run_git(["git", "show", f"{parent}:{file_path}"])
    if not old_content:
        log(f"Could not read parent content for {file_path} — returning 0", "warn")
        return 0

    return len(current - get_domains_from_json(old_content))


# ── Snapshot-based baseline (fallback when git history is shallow) ────────────

def load_snapshot() -> dict:
    if SNAPSHOT_FILE.exists():
        try:
            return json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_snapshot(now: datetime, primary_count: int, community_count: int):
    """Update the rolling snapshot file with today/week/month baselines."""
    snap = load_snapshot()
    today_str = now.strftime("%Y-%m-%d")
    week_str = now.strftime("%G-W%V")
    month_str = now.strftime("%Y-%m")

    if snap.get("today_date") != today_str:
        snap["today_date"] = today_str
        snap["today_primary"] = primary_count
        snap["today_community"] = community_count

    if snap.get("week_id") != week_str:
        snap["week_id"] = week_str
        snap["week_primary"] = primary_count
        snap["week_community"] = community_count

    if snap.get("month_id") != month_str:
        snap["month_id"] = month_str
        snap["month_primary"] = primary_count
        snap["month_community"] = community_count

    save_json(SNAPSHOT_FILE, snap)


def get_delta_from_snapshot(key_primary: str, key_community: str, current_primary: int, current_community: int):
    """Compute delta against stored snapshot baseline; returns (primary_delta, community_delta)."""
    snap = load_snapshot()
    p = max(0, current_primary - snap.get(key_primary, current_primary))
    c = max(0, current_community - snap.get(key_community, current_community))
    return p, c


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

    now = datetime.now(timezone.utc)
    current_primary = len(load_current_domains(LIST_FILE))
    current_community = len(load_current_domains(COMMUNITY_FILE))

    # Try git-history based calculation first
    today_p = get_domains_added_since(LIST_FILE, "1 day ago")
    week_p = get_domains_added_since(LIST_FILE, "1 week ago")
    month_p = get_domains_added_since(LIST_FILE, "1 month ago")
    today_c = get_domains_added_since(COMMUNITY_FILE, "1 day ago")
    week_c = get_domains_added_since(COMMUNITY_FILE, "1 week ago")
    month_c = get_domains_added_since(COMMUNITY_FILE, "1 month ago")

    # Sanity check: if a value equals the full list size the git fallback fired;
    # use the snapshot baseline instead.
    if week_p >= current_primary or month_p >= current_primary:
        log("Git history gave inflated values — falling back to snapshot baseline", "warn")
        snap_today_p, snap_today_c = get_delta_from_snapshot("today_primary", "today_community", current_primary, current_community)
        snap_week_p, snap_week_c = get_delta_from_snapshot("week_primary", "week_community", current_primary, current_community)
        snap_month_p, snap_month_c = get_delta_from_snapshot("month_primary", "month_community", current_primary, current_community)
        today_p, today_c = snap_today_p, snap_today_c
        week_p, week_c = snap_week_p, snap_week_c
        month_p, month_c = snap_month_p, snap_month_c

    stats = {
        "today_added": today_p,
        "week_added": week_p,
        "month_added": month_p,
        "today_community": today_c,
        "week_community": week_c,
        "month_community": month_c,
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

    # Save/refresh snapshot baseline after writing badges
    save_snapshot(now, current_primary, current_community)

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
