#!/usr/bin/env python3
"""
Clean all domain lists against the allowlist.
Removes allowed domains from: list.json, community/blocklist.json, community/live_blocklist.json
"""
import json
import sys
from pathlib import Path
from typing import List, Set, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

ALLOWLIST_FILE = PROJECT_ROOT / "allow" / "allowlist.json"

TARGETS = [
    PROJECT_ROOT / "list.json",
    PROJECT_ROOT / "community" / "blocklist.json",
    PROJECT_ROOT / "community" / "live_blocklist.json",
]


def load_json_list(filepath: Path) -> List[str]:
    if not filepath.exists():
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"FATAL: {filepath.name} — invalid JSON at line {e.lineno}: {e.msg}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        print(f"FATAL: {filepath.name} — expected array, got {type(data).__name__}", file=sys.stderr)
        sys.exit(1)

    return [str(d).strip().lower() for d in data if d and str(d).strip()]


def load_allowlist() -> Tuple[Set[str], Set[str]]:
    entries = load_json_list(ALLOWLIST_FILE)
    if not entries:
        print("Allowlist is empty or missing")
        return set(), set()

    patterns = {d for d in entries if d.startswith(".")}
    exact = set(entries) - patterns
    print(f"Allowlist: {len(exact)} exact + {len(patterns)} patterns = {len(entries)} total")
    return exact, patterns


def filter_domains(domains: List[str], exact: Set[str], patterns: Set[str]) -> Tuple[List[str], int]:
    filtered = []
    removed = 0

    for domain in domains:
        if domain in exact:
            removed += 1
            continue

        matched = False
        for p in patterns:
            if domain.endswith(p) or domain == p[1:]:
                matched = True
                break

        if matched:
            removed += 1
            continue

        filtered.append(domain)

    return filtered, removed


def clean_file(filepath: Path, exact: Set[str], patterns: Set[str]) -> bool:
    if not filepath.exists():
        return False

    domains = load_json_list(filepath)
    if not domains:
        return False

    original_count = len(domains)

    # Filter allowlist
    filtered, removed_allow = filter_domains(domains, exact, patterns)

    # Deduplicate
    unique = sorted(set(filtered))
    removed_dupes = len(filtered) - len(unique)

    total_removed = original_count - len(unique)
    name = filepath.relative_to(PROJECT_ROOT)

    if total_removed == 0:
        print(f"  {name}: {original_count} domains — no changes")
        return False

    print(f"  {name}: {original_count} → {len(unique)} (allowlist: -{removed_allow}, dupes: -{removed_dupes})")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)

    return True


def main():
    print("=== Validate & Clean ===")

    exact, patterns = load_allowlist()
    if not exact and not patterns:
        print("Nothing to filter")
        return 0

    changed = False
    for target in TARGETS:
        if clean_file(target, exact, patterns):
            changed = True

    if changed:
        print("\n✅ Files updated")
    else:
        print("\n✅ No changes needed")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"FATAL: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
