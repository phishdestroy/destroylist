#!/usr/bin/env python3
"""Validate all critical JSON files before any pipeline step."""
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FILES_TO_CHECK = [
    PROJECT_ROOT / "list.json",
    PROJECT_ROOT / "allow" / "allowlist.json",
    PROJECT_ROOT / "community" / "blocklist.json",
    PROJECT_ROOT / "community" / "live_blocklist.json",
    PROJECT_ROOT / "dns" / "active_domains.json",
]

def validate_file(filepath: Path) -> bool:
    if not filepath.exists():
        print(f"SKIP: {filepath.relative_to(PROJECT_ROOT)} (not found)")
        return True

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"FATAL: {filepath.relative_to(PROJECT_ROOT)} — invalid JSON at line {e.lineno}: {e.msg}", file=sys.stderr)
        return False

    if not isinstance(data, list):
        print(f"FATAL: {filepath.relative_to(PROJECT_ROOT)} — expected array, got {type(data).__name__}", file=sys.stderr)
        return False

    bad = [i for i, d in enumerate(data) if not isinstance(d, str) or not d.strip()]
    if bad:
        print(f"WARN: {filepath.relative_to(PROJECT_ROOT)} — {len(bad)} empty/non-string entries (indices: {bad[:5]}...)")

    dupes = len(data) - len(set(d.lower().strip() for d in data))
    if dupes > 0:
        print(f"WARN: {filepath.relative_to(PROJECT_ROOT)} — {dupes} duplicate entries")

    print(f"OK: {filepath.relative_to(PROJECT_ROOT)} — {len(data)} entries")
    return True


def main():
    extra = [Path(a) for a in sys.argv[1:] if Path(a).exists()]
    files = FILES_TO_CHECK + extra

    ok = True
    for f in files:
        if not validate_file(f):
            ok = False

    if not ok:
        print("\n❌ Validation FAILED — fix JSON errors before proceeding", file=sys.stderr)
        sys.exit(1)

    print("\n✅ All files valid")


if __name__ == "__main__":
    main()
