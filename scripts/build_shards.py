#!/usr/bin/env python3
"""Split list.json into array shards for rootlist/arrays/."""
import json
import math
import os
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_FILE = PROJECT_ROOT / "list.json"
OUTPUT_DIR = PROJECT_ROOT / "rootlist" / "arrays"
CHUNK_SIZE = 3000


def main():
    if not SOURCE_FILE.exists():
        print("list.json not found, skipping sharding")
        return

    try:
        data = json.loads(SOURCE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"FATAL: list.json invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list) or not data:
        print("list.json is empty or not a list, skipping")
        return

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_chunks = math.ceil(len(data) / CHUNK_SIZE)

    for i in range(total_chunks):
        chunk = data[i * CHUNK_SIZE : (i + 1) * CHUNK_SIZE]
        outfile = OUTPUT_DIR / f"part_{i:03d}.json"
        outfile.write_text(json.dumps(chunk, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Created {total_chunks} shards ({len(data)} domains)")


if __name__ == "__main__":
    main()
