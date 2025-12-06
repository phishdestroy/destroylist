import json
import logging
import os
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Set, Tuple

from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", stream=sys.stdout)

MAX_WORKERS = int(os.getenv("DNS_MAX_WORKERS", "150"))
DNS_TIMEOUT = float(os.getenv("DNS_TIMEOUT", "3.0"))
REQUEST_DELAY = float(os.getenv("DNS_REQUEST_DELAY", "0.0"))
CUSTOM_RESOLVERS = ["1.1.1.1", "8.8.8.8", "9.9.9.9", "1.0.0.1", "208.67.222.222"]
CACHE_EXPIRATION_SECONDS = 86400
MAX_RETRIES = 2

HOSTING_PLATFORM_SUFFIXES = (
    ".pages.dev",
    ".workers.dev",
    ".vercel.app",
    ".netlify.app",
    ".onrender.com",
    ".replit.dev",
    ".glitch.me",
    ".github.io",
    ".gitlab.io",
    ".webflow.io",
    ".surge.sh",
    ".firebaseapp.com",
    ".web.app",
    ".azurewebsites.net",
    ".herokuapp.com",
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(SCRIPT_DIR).lower() == "scripts":
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
else:
    PROJECT_ROOT = SCRIPT_DIR

COMMUNITY_DIR = os.path.join(PROJECT_ROOT, "community")
INPUT_FILE = os.path.join(COMMUNITY_DIR, "blocklist.json")
LIVE_DOMAINS_FILE = os.path.join(COMMUNITY_DIR, "live_blocklist.json")
DEAD_DOMAINS_FILE = os.path.join(COMMUNITY_DIR, "dead_blocklist.json")
LIVE_COUNT_FILE = os.path.join(COMMUNITY_DIR, "live_count.json")
CACHE_FILENAME = os.path.join(COMMUNITY_DIR, "dns_cache.json")

try:
    import dns.resolver
    import dns.exception
    import tldextract
except ImportError:
    logging.error("Required libraries not found. Install: pip install dnspython tqdm tldextract")
    sys.exit(1)


def get_registered_domain(domain: str) -> str:
    ext = tldextract.extract(domain)
    if not ext.suffix:
        return domain
    return f"{ext.domain}.{ext.suffix}"


def load_cache() -> Dict[str, Dict]:
    if not os.path.exists(CACHE_FILENAME):
        return {}
    try:
        with open(CACHE_FILENAME, "r", encoding="utf-8") as f:
            cache = json.load(f)
            if not isinstance(cache, dict):
                logging.warning("Invalid cache format, starting fresh")
                return {}
            return cache
    except Exception as e:
        logging.warning(f"Cache load error: {e}, starting fresh")
        return {}


def save_cache(cache: Dict[str, Dict]):
    try:
        temp_path = f"{CACHE_FILENAME}.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
        if os.path.exists(CACHE_FILENAME):
            os.replace(CACHE_FILENAME, f"{CACHE_FILENAME}.bak")
        os.replace(temp_path, CACHE_FILENAME)
        if os.path.exists(f"{CACHE_FILENAME}.bak"):
            os.remove(f"{CACHE_FILENAME}.bak")
    except Exception as e:
        logging.error(f"Cache save failed: {e}")


def check_domain(domain: str, resolver: dns.resolver.Resolver, retry: int = 0) -> Tuple[str, str]:
    if REQUEST_DELAY > 0:
        time.sleep(REQUEST_DELAY)
    try:
        resolver.resolve(domain, "A", lifetime=DNS_TIMEOUT)
        return domain, "live"
    except dns.resolver.NXDOMAIN:
        return domain, "nxdomain"
    except (dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        try:
            resolver.resolve(domain, "AAAA", lifetime=DNS_TIMEOUT)
            return domain, "live"
        except Exception:
            return domain, "no_answer"
    except dns.exception.Timeout:
        if retry < MAX_RETRIES:
            time.sleep(0.3)
            return check_domain(domain, resolver, retry + 1)
        return domain, "timeout"
    except Exception:
        return domain, "error"


def write_json_file(file_path: str, data: object):
    temp_path = f"{file_path}.tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(temp_path, file_path)
        logging.info(f"Saved: {file_path}")
    except Exception as e:
        logging.error(f"Save error {file_path}: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)


def main():
    use_cache = "--no-cache" not in sys.argv
    force_all = "--force" in sys.argv

    if not use_cache:
        logging.info("Cache disabled via --no-cache flag")
        if os.path.exists(CACHE_FILENAME):
            try:
                os.remove(CACHE_FILENAME)
            except OSError as e:
                logging.error(f"Error removing cache: {e}")

    if force_all:
        logging.info("Force checking ALL domains via --force flag")

    os.makedirs(COMMUNITY_DIR, exist_ok=True)

    logging.info(f"Loading domains from {INPUT_FILE}...")
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            domains = json.load(f)
    except FileNotFoundError:
        logging.error(f"Input file not found: {INPUT_FILE}")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in {INPUT_FILE}")
        sys.exit(1)

    unique_input_domains = sorted(
        {
            d.lower().strip()
            for d in domains
            if isinstance(d, str) and d.strip() and "." in d
        }
    )

    logging.info(f"Loaded {len(unique_input_domains)} unique valid domains")

    prev_dead: Set[str] = set()
    if os.path.exists(DEAD_DOMAINS_FILE):
        try:
            with open(DEAD_DOMAINS_FILE, "r", encoding="utf-8") as f:
                ddata = json.load(f)
            if isinstance(ddata, list):
                prev_dead = {
                    d.lower().strip()
                    for d in ddata
                    if isinstance(d, str) and d.strip()
                }
            elif isinstance(ddata, dict):
                prev_dead = {
                    d.lower().strip()
                    for d in ddata.get("domains", [])
                    if isinstance(d, str) and d.strip()
                }
            logging.info(f"Loaded {len(prev_dead)} previously dead domains")
        except Exception as e:
            logging.warning(f"Failed to load previous dead domains: {e}")

    platform_domains = {d for d in unique_input_domains if d.endswith(HOSTING_PLATFORM_SUFFIXES)}
    domains_to_check = [d for d in unique_input_domains if d not in platform_domains]

    logging.info(f"Platform domains (always live): {len(platform_domains)}")
    logging.info(f"Domains to validate (before dead-skip): {len(domains_to_check)}")

    cache = load_cache() if use_cache else {}
    live_root_domains: Set[str] = set()
    stats = Counter()
    current_time = time.time()

    registered_domains_map: Dict[str, List[str]] = {}
    for domain in domains_to_check:
        if not force_all and domain in prev_dead:
            stats["skipped_prev_dead"] += 1
            continue
        root = get_registered_domain(domain)
        registered_domains_map.setdefault(root, []).append(domain)

    unique_roots_to_check = list(registered_domains_map.keys())
    logging.info(f"Unique root domains to check: {len(unique_roots_to_check)}")

    roots_for_live_check: List[str] = []

    for root in unique_roots_to_check:
        if force_all:
            roots_for_live_check.append(root)
            continue

        if use_cache and root in cache:
            entry = cache[root]
            if current_time - entry.get("timestamp", 0) < CACHE_EXPIRATION_SECONDS:
                status = entry.get("status", "")
                stats[f"cached_{status}"] += 1
                if status == "live":
                    live_root_domains.add(root)
                continue

        roots_for_live_check.append(root)

    cached_count = len(unique_roots_to_check) - len(roots_for_live_check)
    logging.info(
        f"Using {cached_count} cached results, skipping {stats.get('skipped_prev_dead', 0)} previously dead, "
        f"checking {len(roots_for_live_check)} root domains"
    )

    if roots_for_live_check:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = CUSTOM_RESOLVERS
        resolver.timeout = DNS_TIMEOUT
        resolver.lifetime = DNS_TIMEOUT

        logging.info(f"Starting DNS validation with {MAX_WORKERS} workers...")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(check_domain, root, resolver): root
                for root in roots_for_live_check
            }

            for future in tqdm(
                as_completed(futures),
                total=len(roots_for_live_check),
                desc="Validating root domains",
                unit="domain",
            ):
                try:
                    root, status = future.result()
                    stats[status] += 1
                    cache[root] = {"status": status, "timestamp": current_time}
                    if status == "live":
                        live_root_domains.add(root)
                except Exception as e:
                    logging.error(f"Future error: {e}")

    if use_cache:
        logging.info("Saving cache...")
        save_cache(cache)

    final_live_domains: Set[str] = set(platform_domains)
    for root in live_root_domains:
        final_live_domains.update(registered_domains_map.get(root, []))

    final_live_domains -= prev_dead

    all_domains_set = set(unique_input_domains)
    final_dead_domains = all_domains_set - final_live_domains

    final_live_list = sorted(final_live_domains)
    final_dead_list = sorted(final_dead_domains)

    logging.info("=" * 60)
    logging.info("DNS VALIDATION STATISTICS (COMMUNITY)")
    logging.info("=" * 60)
    logging.info(f"Total input domains:       {len(all_domains_set)}")
    logging.info(f"Platform domains (auto):   {len(platform_domains)}")
    logging.info(f"Root domains checked:      {len(unique_roots_to_check)}")
    logging.info("-" * 60)

    live_count = stats["live"] + stats.get("cached_live", 0)
    logging.info(f"Live root domains:         {live_count}")
    logging.info(f"  - Fresh checks:          {stats['live']}")
    logging.info(f"  - From cache:            {stats.get('cached_live', 0)}")

    logging.info("-" * 60)
    nx_count = stats["nxdomain"] + stats.get("cached_nxdomain", 0)
    logging.info(f"NXDOMAIN:                  {nx_count}")

    timeout_count = stats["timeout"] + stats.get("cached_timeout", 0)
    logging.info(f"Timeout:                   {timeout_count}")

    no_answer = stats["no_answer"] + stats.get("cached_no_answer", 0)
    logging.info(f"No Answer:                 {no_answer}")

    errors = stats["error"] + stats.get("cached_error", 0)
    logging.info(f"Errors:                    {errors}")

    logging.info(f"Skipped previously dead:   {stats.get('skipped_prev_dead', 0)}")
    logging.info("=" * 60)

    logging.info(f"FINAL LIVE domains:        {len(final_live_list)}")
    logging.info(f"FINAL DEAD domains:        {len(final_dead_list)}")
    logging.info("=" * 60)

    write_json_file(LIVE_DOMAINS_FILE, final_live_list)
    write_json_file(DEAD_DOMAINS_FILE, final_dead_list)

    badge_data = {
        "schemaVersion": 1,
        "label": "Live Domains (Community)",
        "message": str(len(final_live_list)),
        "color": "brightgreen" if len(final_live_list) > 0 else "red",
    }
    write_json_file(LIVE_COUNT_FILE, badge_data)

    logging.info("=" * 60)
    logging.info("✅ Process completed successfully!")
    logging.info("=" * 60)


if __name__ == "__main__":
    main()
