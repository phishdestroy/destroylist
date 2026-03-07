#!/usr/bin/env python3
"""Extract registrable root domains and categorize by hosting provider."""
import json
import os
from pathlib import Path
from typing import Dict, List, Set

from utils import (
    PROJECT_ROOT, IPV4_RE, PROVIDER_GROUPS, INFRA_ROOTS,
    get_root, load_allowlist, save_json, log,
)

SOURCE_LIST = PROJECT_ROOT / "list.json"
SOURCE_ACTIVE = PROJECT_ROOT / "dns" / "active_domains.json"
SOURCE_COMMUNITY = PROJECT_ROOT / "community" / "blocklist.json"
SOURCE_COMMUNITY_ACTIVE = PROJECT_ROOT / "community" / "live_blocklist.json"

OUT_DIR = PROJECT_ROOT / "rootlist"
OUT_ACTIVE = OUT_DIR / "active_root_domains.json"
OUT_PROVIDERS = OUT_DIR / "providers_root_domains.json"
OUT_ONLINE = OUT_DIR / "online_root_domains.json"
OUT_COMMUNITY = OUT_DIR / "community_root_domains.json"
OUT_COMMUNITY_ONLINE = OUT_DIR / "community_online_root_domains.json"
OUT_COMMUNITY_PROVIDERS = OUT_DIR / "community_providers_root_domains.json"
OUT_SERVICES = OUT_DIR / "services_domains.json"
OUT_COMMUNITY_SERVICES = OUT_DIR / "community_services_domains.json"


def write_txt(json_path: Path, domains):
    """Write a plain TXT (one domain per line) next to a JSON file."""
    txt_path = json_path.with_suffix(".txt")
    txt_path.write_text("\n".join(sorted(domains)) + "\n", encoding="utf-8")


def load_list(path: Path) -> List[str]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        arr = data.get("domains", [])
    else:
        arr = data
    return [v.strip().strip(".").lower() for v in arr if isinstance(v, str) and v.strip()]


def process_items(
    items: List[str],
    allowlist: Set[str] | None = None,
) -> tuple[Set[str], Dict[str, Dict], Set[str], Set[str]]:
    active_roots: Set[str] = set()
    provider_stats: Dict[str, Dict] = {g: {} for g in PROVIDER_GROUPS}
    cleaned_hosts: Set[str] = set()
    service_hosts: Set[str] = set()
    _allowlist = allowlist or set()

    for entry in items:
        host = entry.split("/")[0].split("?")[0].split("#")[0]
        if IPV4_RE.fullmatch(host):
            continue

        rd = get_root(host)
        if not rd:
            continue

        if rd in INFRA_ROOTS:
            service_hosts.add(host)
            for group, roots in PROVIDER_GROUPS.items():
                if rd in roots:
                    rec = provider_stats[group].setdefault(rd, {"count": 0, "hosts": set()})
                    rec["count"] += 1
                    rec["hosts"].add(entry)
            continue

        if rd in _allowlist:
            continue

        active_roots.add(rd)
        cleaned_hosts.add(host)

    return active_roots, provider_stats, cleaned_hosts, service_hosts


def build_providers_payload(provider_stats: Dict, source_name: str) -> Dict:
    payload = {
        "meta": {"name": "excluded provider roots", "source": source_name},
        "providers": {},
    }

    for group, stats in provider_stats.items():
        if not stats:
            continue

        total_entries = sum(rec["count"] for rec in stats.values())
        items_sorted = sorted(stats.items(), key=lambda kv: kv[1]["count"], reverse=True)

        payload["providers"][group] = {
            "total_domains": len(stats),
            "total_entries": total_entries,
            "items": [
                {"domain": dom, "count": rec["count"], "hosts": sorted(rec["hosts"])}
                for dom, rec in items_sorted
            ],
        }

    return payload


def main():
    log("Build root lists", "step")
    os.makedirs(OUT_DIR, exist_ok=True)
    allowlist = load_allowlist()

    if not SOURCE_LIST.exists():
        raise SystemExit(f"list.json not found: {SOURCE_LIST}")

    # Primary
    items = load_list(SOURCE_LIST)
    roots, providers, _, services = process_items(items, allowlist)
    save_json(OUT_ACTIVE, {"domains": sorted(roots)})
    write_txt(OUT_ACTIVE, roots)
    save_json(OUT_PROVIDERS, build_providers_payload(providers, "list.json"))
    save_json(OUT_SERVICES, sorted(services))
    write_txt(OUT_SERVICES, services)
    log(f"Primary: {len(roots):,} root domains, {len(services):,} service domains", "ok")

    # Primary active
    if SOURCE_ACTIVE.exists():
        items = load_list(SOURCE_ACTIVE)
        _, _, hosts, _ = process_items(items, allowlist)
        save_json(OUT_ONLINE, {"domains": sorted(hosts)})
        write_txt(OUT_ONLINE, hosts)
        log(f"Primary active: {len(hosts):,} hosts", "ok")

    # Community
    if SOURCE_COMMUNITY.exists():
        items = load_list(SOURCE_COMMUNITY)
        roots, providers, _, services = process_items(items, allowlist)
        save_json(OUT_COMMUNITY, {"domains": sorted(roots)})
        write_txt(OUT_COMMUNITY, roots)
        save_json(OUT_COMMUNITY_PROVIDERS, build_providers_payload(providers, "community/blocklist.json"))
        save_json(OUT_COMMUNITY_SERVICES, sorted(services))
        write_txt(OUT_COMMUNITY_SERVICES, services)
        log(f"Community: {len(roots):,} root domains, {len(services):,} service domains", "ok")

    # Community active
    if SOURCE_COMMUNITY_ACTIVE.exists():
        items = load_list(SOURCE_COMMUNITY_ACTIVE)
        _, _, hosts, _ = process_items(items, allowlist)
        save_json(OUT_COMMUNITY_ONLINE, {"domains": sorted(hosts)})
        write_txt(OUT_COMMUNITY_ONLINE, hosts)
        log(f"Community active: {len(hosts):,} hosts", "ok")


if __name__ == "__main__":
    main()
