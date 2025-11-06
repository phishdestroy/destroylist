#!/usr/bin/env python3
import json

try:
    with open('list.json', 'r') as f:
        data = json.load(f)
        if isinstance(data, list):
            domains = data
        else:
            domains = data.get('domains', data.get('list', []))
except:
    domains = []

clean = []
for d in domains:
    d = str(d).strip().lower()
    d = d.replace('https://', '').replace('http://', '')
    d = d.split('/')[0]
    if d and '.' in d and d not in clean:
        clean.append(d)

clean.sort()

with open('list.txt', 'w') as f:
    for domain in clean:
        f.write(f"{domain}\n")

print(f"Created list.txt with {len(clean)} domains")