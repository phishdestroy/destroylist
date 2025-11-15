import json

with open('list.json') as f:
    data = json.load(f)

badge = {
    "label": "Active Domains",
    "message": str(len(data)),
    "color": "important"
}

with open('count.json', 'w') as f:
    json.dump(badge, f)
