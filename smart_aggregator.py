import requests
import json
import os
import hashlib
import re
from urllib.parse import urlparse

COMMUNITY_DIR = "community"
LOCAL_FILES_CONFIG = ["list.json"]
VERBOSE = True

SOURCES_CONFIG = {
    "MetaMask": {"url": "https://raw.githubusercontent.com/MetaMask/eth-phishing-detect/refs/heads/main/src/config.json", "parser": "metamask"},
    "ScamSniffer": {"url": "https://raw.githubusercontent.com/scamsniffer/scam-database/main/blacklist/domains.json", "parser": "json_list"},
    "Polkadot": {"url": "https://raw.githubusercontent.com/polkadot-js/phishing/master/all.json", "parser": "polkadot"},
    "Codeesura": {"url": "https://raw.githubusercontent.com/codeesura/Anti-phishing-extension/main/phishing-sites-list.json", "parser": "json_list"},
    "CryptoFirewall": {"url": "https://raw.githubusercontent.com/chartingshow/crypto-firewall/master/src/blacklists/domains-only.txt", "parser": "text_lines"},
    "OpenPhish": {"url": "https://raw.githubusercontent.com/openphish/public_feed/main/feed.txt", "parser": "text_lines"},
    "PhishDestroy": {"url": "https://raw.githubusercontent.com/phishdestroy/destroylist/main/list.json", "parser": "json_key_domains"},
    "SEAL": {"url": "https://raw.githubusercontent.com/security-alliance/blocklists/refs/heads/main/domain.txt", "parser": "text_lines"},
    "SPMedia_DetectedURLs": {"url": "https://raw.githubusercontent.com/spmedia/Crypto-Scam-and-Crypto-Phishing-Threat-Intel-Feed/refs/heads/main/detected_urls.txt", "parser": "urls_list"},
    "PhishingDatabase_DomainsList": {"url": "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/Phishing.Database/refs/heads/master/domains.list", "parser": "any_text_domains"},
    "Enkrypt_Blacklist": {"url": "https://raw.githubusercontent.com/enkryptcom/phishing-detect/refs/heads/main/dist/lists/blacklist.json", "parser": "json_list"}
}

OUTPUT_FILENAME = os.path.join(COMMUNITY_DIR, "blocklist.json")
STATE_FILENAME = os.path.join(COMMUNITY_DIR, "state.json")
BADGE_FILENAME = os.path.join(COMMUNITY_DIR, "count.json")
COMMIT_MSG_FILENAME = os.path.join(COMMUNITY_DIR, "commit_message.txt")

STRICT_DOMAIN_RE = re.compile(r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b", re.IGNORECASE)
IPV4_RE = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")

def log(msg: str) -> None:
    if VERBOSE:
        print(msg, flush=True)

def is_valid_domain(d: str) -> bool:
    if not d or len(d) > 253:
        return False
    parts = d.split('.')
    if len(parts) < 2:
        return False
    if not re.fullmatch(r"[a-z]{2,63}", parts[-1], re.IGNORECASE):
        return False
    for label in parts:
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label, re.IGNORECASE):
            return False
    return True

def normalize_domain(d: str) -> str:
    d = d.strip().strip('.').lower()
    if IPV4_RE.fullmatch(d):
        return ""
    return d if is_valid_domain(d) else ""

def add_norm(dst: set, candidate: str) -> None:
    nd = normalize_domain(candidate)
    if nd:
        dst.add(nd)

def clean_hosts_ips(text: str) -> str:
    text = re.sub(r"(^|\s)(?:0\.0\.0\.0|127\.0\.0\.1|::1)\s*", " ", text)
    text = re.sub(r"(?:0\.0\.0\.0|127\.0\.0\.1|::1)(?=[A-Za-z0-9])", " ", text)
    return text

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
        return set()
    except Exception:
        return set()

def parse_json_list(content: str) -> set:
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return {normalize_domain(x) for x in data if isinstance(x, str) and normalize_domain(x)}
        return set()
    except Exception:
        return set()

def parse_json_key_domains(content: str) -> set:
    try:
        data = json.loads(content)
        arr = data.get("domains", [])
        if isinstance(arr, list):
            return {normalize_domain(x) for x in arr if isinstance(x, str) and normalize_domain(x)}
        return set()
    except Exception:
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
        if not line or line.startswith(('#', '!', ';')):
            continue
        if line.startswith(('0.0.0.0', '127\.0\.0\.1', '::1')):
            line = clean_hosts_ips(line)
        if line.startswith('||'):
            line = line[2:]
        if '^' in line:
            line = line.split('^', 1)[0]
        if '$' in line:
            line = line.split('$', 1)[0]
        if '://' in line or line.startswith(('www.', 'ftp.', 'http.', 'https.')):
            try:
                host = urlparse(line if '://' in line else 'http://' + line).hostname
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
        if not s or s.startswith(('#', '!', ';')):
            continue
        try:
            host = urlparse(s if '://' in s else 'http://' + s).hostname
            if host:
                add_norm(out, host)
                continue
        except Exception:
            pass
        out.update(extract_domains_from_text(s))
    return out

