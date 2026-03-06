#!/usr/bin/env python3
"""Generate badge count files for shields.io endpoints."""
import json
from pathlib import Path

from utils import PROJECT_ROOT, make_badge, save_json, log

SOURCES = {
    "primary": {
        "input": PROJECT_ROOT / "list.json",
        "output": PROJECT_ROOT / "count.json",
        "label": "Active Domains",
        "color": "important",
    },
    "primary_dns": {
        "input": PROJECT_ROOT / "dns" / "active_domains.json",
        "output": PROJECT_ROOT / "dns" / "active_count.json",
        "label": "Active Domains (DNS)",
        "color": "purple",
    },
    "community": {
        "input": PROJECT_ROOT / "community" / "blocklist.json",
        "output": PROJECT_ROOT / "community" / "count.json",
        "label": "Community Domains",
        "color": "blue",
    },
    "community_dns": {
        "input": PROJECT_ROOT / "community" / "live_blocklist.json",
        "output": PROJECT_ROOT / "community" / "live_count.json",
        "label": "Community Live",
        "color": "brightgreen",
    },
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

        save_json(cfg["output"], make_badge(cfg["label"], f"{count:,}", cfg["color"]))
        log(f"{name}: {count:,}", "ok")


if __name__ == "__main__":
    main()
