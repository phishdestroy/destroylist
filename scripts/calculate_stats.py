#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def get_count(file):
    try:
        return len(json.load(open(file)))
    except:
        return 0

def get_commits_with_counts(file, since_date):
    """Get all commits with domain counts since date"""
    cmd = [
        'git', 'log',
        f'--since={since_date}',
        '--format=%H',
        '--', file
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    commits = result.stdout.strip().split('\n')
    
    counts = []
    for commit in commits:
        if not commit:
            continue
        try:
            result = subprocess.run(
                ['git', 'show', f'{commit}:{file}'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                count = len(json.loads(result.stdout))
                counts.append(count)
        except:
            pass
    
    return counts

current = get_count('list.json')

# Get counts from past
today_counts = get_commits_with_counts('list.json', '1 day ago')
week_counts = get_commits_with_counts('list.json', '7 days ago')

# Calculate differences
yesterday = min(today_counts) if today_counts else current
week_ago = min(week_counts) if week_counts else current

today_added = max(0, current - yesterday)
week_added = max(0, current - week_ago)

def badge(label, val, color):
    return {
        "schemaVersion": 1,
        "label": label,
        "message": f"+{val:,}",
        "color": color
    }

Path('dns').mkdir(exist_ok=True)

json.dump(badge("added today", today_added, "success"), 
          open('dns/today_added.json', 'w'), indent=2)
json.dump(badge("added this week", week_added, "success"), 
          open('dns/week_added.json', 'w'), indent=2)
json.dump(badge("community today", 0, "blue"), 
          open('dns/today_community.json', 'w'), indent=2)
json.dump(badge("community this week", 0, "blue"), 
          open('dns/week_community.json', 'w'), indent=2)

print(f"Current: {current}")
print(f"Yesterday min: {yesterday}")
print(f"Week ago min: {week_ago}")
print(f"Added today: +{today_added}")
print(f"Added this week: +{week_added}")
