#!/usr/bin/env python3
"""
PhishDestroy Destroylist Format Converter
Converts list.json to multiple blocklist formats
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Configuration
BASE_DIR = Path(os.getcwd())
LIST_FILE = BASE_DIR / "list.json"
DNS_DIR = BASE_DIR / "dns"
COMMUNITY_DIR = BASE_DIR / "community"

def ensure_directories():
    """Create output directories if they don't exist"""
    DNS_DIR.mkdir(exist_ok=True)
    COMMUNITY_DIR.mkdir(exist_ok=True)
    print(f"✓ Directories ready: dns/, community/")

def load_domains():
    """
    Load domains from list.json
    Supports multiple JSON structures
    """
    try:
        with open(LIST_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Try common keys
                for key in ['domains', 'blocklist', 'list', 'items', 'urls', 'hosts']:
                    if key in data and isinstance(data[key], list):
                        return data[key]
                # If single key dict, return its value
                if len(data) == 1:
                    return list(data.values())[0]
            
            print(f"Warning: Unexpected JSON structure")
            return []
            
    except FileNotFoundError:
        print(f"Error: {LIST_FILE} not found")
        print("Creating sample list.json file...")
        
        # Create sample file
        sample = [
            "phishing-example.com",
            "scam-site.org",
            "fake-bank.net"
        ]
        with open(LIST_FILE, 'w') as f:
            json.dump(sample, f, indent=2)
        print(f"Created sample {LIST_FILE}")
        return sample
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {LIST_FILE}")
        print(f"Details: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def clean_domain(domain):
    """
    Clean and validate domain
    Remove protocols, paths, ports, etc.
    """
    if not domain:
        return None
    
    # Convert to string and clean
    domain = str(domain).strip().lower()
    
    # Remove protocols
    protocols = ['https://', 'http://', 'ftp://', 'ws://', 'wss://']
    for proto in protocols:
        if domain.startswith(proto):
            domain = domain[len(proto):]
    
    # Remove www prefix (optional, uncomment if needed)
    # if domain.startswith('www.'):
    #     domain = domain[4:]
    
    # Remove path, query, fragment
    domain = domain.split('/')[0]
    domain = domain.split('?')[0]
    domain = domain.split('#')[0]
    
    # Remove port (but keep IPv6 addresses intact)
    if ':' in domain and '[' not in domain:  # Not IPv6
        domain = domain.split(':')[0]
    
    # Remove trailing dot
    domain = domain.rstrip('.')
    
    # Basic validation
    if not domain or '.' not in domain:
        return None
    
    # Check for invalid characters
    invalid_chars = [' ', '\t', '\n', '\r', '@', '*', '|', '\\']
    if any(char in domain for char in invalid_chars):
        return None
    
    return domain

def save_json(data, filepath):
    """Save data as JSON with proper formatting"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)
    print(f"  ✓ JSON: {filepath.name}")

def save_text_list(domains, filepath):
    """Save as plain text list (one domain per line)"""
    with open(filepath, 'w', encoding='utf-8') as f:
        for domain in domains:
            f.write(f"{domain}\n")
    print(f"  ✓ Text: {filepath.name}")

def save_hosts_format(domains, filepath):
    """
    Save in hosts file format
    Compatible with /etc/hosts, Windows hosts, etc.
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        # Header
        f.write("# PhishDestroy Blocklist - Hosts Format\n")
        f.write("# Source: https://github.com/phishdestroy/destroylist\n")
        f.write(f"# Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
        f.write(f"# Total domains: {len(domains)}\n")
        f.write("# Format: 0.0.0.0 domain.com\n")
        f.write("#\n\n")
        
        # Domains
        for domain in domains:
            f.write(f"0.0.0.0 {domain}\n")
            # Optional: also block www subdomain
            if not domain.startswith('www.'):
                f.write(f"0.0.0.0 www.{domain}\n")
    
    print(f"  ✓ Hosts: {filepath.name}")

def save_dnsmasq_format(domains, filepath):
    """
    Save in dnsmasq format
    For routers and DNS servers using dnsmasq
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        # Header
        f.write("# PhishDestroy Blocklist - Dnsmasq Format\n")
        f.write("# Source: https://github.com/phishdestroy/destroylist\n")
        f.write(f"# Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
        f.write(f"# Total domains: {len(domains)}\n")
        f.write("# Usage: include in dnsmasq.conf\n")
        f.write("#\n\n")
        
        # Domains
        for domain in domains:
            f.write(f"server=/{domain}/\n")
    
    print(f"  ✓ Dnsmasq: {filepath.name}")

def save_adblock_format(domains, filepath):
    """
    Save in AdBlock/uBlock Origin format
    Compatible with browser ad blockers
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        # Header
        f.write("[Adblock Plus 2.0]\n")
        f.write("! Title: PhishDestroy Blocklist\n")
        f.write("! Homepage: https://github.com/phishdestroy/destroylist\n")
        f.write(f"! Last modified: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
        f.write(f"! Total entries: {len(domains)}\n")
        f.write("! License: MIT\n")
        f.write("!\n\n")
        
        # Domains
        for domain in domains:
            f.write(f"||{domain}^\n")
    
    print(f"  ✓ AdBlock: {filepath.name}")

def save_pihole_format(domains, filepath):
    """
    Save in Pi-hole format
    Simple domain list for Pi-hole
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        for domain in domains:
            f.write(f"{domain}\n")
    print(f"  ✓ Pi-hole: {filepath.name}")

def save_unbound_format(domains, filepath):
    """
    Save in Unbound DNS format
    For Unbound recursive DNS servers
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        # Header
        f.write("# PhishDestroy Blocklist - Unbound Format\n")
        f.write("# Source: https://github.com/phishdestroy/destroylist\n")
        f.write(f"# Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
        f.write(f"# Total domains: {len(domains)}\n")
        f.write("#\n\n")
        
        # Domains
        for domain in domains:
            f.write(f'local-zone: "{domain}" always_nxdomain\n')
    
    print(f"  ✓ Unbound: {filepath.name}")

def generate_statistics(domains):
    """Generate statistics about the blocklist"""
    stats = {
        "total_domains": len(domains),
        "updated": datetime.utcnow().isoformat(),
        "updated_human": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
        "formats_available": [
            "json", "txt", "hosts", "dnsmasq", 
            "adblock", "pihole", "unbound"
        ],
        "source": "PhishDestroy",
        "homepage": "https://github.com/phishdestroy/destroylist"
    }
    
    # Top level domains distribution
    tld_count = {}
    for domain in domains:
        parts = domain.split('.')
        if len(parts) >= 2:
            tld = parts[-1]
            tld_count[tld] = tld_count.get(tld, 0) + 1
    
    # Sort and get top 10 TLDs
    top_tlds = sorted(tld_count.items(), key=lambda x: x[1], reverse=True)[:10]
    stats["top_tlds"] = [{"tld": tld, "count": count} for tld, count in top_tlds]
    
    return stats

def main():
    """Main execution function"""
    print("\n" + "="*60)
    print(" PhishDestroy Blocklist Format Converter")
    print("="*60 + "\n")
    
    # Setup directories
    ensure_directories()
    
    # Load domains
    print("Loading domains...")
    raw_domains = load_domains()
    
    if not raw_domains:
        print("❌ No domains found. Exiting.")
        return 1
    
    print(f"  → Found {len(raw_domains)} entries in list.json")
    
    # Clean and deduplicate domains
    print("\nCleaning domains...")
    domains = []
    invalid_count = 0
    
    for entry in raw_domains:
        cleaned = clean_domain(entry)
        if cleaned:
            if cleaned not in domains:
                domains.append(cleaned)
        else:
            invalid_count += 1
    
    # Sort for consistency
    domains.sort()
    
    print(f"  → {len(domains)} valid unique domains")
    if invalid_count > 0:
        print(f"  → {invalid_count} invalid entries removed")
    
    if not domains:
        print("❌ No valid domains after cleaning. Exiting.")
        return 1
    
    # Generate formats for DNS directory
    print("\nGenerating DNS formats...")
    
    # JSON formats
    save_json(domains, DNS_DIR / "active_domains.json")
    save_json({"domains": domains, "count": len(domains)}, DNS_DIR / "blocklist.json")
    
    # Text formats
    save_text_list(domains, DNS_DIR / "domains.txt")
    save_text_list(domains, DNS_DIR / "blocklist.txt")
    
    # Specialized formats
    save_hosts_format(domains, DNS_DIR / "hosts.txt")
    save_dnsmasq_format(domains, DNS_DIR / "dnsmasq.conf")
    save_adblock_format(domains, DNS_DIR / "adblock.txt")
    save_pihole_format(domains, DNS_DIR / "pihole.txt")
    save_unbound_format(domains, DNS_DIR / "unbound.conf")
    
    # Generate community formats
    print("\nGenerating Community formats...")
    
    # Full metadata format
    community_data = {
        "name": "PhishDestroy Blocklist",
        "description": "Up-to-date blacklist of phishing and scam domains",
        "homepage": "https://github.com/phishdestroy/destroylist",
        "source": "PhishDestroy",
        "license": "MIT",
        "domains": domains,
        "count": len(domains),
        "updated": datetime.utcnow().isoformat(),
        "format_version": "1.0"
    }
    
    save_json(community_data, COMMUNITY_DIR / "blocklist.json")
    save_json(community_data, COMMUNITY_DIR / "live_blocklist.json")
    
    # Statistics
    stats = generate_statistics(domains)
    save_json(stats, DNS_DIR / "stats.json")
    
    # Summary
    print("\n" + "="*60)
    print(" ✅ Conversion completed successfully!")
    print("="*60)
    print(f"\n📊 Statistics:")
    print(f"  • Total domains: {len(domains)}")
    print(f"  • Formats created: 11")
    print(f"  • Output directories: dns/, community/")
    
    if stats.get("top_tlds"):
        print(f"\n🌐 Top 5 TLDs:")
        for item in stats["top_tlds"][:5]:
            print(f"  • .{item['tld']}: {item['count']} domains")
    
    print("\n" + "="*60 + "\n")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)