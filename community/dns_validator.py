import dns.resolver
import json
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # A library for a nice progress bar

# List of hosting platform suffixes to automatically include without a DNS check,
# as the root domain is always online.
HOSTING_PLATFORM_SUFFIXES = (
    # PaaS/FaaS Platforms
    '.pages.dev',
    '.workers.dev',
    '.vercel.app',
    '.netlify.app',
    '.onrender.com',
    '.replit.dev',
    '.glitch.me',
    
    # Git-based Pages
    '.github.io',
    '.gitlab.io',

    # Static Site Hosting
    '.webflow.io',
    '.surge.sh',

    # Google Firebase
    '.firebaseapp.com',
    '.web.app'
)

def check_domain(domain):
    """
    Checks if a domain has an active DNS A record.
    Returns the domain if it's active, otherwise None.
    """
    try:
        # Attempt to resolve the A record. This is the most common record type.
        dns.resolver.resolve(domain, 'A')
        return domain
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout, dns.resolver.NoNameservers):
        # NXDOMAIN: The domain does not exist.
        # NoAnswer: The server replied, but there's no A record.
        # Timeout: The query timed out.
        # NoNameservers: Could not find authoritative name servers.
        return None
    except Exception:
        # Catch any other potential DNS-related exceptions.
        return None

def main(input_file, output_file):
    """
    Main function to read a list of domains, validate them via DNS,
    and write the live domains to a new file.
    """
    print(f"Loading domains from {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            domains = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from file: {input_file}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(domains, list):
        print(f"Error: Expected a list of domains in {input_file}, but got {type(domains).__name__}.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(domains)} total domains.")

    # --- Smart Filtering Logic ---
    live_domains = []
    domains_to_check = []

    print("Filtering domains: separating always-on platforms from domains needing DNS checks...")
    for domain in domains:
        if domain.endswith(HOSTING_PLATFORM_SUFFIXES):
            # Automatically consider domains on these platforms as "live"
            live_domains.append(domain)
        else:
            domains_to_check.append(domain)
    
    print(f"Found {len(live_domains)} domains on always-on platforms. They will be included automatically.")
    print(f"Validating {len(domains_to_check)} remaining domains via DNS...")
    # --- End of Smart Filtering Logic ---

    # Use ThreadPoolExecutor to perform DNS queries in parallel for speed.
    with ThreadPoolExecutor(max_workers=50) as executor:
        future_to_domain = {executor.submit(check_domain, domain): domain for domain in domains_to_check}
        
        # Use tqdm to display a clean progress bar in the console.
        for future in tqdm(as_completed(future_to_domain), total=len(domains_to_check), desc="Validating domains"):
            result = future.result()
            if result:
                live_domains.append(result)

    # Sort the final list for consistency.
    live_domains.sort()

    print(f"\nValidation complete. Found {len(live_domains)} total live domains.")

    # Ensure the output directory exists.
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    print(f"Saving live domains to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(live_domains, f, indent=2)

    print("Done!")

if __name__ == "__main__":
    # Get the directory where this script is located.
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Set default paths relative to the script's location.
    # Assumes blocklist.json is in the same directory as this script.
    default_input = os.path.join(script_dir, "blocklist.json")
    default_output = os.path.join(script_dir, "live_blocklist.json")

    # The script can be run with arguments or use the defaults.
    input_arg = sys.argv[1] if len(sys.argv) > 1 else default_input
    output_arg = sys.argv[2] if len(sys.argv) > 2 else default_output
    
    main(input_arg, output_arg)
