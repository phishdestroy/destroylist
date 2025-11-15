#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

def get_count(file):
    try:
        return len(json.load(open(file)))
    except:
        return 0

def get_commits_with_counts(file, since_date):
    cmd = ['git', 'log', f'--since={since_date}', '--format=%H', '--', file]
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

# Primary list stats
current = get_count('list.json')
today_counts = get_commits_with_counts('list.json', '1 day ago')
week_counts = get_commits_with_counts('list.json', '7 days ago')

yesterday = min(today_counts) if today_counts else current
week_ago = min(week_counts) if week_counts else current

today_added = max(0, current - yesterday)
week_added = max(0, current - week_ago)

# Community list stats
current_comm = get_count('community/blocklist.json')
today_comm_counts = get_commits_with_counts('community/blocklist.json', '1 day ago')
week_comm_counts = get_commits_with_counts('community/blocklist.json', '7 days ago')

yesterday_comm = min(today_comm_counts) if today_comm_counts else current_comm
week_ago_comm = min(week_comm_counts) if week_comm_counts else current_comm

today_comm = max(0, current_comm - yesterday_comm)
week_comm = max(0, current_comm - week_ago_comm)

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
json.dump(badge("community today", today_comm, "blue"), 
          open('dns/today_community.json', 'w'), indent=2)
json.dump(badge("community this week", week_comm, "blue"), 
          open('dns/week_community.json', 'w'), indent=2)

print(f"Primary - Current: {current}, Today: +{today_added}, Week: +{week_added}")
print(f"Community - Current: {current_comm}, Today: +{today_comm}, Week: +{week_comm}")
