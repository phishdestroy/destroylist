#!/usr/bin/env python3
"""Validate all critical JSON files before any pipeline step."""
import json
import sys
from pathlib import Path

from utils import PROJECT_ROOT, IPV4_RE, log

FILES_TO_CHECK = [
    PROJECT_ROOT / "list.json",
    PROJECT_ROOT / "allow" / "allowlist.json",
    PROJECT_ROOT / "community" / "blocklist.json",
    PROJECT_ROOT / "community" / "live_blocklist.json",
    PROJECT_ROOT / "dns" / "active_domains.json",
]


def validate_file(filepath: Path) -> bool:
    rel = filepath.relative_to(PROJECT_ROOT)

    if not filepath.exists():
        log(f"{rel} (not found, skipped)", "warn")
        return True

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        log(f"{rel} — invalid JSON at line {e.lineno}: {e.msg}", "error")
        return False

    if not isinstance(data, list):
        log(f"{rel} — expected array, got {type(data).__name__}", "error")
        return False

    bad = [i for i, d in enumerate(data) if not isinstance(d, str) or not d.strip()]
    if bad:
        log(f"{rel} — {len(bad)} empty/non-string entries (indices: {bad[:5]}...)", "warn")

    str_entries = [d for d in data if isinstance(d, str) and d.strip()]
    dupes = len(str_entries) - len(set(d.lower().strip() for d in str_entries))
    if dupes > 0:
        log(f"{rel} — {dupes} duplicate entries", "warn")

    no_dots = [d for d in str_entries if "." not in d.split("/")[0]]
    if no_dots:
        log(f"{rel} — {len(no_dots)} entries without dots: {no_dots[:5]}...", "warn")

    ips = [d for d in str_entries if IPV4_RE.fullmatch(d.split("/")[0])]
    if ips:
        log(f"{rel} — {len(ips)} IP address entries", "info")

    log(f"{rel} — {len(data):,} entries", "ok")
    return True


def main():
    extra = [Path(a) for a in sys.argv[1:] if Path(a).exists()]
    files = FILES_TO_CHECK + extra

    ok = all(validate_file(f) for f in files)

    if not ok:
        log("Validation FAILED — fix JSON errors before proceeding", "error")
        sys.exit(1)

    log("All files valid", "ok")


if __name__ == "__main__":
    main()
