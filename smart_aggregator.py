import requests
import re
import json
import os
import hashlib

# --- PARSERS FOR DIFFERENT SOURCE FORMATS ---

def parse_default_text(content):
    """
    Default parser for simple text files (e.g., one domain per line).
    Uses regex to find all valid domain patterns in the text content.
    """
    try:
        return set(re.findall(r'([a-zA-Z0-9][a-zA-Z0-9\.-]+\.[a-zA-Z]{2,})', content))
    except Exception as e:
        print(f"Error: Failed to parse content with default_text parser: {e}")
        return set()

def parse_json_list(content):
    """Parses JSON files that are a simple list of domain strings."""
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return set(data)
        print("Warning: JSON content is not a list.")
        return set()
    except json.JSONDecodeError:
        print("Error: Could not decode content as JSON.")
        return set()

def parse_metamask_blacklist(content):
    """Parses the MetaMask config file to extract domains from the 'blacklist' key."""
    try:
        data = json.loads(content)
        return set(data.get('blacklist', []))
    except json.JSONDecodeError:
        print("Error: Could not decode MetaMask JSON.")
        return set()

def parse_polkadot_denylist(content):
    """Parses the Polkadot config file to extract domains from the keys of the 'deny' object."""
    try:
        data = json.loads(content)
        # The domains are the keys of the 'deny' dictionary
        return set(data.get('deny', {}).keys())
    except json.JSONDecodeError:
        print("Error: Could not decode Polkadot JSON.")
        return set()

# Dictionary to map parser names to their respective functions
PARSERS = {
    'default_text': parse_default_text,
    'json_list': parse_json_list,
    'metamask_blacklist': parse_metamask_blacklist,
    'polkadot_denylist': parse_polkadot_denylist,
}


# --- CONFIGURATION ---

LOCAL_FILES_CONFIG = ["list.json"]

# Updated source configuration with URLs and their designated parsers
SOURCES_CONFIG = {
    "MetaMask": {
        "url": "https://raw.githubusercontent.com/MetaMask/eth-phishing-detect/main/src/config.json",
        "parser": "metamask_blacklist"
    },
    "ScamSniffer": {
        "url": "https://raw.githubusercontent.com/scamsniffer/scam-database/main/blacklist/domains.json",
        "parser": "json_list"
    },
    "Polkadot": {
        "url": "https://raw.githubusercontent.com/polkadot-js/phishing/master/all.json",
        "parser": "polkadot_denylist"
    },
    "Codeesura": {
        "url": "https://raw.githubusercontent.com/codeesura/Anti-phishing-extension/main/phishing-sites-list.json",
        "parser": "json_list"
    },
    "CryptoFirewall": {
        "url": "https://raw.githubusercontent.com/chartingshow/crypto-firewall/master/src/blacklists/domains-only.txt",
        "parser": "default_text"
    },
    "OpenPhish": {
        "url": "https://raw.githubusercontent.com/openphish/public_feed/main/feed.txt",
        "parser": "default_text"
    }
}

OUTPUT_FILENAME = "community_blocklist.json"
STATE_FILENAME = "community_state.json"
BADGE_FILENAME = "community_count.json"
COMMIT_MSG_FILENAME = "commit_message.txt"


def load_state():
    """Loads the last saved state from the state file."""
    if not os.path.exists(STATE_FILENAME):
        return {}
    with open(STATE_FILENAME, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_state(state):
    """Saves the current state to the state file."""
    with open(STATE_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

def fetch_content(url):
    """Fetches text content from a given URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, timeout=30, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error: Failed to fetch {url}: {e}")
        return None

def update_badge_json(count):
    """Updates the JSON file used for generating a repository badge."""
    badge_data = {"schemaVersion": 1, "label": "Total Domains", "message": str(count), "color": "blue"}
    with open(BADGE_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(badge_data, f)
    print(f"Badge file '{BADGE_FILENAME}' updated with count: {count}")

def main():
    """Main function to run the aggregation process."""
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
    for name, config in SOURCES_CONFIG.items():
        url = config['url']
        parser_name = config['parser']
        parser_func = PARSERS[parser_name]

        print(f"-> Processing {name} from {url} using '{parser_name}' parser...")
        
        content = fetch_content(url)
        domains = set()
        content_hash = None
        
        if content is None:
            # Use stale data from the last state if fetch fails
            stale_domains = last_state.get(name, {}).get('domains', [])
            domains = set(stale_domains)
            content_hash = last_state.get(name, {}).get('hash')
            print(f"Warning: Using stale data for {name} due to fetch error.")
        else:
            domains = parser_func(content)
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        all_domains.update(domains)
        
        last_hash = last_state.get(name, {}).get('hash')
        
        if content_hash != last_hash and content is not None:
            last_count = last_state.get(name, {}).get('count', 0)
            diff = len(domains) - last_count
            changes.append({"name": name, "diff": diff, "sign": '+' if diff >= 0 else ''})
        
        new_state[name] = {'hash': content_hash, 'count': len(domains), 'domains': list(domains)}

    last_total_count = last_state.get("total_count", 0)
    if len(all_domains) == last_total_count and not changes:
        print("No changes detected. Exiting.")
        return

    print("Changes detected! Updating blocklist...")
    new_state["total_count"] = len(all_domains)

    # Prepare commit message
    commit_title = "Update community blocklist"
    commit_body = f"Total unique domains in the list is now {len(all_domains)}.\n\n"
    if changes:
        title_parts = [f"{c['sign']}{c['diff']} from {c['name']}" for c in changes]
        commit_title = f"Sync: {', '.join(title_parts)}"
        commit_body += "Summary of external changes:\n"
        for c in changes:
            commit_body += f"- {c['name']}: {c['sign']}{c['diff']} domains\n"
    
    full_commit_message = f"{commit_title}\n\n{commit_body}"
    with open(COMMIT_MSG_FILENAME, 'w', encoding='utf-8') as f:
        f.write(full_commit_message)

    # Write output files
    sorted_domains = sorted(list(all_domains))
    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(sorted_domains, f, indent=2)
    
    save_state(new_state)
    update_badge_json(len(all_domains))
    
    print(f"Files '{OUTPUT_FILENAME}', '{STATE_FILENAME}', and '{BADGE_FILENAME}' have been updated.")
    print(f"Commit message saved to '{COMMIT_MSG_FILENAME}'.")

if __name__ == "__main__":
    main()
