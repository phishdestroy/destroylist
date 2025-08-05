import dns.resolver
import json
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import logging
from typing import List, Set

# --- LOGGING CONFIGURATION ---
# Configure logging for console output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- PERFORMANCE CONFIGURATION ---
MAX_WORKERS = 400
DNS_TIMEOUT = 2.0
CUSTOM_RESOLVERS = ['1.1.1.1', '8.8.8.8']

# List of hosting platform suffixes to automatically include without a DNS check.
HOSTING_PLATFORM_SUFFIXES = (
    '.pages.dev', '.workers.dev', '.vercel.app', '.netlify.app',
    '.onrender.com', '.replit.dev', '.glitch.me', '.github.io',
    '.gitlab.io', '.webflow.io', '.surge.sh', '.firebaseapp.com', '.web.app'
)

def get_root_domain(domain: str) -> str:
    """Extracts the root domain from a given domain string."""
    parts = domain.split('.')
    if len(parts) > 2 and parts[-2] in ('co', 'com', 'org', 'net', 'gov', 'edu'):
        return '.'.join(parts[-3:])
    return '.'.join(parts[-2:])

def check_domain(domain: str, resolver: dns.resolver.Resolver) -> str | None:
    """Checks if a domain has an active DNS A record."""
    try:
        resolver.resolve(domain, 'A')
        return domain
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout, dns.resolver.NoNameservers):
        return None
    except Exception as e:
        logging.debug(f"Error checking domain {domain}: {e}")
        return None

def process_domains(domains: List[str], output_file: str):
    """Main function to read, validate, and write live domains."""
    logging.info(f"Found {len(domains)} total domains.")

    # --- Smart Filtering and Root Domain Extraction ---
    platform_domains = []
    domains_to_process = []
    logging.info("Filtering domains: separating always-on platforms...")
    for domain in domains:
        if domain.endswith(HOSTING_PLATFORM_SUFFIXES):
            platform_domains.append(domain)
        else:
            domains_to_process.append(domain)
    
    logging.info(f"Found {len(platform_domains)} domains on always-on platforms (auto-included).")

    root_domains_to_check: Set[str] = {get_root_domain(d) for d in domains_to_process}
    logging.info(f"Extracted {len(root_domains_to_check)} unique root domains for validation.")
    
    # --- High-performance DNS check on ROOT domains ---
    resolver = dns.resolver.Resolver()
    resolver.nameservers = CUSTOM_RESOLVERS
    resolver.timeout = DNS_TIMEOUT
    resolver.lifetime = DNS_TIMEOUT

    live_root_domains: Set[str] = set()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_domain = {executor.submit(check_domain, root_domain, resolver): root_domain for root_domain in root_domains_to_check}
        
        for future in tqdm(as_completed(future_to_domain), total=len(root_domains_to_check), desc="Validating root domains"):
            result = future.result()
            if result:
                live_root_domains.add(result)
    
    logging.info(f"\nFound {len(live_root_domains)} live root domains.")

    # --- Final List Construction ---
    logging.info("Constructing final list of live domains...")
    final_live_domains = platform_domains[:]
    for domain in domains_to_process:
        root_domain = get_root_domain(domain)
        if root_domain in live_root_domains:
            final_live_domains.append(domain)

    final_live_domains.sort()

    logging.info(f"Validation complete. Found {len(final_live_domains)} total live domains.")

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    logging.info(f"Saving live domains to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_live_domains, f, indent=2)

    logging.info("Done! ✅")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_input = os.path.join(script_dir, "blocklist.json")
    default_output = os.path.join(script_dir, "live_blocklist.json")

    input_arg = sys.argv[1] if len(sys.argv) > 1 else default_input
    output_arg = sys.argv[2] if len(sys.argv) > 2 else default_output

    logging.info(f"Loading domains from {input_arg}...")
    try:
        with open(input_arg, 'r', encoding='utf-8') as f:
            domains = json.load(f)
    except FileNotFoundError:
        logging.error(f"Error: Input file not found: {input_arg}")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error(f"Error: Could not decode JSON from file: {input_arg}")
        sys.exit(1)
    
    if not isinstance(domains, list):
        logging.error(f"Error: Expected a list of domains, but got {type(domains).__name__}.")
        sys.exit(1)
        
    process_domains(domains, output_arg)

if __name__ == "__main__":
    main()