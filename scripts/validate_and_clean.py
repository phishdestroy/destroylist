#!/usr/bin/env python3
"""
Clean all domain lists against the allowlist.
Removes allowed domains, invalid entries, and handles path-based entries.
Targets: list.json, community/blocklist.json, community/live_blocklist.json
"""
import json
import re
import sys
from pathlib import Path
from typing import List, Set, Tuple

import tldextract

# Allow importing sibling modules when run as `python scripts/validate_and_clean.py`
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_rootlist import INFRA_ROOTS

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

ALLOWLIST_FILE = PROJECT_ROOT / "allow" / "allowlist.json"

TARGETS = [
    PROJECT_ROOT / "list.json",
    PROJECT_ROOT / "community" / "blocklist.json",
    PROJECT_ROOT / "community" / "live_blocklist.json",
]

IPV4_RE = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")


def extract_domain(entry: str) -> str:
    """Extract the domain part from an entry that may contain a path.

    Examples:
        'github.com/ledger-live-download' -> 'github.com'
        'evil-site.com'                   -> 'evil-site.com'
        '192.168.1.1/admin'               -> '192.168.1.1'
    """
    return entry.split("/")[0].split("?")[0].split("#")[0]


def is_valid_entry(entry: str) -> bool:
    """Check if an entry is a plausible domain or domain/path.

    Rejects entries that are clearly not domains:
    - No dots (e.g. '123', 'c', 'chrome', 'dsadasasd')
    - Pure numbers (e.g. '0.512752', '5535830600076817')
    - TLD is single char or non-alphabetic (e.g. 'kro44.c')
    - Empty or whitespace-only

    Accepts Punycode TLDs (xn--*) as valid.
    """
    if not entry:
        return False
    domain = extract_domain(entry)
    if not domain:
        return False
    # Must contain at least one dot
    if "." not in domain:
        return False
    # Must have at least one alphabetic character (filters out numeric garbage)
    if not any(c.isalpha() for c in domain):
        return False
    # TLD (last part after dot) must be valid
    parts = domain.split(".")
    tld = parts[-1]
    # Allow Punycode TLDs (xn--*)
    if tld.startswith("xn--"):
        return len(tld) >= 6  # xn-- + at least 2 chars
    # Regular TLD must be alphabetic and at least 2 chars
    if len(tld) < 2 or not tld.isalpha():
        return False
    return True


def is_ip_entry(entry: str) -> bool:
    """Check if the domain part of an entry is an IP address."""
    domain = extract_domain(entry)
    return bool(IPV4_RE.fullmatch(domain))


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

    cleaned = []
    for d in data:
        if not d:
            continue
        s = str(d).strip().lower()
        if not s:
            continue
        # Strip protocol prefixes
        s = s.removeprefix("https://").removeprefix("http://")
        cleaned.append(s)
    return cleaned


def load_allowlist() -> Tuple[Set[str], Set[str]]:
    entries = load_json_list(ALLOWLIST_FILE)
    if not entries:
        print("Allowlist is empty or missing")
        return set(), set()

    patterns = {d for d in entries if d.startswith(".")}
    exact = set(entries) - patterns
    print(f"Allowlist: {len(exact)} exact + {len(patterns)} patterns = {len(entries)} total")
    return exact, patterns


def get_root(host: str) -> str:
    """Extract root domain using tldextract (e.g. sites.google.com -> google.com)."""
    ext = tldextract.extract(host)
    rd = ext.top_domain_under_public_suffix if hasattr(ext, "top_domain_under_public_suffix") else ext.registered_domain
    return rd.lower() if rd else ""


def is_allowed(domain: str, exact: Set[str], patterns: Set[str]) -> bool:
    """Check if a domain matches the allowlist (exact or pattern)."""
    if domain in exact:
        return True
    for p in patterns:
        if domain.endswith(p) or domain == p[1:]:
            return True
    return False


def filter_domains(domains: List[str], exact: Set[str], patterns: Set[str]) -> Tuple[List[str], int]:
    """Filter domains against the allowlist.

    For each entry:
    1. Exact match on the full entry (e.g. 'github.com' in allowlist).
    2. Extract domain part (strip path/query/fragment) and check allowlist.
    3. Extract root domain via tldextract and check allowlist — but ONLY
       for non-hosting platforms (INFRA_ROOTS), because subdomains on
       hosting platforms (e.g. phish.ghost.io) are separate malicious sites.
    """
    filtered = []
    removed = 0

    for entry in domains:
        # 1. Full entry exact/pattern match
        if is_allowed(entry, exact, patterns):
            removed += 1
            continue

        # 2. Domain part (without path) — handles 'github.com/something'
        domain = extract_domain(entry)
        if domain != entry and is_allowed(domain, exact, patterns):
            root = get_root(domain)
            # Keep entries on hosting platforms (subdomains = separate sites)
            if root and root in INFRA_ROOTS:
                filtered.append(entry)
            else:
                removed += 1
            continue

        # 3. Root domain check — handles 'sites.google.com'
        root = get_root(domain)
        if root and root != domain and is_allowed(root, exact, patterns) and root not in INFRA_ROOTS:
            removed += 1
            continue

        filtered.append(entry)

    return filtered, removed


def clean_file(filepath: Path, exact: Set[str], patterns: Set[str]) -> bool:
    if not filepath.exists():
        return False

    domains = load_json_list(filepath)
    if not domains:
        return False

    original_count = len(domains)

    # Remove invalid entries (garbage, IPs, pure numbers, etc.)
    valid = []
    removed_invalid = 0
    removed_ips = 0
    for entry in domains:
        if is_ip_entry(entry):
            removed_ips += 1
        elif not is_valid_entry(entry):
            removed_invalid += 1
        else:
            valid.append(entry)

    if removed_invalid > 0:
        print(f"  Removed {removed_invalid} invalid entries from {filepath.name}")
    if removed_ips > 0:
        print(f"  Removed {removed_ips} IP address entries from {filepath.name}")

    # Filter allowlist (now handles path-based entries correctly)
    filtered, removed_allow = filter_domains(valid, exact, patterns)

    # Deduplicate and sort
    unique = sorted(set(filtered))
    removed_dupes = len(filtered) - len(unique)

    total_removed = original_count - len(unique)
    name = filepath.relative_to(PROJECT_ROOT)

    # Always rewrite file to ensure consistent formatting (indent=2, sorted)
    expected = json.dumps(unique, indent=2, ensure_ascii=False)
    current = filepath.read_text(encoding="utf-8").rstrip("\n")
    needs_reformat = current != expected

    if total_removed == 0 and not needs_reformat:
        print(f"  {name}: {original_count} domains — no changes")
        return False

    if total_removed > 0:
        print(f"  {name}: {original_count} -> {len(unique)} "
              f"(invalid: -{removed_invalid}, IPs: -{removed_ips}, allowlist: -{removed_allow}, dupes: -{removed_dupes})")
    elif needs_reformat:
        print(f"  {name}: {original_count} domains — reformatted")

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
