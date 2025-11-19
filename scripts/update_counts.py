#!/usr/bin/env python3
"""
Updates the primary domain count badge (count.json).
This script only updates the count for list.json.

Note: dns/active_count.json is managed by dns_validator_primary.py
"""
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
LIST_FILE = PROJECT_ROOT / 'list.json'
COUNT_FILE = PROJECT_ROOT / 'count.json'

# Read primary domain list
with open(LIST_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create badge for primary list
badge = {
    "schemaVersion": 1,
    "label": "Active Domains",
    "message": str(len(data)),
    "color": "important"
}

# Write count badge
with open(COUNT_FILE, 'w', encoding='utf-8') as f:
    json.dump(badge, f, indent=2)

print(f"✅ Updated count.json: {len(data)} domains")
