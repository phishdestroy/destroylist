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

MAX_WORKERS = 100
DNS_TIMEOUT = 3.0
CUSTOM_RESOLVERS = ['1.1.1.1', '8.8.8.8', '9.9.9.9', '208.67.222.222']
MAX_RETRIES = 2

SOURCE_URL = "https://github.com/phishdestroy/destroylist/raw/main/list.json"
ACTIVE_DOMAINS_FILE = "active_domains.json"
DEAD_DOMAINS_FILE = "dead_domains.json"
ACTIVE_COUNT_FILE = "active_count.json"
CACHE_FILENAME = "dns_check_cache.json"
CACHE_EXPIRATION_SECONDS = 86400

try:
    import dns.resolver
except ImportError:
    logging.error("dnspython not found. Install: pip install dnspython tqdm")
    sys.exit(1)

def load_cache() -> Dict[str, Dict]:
    if not os.path.exists(CACHE_FILENAME):
        return {}
    try:
        with open(CACHE_FILENAME, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_cache(cache: Dict[str, Dict]):
    try:
        with open(CACHE_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        logging.error(f"Cache save failed: {e}")

def check_domain(domain: str, resolver: dns.resolver.Resolver, retry: int = 0) -> Tuple[str, str]:
    try:
        resolver.resolve(domain, 'A', lifetime=DNS_TIMEOUT)
        return (domain, 'live')
    except dns.resolver.NXDOMAIN:
        return (domain, 'nxdomain')
    except (dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        try:
            resolver.resolve(domain, 'AAAA', lifetime=DNS_TIMEOUT)
            return (domain, 'live')
        except:
            return (domain, 'no_answer')
    except dns.exception.Timeout:
        if retry < MAX_RETRIES:
            time.sleep(0.5)
            return check_domain(domain, resolver, retry + 1)
        return (domain, 'timeout')
    except:
        return (domain, 'error')

def fetch_domains(url: str) -> Set[str]:
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        
        if isinstance(data, dict) and 'domains' in data:
            domains = data['domains']
        elif isinstance(data, list):
            domains = data
        else:
            logging.error("Bad JSON format")
            return set()
        
        return {d.lower().strip() for d in domains if d.strip() and '.' in d}
    except Exception as e:
        logging.error(f"Fetch error: {e}")
        return set()

def load_file(path: str) -> Set[str]:
    if not os.path.exists(path):
        return set()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {d.lower().strip() for d in data if d.strip()}
    except:
        return set()

def save_file(path: str, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Saved: {path}")
    except Exception as e:
        logging.error(f"Save error {path}: {e}")

def set_output(name: str, value: str):
    out = os.getenv('GITHUB_OUTPUT')
    if out:
        with open(out, 'a') as f:
            f.write(f"{name}={value}\n")
    else:
        print(f"::set-output name={name}::{value}")

def main():
    no_cache = '--no-cache' in sys.argv
    force_all = '--force' in sys.argv
    
    logging.info(f"Fetching from {SOURCE_URL}...")
    source_domains = fetch_domains(SOURCE_URL)
    
    if not source_domains:
        logging.error("No domains fetched!")
        set_output("has_changes", "false")
        return
    
    logging.info(f"Source domains: {len(source_domains)}")
    
    existing_active = load_file(ACTIVE_DOMAINS_FILE)
    logging.info(f"Existing active: {len(existing_active)}")
    
    # Combine all domains
    all_domains = source_domains | existing_active
    logging.info(f"Total unique: {len(all_domains)}")
    
    # Load cache
    cache = {} if no_cache else load_cache()
    now = time.time()
    
    # Determine what to check
    to_check = []
    live = set()
    dead = set()
    stats = Counter()
    
    for domain in all_domains:
        # Always check new domains from source
        if domain in source_domains and domain not in existing_active:
            to_check.append(domain)
            continue
        
        # Force all if flag set
        if force_all:
            to_check.append(domain)
            continue
        
        # Use cache if valid
        if domain in cache:
            entry = cache[domain]
            if now - entry.get('timestamp', 0) < CACHE_EXPIRATION_SECONDS:
                status = entry['status']
                stats[f"cached_{status}"] += 1
                if status == 'live':
                    live.add(domain)
                else:
                    dead.add(domain)
                continue
        
        # Otherwise check it
        to_check.append(domain)
    
    logging.info(f"Cached: {len(all_domains) - len(to_check)}, Checking: {len(to_check)}")
    
    # Run DNS checks
    if to_check:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = CUSTOM_RESOLVERS
        resolver.timeout = DNS_TIMEOUT
        resolver.lifetime = DNS_TIMEOUT
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
            futures = {ex.submit(check_domain, d, resolver): d for d in to_check}
            
            for future in tqdm(as_completed(futures), total=len(to_check), desc="DNS checks"):
                domain, status = future.result()
                stats[status] += 1
                cache[domain] = {'status': status, 'timestamp': now}
                
                if status == 'live':
                    live.add(domain)
                else:
                    dead.add(domain)
    
    # Save cache
    if not no_cache:
        save_cache(cache)
    
    # Results
    active_list = sorted(live)
    dead_list = sorted(dead)
    
    logging.info("=" * 50)
    logging.info(f"Total:    {len(all_domains)}")
    logging.info(f"Active:   {len(active_list)}")
    logging.info(f"Dead:     {len(dead_list)}")
    logging.info("-" * 50)
    logging.info(f"Live:     {stats['live'] + stats.get('cached_live', 0)}")
    logging.info(f"NXDOMAIN: {stats['nxdomain'] + stats.get('cached_nxdomain', 0)}")
    logging.info(f"Timeout:  {stats['timeout'] + stats.get('cached_timeout', 0)}")
    logging.info(f"NoAns:    {stats['no_answer'] + stats.get('cached_no_answer', 0)}")
    logging.info(f"Error:    {stats['error'] + stats.get('cached_error', 0)}")
    logging.info("=" * 50)
    
    # Changes
    added = len(live - existing_active)
    removed = len(existing_active - live)
    has_changes = added > 0 or removed > 0
    
    logging.info(f"Added:   {added}")
    logging.info(f"Removed: {removed}")
    
    if has_changes:
        logging.info("CHANGES DETECTED - updating files")
        
        save_file(ACTIVE_DOMAINS_FILE, active_list)
        save_file(DEAD_DOMAINS_FILE, dead_list)
        
        badge = {
            "schemaVersion": 1,
            "label": "Active Phishing Domains",
            "message": str(len(active_list)),
            "color": "red"
        }
        save_file(ACTIVE_COUNT_FILE, badge)
        
        # Show samples
        if added > 0:
            samples = list(live - existing_active)[:5]
            logging.info(f"Sample added: {', '.join(samples)}")
        if removed > 0:
            samples = list(existing_active - live)[:5]
            logging.info(f"Sample removed: {', '.join(samples)}")
    else:
        logging.info("NO CHANGES")
    
    set_output("added_count", str(added))
    set_output("removed_count", str(removed))
    set_output("has_changes", str(has_changes).lower())
    set_output("total_active", str(len(active_list)))
    
    logging.info("=" * 50)
    logging.info("✅ DONE")

if __name__ == "__main__":
    main()