def parse_any_text_domains(content: str) -> set:
    return extract_domains_from_text(content)

PARSERS = {
    "metamask": parse_metamask,
    "polkadot": parse_polkadot,
    "json_list": parse_json_list,
    "text_lines": parse_text_lines,
    "urls_list": parse_urls_list,
    "any_text_domains": parse_any_text_domains,
    "json_key_domains": parse_json_key_domains,
}

def load_state() -> dict:
    if not os.path.exists(STATE_FILENAME):
        return {}
    try:
        with open(STATE_FILENAME, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state: dict) -> None:
    with open(STATE_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

def fetch_content(url: str) -> str | None:
    try:
        r = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0 Aggregator/2.0'})
        r.raise_for_status()
        return r.text
    except Exception:
        return None

def update_badge_json(count: int) -> None:
    badge = {"schemaVersion": 1, "label": "Community Domains", "message": str(count), "color": "blue"}
    with open(BADGE_FILENAME, 'w', encoding='utf-8', newline='') as f:
        json.dump(badge, f, separators=(",", ":"))

def main() -> None:
    log("[start] community aggregation")
    os.makedirs(COMMUNITY_DIR, exist_ok=True)
    last_state = load_state()
    new_state: dict = {}
    all_domains: set[str] = set()
    changes: list[dict] = []

    log("[local] loading local JSON files")
    for file_path in LOCAL_FILES_CONFIG:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    local_domains = json.load(f)
                    if isinstance(local_domains, list):
                        before = len(all_domains)
                        for d in local_domains:
                            add_norm(all_domains, d)
                        added_count = len(all_domains) - before
                        log(f"  + Added: {added_count} from {file_path}")
        except Exception:
            log(f"  ! skip {file_path}")

    log("[remote] fetching sources")
    for name, cfg in SOURCES_CONFIG.items():
        url = cfg['url']
        parser_func = PARSERS.get(cfg['parser'])
        log(f"-> {name}: {url}")
        content = fetch_content(url)
        domains, content_hash = set(), None
        
        before_add = len(all_domains)
        
        if content and parser_func:
            domains = parser_func(content)
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            all_domains.update(domains)
            added_count = len(all_domains) - before_add
            log(f"    Parsed: {len(domains)}, Added new unique: {added_count}")
        else:
            domains = set(last_state.get(name, {}).get('domains', []))
            content_hash = last_state.get(name, {}).get('hash')
            all_domains.update(domains)
            added_count = len(all_domains) - before_add
            log(f"    fallback (cached): {len(domains)} domains, Added new unique: {added_count}")

        last_hash = last_state.get(name, {}).get('hash')
        if content_hash != last_hash and content is not None:
            last_count = last_state.get(name, {}).get('count', 0)
            diff = len(domains) - last_count
            changes.append({"name": name, "diff": diff, "sign": '+' if diff >= 0 else ''})

        new_state[name] = {'hash': content_hash, 'count': len(domains), 'domains': sorted(list(domains))}

    last_total = last_state.get("total_count", 0)
    if len(all_domains) == last_total and not changes:
        log("[no-op] no changes detected")
        return

    new_state["total_count"] = len(all_domains)
    commit_title = "Update community blocklist"
    commit_body = f"Total domains: {len(all_domains)}\n\n"
    if changes:
        title_parts = [f"{c['sign']}{c['diff']} {c['name']}" for c in changes]
        commit_title = f"Sync: {', '.join(title_parts)}"
        commit_body += "Changes:\n" + "\n".join([f"- {c['name']}: {c['sign']}{c['diff']}" for c in changes])

    with open(COMMIT_MSG_FILENAME, 'w', encoding='utf-8') as f:
        f.write(commit_title + "\n\n" + commit_body)
    log(f"[write] {COMMIT_MSG_FILENAME}")

    sorted_domains = sorted(list(all_domains))
    with open(OUTPUT_FILENAME, 'w', encoding='utf-8', newline='') as f:
        json.dump(sorted_domains, f, indent=2)
    log(f"[write] {OUTPUT_FILENAME} (count={len(sorted_domains)})")

    save_state(new_state)
    update_badge_json(len(all_domains))
    log(f"[write] {STATE_FILENAME}")
    log(f"[write] {BADGE_FILENAME} — message={len(all_domains)}")
    log("[done] community aggregation complete")

if __name__ == "__main__":
    main()

