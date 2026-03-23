#!/usr/bin/env python3
"""Aggregate external blocklist sources into community/blocklist.json."""
import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

import requests
from tqdm import tqdm

from utils import (
    PROJECT_ROOT, IPV4_RE, INFRA_ROOTS,
    load_allowlist_split, is_allowed, save_json, make_badge, log,
)

COMMUNITY_DIR = PROJECT_ROOT / "community"
LOCAL_FILES = [PROJECT_ROOT / "list.json"]
ALLOWLIST_FILE = PROJECT_ROOT / "allow" / "allowlist.json"

SOURCES_CONFIG = {
    "MetaMask": {"url": "https://raw.githubusercontent.com/MetaMask/eth-phishing-detect/refs/heads/main/src/config.json", "parser": "metamask"},
    "ScamSniffer": {"url": "https://raw.githubusercontent.com/scamsniffer/scam-database/main/blacklist/domains.json", "parser": "json_list"},
    "Polkadot": {"url": "https://raw.githubusercontent.com/polkadot-js/phishing/master/all.json", "parser": "polkadot"},
    "Codeesura": {"url": "https://raw.githubusercontent.com/codeesura/Anti-phishing-extension/main/phishing-sites-list.json", "parser": "json_list"},
    "CryptoFirewall": {"url": "https://raw.githubusercontent.com/chartingshow/crypto-firewall/master/src/blacklists/domains-only.txt", "parser": "text_lines"},
    "OpenPhish": {"url": "https://raw.githubusercontent.com/openphish/public_feed/main/feed.txt", "parser": "text_lines"},
    "PhishDestroy": {"url": "https://raw.githubusercontent.com/phishdestroy/destroylist/main/list.json", "parser": "json_list"},
    "SEAL": {"url": "https://raw.githubusercontent.com/security-alliance/blocklists/refs/heads/main/domain.txt", "parser": "text_lines"},
    "SPMedia_DetectedURLs": {"url": "https://raw.githubusercontent.com/spmedia/Crypto-Scam-and-Crypto-Phishing-Threat-Intel-Feed/refs/heads/main/detected_urls.txt", "parser": "urls_list"},
    "Enkrypt_Blacklist": {"url": "https://raw.githubusercontent.com/enkryptcom/phishing-detect/refs/heads/main/dist/lists/blacklist.json", "parser": "json_list"},
    "DiscordPhishing_Nikolai": {"url": "https://raw.githubusercontent.com/nikolaischunk/discord-phishing-links/main/domain-list.json", "parser": "json_key_domains"},
    "DiscordPhishing_Dogino": {"url": "https://raw.githubusercontent.com/Dogino/Discord-Phishing-URLs/main/scam-urls.txt", "parser": "text_lines"},
    "Phishunt": {"url": "https://phishunt.io/feed.txt", "parser": "urls_list"},
}

OUTPUT_FILE = COMMUNITY_DIR / "blocklist.json"
STATE_FILE = COMMUNITY_DIR / "state.json"
BADGE_FILE = COMMUNITY_DIR / "count.json"
COMMIT_MSG_FILE = COMMUNITY_DIR / "commit_message.txt"

STRICT_DOMAIN_RE = re.compile(
    r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b", re.IGNORECASE
)


# ── Domain helpers ───────────────────────────────────────────────────────────

def is_valid_domain(d: str) -> bool:
    if not d or len(d) > 253:
        return False
    parts = d.split(".")
    if len(parts) < 2:
        return False
    if not re.fullmatch(r"[a-z]{2,63}", parts[-1], re.IGNORECASE):
        return False
    return all(
        re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", p, re.IGNORECASE)
        for p in parts
    )


def normalize_domain(d: str) -> str:
    d = d.strip().strip(".").lower()
    if IPV4_RE.fullmatch(d):
        return ""
    if not is_valid_domain(d):
        return ""
    if d in INFRA_ROOTS:
        return ""
    return d


def add_norm(dst: set, candidate: str):
    nd = normalize_domain(candidate)
    if nd:
        dst.add(nd)


