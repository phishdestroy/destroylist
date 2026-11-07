#!/usr/bin/env python3
"""Calculate domain addition statistics using git history."""
import json
import argparse
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Set, Optional

from utils import PROJECT_ROOT, make_badge, save_json, log

DNS_DIR = PROJECT_ROOT / "dns"
ARCHIVES_DIR = PROJECT_ROOT / "archives"
SNAPSHOT_FILE = DNS_DIR / "stats_snapshot.json"

# Above this many added+removed entries a daily diff file would exceed
# GitHub's 350 KiB code-search indexing limit; fall back to counts only.
MAX_DIFF_ENTRIES = 12_000

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


def plausible_baseline(old: Set[str], current: Set[str]) -> bool:
    """Guard against false baselines left behind by history slimming.

    Stripped blobs can make `git show` resolve to an ancient surviving
    version of the file; a real baseline within any stats window is never
    less than half the current list size.
    """
    return bool(old) and len(old) >= len(current) * 0.5


def get_domains_added_since(file_path: str, since_date: str) -> Optional[int]:
    """Return count of domains added since since_date using git history.

    None means history is unavailable; zero is a valid measured result.
    """
    current = load_current_domains(file_path)
    if not current:
        return None

    commits = run_git(["git", "log", f"--since={since_date}", "--reverse", "--format=%H", "--", file_path]).strip().split("\n")
    if not commits or not commits[0]:
        return 0

    parent = run_git(["git", "rev-parse", f"{commits[0]}^"]).strip()
    if not parent:
        log(f"No parent commit accessible for {file_path} since {since_date}", "warn")
        return None

    old_content = run_git(["git", "show", f"{parent}:{file_path}"])
    if not old_content:
        log(f"Could not read parent content for {file_path}", "warn")
        return None

    old = get_domains_from_json(old_content)
    if not plausible_baseline(old, current):
        log(f"Baseline for {file_path} since {since_date} looks stripped/ancient "
            f"({len(old):,} vs {len(current):,} current)", "warn")
        return None

    return len(current - old)


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


def get_delta_from_snapshot(key_primary: str, key_community: str, current_primary: int, current_community: int,
                            period_key: str, period_value: str):
    """Compute delta against stored snapshot baseline; returns (primary_delta, community_delta)."""
    snap = load_snapshot()
    if snap.get(period_key) != period_value:
        return None, None
    p = max(0, current_primary - snap.get(key_primary, current_primary))
    c = max(0, current_community - snap.get(key_community, current_community))
    return p, c


def domains_before(file_path: str, boundary: datetime) -> Optional[Set[str]]:
    """Read the last first-parent snapshot strictly before a UTC boundary."""
    cutoff = (boundary.astimezone(timezone.utc) - timedelta(seconds=1)).isoformat()
    commit = run_git(["git", "rev-list", "--first-parent", "-1", f"--before={cutoff}", "HEAD"]).strip()
    if not commit:
        return None
    content = run_git(["git", "show", f"{commit}:{file_path}"])
    return get_domains_from_json(content) if content else None


