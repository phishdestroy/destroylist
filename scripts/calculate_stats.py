#!/usr/bin/env python3
"""
Calculate domain addition statistics from git history.
Generates badge JSON files for domains added today and this week.
"""
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Set

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DNS_DIR = PROJECT_ROOT / "dns"

LIST_FILE = "list.json"
COMMUNITY_FILE = "community/blocklist.json"

OUTPUT_FILES = {
    "today_added": DNS_DIR / "today_added.json",
    "week_added": DNS_DIR / "week_added.json",
    "today_community": DNS_DIR / "today_community.json",
    "week_community": DNS_DIR / "week_community.json",
}


def run_git_command(cmd: list) -> str:
    """Execute git command and return output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}", file=sys.stderr)
        return ""


def get_domains_from_json(json_content: str) -> Set[str]:
    """Extract domains from JSON content."""
    try:
        data = json.loads(json_content)
        if isinstance(data, list):
            return set(d.lower().strip() for d in data if isinstance(d, str))
        elif isinstance(data, dict) and "domains" in data:
            return set(d.lower().strip() for d in data["domains"] if isinstance(d, str))
        return set()
    except (json.JSONDecodeError, KeyError):
        return set()


def get_domains_added_since(file_path: str, since_date: str) -> int:
    """
    Count domains added to a file since a specific date.

    Args:
        file_path: Path to the JSON file to track
        since_date: Git date format (e.g., "1 day ago", "1 week ago")

    Returns:
        Number of new domains added
    """
    # Get current domains
    try:
        with open(PROJECT_ROOT / file_path, 'r', encoding='utf-8') as f:
            current_domains = get_domains_from_json(f.read())
    except FileNotFoundError:
        print(f"Warning: {file_path} not found", file=sys.stderr)
        return 0

    # Get domains from git history at the specified date
    git_cmd = [
        "git", "log",
        f"--since={since_date}",
        "--reverse",
        "--format=%H",
        "--", file_path
    ]

    commits = run_git_command(git_cmd).strip().split('\n')

    if not commits or commits[0] == '':
        # No commits in this time period
        return 0

    # Get the first commit's parent (state before the period)
    first_commit = commits[0]
    parent_cmd = ["git", "rev-parse", f"{first_commit}^"]
    parent_commit = run_git_command(parent_cmd).strip()

    if not parent_commit:
        # This is the initial commit, all domains are new
        return len(current_domains)

    # Get file content at parent commit
    show_cmd = ["git", "show", f"{parent_commit}:{file_path}"]
    old_content = run_git_command(show_cmd)

    if not old_content:
        # File didn't exist before this period
        return len(current_domains)

    old_domains = get_domains_from_json(old_content)
    new_domains = current_domains - old_domains

    return len(new_domains)


def create_badge_json(label: str, count: int, color: str = "success") -> Dict:
    """Create badge JSON structure."""
    message = f"+{count:,}" if count > 0 else "+0"
    return {
        "schemaVersion": 1,
        "label": label,
        "message": message,
        "color": color
    }


def main():
    """Generate statistics badges."""
    print("Calculating domain addition statistics...")

    # Ensure DNS directory exists
    DNS_DIR.mkdir(exist_ok=True)

    # Calculate statistics
    stats = {
        "today_added": get_domains_added_since(LIST_FILE, "1 day ago"),
        "week_added": get_domains_added_since(LIST_FILE, "1 week ago"),
        "today_community": get_domains_added_since(COMMUNITY_FILE, "1 day ago"),
        "week_community": get_domains_added_since(COMMUNITY_FILE, "1 week ago"),
    }

    # Display results
    print("\nStatistics:")
    print(f"  Primary list - Today:     +{stats['today_added']}")
    print(f"  Primary list - This week: +{stats['week_added']}")
    print(f"  Community - Today:        +{stats['today_community']}")
    print(f"  Community - This week:    +{stats['week_community']}")

    # Generate badge files
    badges = {
        "today_added": create_badge_json("added today", stats["today_added"], "success"),
        "week_added": create_badge_json("added this week", stats["week_added"], "success"),
        "today_community": create_badge_json("community today", stats["today_community"], "blue"),
        "week_community": create_badge_json("community this week", stats["week_community"], "blue"),
    }

    # Write badge files
    for key, badge_data in badges.items():
        output_file = OUTPUT_FILES[key]
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(badge_data, f, indent=2)
        print(f"  Created: {output_file.name}")

    print("\n✅ Statistics updated successfully!")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
