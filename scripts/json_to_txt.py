#!/usr/bin/env python3
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
LIST_FILE = PROJECT_ROOT / 'list.json'
OUTPUT_FILE = PROJECT_ROOT / 'list.txt'

try:
    with open(LIST_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if isinstance(data, list):
            domains = data
        else:
            domains = data.get('domains', data.get('list', []))
except FileNotFoundError:
    print(f"Error: {LIST_FILE} not found", file=sys.stderr)
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON in {LIST_FILE}: {e}", file=sys.stderr)
    sys.exit(1)

clean = []
for d in domains:
    d = str(d).strip().lower()
    d = d.replace('https://', '').replace('http://', '')
    d = d.split('/')[0].split('?')[0]
    if d and '.' in d and d not in clean:
        clean.append(d)

clean.sort()

try:
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for domain in clean:
            f.write(f"{domain}\n")
    print(f"Created list.txt with {len(clean)} domains")
except IOError as e:
    print(f"Error writing list.txt: {e}", file=sys.stderr)
    sys.exit(1)