import json
import logging
import os
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Set, Tuple

from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

# --- Configuration ---
MAX_WORKERS = 500
DNS_TIMEOUT = 2.0
CUSTOM_RESOLVERS = ['1.1.1.1', '8.8.8.8', '9.9.9.9', '1.0.0.1']
CACHE_EXPIRATION_SECONDS = 86400  # 24 hours

HOSTING_PLATFORM_SUFFIXES = (
    '.pages.dev', '.workers.dev', '.vercel.app', '.netlify.app',
    '.onrender.com', '.replit.dev', '.glitch.me', '.github.io',
    '.gitlab.io', '.webflow.io', '.surge.sh', '.firebaseapp.com', '.web.app'
)

# --- Smart Pathing Logic ---
# Determines the project root directory regardless of where the script is run from.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(SCRIPT_DIR).lower() == 'community':
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
else:
    PROJECT_ROOT = SCRIPT_DIR

# --- File Paths (Defined from project root) ---
COMMUNITY_DIR = os.path.join(PROJECT_ROOT, "community")
INPUT_FILE = os.path.join(COMMUNITY_DIR, "blocklist.json")
LIVE_DOMAINS_FILE = os.path.join(COMMUNITY_DIR, "live_blocklist.json")
DEAD_DOMAINS_FILE = os.path.join(COMMUNITY_DIR, "dead_blocklist.json")
LIVE_COUNT_FILE = os.path.join(COMMUNITY_DIR, "live_count.json")
CACHE_FILENAME = os.path.join(COMMUNITY_DIR, "dns_cache.json")


try:
    import dns.resolver
    import tldextract
except ImportError:
    logging.error("Required libraries not found. Please run: pip install dnspython tqdm tldextract")
    sys.exit(1)

def get_registered_domain(domain: str) -> str:
    """Extracts the registrable part of the domain (e.g., 'google.co.uk')."""
    ext = tldextract.extract(domain)
    if not ext.suffix:
        return domain
    return f"{ext.domain}.{ext.suffix}"

