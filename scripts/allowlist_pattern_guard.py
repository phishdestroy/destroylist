#!/usr/bin/env python3
"""Detect and CAS-restore removed leading-dot allowlist patterns.

The script is deliberately network-free.  The workflow owns fetch/reset/push;
this helper only reads immutable git revisions and merges missing patterns into
the latest checked-out allowlist.
"""

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path


ALLOWLIST_PATH = "allow/allowlist.json"
APPROVED_PATTERNS = {".microsoft", ".paypal.com"}


def _load_array(raw: str, source: str) -> list[str]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{source}: invalid JSON: {exc}") from exc
    if not isinstance(data, list) or any(not isinstance(item, str) for item in data):
        raise ValueError(f"{source}: expected a JSON array of strings")
    return data


def _pattern_map(entries: list[str], source: str) -> dict[str, str]:
    """Map semantic pattern keys to their original stored representation."""
    patterns = {}
    for item in entries:
        stripped = item.strip()
        if stripped.startswith("."):
            key = stripped.lower()
            if key not in APPROVED_PATTERNS:
                raise ValueError(
                    f"{source}: unapproved allowlist suffix pattern: {item!r}"
                )
            patterns.setdefault(key, item)
    return patterns


def _git_file(revision: str, path: str = ALLOWLIST_PATH) -> list[str]:
    result = subprocess.run(
        ["git", "show", f"{revision}:{path}"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "git show failed"
        raise RuntimeError(f"cannot read {path} at {revision}: {detail}")
    return _load_array(result.stdout, f"{revision}:{path}")


def detect_removed(before: str, after: str) -> list[str]:
    before_patterns = _pattern_map(_git_file(before), f"{before}:{ALLOWLIST_PATH}")
    after_patterns = _pattern_map(_git_file(after), f"{after}:{ALLOWLIST_PATH}")
    removed_keys = sorted(set(before_patterns) - set(after_patterns))
    return [before_patterns[key] for key in removed_keys]


def _atomic_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def restore_file(path: Path, removed: list[str]) -> list[str]:
    current = _load_array(path.read_text(encoding="utf-8"), str(path))
    current_patterns = _pattern_map(current, str(path))
    restored = []
    for pattern in removed:
        key = pattern.strip().lower()
        if key not in APPROVED_PATTERNS:
            raise ValueError(f"refusing unapproved pattern restore entry: {pattern!r}")
        if key not in current_patterns:
            current.append(pattern)
            current_patterns[key] = pattern
            restored.append(pattern)
    if restored:
        current.sort(key=lambda item: (item.strip().lower(), item))
        _atomic_json(path, current)
    return restored


def _load_removed(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("removed-pattern state must be an object")
    removed = payload.get("removed")
    if not isinstance(removed, list) or any(not isinstance(item, str) for item in removed):
        raise ValueError("removed-pattern state must contain a string array")
    return removed


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    detect = sub.add_parser("detect")
    detect.add_argument("--before", required=True)
    detect.add_argument("--after", required=True)
    detect.add_argument("--output", type=Path, required=True)

    restore = sub.add_parser("restore")
    restore.add_argument("--removed-file", type=Path, required=True)
    restore.add_argument("--allowlist", type=Path, default=Path(ALLOWLIST_PATH))
    restore.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "detect":
        removed = detect_removed(args.before, args.after)
        _atomic_json(args.output, {
            "before": args.before,
            "after": args.after,
            "removed": removed,
            "removed_count": len(removed),
        })
        print(f"removed_patterns={len(removed)}")
        return 0

    removed = _load_removed(args.removed_file)
    restored = restore_file(args.allowlist, removed)
    _atomic_json(args.output, {
        "restored": restored,
        "restored_count": len(restored),
    })
    print(f"restored_patterns={len(restored)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
