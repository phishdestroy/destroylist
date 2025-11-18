#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from typing import Set, List, Tuple
import tldextract

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

LIST_FILE = PROJECT_ROOT / 'list.json'
ALLOWLIST_FILE = PROJECT_ROOT / 'allow' / 'allowlist.json'

def load_json_list(filepath: Path) -> List[str]:
    if not filepath.exists():
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return [str(d).strip().lower() for d in data if d]
            return []
    except Exception as e:
        print(f"Error loading {filepath}: {e}", file=sys.stderr)
        return []

def get_registered_domain(domain: str) -> str:
    ext = tldextract.extract(domain)
    if not ext.suffix:
        return domain
    return f"{ext.domain}.{ext.suffix}"

def deduplicate_subdomains(domains: List[str]) -> Tuple[List[str], int]:
    root_map = {}

    for domain in domains:
        root = get_registered_domain(domain)
        if root not in root_map:
            root_map[root] = []
        root_map[root].append(domain)

    kept = []
    removed_count = 0

    for root, subdomain_list in root_map.items():
        if root in subdomain_list:
            kept.append(root)
            removed_count += len(subdomain_list) - 1
        else:
            kept.extend(subdomain_list)

    return sorted(kept), removed_count

def main():
    import sys
    dedupe_subdomains = '--dedupe-subdomains' in sys.argv

    print("Loading lists...")
    domains = load_json_list(LIST_FILE)
    allowlist = load_json_list(ALLOWLIST_FILE)

    if not domains:
        print("No domains found in list.json")
        return 1

    print(f"Loaded {len(domains)} domains")
    print(f"Loaded {len(allowlist)} allowlist entries")

    original_count = len(domains)

    allowlist_set = set(allowlist)
    allowlist_patterns = {d for d in allowlist if d.startswith('.')}
    allowlist_exact = allowlist_set - allowlist_patterns

    filtered = []
    removed_by_allowlist = 0

    for domain in domains:
        if domain in allowlist_exact:
            removed_by_allowlist += 1
            continue

        is_allowed = False
        for pattern in allowlist_patterns:
            if domain.endswith(pattern) or domain == pattern[1:]:
                is_allowed = True
                break

        if is_allowed:
            removed_by_allowlist += 1
            continue

        filtered.append(domain)

    print(f"Removed {removed_by_allowlist} domains via allowlist")

    if dedupe_subdomains:
        deduplicated, removed_dupes = deduplicate_subdomains(filtered)
        print(f"Removed {removed_dupes} subdomain duplicates (--dedupe-subdomains enabled)")
    else:
        deduplicated = filtered
        print("Subdomain deduplication disabled (use --dedupe-subdomains to enable)")

    unique = sorted(list(set(deduplicated)))
    removed_exact_dupes = len(deduplicated) - len(unique)
    if removed_exact_dupes > 0:
        print(f"Removed {removed_exact_dupes} exact duplicates")

    total_removed = original_count - len(unique)
    print(f"\nTotal: {original_count} -> {len(unique)} (removed {total_removed})")

    if total_removed == 0:
        print("No changes needed")
        return 0

    with open(LIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)

    print(f"Updated {LIST_FILE.name}")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