def load_cache() -> Dict[str, Dict]:
    if not os.path.exists(CACHE_FILENAME):
        return {}
    try:
        with open(CACHE_FILENAME, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_cache(cache: Dict[str, Dict]):
    try:
        with open(CACHE_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save cache: {e}")

def check_domain(domain: str, resolver: dns.resolver.Resolver) -> Tuple[str, str]:
    """Checks a single domain and returns its status."""
    try:
        resolver.resolve(domain, 'A', lifetime=DNS_TIMEOUT)
        return (domain, 'live')
    except dns.resolver.NXDOMAIN:
        return (domain, 'nxdomain')
    except (dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return (domain, 'no_answer')
    except dns.exception.Timeout:
        return (domain, 'timeout')
    except Exception:
        return (domain, 'error')

def write_json_file(file_path: str, data: object):
    """Writes data to a JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Successfully saved to {file_path}")
    except Exception as e:
        logging.error(f"Error saving to {file_path}: {e}")

def main():
    use_cache = '--no-cache' not in sys.argv
    if not use_cache:
        logging.info("Cache ignored due to --no-cache flag. Performing a full check.")
        if os.path.exists(CACHE_FILENAME):
            try:
                os.remove(CACHE_FILENAME)
            except OSError as e:
                logging.error(f"Error removing cache file: {e}")

    if not os.path.exists(COMMUNITY_DIR):
        os.makedirs(COMMUNITY_DIR)

    logging.info(f"Loading domains from {INPUT_FILE}...")
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            domains = json.load(f)
    except FileNotFoundError:
        logging.error(f"Error: Input file not found at {INPUT_FILE}")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error(f"Error: Could not decode JSON from {INPUT_FILE}")
        sys.exit(1)

    unique_input_domains = sorted(list({d.lower().strip() for d in domains if isinstance(d, str)}))
    logging.info(f"Loaded {len(unique_input_domains)} unique domains to process.")

    platform_domains = {d for d in unique_input_domains if d.endswith(HOSTING_PLATFORM_SUFFIXES)}
    domains_to_check = [d for d in unique_input_domains if d not in platform_domains]
    
    logging.info(f"Found {len(platform_domains)} domains on always-on platforms (auto-included).")
    
    registered_domains_map: Dict[str, List[str]] = {}
    for domain in domains_to_check:
        root = get_registered_domain(domain)
        if root not in registered_domains_map:
            registered_domains_map[root] = []
        registered_domains_map[root].append(domain)
    
    unique_roots_to_check = list(registered_domains_map.keys())
    logging.info(f"Extracted {len(unique_roots_to_check)} unique registered domains for validation.")

    cache = load_cache()
    live_root_domains: Set[str] = set()
    roots_for_live_check: List[str] = []
    stats = Counter()
    current_time = time.time()

    logging.info("Checking cache...")
    for root in unique_roots_to_check:
        if use_cache and root in cache and current_time - cache[root]['timestamp'] < CACHE_EXPIRATION_SECONDS:
            status = cache[root]['status']
            stats[f"cached_{status}"] += 1
            if status == 'live':
                live_root_domains.add(root)
        else:
            roots_for_live_check.append(root)

    checked_from_cache = len(unique_roots_to_check) - len(roots_for_live_check)
    logging.info(f"Loaded {checked_from_cache} results from cache. Need to check {len(roots_for_live_check)} domains.")

    if roots_for_live_check:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = CUSTOM_RESOLVERS
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_domain = {executor.submit(check_domain, root, resolver): root for root in roots_for_live_check}
            
            for future in tqdm(as_completed(future_to_domain), total=len(roots_for_live_check), desc="Validating registered domains"):
                root, status = future.result()
                stats[status] += 1
                cache[root] = {'status': status, 'timestamp': current_time}
                if status == 'live':
                    live_root_domains.add(root)

    logging.info("Saving updated cache...")
    save_cache(cache)

    final_live_domains: Set[str] = set(platform_domains)
    for root in live_root_domains:
        final_live_domains.update(registered_domains_map.get(root, []))
        
    all_domains_set = set(unique_input_domains)
    final_dead_domains = all_domains_set - final_live_domains

    final_live_list = sorted(list(final_live_domains))
    final_dead_list = sorted(list(final_dead_domains))

    logging.info("--- DNS Validation Statistics ---")
    logging.info(f"Total Unique Input Domains:    {len(all_domains_set)}")
    live_count = stats['live'] + stats['cached_live']
    logging.info(f"Live Registered Domains:       {live_count} (Checked: {stats['live']}, Cached: {stats['cached_live']})")
    nx_count = stats['nxdomain'] + stats['cached_nxdomain']
    logging.info(f"  - Not Found (NXDOMAIN):      {nx_count}")
    timeout_count = stats['timeout'] + stats['cached_timeout']
    logging.info(f"  - Timed Out:                 {timeout_count}")
    other_errors = stats['no_answer'] + stats['error'] + stats['no_nameservers'] + \
                   stats['cached_no_answer'] + stats['cached_error'] + stats['cached_no_nameservers']
    logging.info(f"  - Other Errors:              {other_errors}")
    logging.info("---------------------------------")
    logging.info(f"Final list (Live): {len(final_live_list)} domains (including subdomains and platforms).")
    logging.info(f"Final list (Inactive): {len(final_dead_list)} domains.")

    write_json_file(LIVE_DOMAINS_FILE, final_live_list)
    write_json_file(DEAD_DOMAINS_FILE, final_dead_list)

    count_badge_data = {
        "schemaVersion": 1,
        "label": "Live Domains",
        "message": str(len(final_live_list)),
        "color": "brightgreen"
    }
    write_json_file(LIVE_COUNT_FILE, count_badge_data)
    
    logging.info("Process finished! ✅")

if __name__ == "__main__":
    main()

