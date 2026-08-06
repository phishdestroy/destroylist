#!/usr/bin/env python3
"""Generate badge count files for shields.io endpoints."""
import json
from datetime import datetime, timezone
from pathlib import Path

from utils import PROJECT_ROOT, make_badge, save_json, log

SOURCES = {
    "primary": {
        "input": PROJECT_ROOT / "list.json",
        "output": PROJECT_ROOT / "count.json",
        "label": "Primary Entries",
        "color": "important",
        "definition": "Entries published in list.json; this is not a liveness count.",
    },
    "primary_dns": {
        "input": PROJECT_ROOT / "dns" / "active_domains.json",
        "output": PROJECT_ROOT / "dns" / "active_count.json",
        "label": "Primary DNS-Active Entries",
        "color": "purple",
        "definition": "Entries published in dns/active_domains.json after DNS validation.",
    },
    "community": {
        "input": PROJECT_ROOT / "community" / "blocklist.json",
        "output": PROJECT_ROOT / "community" / "count.json",
        "label": "Community Entries",
        "color": "blue",
        "definition": "Entries published in community/blocklist.json.",
    },
    "community_dns": {
        "input": PROJECT_ROOT / "community" / "live_blocklist.json",
        "output": PROJECT_ROOT / "community" / "live_count.json",
        "label": "Community DNS-Active Entries",
        "color": "brightgreen",
        "definition": "Entries published in community/live_blocklist.json after DNS validation.",
    },
    "primary_content": {
        "input": PROJECT_ROOT / "dns" / "content_active.json",
        "output": PROJECT_ROOT / "dns" / "content_active_count.json",
        "label": "Primary Content-Verified Entries",
        "color": "orange",
        "definition": "Entries published in dns/content_active.json after HTTP content validation.",
    },
    "community_content": {
        "input": PROJECT_ROOT / "community" / "content_live.json",
        "output": PROJECT_ROOT / "community" / "content_active_count.json",
        "label": "Community Content-Verified Entries",
        "color": "yellow",
        "definition": "Entries published in community/content_live.json after HTTP content validation.",
    },
}
METRICS_FILE = PROJECT_ROOT / "dns" / "metrics.json"


def count_domains(filepath: Path) -> int:
    if not filepath.exists():
        return 0
    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            return len(data.get("domains", []))
    except Exception as e:
        log(f"Failed to read {filepath.name}: {e}", "warn")
    return 0


def build_metrics(counts: dict, generated_at: str | None = None) -> dict:
    """Build one machine-readable manifest for every public feed counter."""
    if generated_at is None:
        generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "schemaVersion": 1,
        "generatedAt": generated_at,
        "countType": "feed_entries",
        "note": (
            "Counts are exact entries in each published feed. The API may report smaller "
            "normalized-unique domain counts after URL, www and duplicate normalization."
        ),
        "counts": {
            name: {
                "value": counts[name],
                "source": str(cfg["input"].relative_to(PROJECT_ROOT)),
                "definition": cfg["definition"],
            }
            for name, cfg in SOURCES.items()
            if name in counts
        },
    }


def main():
    counts = {}
    for name, cfg in SOURCES.items():
        count = count_domains(cfg["input"])
        if count == 0:
            log(f"{name}: source missing, invalid or empty; existing outputs preserved", "warn")
            continue

        counts[name] = count
        save_json(cfg["output"], make_badge(cfg["label"], f"{count:,}", cfg["color"]))
        log(f"{name}: {count:,}", "ok")

    if len(counts) == len(SOURCES):
        save_json(METRICS_FILE, build_metrics(counts))
        log(f"metrics manifest: {METRICS_FILE.name}", "ok")
    else:
        missing = ", ".join(sorted(set(SOURCES) - set(counts)))
        log(f"metrics manifest preserved; incomplete source set: {missing}", "warn")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"FATAL: {e}", "error")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)
