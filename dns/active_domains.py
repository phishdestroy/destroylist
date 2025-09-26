import requests
import json
import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
from tqdm import tqdm
import logging
from typing import List, Set, Dict, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

MAX_WORKERS = 500
DNS_TIMEOUT = 2.0
CUSTOM_RESOLVERS = ['1.1.1.1', '8.8.8.8', '9.9.9.9']

SOURCE_URL = "https://github.com/phishdestroy/destroylist/raw/main/list.json"
ACTIVE_DOMAINS_FILE = "active_domains.json"
DEAD_DOMAINS_FILE = "dead_domains.json"
ACTIVE_COUNT_FILE = "active_count.json"
CACHE_FILENAME = "dns_check_cache.json"
CACHE_EXPIRATION_SECONDS = 86400

try:
    import dns.resolver
    import tldextract
except ImportError:
    logging.error("Required libraries not found. Please run: pip install dnspython tqdm tldextract")
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

def fetch_source_domains(url: str) -> Set[str]:
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and 'domains' in data and isinstance(data['domains'], list):
            return {domain.lower().strip() for domain in data['domains']}
        elif isinstance(data, list):
             return {domain.lower().strip() for domain in data}
        else:
            logging.error(f"Unexpected JSON format from {url}")
            return set()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching domains from {url}: {e}")
        return set()
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from {url}: {e}")
        return set()

def load_existing_active_domains(file_path: str) -> Set[str]:
    if not os.path.exists(file_path):
        return set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return set(json.loads(content)) if content else set()
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logging.error(f"Error loading existing domains from {file_path}: {e}")
        return set()

def write_json_file(file_path: str, data: object):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Successfully saved to {file_path}")
    except Exception as e:
        logging.error(f"Error saving to {file_path}: {e}")

def set_github_action_output(name: str, value: str):
    github_output_file = os.getenv('GITHUB_OUTPUT')
    if github_output_file:
        with open(github_output_file, 'a') as f:
            f.write(f"{name}={value}\n")
    else:
        # Fallback for local execution or older Actions runners
        print(f"::set-output name={name}::{value}")

def main():
    use_cache = '--no-cache' not in sys.argv
    if not use_cache:
        logging.info("Cache ignored due to --no-cache flag.")
        if os.path.exists(CACHE_FILENAME):
            os.remove(CACHE_FILENAME)

    logging.info(f"Fetching latest domains from {SOURCE_URL}...")
    new_domains_set = fetch_source_domains(SOURCE_URL)
    if not new_domains_set:
        logging.error("Failed to fetch new domains. Exiting.")
        set_github_action_output("has_changes", "false")
        return
        
    logging.info(f"Fetched {len(new_domains_set)} unique domains from source.")

    existing_active_domains = load_existing_active_domains(ACTIVE_DOMAINS_FILE)
    logging.info(f"Loaded {len(existing_active_domains)} existing active domains.")

    candidate_domains = new_domains_set.union(existing_active_domains)
    logging.info(f"Processing {len(candidate_domains)} total unique candidate domains.")

    cache = load_cache()
    domains_for_live_check: List[str] = []
    live_domains: Set[str] = set()
    dead_domains: Set[str] = set()
    stats = Counter()
    current_time = time.time()

    for domain in candidate_domains:
        if use_cache and domain in cache and current_time - cache[domain]['timestamp'] < CACHE_EXPIRATION_SECONDS:
            status = cache[domain]['status']
            stats[f"cached_{status}"] += 1
            if status == 'live':
                live_domains.add(domain)
            else:
                dead_domains.add(domain)
        else:
            domains_for_live_check.append(domain)

    logging.info(f"Loaded {len(candidate_domains) - len(domains_for_live_check)} results from cache. Need to check {len(domains_for_live_check)} domains.")

    if domains_for_live_check:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = CUSTOM_RESOLVERS
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_domain = {executor.submit(check_domain, domain, resolver): domain for domain in domains_for_live_check}
            
            for future in tqdm(as_completed(future_to_domain), total=len(domains_for_live_check), desc="Validating domains"):
                domain, status = future.result()
                stats[status] += 1
                cache[domain] = {'status': status, 'timestamp': current_time}
                if status == 'live':
                    live_domains.add(domain)
                else:
                    dead_domains.add(domain)

    logging.info("Saving updated cache...")
    save_cache(cache)
    
    final_active_list = sorted(list(live_domains))
    final_dead_list = sorted(list(dead_domains))

    logging.info("--- DNS Validation Statistics ---")
    logging.info(f"Total Unique Candidates: {len(candidate_domains)}")
    logging.info(f"Live: {stats['live'] + stats['cached_live']} | Inactive: {len(final_dead_list)}")
    logging.info(f"  - Not Found (NXDOMAIN): {stats['nxdomain'] + stats['cached_nxdomain']}")
    logging.info(f"  - Timed Out: {stats['timeout'] + stats['cached_timeout']}")
    logging.info(f"  - Other Errors: {stats['no_answer'] + stats['error'] + stats['cached_no_answer'] + stats['cached_error']}")
    logging.info("---------------------------------")
    
    added_count = len(live_domains - existing_active_domains)
    removed_count = len(existing_active_domains - live_domains)
    has_changes = (added_count > 0 or removed_count > 0)

    logging.info(f"New active domains: {added_count}, Removed domains: {removed_count}")
    
    if has_changes:
        logging.info("Changes detected, updating files.")
        write_json_file(ACTIVE_DOMAINS_FILE, final_active_list)
        write_json_file(DEAD_DOMAINS_FILE, final_dead_list)
        
        count_data = {
            "schemaVersion": 1,
            "label": "Active Phishing Domains",
            "message": str(len(final_active_list)),
            "color": "purple"
        }
        write_json_file(ACTIVE_COUNT_FILE, count_data)
    else:
        logging.info("No changes in the active domain list. Files are up to date.")
    
    set_github_action_output("added_count", str(added_count))
    set_github_action_output("removed_count", str(removed_count))
    set_github_action_output("has_changes", str(has_changes).lower())

    logging.info("Process finished! ✅")

if __name__ == "__main__":
    main()
