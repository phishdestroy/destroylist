import json
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
LIST_FILE = PROJECT_ROOT / 'list.json'
COUNT_FILE = PROJECT_ROOT / 'count.json'
DNS_DIR = PROJECT_ROOT / 'dns'
DNS_ACTIVE_FILE = DNS_DIR / 'active_domains.json'
DNS_COUNT_FILE = DNS_DIR / 'active_count.json'

with open(LIST_FILE) as f:
    data = json.load(f)

badge = {
    "schemaVersion": 1,
    "label": "Active Domains",
    "message": str(len(data)),
    "color": "important"
}

with open(COUNT_FILE, 'w') as f:
    json.dump(badge, f, indent=2)

DNS_DIR.mkdir(exist_ok=True)

if DNS_ACTIVE_FILE.exists():
    with open(DNS_ACTIVE_FILE) as f:
        active = json.load(f)

    active_badge = {
        "schemaVersion": 1,
        "label": "Active Domains (DNS)",
        "message": str(len(active)),
        "color": "purple"
    }

    with open(DNS_COUNT_FILE, 'w') as f:
        json.dump(active_badge, f, indent=2)
