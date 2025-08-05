import requests
import json
import os
from datetime import datetime
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

SOURCE_URL = "https://github.com/phishdestroy/destroylist/raw/main/list.json"

ACTIVE_DOMAINS_FILE = "active_domains.json"
ACTIVE_COUNT_FILE = "active_count.json"

MAX_WORKERS = 20
DNS_TIMEOUT = 5

def extract_domain(url_or_domain):
    try:
        parsed_url = urlparse(url_or_domain)
        domain = parsed_url.netloc
        if not domain:
            domain = parsed_url.path
        
        domain = domain.split(':')[0]
        domain = domain.split('/')[0].split('?')[0].split('#')[0]
        
        return domain.lower().strip()
    except Exception:
        return url_or_domain.lower().strip()

def fetch_domains(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching domains from {url}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {url}: {e}")
        return None

def load_existing_domains(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return set()
                return set(json.loads(content))
        except json.JSONDecodeError as e:
            print(f"Error decoding existing JSON from {file_path}: {e}")
            return set()
        except Exception as e:
            print(f"Error loading existing domains from {file_path}: {e}")
            return set()
    return set()

def save_domains(file_path, domains):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sorted(list(domains)), f, indent=2)
        print(f"Saved {len(domains)} domains to {file_path}")
    except Exception as e:
        print(f"Error saving domains to {file_path}: {e}")

def save_count(file_path, count):
    try:
        data = {
            "schemaVersion": 1,
            "label": "Active Domains",
            "message": str(count),
            "color": "purple"
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Saved count {count} to {file_path}")
    except Exception as e:
        print(f"Error saving count to {file_path}: {e}")

def check_resolvable_wrapper(domain, timeout):
    return domain, is_domain_resolvable(domain, timeout)

def is_domain_resolvable(domain, timeout):
    if not domain:
        return False
    try:
        original_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)
        socket.gethostbyname(domain)
        socket.setdefaulttimeout(original_timeout)
        return True
    except socket.gaierror:
        socket.setdefaulttimeout(original_timeout)
        return False
    except Exception as e:
        socket.setdefaulttimeout(original_timeout)
        return False

def main():
    print(f"[{datetime.now()}] Starting DNS active domain update...")

    new_domains_list_raw = fetch_domains(SOURCE_URL)
    if new_domains_list_raw is None:
        print("Failed to fetch new domains. Exiting.")
        # Set outputs for GitHub Actions even on failure
        print(f"::set-output name=added_count::0")
        print(f"::set-output name=removed_count::0")
        print(f"::set-output name=has_changes::false")
        return

    new_domains_set = set()
    for item in new_domains_list_raw:
        domain = extract_domain(item)
        if domain:
            new_domains_set.add(domain)

    print(f"Fetched {len(new_domains_set)} unique domains from source after extraction.")

    existing_active_domains = load_existing_domains(ACTIVE_DOMAINS_FILE)
    print(f"Loaded {len(existing_active_domains)} existing active domains.")

    candidate_active_domains = new_domains_set.union(existing_active_domains)
    print(f"Total unique candidate domains (before DNS check): {len(candidate_active_domains)}")

    resolvable_domains = set()
    print(f"Performing concurrent DNS checks on {len(candidate_active_domains)} domains with {MAX_WORKERS} workers...")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_domain = {executor.submit(check_resolvable_wrapper, domain, DNS_TIMEOUT): domain for domain in candidate_active_domains}
        
        checked_count = 0
        for future in as_completed(future_to_domain):
            domain, is_resolvable = future.result()
            if is_resolvable:
                resolvable_domains.add(domain)
            
            checked_count += 1
            if checked_count % 100 == 0:
                print(f"  Checked {checked_count}/{len(candidate_active_domains)} domains...")

    updated_active_domains = resolvable_domains
    print(f"Finished DNS checks. {len(updated_active_domains)} domains are currently DNS active.")

    domains_changed = False

    desired_domains_content = json.dumps(sorted(list(updated_active_domains)), indent=2)
    desired_count_data = {
        "schemaVersion": 1,
        "label": "Active Domains",
        "message": str(len(updated_active_domains)),
        "color": "purple"
    }
    desired_count_content = json.dumps(desired_count_data, indent=2)

    current_domains_content = ""
    if os.path.exists(ACTIVE_DOMAINS_FILE):
        try:
            with open(ACTIVE_DOMAINS_FILE, 'r', encoding='utf-8') as f:
                current_domains_content = f.read()
        except Exception:
            pass

    if current_domains_content != desired_domains_content:
        domains_changed = True
        print(f"Content of {ACTIVE_DOMAINS_FILE} has changed or file is new. Updating.")
        save_domains(ACTIVE_DOMAINS_FILE, updated_active_domains)

    current_count_content = ""
    if os.path.exists(ACTIVE_COUNT_FILE):
        try:
            with open(ACTIVE_COUNT_FILE, 'r', encoding='utf-8') as f:
                current_count_content = f.read()
        except Exception:
            pass

    if current_count_content != desired_count_content:
        domains_changed = True
        print(f"Content of {ACTIVE_COUNT_FILE} has changed or file is new. Updating.")
        save_count(ACTIVE_COUNT_FILE, len(updated_active_domains))

    # Calculate added and removed domains for the commit message
    added_count = len(updated_active_domains - existing_active_domains)
    removed_count = len(existing_active_domains - updated_active_domains)

    print(f"Added domains: {added_count}, Removed domains: {removed_count}")
    print(f"Has changes to commit: {domains_changed}")

    # Set outputs for GitHub Actions
    print(f"::set-output name=added_count::{added_count}")
    print(f"::set-output name=removed_count::{removed_count}")
    print(f"::set-output name=has_changes::{'true' if domains_changed else 'false'}")

    if domains_changed:
        print("Files updated. Ready for commit.")
    else:
        print("No changes to commit.")

if __name__ == "__main__":
    main()
