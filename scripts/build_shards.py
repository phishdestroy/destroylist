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

    import tempfile
    total_chunks = math.ceil(len(data) / CHUNK_SIZE)

    # Write to temp dir first, then swap atomically
    tmp_dir = Path(tempfile.mkdtemp(prefix="shards_", dir=PROJECT_ROOT))
    try:
        for i in range(total_chunks):
            chunk = data[i * CHUNK_SIZE : (i + 1) * CHUNK_SIZE]
            outfile = tmp_dir / f"part_{i:03d}.json"
            try:
                outfile.write_text(json.dumps(chunk, indent=2, ensure_ascii=False), encoding="utf-8")
            except OSError as e:
                log(f"Failed to write {outfile.name}: {e}", "error")
                shutil.rmtree(tmp_dir, ignore_errors=True)
                sys.exit(1)

        if OUTPUT_DIR.exists():
            # Keep the folder's own files (README.md, banner.svg); only the
            # part_NNN.json shards are regenerated.
            for item in OUTPUT_DIR.iterdir():
                if item.is_file() and not (item.name.startswith("part_") and item.suffix == ".json"):
                    shutil.copy2(item, tmp_dir / item.name)
            shutil.rmtree(OUTPUT_DIR)
        tmp_dir.rename(OUTPUT_DIR)
    except Exception as e:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    log(f"Created {total_chunks} shards ({len(data):,} domains)", "ok")


if __name__ == "__main__":
    main()
