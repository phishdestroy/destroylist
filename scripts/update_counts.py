#!/usr/bin/env python3
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

SOURCES = {
    "primary": {
        "input": PROJECT_ROOT / "list.json",
        "output": PROJECT_ROOT / "count.json",
        "label": "Active Domains",
        "color": "important"
    },
    "primary_dns": {
        "input": PROJECT_ROOT / "dns" / "active_domains.json",
        "output": PROJECT_ROOT / "dns" / "active_count.json",
        "label": "Active Domains (DNS)",
        "color": "purple"
    },
    "community": {
        "input": PROJECT_ROOT / "community" / "blocklist.json",
        "output": PROJECT_ROOT / "community" / "count.json",
        "label": "Community Domains",
        "color": "blue"
    },
    "community_dns": {
        "input": PROJECT_ROOT / "community" / "live_blocklist.json",
        "output": PROJECT_ROOT / "community" / "live_count.json",
        "label": "Community Live",
        "color": "brightgreen"
    }
}


def count_domains(filepath: Path) -> int:
    if not filepath.exists():
        return 0
    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            return len(data.get("domains", []))
    except Exception:
        pass
    return 0


def main():
    for name, cfg in SOURCES.items():
        count = count_domains(cfg["input"])
        if count == 0:
            continue
        
        badge = {
            "schemaVersion": 1,
            "label": cfg["label"],
            "message": str(count),
            "color": cfg["color"]
        }
        
        cfg["output"].parent.mkdir(parents=True, exist_ok=True)
        cfg["output"].write_text(json.dumps(badge, indent=2), encoding="utf-8")
        print(f"{name}: {count}")


if __name__ == "__main__":
    main()