def clean_hosts_ips(text: str) -> str:
    text = re.sub(r"(^|\s)(?:0\.0\.0\.0|127\.0\.0\.1|::1)\s*", " ", text)
    text = re.sub(r"(?:0\.0\.0\.0|127\.0\.0\.1|::1)(?=[A-Za-z0-9])", " ", text)
    return text


# ── Parsers ──────────────────────────────────────────────────────────────────

def parse_metamask(content: str) -> set:
    try:
        data = json.loads(content)
        return {normalize_domain(x) for x in data.get("blacklist", []) if normalize_domain(x)}
    except Exception:
        return set()


def parse_polkadot(content: str) -> set:
    try:
        data = json.loads(content)
        deny = data.get("deny", [])
        if isinstance(deny, list):
            return {normalize_domain(x) for x in deny if normalize_domain(x)}
    except Exception:
        pass
    return set()


def parse_json_list(content: str) -> set:
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return {normalize_domain(x) for x in data if isinstance(x, str) and normalize_domain(x)}
    except Exception:
        pass
    return set()


def parse_json_key_domains(content: str) -> set:
    try:
        data = json.loads(content)
        arr = data.get("domains", [])
        if isinstance(arr, list):
            return {normalize_domain(x) for x in arr if isinstance(x, str) and normalize_domain(x)}
    except Exception:
        pass
    return set()


def extract_domains_from_text(text: str) -> set:
    text = clean_hosts_ips(text)
    out = set()
    for m in STRICT_DOMAIN_RE.finditer(text):
        add_norm(out, m.group(0))
    return out


def parse_text_lines(content: str) -> set:
    out = set()
    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "!", ";")):
            continue
        if line.startswith(("0.0.0.0", "127.0.0.1", "::1")):
            line = clean_hosts_ips(line)
        if line.startswith("||"):
            line = line[2:]
        if "^" in line:
            line = line.split("^", 1)[0]
        if "$" in line:
            line = line.split("$", 1)[0]
        if "://" in line or line.startswith(("www.", "ftp.", "http.", "https.")):
            try:
                host = urlparse(line if "://" in line else "http://" + line).hostname
                if host:
                    add_norm(out, host)
                    continue
            except Exception:
                pass
        out.update(extract_domains_from_text(line))
    return out


def parse_urls_list(content: str) -> set:
    out = set()
    for raw in content.splitlines():
        s = raw.strip()
        if not s or s.startswith(("#", "!", ";")):
            continue
        try:
            host = urlparse(s if "://" in s else "http://" + s).hostname
            if host:
                add_norm(out, host)
                continue
        except Exception:
            pass
        out.update(extract_domains_from_text(s))
    return out


PARSERS = {
    "metamask": parse_metamask,
    "polkadot": parse_polkadot,
    "json_list": parse_json_list,
    "text_lines": parse_text_lines,
    "urls_list": parse_urls_list,
    "json_key_domains": parse_json_key_domains,
}


# ── Network ──────────────────────────────────────────────────────────────────

def fetch_content(url: str) -> str | None:
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0 Aggregator/2.0"})
        r.raise_for_status()
        return r.text
    except requests.exceptions.Timeout:
        log(f"TIMEOUT: {url}", "warn")
    except requests.exceptions.HTTPError as e:
        log(f"HTTP {e.response.status_code}: {url}", "warn")
    except Exception as e:
        log(f"{type(e).__name__}: {e}", "error")
    return None


def fetch_source(name: str, cfg: dict) -> tuple:
    """Fetch and parse a single source. Returns (name, domains, hash, success)."""
    url = cfg["url"]
    parser_func = PARSERS.get(cfg["parser"])
    content = fetch_content(url)
    if content and parser_func:
        domains = parser_func(content)
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return name, domains, content_hash, True
    return name, set(), None, False


# ── Allowlist filter ─────────────────────────────────────────────────────────

def filter_by_allowlist(domains: set) -> tuple:
    exact, patterns = load_allowlist_split()
    if not exact and not patterns:
        return domains, 0
    filtered, removed = set(), 0
    for domain in domains:
        if is_allowed(domain, exact, patterns):
            removed += 1
        else:
            filtered.add(domain)
    return filtered, removed