def save_daily_diff(now: datetime):
    """Refresh today's UTC diff and finalize yesterday at its own midnight.

    An early-morning snapshot is provisional. Later additions must be included,
    while today's additions must never be attributed to yesterday. Older days
    are left alone; unavailable history never replaces a known archive.
    """
    now = now.astimezone(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    current = {
        LIST_FILE: load_current_domains(LIST_FILE),
        COMMUNITY_FILE: load_current_domains(COMMUNITY_FILE),
    }
    snapshots = {}

    def at(path, boundary):
        key = (path, boundary)
        if key not in snapshots:
            snapshots[key] = domains_before(path, boundary)
        return snapshots[key]

    for start in (today - timedelta(days=1), today):
        try:
            finished = start < today
            end = start + timedelta(days=1) if finished else now
            out_file = (PROJECT_ROOT / "archives" / "changes" /
                        start.strftime("%Y-%m") / f"{start:%Y-%m-%d}.json")
            diff = {
                "date": start.strftime("%Y-%m-%d"),
                "period_start": start.isoformat(),
                "period_end": end.isoformat(),
                "complete": finished,
            }
            entries = 0
            for label, path in (("primary", LIST_FILE), ("community", COMMUNITY_FILE)):
                old = at(path, start)
                final = at(path, end) if finished else current[path]
                if not final or old is None or not plausible_baseline(old, final):
                    raise ValueError(f"no usable {label} baseline for {start:%Y-%m-%d}")
                added, removed = sorted(final - old), sorted(old - final)
                diff[label + "_added"] = added
                diff[label + "_removed"] = removed
                diff[label + "_count"] = len(final)
                entries += len(added) + len(removed)

            if entries > MAX_DIFF_ENTRIES:
                for key in [k for k in diff if k.endswith("_added") or k.endswith("_removed")]:
                    diff[key + "_count"] = len(diff.pop(key))
                diff["note"] = f"{entries:,} changes exceed search-indexable size; counts only"

            out_file.parent.mkdir(parents=True, exist_ok=True)
            content = json.dumps(diff, indent=1)
            if not out_file.exists() or out_file.read_text(encoding="utf-8") != content:
                out_file.write_text(content, encoding="utf-8")
            added_count = len(diff["primary_added"]) if "primary_added" in diff else diff["primary_added_count"]
            log(f"Daily diff: {out_file.name} (+{added_count} primary, complete={finished})", "ok")
        except Exception as e:
            log(f"Daily diff {start:%Y-%m-%d} retained: {e}", "warn")


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


def calendar_windows(now: datetime) -> dict:
    """Badge labels refer to UTC calendar periods, not rolling 24h/7d/30d."""
    today = now.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return {
        "today": today.isoformat(),
        "week": (today - timedelta(days=today.weekday())).isoformat(),
        "month": today.replace(day=1).isoformat(),
    }


def pick_count(git_value: Optional[int], snapshot_value: Optional[int]) -> Optional[int]:
    return git_value if git_value is not None else snapshot_value


def format_count(value: Optional[int]) -> str:
    return "unavailable" if value is None else f"+{value:,}"


def main(counters_only: bool = False, live: bool = False):
    log("Calculate statistics", "step")
    DNS_DIR.mkdir(exist_ok=True)

    now = datetime.now(timezone.utc)
    current_primary = len(load_current_domains(LIST_FILE))
    current_community = len(load_current_domains(COMMUNITY_FILE))

    # Try git-history based calculation first
    windows = calendar_windows(now)
    today_p = get_domains_added_since(LIST_FILE, windows["today"])
    week_p = get_domains_added_since(LIST_FILE, windows["week"])
    month_p = get_domains_added_since(LIST_FILE, windows["month"])
    today_c = get_domains_added_since(COMMUNITY_FILE, windows["today"])
    week_c = get_domains_added_since(COMMUNITY_FILE, windows["week"])
    month_c = get_domains_added_since(COMMUNITY_FILE, windows["month"])

    # A real zero must not revive yesterday's snapshot delta. A stale snapshot
    # cannot describe the current calendar period when Git history is absent.
    snap_today_p, snap_today_c = get_delta_from_snapshot("today_primary", "today_community", current_primary, current_community, "today_date", now.strftime("%Y-%m-%d"))
    snap_week_p, snap_week_c = get_delta_from_snapshot("week_primary", "week_community", current_primary, current_community, "week_id", now.strftime("%G-W%V"))
    snap_month_p, snap_month_c = get_delta_from_snapshot("month_primary", "month_community", current_primary, current_community, "month_id", now.strftime("%Y-%m"))

    today_p = pick_count(today_p, snap_today_p)
    week_p = pick_count(week_p, snap_week_p)
    month_p = pick_count(month_p, snap_month_p)
    today_c = pick_count(today_c, snap_today_c)
    week_c = pick_count(week_c, snap_week_c)
    month_c = pick_count(month_c, snap_month_c)

    stats = {
        "today_added": today_p,
        "week_added": week_p,
        "month_added": month_p,
        "today_community": today_c,
        "week_community": week_c,
        "month_community": month_c,
    }

    log(f"Primary  — today: {format_count(today_p)}, week: {format_count(week_p)}, month: {format_count(month_p)}")
    log(f"Community — today: {format_count(today_c)}, week: {format_count(week_c)}, month: {format_count(month_c)}")

    badges = {
        "today_added": make_badge("added today", format_count(today_p), "success"),
        "week_added": make_badge("added this week", format_count(week_p), "success"),
        "month_added": make_badge("added this month", format_count(month_p), "success"),
        "today_community": make_badge("community today", format_count(today_c), "blue"),
        "week_community": make_badge("community this week", format_count(week_c), "blue"),
        "month_community": make_badge("community this month", format_count(month_c), "blue"),
    }

    for key, data in badges.items():
        data["cacheSeconds"] = 300
        save_json(OUTPUT_FILES[key], data)

    # Save/refresh snapshot baseline after writing badges
    save_snapshot(now, current_primary, current_community)

    if not counters_only:
        save_daily_diff(now)
        if not live:
            save_archive()
    log("Done", "ok")


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument("--counters-only", action="store_true",
                            help="Refresh badges without writing historical archives")
        mode.add_argument("--live", action="store_true",
                          help="Refresh badges and current/recent daily diffs without full snapshots")
        args = parser.parse_args()
        main(counters_only=args.counters_only, live=args.live)
    except Exception as e:
        log(f"FATAL: {e}", "error")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)

