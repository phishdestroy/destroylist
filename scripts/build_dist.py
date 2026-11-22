#!/usr/bin/env python3
"""Assemble the dist branch: feeds, meta.json and hotlist.json."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DIST_GLOBS = (
    "list.json",
    "list.txt",
    "count.json",
    "allow/allowlist.json",
    "community/blocklist.json",
    "community/blocklist.txt",
    "community/live_blocklist.json",
    "community/live_blocklist.txt",
    "community/content_live.json",
    "community/content_live.txt",
    "community/count.json",
    "community/live_count.json",
    "community/content_active_count.json",
    "dns/active_domains.json",
    "dns/active_domains.txt",
    "dns/content_active.json",
    "dns/content_active.txt",
    "dns/active_count.json",
    "dns/content_active_count.json",
    "dns/metrics.json",
    "rootlist/*.json",
    "rootlist/*.txt",
    "rootlist/formats/*/*",
    "rootlist/arrays/*.json",
)

LISTS = {
    "primary": "list.json",
    "primary_active": "dns/active_domains.json",
    "community": "community/blocklist.json",
    "community_live": "community/live_blocklist.json",
}
JOURNAL_LISTS = {"primary": "list.json", "community": "community/blocklist.json"}

GITHUB_FILE_LIMIT = 100 * 1024 * 1024
GITHUB_FILE_WARN = 50 * 1024 * 1024

DIST_README = """# Destroylist feeds (dist)

Current version of every Destroylist feed, rebuilt from `main` after each list update.
This branch is replaced on every build and has no history.

- Feeds: `https://raw.githubusercontent.com/phishdestroy/destroylist/dist/<path>`
- `meta.json`: source commit on `main`, list sizes, size and sha256 of every file
- `hotlist.json`: domains added or removed during the last two UTC days
- History, sources and the daily change journal: [`main`](https://github.com/phishdestroy/destroylist/tree/main)
"""


def collect(root: Path) -> list[Path]:
    found: set[Path] = set()
    for pattern in DIST_GLOBS:
        for path in root.glob(pattern):
            if path.is_file():
                found.add(path.relative_to(root))
    return sorted(found, key=lambda p: p.as_posix())


def load_list(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(f"{path} is not a JSON array")
    return data


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def build_hotlist(root: Path, now: datetime, current: dict[str, set[str]]) -> dict:
    days = [(now - timedelta(days=offset)).date() for offset in (1, 0)]
    journals = []
    for day in days:
        path = root / "archives" / "changes" / f"{day:%Y-%m}" / f"{day:%Y-%m-%d}.json"
        if path.is_file():
            with path.open(encoding="utf-8") as fh:
                journals.append(json.load(fh))

    hotlist: dict = {
        "generated_at": now.isoformat(timespec="seconds"),
        "window_start": f"{days[0]:%Y-%m-%d}T00:00:00+00:00",
        "journal_days": [j.get("date") for j in journals],
    }
    for name, source in JOURNAL_LISTS.items():
        added: set[str] = set()
        removed: set[str] = set()
        for journal in journals:
            added.update(journal.get(f"{name}_added", []))
            removed.update(journal.get(f"{name}_removed", []))
        listed = current[source]
        hotlist[name] = {
            "added": sorted(d for d in added if d in listed),
            "removed": sorted(d for d in added | removed if d not in listed),
        }
    return hotlist


def build(out: Path, source_commit: str, now: datetime, root: Path = PROJECT_ROOT) -> dict:
    files = collect(root)
    if not files:
        raise SystemExit("no feed files found: run the generators first")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    too_big, warnings, manifest = [], [], {}
    for rel in files:
        src = root / rel
        size = src.stat().st_size
        if size > GITHUB_FILE_LIMIT:
            too_big.append(f"{rel.as_posix()} ({size / 1048576:.1f} MB)")
            continue
        if size > GITHUB_FILE_WARN:
            warnings.append(f"{rel.as_posix()} ({size / 1048576:.1f} MB)")
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        manifest[rel.as_posix()] = {"size": size, "sha256": sha256_of(dst)}
    if too_big:
        raise SystemExit("files over GitHub's 100 MB limit: " + ", ".join(too_big))

    current = {source: set(load_list(root / source)) for source in set(LISTS.values()) if (root / source).is_file()}
    counts = {name: len(current[source]) for name, source in LISTS.items() if source in current}

    hotlist = build_hotlist(root, now, current)
    (out / "hotlist.json").write_text(json.dumps(hotlist, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    meta = {
        "schema": 1,
        "source_commit": source_commit,
        "built_at": now.isoformat(timespec="seconds"),
        "counts": counts,
        "files": manifest,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "README.md").write_text(DIST_README, encoding="utf-8")

    for warning in warnings:
        print(f"::warning::{warning} is over 50 MB and approaches GitHub's 100 MB file limit")
    total = sum(item["size"] for item in manifest.values())
    print(
        f"dist: {len(manifest)} feeds, {total / 1048576:.0f} MB, "
        f"hotlist +{len(hotlist['primary']['added'])}/-{len(hotlist['primary']['removed'])} primary, "
        f"+{len(hotlist['community']['added'])}/-{len(hotlist['community']['removed'])} community"
    )
    return meta


def parse_now(value: str | None) -> datetime:
    now = datetime.fromisoformat(value) if value else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assemble the dist branch")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--source-commit", default="unknown")
    parser.add_argument("--now")
    args = parser.parse_args(argv)
    build(args.out, args.source_commit, parse_now(args.now))
    return 0


if __name__ == "__main__":
    sys.exit(main())
