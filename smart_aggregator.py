import requests
import re
import json
import os
import hashlib

LOCAL_FILES_CONFIG = [
    "list.json"
]

SOURCES_CONFIG = {
    "MetaMask": "https://raw.githubusercontent.com/MetaMask/eth-phishing-detect/main/src/hosts.json",
    "PhishFort": "https://raw.githubusercontent.com/phishfort/phishfort-lists/master/latest/domains.json",
    "ScamSniffer": "https://raw.githubusercontent.com/scamsniffer/scam-database/main/pii/scam-base.json",
    "Polkadot": "https://raw.githubusercontent.com/polkadot-js/phishing/master/all.json",
    "Discord-AntiScam": "https://raw.githubusercontent.com/Discord-AntiScam/scam-links/main/links.json",
    "Phantom": "https://raw.githubusercontent.com/phantom/blocklist/master/blocklist.json",
    "CryptoFirewall": "https://raw.githubusercontent.com/chartingshow/crypto-firewall/master/blocklist.csv",
    "OpenPhish": "https://openphish.com/feed.txt",
}

OUTPUT_FILENAME = "community_blocklist.txt"
STATE_FILENAME = "community_state.json"
BADGE_FILENAME = "community_count.json"
GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

def load_state():
    if not os.path.exists(STATE_FILENAME): return {}
    with open(STATE_FILENAME, 'r', encoding='utf-8') as f:
        try: return json.load(f)
        except json.JSONDecodeError: return {}

def save_state(state):
    with open(STATE_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

def fetch_and_parse(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, timeout=30, headers=headers)
        response.raise_for_status()
        content = response.text
        domains = set(re.findall(r'([a-zA-Z0-9][a-zA-Z0-9\.-]+\.[a-zA-Z]{2,})', content))
        return content, domains
    except requests.RequestException as e:
        print(f"Error: Failed to fetch {url}: {e}")
        return None, set()

def create_github_issue(title, body):
    if not GITHUB_REPO or not GITHUB_TOKEN: return
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    payload = {"title": title, "body": body, "labels": ["automated-update", "community-list"]}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201: print(f"Successfully created Issue: '{title}'")
    else: print(f"Error: Failed to create Issue. Status: {response.status_code}, Response: {response.text}")

def update_badge_json(count):
    badge_data = {"schemaVersion": 1, "label": "Total Domains", "message": str(count), "color": "blue"}
    with open(BADGE_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(badge_data, f)
    print(f"Badge file '{BADGE_FILENAME}' updated with count: {count}")

def main():
    print("Starting smart aggregation process...")
    last_state = load_state()
    new_state = {}
    all_domains = set()
    changes = []

    print("Processing local repository files...")
    for file_path in LOCAL_FILES_CONFIG:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    local_domains = json.load(f)
                    all_domains.update(local_domains)
                    print(f"  -> Added {len(local_domains)} domains from {file_path}")
        except FileNotFoundError:
            print(f"Warning: Local file not found: {file_path}. Skipping.")
        except json.JSONDecodeError:
            print(f"Warning: Could not parse JSON from {file_path}. Skipping.")

    print("Processing external community sources...")
    for name, url in SOURCES_CONFIG.items():
        content, domains = fetch_and_parse(url)
        if content is None:
            domains = set(last_state.get(name, {}).get('domains', []))
            print(f"Warning: Using stale data for {name} due to fetch error.")
        
        all_domains.update(domains)
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest() if content else None
        last_hash = last_state.get(name, {}).get('hash')
        
        if content_hash != last_hash and content_hash is not None:
            last_count = last_state.get(name, {}).get('count', 0)
            diff = len(domains) - last_count
            changes.append({"name": name, "diff": diff, "sign": '+' if diff >= 0 else ''})
        
        new_state[name] = {'hash': content_hash, 'count': len(domains), 'domains': list(domains)}

    last_total_count_data = load_state().get("total_count", 0)
    if len(all_domains) == last_total_count_data and not changes:
         print("No changes detected. Exiting.")
         return

    print("Changes detected! Updating blocklist...")
    new_state["total_count"] = len(all_domains)

    issue_title = "Community List Sync: Total count updated"
    issue_body = f"Total domains in the list is now {len(all_domains)}.\n\n"
    if changes:
        title_parts = [f"{c['sign']}{c['diff']} from {c['name']}" for c in changes]
        issue_title = f"Community List Sync: {', '.join(title_parts)}"
        issue_body += "**Summary of external changes:**\n"
        for c in changes:
            issue_body += f"- **{c['name']}:** {c['sign']}{c['diff']} domains\n"
    
    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
        for domain in sorted(list(all_domains)):
            f.write(f"{domain}\n")
    
    save_state(new_state)
    update_badge_json(len(all_domains))
    
    print(f"Files '{OUTPUT_FILENAME}', '{STATE_FILENAME}', and '{BADGE_FILENAME}' are updated.")
    create_github_issue(issue_title, issue_body)

if __name__ == "__main__":
    main()