# ── State ────────────────────────────────────────────────────────────────────

def load_state() -> dict:
    path = STATE_FILE
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    log("Community aggregation", "step")
    COMMUNITY_DIR.mkdir(parents=True, exist_ok=True)
    last_state = load_state()
    new_state: dict = {}
    changes: list = []

    # Load existing blocklist as base
    all_domains: set = set()
    if OUTPUT_FILE.exists():
        try:
            existing = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
            if isinstance(existing, list):
                all_domains = {normalize_domain(d) for d in existing if normalize_domain(d)}
                log(f"Base: {len(all_domains):,} existing domains")
        except Exception:
            log("Could not load existing blocklist, starting fresh", "warn")

    # Load local JSON files
    for file_path in LOCAL_FILES:
        if not file_path.exists():
            continue
        try:
            local_domains = json.loads(file_path.read_text(encoding="utf-8"))
            if isinstance(local_domains, list):
                before = len(all_domains)
                for d in local_domains:
                    add_norm(all_domains, d)
                log(f"Local {file_path.name}: +{len(all_domains) - before:,}")
        except Exception:
            log(f"Skip {file_path.name}", "warn")

    # Fetch remote sources in parallel
    log("Fetching remote sources", "step")
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(fetch_source, name, cfg): name
            for name, cfg in SOURCES_CONFIG.items()
        }
        for future in tqdm(as_completed(futures), total=len(futures),
                           desc="  Sources", unit="src", leave=True):
            name, domains, content_hash, success = future.result()
            before = len(all_domains)
            if success:
                all_domains.update(domains)
                added = len(all_domains) - before
                log(f"{name}: {len(domains):,} parsed, +{added:,} new")
            else:
                content_hash = last_state.get(name, {}).get("hash")
                log(f"{name}: unavailable, kept existing", "warn")

            last_hash = last_state.get(name, {}).get("hash")
            if content_hash != last_hash and success:
                last_count = last_state.get(name, {}).get("count", 0)
                diff = len(domains) - last_count
                changes.append({"name": name, "diff": diff, "sign": "+" if diff >= 0 else ""})

            # Track source health
            prev_failures = last_state.get(name, {}).get("consecutive_failures", 0)
            if success:
                new_state[name] = {"hash": content_hash, "count": len(domains), "consecutive_failures": 0}
            else:
                failures = prev_failures + 1
                new_state[name] = {
                    "hash": content_hash,
                    "count": last_state.get(name, {}).get("count", 0),
                    "consecutive_failures": failures,
                }
                if failures >= 3:
                    log(f"HEALTH: {name} has failed {failures} consecutive times", "warn")

    last_total = last_state.get("total_count", 0)
    if len(all_domains) == last_total and not changes:
        log("No changes detected", "ok")
        return

    # Filter allowlist
    all_domains, removed = filter_by_allowlist(all_domains)
    if removed:
        log(f"Allowlist: removed {removed:,} domains")

    new_state["total_count"] = len(all_domains)

    # Commit message
    commit_title = "Update community blocklist"
    commit_body = f"Total domains: {len(all_domains):,}\n\n"
    if changes:
        title_parts = [f"{c['sign']}{c['diff']} {c['name']}" for c in changes]
        commit_title = f"Sync: {', '.join(title_parts)}"
        commit_body += "Changes:\n" + "\n".join(f"- {c['name']}: {c['sign']}{c['diff']}" for c in changes)

    COMMIT_MSG_FILE.write_text(commit_title + "\n\n" + commit_body, encoding="utf-8")

    # Write outputs
    sorted_domains = sorted(all_domains)
    save_json(OUTPUT_FILE, sorted_domains)
    save_json(STATE_FILE, new_state)
    save_json(BADGE_FILE, make_badge("Community Domains", len(all_domains), "blue"), indent=None)

    log(f"Done: {len(sorted_domains):,} domains", "ok")


if __name__ == "__main__":
    import sys
    try:
        main()
    except Exception as e:
        log(f"FATAL: {e}", "error")
        import traceback
        traceback.print_exc()
        sys.exit(1)
