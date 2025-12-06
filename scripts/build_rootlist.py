import json
import os
from pathlib import Path
from typing import Dict, List, Set

import tldextract

ROOT = Path(__file__).resolve().parents[1]

SOURCE_LIST = ROOT / "list.json"
SOURCE_ACTIVE = ROOT / "dns" / "active_domains.json"

OUT_DIR = ROOT / "rootlist"
OUT_ACTIVE = OUT_DIR / "active_root_domains.json"
OUT_PROVIDERS = OUT_DIR / "providers_root_domains.json"
OUT_ONLINE = OUT_DIR / "online_root_domains.json"

PROVIDER_GROUPS: Dict[str, Set[str]] = {
    "multi_tenant_hosting": {
        "vercel.app",
        "netlify.app",
        "github.io",
        "render.com",
        "onrender.com",
        "digitaloceanspaces.com",
        "windows.net",
        "fastly.net",
        "cprapid.com",
        "sslip.io",
        "duckdns.org",
        "replit.dev",
        "surge.sh",
        "typedream.app",
        "hostingersite.com",
        "firebaseapp.com",
        "web.app",
        "pages.dev",
        "workers.dev",
    },
    "site_builders": {
        "weebly.com",
        "weeblysite.com",
        "wixsite.com",
        "wordpress.com",
        "blogspot.com",
        "blogspot.am",
        "square.site",
        "webflow.io",
        "godaddysites.com",
        "webcindario.com",
        "home.pl",
        "pineapple.page",
        "gitbook.io",
    },
    "decentralized_storage": {
        "ipfs.io",
        "cloudflare-ipfs.com",
        "dweb.link",
        "infura-ipfs.io",
        "eth.limo",
        "fleek.co",
    },
    "saas_platforms": {
        "teachable.com",
    },
}

INFRA_ROOTS: Set[str] = set().union(*PROVIDER_GROUPS.values())


def load_list(path: Path) -> List[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        arr = data.get("domains", [])
    else:
        arr = data
    out: List[str] = []
    for v in arr:
        if isinstance(v, str):
            d = v.strip().strip(".").lower()
            if d:
                out.append(d)
    return out


def get_root(host: str) -> str | None:
    ext = tldextract.extract(host)
    rd = getattr(ext, "top_domain_under_public_suffix", None)
    return rd.lower() if rd else None


def process_items(items: List[str]) -> tuple[Set[str], Dict[str, Dict[str, Dict[str, object]]], Set[str]]:
    active_roots: Set[str] = set()
    provider_stats: Dict[str, Dict[str, Dict[str, object]]] = {
        g: {} for g in PROVIDER_GROUPS.keys()
    }
    cleaned_hosts: Set[str] = set()

    for entry in items:
        rd = get_root(entry)
        if not rd:
            continue

        if rd in INFRA_ROOTS:
            for group, roots in PROVIDER_GROUPS.items():
                if rd in roots:
                    gmap = provider_stats[group]
                    rec = gmap.get(rd)
                    if rec is None:
                        rec = {"count": 0, "hosts": set()}
                        gmap[rd] = rec
                    rec["count"] = int(rec["count"]) + 1
                    rec["hosts"].add(entry)
            continue

        active_roots.add(rd)
        cleaned_hosts.add(entry)

    return active_roots, provider_stats, cleaned_hosts


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    if not SOURCE_LIST.exists():
        raise SystemExit(f"list.json not found: {SOURCE_LIST}")

    items_primary = load_list(SOURCE_LIST)
    primary_roots, primary_providers, _ = process_items(items_primary)

    OUT_ACTIVE.write_text(
        json.dumps(
            {
                "domains": sorted(primary_roots),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    providers_payload = {
        "meta": {
            "name": "excluded provider roots",
            "source": "list.json",
        },
        "providers": {},
    }

    for group, stats in primary_providers.items():
        if not stats:
            continue

        total_entries = sum(int(rec["count"]) for rec in stats.values())
        items_sorted = sorted(
            stats.items(), key=lambda kv: int(kv[1]["count"]), reverse=True
        )

        group_items = []
        for dom, rec in items_sorted:
            hosts = sorted(rec["hosts"])
            group_items.append(
                {
                    "domain": dom,
                    "count": int(rec["count"]),
                    "hosts": hosts,
                }
            )

        providers_payload["providers"][group] = {
            "total_domains": len(stats),
            "total_entries": total_entries,
            "items": group_items,
        }

    OUT_PROVIDERS.write_text(
        json.dumps(providers_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if SOURCE_ACTIVE.exists():
        items_active = load_list(SOURCE_ACTIVE)
        _, _, online_hosts = process_items(items_active)

        OUT_ONLINE.write_text(
            json.dumps(
                {
                    "domains": sorted(online_hosts),
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
