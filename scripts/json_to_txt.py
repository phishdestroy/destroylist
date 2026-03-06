#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Set

import tldextract

# Allow importing sibling modules when run as `python scripts/json_to_txt.py`
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_rootlist import INFRA_ROOTS

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
FORMATS_DIR = PROJECT_ROOT / "rootlist" / "formats"
ALLOWLIST_FILE = PROJECT_ROOT / "allow" / "allowlist.json"

SOURCES = {
    "primary": PROJECT_ROOT / "list.json",
    "primary_active": PROJECT_ROOT / "dns" / "active_domains.json",
    "community": PROJECT_ROOT / "community" / "blocklist.json",
    "community_active": PROJECT_ROOT / "community" / "live_blocklist.json",
}

IPV4_RE = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")


def get_root(host: str) -> str:
    """Extract root domain using tldextract (e.g. sites.google.com -> google.com)."""
    ext = tldextract.extract(host)
    rd = ext.top_domain_under_public_suffix if hasattr(ext, "top_domain_under_public_suffix") else ext.registered_domain
    return rd.lower() if rd else ""


def load_allowlist() -> Set[str]:
    """Load allowlist domains for filtering at output generation time."""
    if not ALLOWLIST_FILE.exists():
        return set()
    try:
        data = json.loads(ALLOWLIST_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return {str(d).strip().lower() for d in data if d}
    except Exception:
        pass
    return set()


def load_domains(filepath: Path, allowlist: Set[str]) -> list:
    if not filepath.exists():
        return []
    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
        domains = data if isinstance(data, list) else data.get("domains", [])
        clean = set()
        for d in domains:
            d = str(d).strip().lower().replace("https://", "").replace("http://", "").split("/")[0].split("?")[0]
            if not d or "." not in d:
                continue
            # Skip IP addresses — this is a domain blacklist
            if IPV4_RE.fullmatch(d):
                continue
            # Skip entries without alphabetic characters (numeric garbage like '0.512752')
            if not any(c.isalpha() for c in d):
                continue
            # Skip domains that are in the allowlist.
            # Exact match: always filter (e.g. ghost.io itself is allowed).
            # Root match: only filter if root is NOT a hosting platform,
            # because subdomains on hosting platforms (e.g. phish.ghost.io)
            # are separate sites and may be malicious.
            if d in allowlist:
                continue
            root = get_root(d)
            if root and root in allowlist and root not in INFRA_ROOTS:
                continue
            clean.add(d)
        return sorted(clean)
    except Exception:
        return []


ADBLOCK_DESCRIPTIONS = {
    "primary": "Curated phishing and scam domain blocklist by PhishDestroy",
    "primary_active": "DNS-verified active phishing and scam domains by PhishDestroy",
    "community": "Community-aggregated phishing and scam domains from 35+ threat intel sources",
    "community_active": "DNS-verified community-aggregated phishing and scam domains",
}


def header(name: str, count: int, fmt: str, c: str = "#") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"{c} Destroylist - {name} | {fmt} | {count} domains | {ts}\n{c} https://github.com/phishdestroy/destroylist\n\n"


def adblock_header(name: str, source_key: str, count: int) -> str:
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%d %H:%M UTC")
    version = now.strftime("%Y%m%d%H%M")
    description = ADBLOCK_DESCRIPTIONS.get(source_key, f"Destroylist - {name}")
    return (
        f"[Adblock Plus]\n"
        f"! Title: Destroylist - {name}\n"
        f"! Description: {description}\n"
        f"! Homepage: https://github.com/phishdestroy/destroylist\n"
        f"! License: https://github.com/phishdestroy/destroylist/blob/main/LICENSE\n"
        f"! Expires: 1 day\n"
        f"! Last modified: {ts}\n"
        f"! Version: {version}\n"
        f"! Total domains: {count}\n"
    )


def rpz_header(name: str, count: int) -> str:
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%d %H:%M UTC")
    serial = now.strftime("%Y%m%d%H")
    return (
        f"; Destroylist - {name} | RPZ zone | {count} domains | {ts}\n"
        f"; https://github.com/phishdestroy/destroylist\n"
        f"$TTL 300\n"
        f"@ SOA localhost. root.localhost. {serial} 86400 7200 2592000 300\n"
        f"  NS  localhost.\n\n"
    )


def write(path: Path, content: str):
    path.write_text(content, encoding="utf-8")


def main():
    FORMATS_DIR.mkdir(parents=True, exist_ok=True)
    allowlist = load_allowlist()

    for name, src in SOURCES.items():
        domains = load_domains(src, allowlist)
        if not domains:
            continue

        out = FORMATS_DIR / name
        out.mkdir(exist_ok=True)
        n = name.replace("_", " ").title()

        write(out / "domains.txt", header(n, len(domains), "plain") + "\n".join(domains) + "\n")
        write(out / "hosts.txt", header(n, len(domains), "hosts") + "\n".join(f"0.0.0.0 {d}" for d in domains) + "\n")
        write(out / "adblock.txt", adblock_header(n, name, len(domains)) + "\n".join(f"||{d}^" for d in domains) + "\n")
        write(out / "dnsmasq.conf", header(n, len(domains), "dnsmasq") + "\n".join(f"address=/{d}/0.0.0.0" for d in domains) + "\n")
        write(out / "unbound.conf", header(n, len(domains), "unbound") + "\n".join(f'local-zone: "{d}" always_nxdomain' for d in domains) + "\n")
        write(out / "rpz.zone", rpz_header(n, len(domains)) + "\n".join(f"{d} CNAME ." for d in domains) + "\n")

        print(f"{name}: {len(domains)}")

    primary = load_domains(SOURCES["primary"], allowlist)
    if primary:
        write(PROJECT_ROOT / "list.txt", "\n".join(primary) + "\n")


if __name__ == "__main__":
    main()