#!/usr/bin/env python3
"""Split list.json into array shards for rootlist/arrays/."""
import json
import math
import shutil
import sys
from pathlib import Path

from utils import PROJECT_ROOT, log

SOURCE_FILE = PROJECT_ROOT / "list.json"
OUTPUT_DIR = PROJECT_ROOT / "rootlist" / "arrays"
CHUNK_SIZE = 3000


def main():
    if not SOURCE_FILE.exists():
        log("list.json not found, skipping sharding", "warn")
        return

    try:
        data = json.loads(SOURCE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        log(f"list.json invalid JSON: {e}", "error")
        sys.exit(1)

    if not isinstance(data, list) or not data:
        log("list.json is empty or not a list, skipping", "warn")
        return

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_chunks = math.ceil(len(data) / CHUNK_SIZE)

    for i in range(total_chunks):
        chunk = data[i * CHUNK_SIZE : (i + 1) * CHUNK_SIZE]
        outfile = OUTPUT_DIR / f"part_{i:03d}.json"
        outfile.write_text(json.dumps(chunk, indent=2, ensure_ascii=False), encoding="utf-8")

    log(f"Created {total_chunks} shards ({len(data):,} domains)", "ok")


if __name__ == "__main__":
    main()
