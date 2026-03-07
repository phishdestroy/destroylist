#!/usr/bin/env python3
"""
Clean all domain lists against the allowlist.
Removes allowed domains, invalid entries, and handles path-based entries.
"""
import json
import sys
from pathlib import Path
from typing import List, Set, Tuple

from utils import (
    PROJECT_ROOT, IPV4_RE, INFRA_ROOTS,
    extract_domain, get_root, is_valid_entry, is_ip,
    load_json_list, load_allowlist_split, is_allowed, log,
)

ALLOWLIST_FILE = PROJECT_ROOT / "allow" / "allowlist.json"

TARGETS = [
    PROJECT_ROOT / "list.json",
    PROJECT_ROOT / "community" / "blocklist.json",
    PROJECT_ROOT / "community" / "live_blocklist.json",
    PROJECT_ROOT / "community" / "content_live.json",
    PROJECT_ROOT / "dns" / "active_domains.json",
    PROJECT_ROOT / "dns" / "content_active.json",
]


def filter_domains(domains: List[str], exact: Set[str], patterns: Set[str]) -> Tuple[List[str], int]:
    """Filter domains against the allowlist.

    Handles path-based entries and hosting platform subdomains correctly.
    """
    filtered = []
    removed = 0

    for entry in domains:
        # 1. Full entry exact/pattern match
        if is_allowed(entry, exact, patterns):
            removed += 1
            continue

        # 2. Domain part (without path)
        domain = extract_domain(entry)
        if domain != entry and is_allowed(domain, exact, patterns):
            root = get_root(domain)
            if root and root in INFRA_ROOTS:
                filtered.append(entry)
            else:
                removed += 1
            continue

        # 3. Root domain check
        root = get_root(domain)
        if root and root != domain and is_allowed(root, exact, patterns) and root not in INFRA_ROOTS:
            removed += 1
            continue

        filtered.append(entry)

    return filtered, removed


ANOMALY_THRESHOLD = 0.20  # warn if count drops more than 20%


def clean_file(filepath: Path, exact: Set[str], patterns: Set[str]) -> bool:
    if not filepath.exists():
        return False

    domains = load_json_list(filepath)
    if not domains:
        return False

    original_count = len(domains)

    # Remove invalid entries
    valid = []
    removed_invalid = 0
    removed_ips = 0
    for entry in domains:
        if is_ip(entry):
            removed_ips += 1
        elif not is_valid_entry(entry):
            removed_invalid += 1
        else:
            valid.append(entry)

    if removed_invalid > 0:
        log(f"Removed {removed_invalid} invalid entries from {filepath.name}")
    if removed_ips > 0:
        log(f"Removed {removed_ips} IP entries from {filepath.name}")

    # Filter allowlist
    filtered, removed_allow = filter_domains(valid, exact, patterns)

    # Deduplicate and sort
    unique = sorted(set(filtered))
    removed_dupes = len(filtered) - len(unique)

    total_removed = original_count - len(unique)
    name = filepath.relative_to(PROJECT_ROOT)

    # Always rewrite for consistent formatting
    expected = json.dumps(unique, indent=2, ensure_ascii=False)
    current = filepath.read_text(encoding="utf-8").rstrip("\n")
    needs_reformat = current != expected

    # Anomaly detection: warn if count dropped significantly
    if original_count > 0 and total_removed / original_count > ANOMALY_THRESHOLD:
        drop_pct = total_removed / original_count * 100
        log(f"ANOMALY {name}: count dropped {drop_pct:.1f}% "
            f"({original_count:,} -> {len(unique):,})", "warn")

    if total_removed == 0 and not needs_reformat:
        log(f"{name}: {original_count:,} domains — no changes", "ok")
        return False

    if total_removed > 0:
        log(f"{name}: {original_count:,} -> {len(unique):,} "
            f"(invalid: -{removed_invalid}, IPs: -{removed_ips}, "
            f"allowlist: -{removed_allow}, dupes: -{removed_dupes})")
    elif needs_reformat:
        log(f"{name}: {original_count:,} domains — reformatted")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)

    return True


def main():
    log("Validate & Clean", "step")

    exact, patterns = load_allowlist_split()
    if not exact and not patterns:
        log("Allowlist is empty or missing", "warn")
        return 0

    log(f"Allowlist: {len(exact)} exact + {len(patterns)} patterns")

    changed = sum(clean_file(target, exact, patterns) for target in TARGETS) > 0

    if changed:
        log("Files updated", "ok")
    else:
        log("No changes needed", "ok")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        log(f"FATAL: {e}", "error")
        import traceback
        traceback.print_exc()
        sys.exit(1)
