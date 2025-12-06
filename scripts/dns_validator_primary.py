#!/usr/bin/env python3
import json
import logging
import os
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Set, Tuple

from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", stream=sys.stdout)

MAX_WORKERS = int(os.getenv("DNS_MAX_WORKERS", "150"))
DNS_TIMEOUT = float(os.getenv("DNS_TIMEOUT", "3.0"))
REQUEST_DELAY = float(os.getenv("DNS_REQUEST_DELAY", "0.0"))
CUSTOM_RESOLVERS = ["1.1.1.1", "8.8.8.8", "9.9.9.9", "1.0.0.1", "208.67.222.222"]
CACHE_EXPIRATION_SECONDS = 86400
MAX_RETRIES = 2

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

DNS_DIR = PROJECT_ROOT / "dns"
INPUT_FILE = PROJECT_ROOT / "list.json"
LIVE_DOMAINS_FILE = DNS_DIR / "active_domains.json"
DEAD_DOMAINS_FILE = DNS_DIR / "dead_domains.json"
COUNT_FILE = DNS_DIR / "active_count.json"
CACHE_FILENAME = DNS_DIR / "dns_check_cache.json"

try:
    import dns.resolver
    import dns.exception
except ImportError:
    logging.error("Required libraries not found. Install: pip install dnspython tqdm")
    sys.exit(1)


def load_cache() -> Dict[str, Dict]:
    if not CACHE_FILENAME.exists():
        return {}
    try:
        with open(CACHE_FILENAME, "r", encoding="utf-8") as f:
            cache = json.load(f)
            if not isinstance(cache, dict):
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
        if CACHE_FILENAME.exists():
            os.replace(str(CACHE_FILENAME), f"{CACHE_FILENAME}.bak")
        os.replace(temp_path, str(CACHE_FILENAME))
        if Path(f"{CACHE_FILENAME}.bak").exists():
            os.remove(f"{CACHE_FILENAME}.bak")
    except Exception as e:
        logging.error(f"Cache save failed: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)


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


def write_json_file(file_path: Path, data: object):
    temp_path = f"{file_path}.tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(temp_path, str(file_path))
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

    if force_all:
        logging.info("Force checking ALL domains via --force flag")

    DNS_DIR.mkdir(exist_ok=True)

    logging.info(f"Loading domains from {INPUT_FILE}...")
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        logging.error(f"Input file not found: {INPUT_FILE}")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in {INPUT_FILE}")
        sys.exit(1)

    if isinstance(data, dict):
        domains_source = data.get("domains", [])
    else:
        domains_source = data

    unique_domains = sorted(
        {
            d.lower().strip()
            for d in domains_source
            if isinstance(d, str) and d.strip() and "." in d
        }
    )

    logging.info(f"Loaded {len(unique_domains)} unique valid domains")

    prev_dead: Set[str] = set()
    if DEAD_DOMAINS_FILE.exists():
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

    cache = load_cache() if use_cache else {}
    live_domains: Set[str] = set()
    domains_to_check: List[str] = []
    stats = Counter()
    current_time = time.time()

    for domain in unique_domains:
        if not force_all and domain in prev_dead:
            stats["skipped_prev_dead"] += 1
            continue

        if force_all:
            domains_to_check.append(domain)
            continue

        if use_cache and domain in cache:
            entry = cache[domain]
            if current_time - entry.get("timestamp", 0) < CACHE_EXPIRATION_SECONDS:
                status = entry.get("status", "")
                stats[f"cached_{status}"] += 1
                if status == "live":
                    live_domains.add(domain)
                continue

        domains_to_check.append(domain)

    cached_count = len(unique_domains) - len(domains_to_check) - stats.get("skipped_prev_dead", 0)
    logging.info(
        f"Using {cached_count} cached results, skipping {stats.get('skipped_prev_dead', 0)} previously dead, "
        f"checking {len(domains_to_check)} domains"
    )

    if domains_to_check:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = CUSTOM_RESOLVERS
        resolver.timeout = DNS_TIMEOUT
        resolver.lifetime = DNS_TIMEOUT

        logging.info(f"Starting DNS validation with {MAX_WORKERS} workers...")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(check_domain, domain, resolver): domain
                for domain in domains_to_check
            }

            for future in tqdm(
                as_completed(futures),
                total=len(domains_to_check),
                desc="Validating domains",
                unit="domain",
            ):
                try:
                    domain, status = future.result()
                    stats[status] += 1
                    cache[domain] = {"status": status, "timestamp": current_time}
                    if status == "live":
                        live_domains.add(domain)
                except Exception as e:
                    logging.error(f"Future error: {e}")

    if use_cache:
        logging.info("Saving cache...")
        save_cache(cache)

    all_domains_set = set(unique_domains)
    dead_domains = all_domains_set - live_domains

    live_list = sorted(live_domains)
    dead_list = sorted(dead_domains)

    logging.info("=" * 60)
    logging.info("DNS VALIDATION STATISTICS (PRIMARY LIST)")
    logging.info("=" * 60)
    logging.info(f"Total input domains:       {len(all_domains_set)}")
    logging.info(f"Domains checked:           {len(domains_to_check)}")
    logging.info("-" * 60)

    live_count = stats["live"] + stats.get("cached_live", 0)
    logging.info(f"Live domains:              {live_count}")
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

    logging.info(f"FINAL LIVE domains:        {len(live_list)}")
    logging.info(f"FINAL DEAD domains:        {len(dead_list)}")
    logging.info("=" * 60)

    write_json_file(LIVE_DOMAINS_FILE, live_list)
    write_json_file(DEAD_DOMAINS_FILE, dead_list)

    badge_data = {
        "schemaVersion": 1,
        "label": "Active Domains (DNS)",
        "message": str(len(live_list)),
        "color": "purple" if len(live_list) > 0 else "red",
    }
    write_json_file(COUNT_FILE, badge_data)

    logging.info("=" * 60)
    logging.info("✅ Process completed successfully!")
    logging.info("=" * 60)


if __name__ == "__main__":
    main()
