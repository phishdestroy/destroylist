#!/usr/bin/env python3
"""Convert JSON domain lists to multiple output formats."""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Set

from utils import (
    PROJECT_ROOT, IPV4_RE, INFRA_ROOTS,
    extract_domain, is_allowed, is_public_suffix, load_publication_exclusions, load_json_list, log,
    normalize_entry,
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


def load_domains(
    filepath: Path,
    exact: Set[str],
    patterns: Set[str] | None = None,
) -> list:
    if not filepath.exists():
        return []
    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
        domains = data if isinstance(data, list) else data.get("domains", [])
        clean = set()
        suffix_patterns = patterns or set()
        for d in domains:
            d = normalize_entry(d)
            # Hosts/Adblock/DNSMasq/RPZ formats cannot represent URL paths.
            # Converting a path-scoped indicator to its host would block the
            # entire shared service, so omit it from domain-only formats.
            if "/" in d or "?" in d or "#" in d:
                continue
            d = extract_domain(d)
            if not d or "." not in d:
                continue
            if IPV4_RE.fullmatch(d):
                continue
            if not any(c.isalpha() for c in d):
                continue
            if is_allowed(d, exact, suffix_patterns):
                continue
            # A public suffix (e.g. kasserver.com, a hosting provider's
            # customer namespace) would block every tenant in the
            # subtree-blocking formats (dnsmasq, unbound, adblock, RPZ *.).
            if is_public_suffix(d) or d in INFRA_ROOTS:
                continue
            clean.add(d)
        return sorted(clean)
    except Exception as e:
        log(f"Failed to load {filepath.name}: {e}", "error")
        return []


def load_plain_entries(filepath: Path) -> list:
    """Load the lossless plain-list representation, including URL paths."""
    return sorted(set(load_json_list(filepath)))


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
    # SOA SERIAL is an unsigned 32-bit integer (RFC 1035); YYYYMMDDHHMM does
    # not fit and BIND/Knot/dnspython reject the zone. Unix time fits until 2106.
    serial = int(now.timestamp())
    return (
        f"; Destroylist - {name} | RPZ zone | {count:,} domains | {ts}\n"
        f"; https://github.com/phishdestroy/destroylist\n"
        f"$TTL 300\n"
        f"@ SOA localhost. root.localhost. {serial} 86400 7200 2592000 300\n"
        f"  NS  localhost.\n\n"
    )


def redis_format(source_key: str, domains: list) -> str:
    """redis-cli --pipe compatible loader.

    Builds the set under a temporary key and atomically swaps it in with
    RENAME, so readers never observe a partially loaded set. Usage:
        curl -s <url>/redis.txt | redis-cli --pipe
    Lookup: SISMEMBER destroylist:primary example.com
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    key = f"destroylist:{source_key}"
    tmp = f"{key}:loading"
    lines = [
        f'ECHO "Destroylist {source_key} | {len(domains):,} domains | {ts}"',
        f"DEL {tmp}",
    ]
    batch_size = 500
    for i in range(0, len(domains), batch_size):
        lines.append(f"SADD {tmp} " + " ".join(domains[i:i + batch_size]))
    lines.append(f"RENAME {tmp} {key}")
    lines.append(f'ECHO "Loaded {key}"')
    return "\n".join(lines) + "\n"


def write(path: Path, content: str):
    path.write_text(content, encoding="utf-8")


def rpz_serial_valid(path: Path) -> bool:
    """False when the published zone still carries an out-of-range SOA serial."""
    try:
        with path.open(encoding="utf-8") as fh:
            for _ in range(10):
                line = fh.readline()
                if " SOA " in line:
                    return int(line.split()[4]) <= 0xFFFFFFFF
    except (OSError, ValueError, IndexError):
        return False
    return False


def write_if_changed(path: Path, head: str, body: str) -> bool:
    """Rewrite a feed only when its entries changed.

    Headers carry a timestamp; rewriting all formats on every run produced a
    new commit of every feed file each hour even when no domain changed.
    The existing file is split after exactly as many lines as the new header
    has, so a shorter or longer domain set never compares equal by accident.
    """
    if path.exists() and (path.suffix != ".zone" or rpz_serial_valid(path)):
        current = path.read_text(encoding="utf-8")
        parts = current.split("\n", head.count("\n"))
        if len(parts) > head.count("\n") and parts[-1] == body:
            return False
    write(path, head + body)
    return True


def main():
    FORMATS_DIR.mkdir(parents=True, exist_ok=True)
    exact, patterns = load_publication_exclusions()

    for name, src in SOURCES.items():
        domains = load_domains(src, exact, patterns)
        if not domains:
            continue

        out = FORMATS_DIR / name
        out.mkdir(exist_ok=True)
        n = name.replace("_", " ").title()

        feeds = [
            ("domains.txt", header(n, len(domains), "plain"), "\n".join(domains) + "\n"),
            ("hosts.txt", header(n, len(domains), "hosts"), "\n".join(f"0.0.0.0 {d}" for d in domains) + "\n"),
            ("adblock.txt", adblock_header(n, name, len(domains)), "\n".join(f"||{d}^" for d in domains) + "\n"),
            ("dnsmasq.conf", header(n, len(domains), "dnsmasq"), "\n".join(f"address=/{d}/0.0.0.0" for d in domains) + "\n"),
            ("unbound.conf", header(n, len(domains), "unbound"), "\n".join(f'local-zone: "{d}" always_nxdomain' for d in domains) + "\n"),
            # Apex and every subdomain, matching dnsmasq/unbound/adblock semantics.
            ("rpz.zone", rpz_header(n, len(domains)), "\n".join(f"{d} CNAME .\n*.{d} CNAME ." for d in domains) + "\n"),
        ]
        redis_text = redis_format(name, domains)
        redis_head, redis_body = redis_text.split("\n", 1)
        feeds.append(("redis.txt", redis_head + "\n", redis_body))

        changed = sum(write_if_changed(out / fname, head, body) for fname, head, body in feeds)
        log(f"{name}: {len(domains):,} domains -> {changed}/{len(feeds)} formats rewritten", "ok")

    primary = load_plain_entries(SOURCES["primary"])
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
        domains = load_plain_entries(src_json)
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
