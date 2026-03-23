#!/usr/bin/env python3
"""Convert JSON domain lists to multiple output formats."""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Set

from utils import (
    PROJECT_ROOT, IPV4_RE, INFRA_ROOTS,
    extract_domain, get_root, load_allowlist, save_json, log,
)

FORMATS_DIR = PROJECT_ROOT / "rootlist" / "formats"
ALLOWLIST_FILE = PROJECT_ROOT / "allow" / "allowlist.json"

SOURCES = {
    "primary": PROJECT_ROOT / "list.json",
    "primary_active": PROJECT_ROOT / "dns" / "active_domains.json",
    "community": PROJECT_ROOT / "community" / "blocklist.json",
    "community_active": PROJECT_ROOT / "community" / "live_blocklist.json",
}

ADBLOCK_DESCRIPTIONS = {
    "primary": "Curated phishing and scam domain blocklist by PhishDestroy",
    "primary_active": "DNS-verified active phishing and scam domains by PhishDestroy",
    "community": "Community-aggregated phishing and scam domains from 13+ threat intel sources",
    "community_active": "DNS-verified community-aggregated phishing and scam domains",
}


def load_domains(filepath: Path, allowlist: Set[str]) -> list:
    if not filepath.exists():
        return []
    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
        domains = data if isinstance(data, list) else data.get("domains", [])
        clean = set()
        for d in domains:
            d = str(d).strip().lower().removeprefix("https://").removeprefix("http://")
            d = extract_domain(d)
            if not d or "." not in d:
                continue
            if IPV4_RE.fullmatch(d):
                continue
            if not any(c.isalpha() for c in d):
                continue
            if d in allowlist:
                continue
            root = get_root(d)
            if root and root in allowlist and root not in INFRA_ROOTS:
                continue
            clean.add(d)
        return sorted(clean)
    except Exception as e:
        log(f"Failed to load {filepath.name}: {e}", "error")
        return []


def header(name: str, count: int, fmt: str, c: str = "#") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"{c} Destroylist - {name} | {fmt} | {count:,} domains | {ts}\n{c} https://github.com/phishdestroy/destroylist\n\n"


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
        f"! Total domains: {count:,}\n"
    )


def rpz_header(name: str, count: int) -> str:
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%d %H:%M UTC")
    serial = now.strftime("%Y%m%d%H")
    return (
        f"; Destroylist - {name} | RPZ zone | {count:,} domains | {ts}\n"
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

        log(f"{name}: {len(domains):,} domains -> 6 formats", "ok")

    primary = load_domains(SOURCES["primary"], allowlist)
    if primary:
        write(PROJECT_ROOT / "list.txt", "\n".join(primary) + "\n")

    # Generate plain TXT next to each source JSON
    TXT_SOURCES = {
        PROJECT_ROOT / "dns" / "active_domains.json": PROJECT_ROOT / "dns" / "active_domains.txt",
        PROJECT_ROOT / "dns" / "content_active.json": PROJECT_ROOT / "dns" / "content_active.txt",
        PROJECT_ROOT / "community" / "blocklist.json": PROJECT_ROOT / "community" / "blocklist.txt",
        PROJECT_ROOT / "community" / "live_blocklist.json": PROJECT_ROOT / "community" / "live_blocklist.txt",
        PROJECT_ROOT / "community" / "content_live.json": PROJECT_ROOT / "community" / "content_live.txt",
    }
    for src_json, dst_txt in TXT_SOURCES.items():
        domains = load_domains(src_json, allowlist)
        if domains:
            write(dst_txt, "\n".join(domains) + "\n")
            log(f"{dst_txt.relative_to(PROJECT_ROOT)}: {len(domains):,} domains", "ok")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"FATAL: {e}", "error")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)
