import requests
import json
import os
from datetime import datetime
import socket

SOURCE_URL = "https://github.com/phishdestroy/destroylist/raw/main/list.json"

DNS_ACTIVE_DOMAINS_FILE = "dns_active_domains.json"
DNS_ACTIVE_COUNT_FILE = "dns_active_count.json"

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
                return set(json.load(f))
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
            "label": "DNS Active Domains",
            "message": str(count),
            "color": "purple"
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Saved count {count} to {file_path}")
    except Exception as e:
        print(f"Error saving count to {file_path}: {e}")

def is_domain_resolvable(domain):
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False
    except Exception as e:
        print(f"Error checking resolvability for {domain}: {e}")
        return False

def main():
    print(f"[{datetime.now()}] Starting DNS active domain update...")

    new_domains_list = fetch_domains(SOURCE_URL)
    if new_domains_list is None:
        print("Failed to fetch new domains. Exiting.")
        return

    new_domains_set = set(new_domains_list)
    print(f"Fetched {len(new_domains_set)} domains from source.")

    existing_dns_active_domains = load_existing_domains(DNS_ACTIVE_DOMAINS_FILE)
    print(f"Loaded {len(existing_dns_active_domains)} existing DNS active domains.")

    candidate_dns_active_domains = new_domains_set.union(existing_dns_active_domains)
    print(f"Total unique candidate domains (before DNS check): {len(candidate_dns_active_domains)}")

    resolvable_domains = set()
    print("Performing DNS checks on candidate domains...")
    for i, domain in enumerate(sorted(list(candidate_dns_active_domains))):
        if i % 100 == 0:
            print(f"  Checked {i}/{len(candidate_dns_active_domains)} domains...")
        if is_domain_resolvable(domain):
            resolvable_domains.add(domain)
    
    updated_dns_active_domains = resolvable_domains
    print(f"Finished DNS checks. {len(updated_dns_active_domains)} domains are currently DNS active.")

    domains_changed = False

    if updated_dns_active_domains != existing_dns_active_domains:
        domains_changed = True
        print("DNS active domains have changed. Updating files.")
        save_domains(DNS_ACTIVE_DOMAINS_FILE, updated_dns_active_domains)
        save_count(DNS_ACTIVE_COUNT_FILE, len(updated_dns_active_domains))
    else:
        print("No new domains detected in DNS active domains.")
        current_count_from_file = 0
        if os.path.exists(DNS_ACTIVE_COUNT_FILE):
             try:
                 with open(DNS_ACTIVE_COUNT_FILE, 'r', encoding='utf-8') as f:
                     current_count_from_file = int(json.load(f).get("message", "0"))
             except Exception:
                 pass

        if current_count_from_file != len(updated_dns_active_domains):
            domains_changed = True
            print("DNS active domain count file is outdated. Updating count file.")
            save_count(DNS_ACTIVE_COUNT_FILE, len(updated_dns_active_domains))

    if domains_changed:
        print("Files updated. Ready for commit.")
    else:
        print("No changes to commit.")

if __name__ == "__main__":
    main()
