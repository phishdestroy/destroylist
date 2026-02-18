#!/usr/bin/env python3
"""PhishDestroy — Daily Gist Updater (runs inside GitHub Actions)."""

import json
import os
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

GIST_TOKEN = os.environ["GIST_TOKEN"]
REPO_PATH  = Path(os.environ.get("GITHUB_WORKSPACE", Path(__file__).resolve().parent.parent))

LIST_FILE      = "list.json"
COMMUNITY_FILE = "community/blocklist.json"
DNS_DIR        = REPO_PATH / "dns"


def run_git(args: list) -> str:
    try:
        r = subprocess.run(
            ["git"] + args, cwd=REPO_PATH,
            capture_output=True, text=True, check=True
        )
        return r.stdout
    except subprocess.CalledProcessError:
        return ""


def load_set(path: Path) -> set:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return {d.lower().strip() for d in data if isinstance(d, str)}
        if isinstance(data, dict) and "domains" in data:
            return {d.lower().strip() for d in data["domains"] if isinstance(d, str)}
    except Exception:
        pass
    return set()


def new_domains_since(file_rel: str, since: str) -> list:
    current = load_set(REPO_PATH / file_rel)
    if not current:
        return []
    commits = run_git(["log", f"--since={since}", "--reverse", "--format=%H", "--", file_rel]).strip().split("\n")
    if not commits or commits[0] == "":
        return []
    parent = run_git(["rev-parse", f"{commits[0]}^"]).strip()
    if not parent:
        return sorted(current)
    old_raw = run_git(["show", f"{parent}:{file_rel}"])
    old: set = set()
    if old_raw:
        try:
            data = json.loads(old_raw)
            if isinstance(data, list):
                old = {d.lower().strip() for d in data if isinstance(d, str)}
            elif isinstance(data, dict) and "domains" in data:
                old = {d.lower().strip() for d in data["domains"] if isinstance(d, str)}
        except Exception:
            pass
    return sorted(current - old)


def read_badge(key: str) -> int:
    try:
        d = json.loads((DNS_DIR / f"{key}.json").read_text(encoding="utf-8"))
        return int(d.get("message", "0").replace("+", "").replace(",", ""))
    except Exception:
        return 0


def build_content(now: datetime) -> str:
    new_p = new_domains_since(LIST_FILE, "1 day ago")
    new_c = new_domains_since(COMMUNITY_FILE, "1 day ago")

    total_p = len(load_set(REPO_PATH / LIST_FILE))
    total_c = len(load_set(REPO_PATH / COMMUNITY_FILE))

    s60 = "═" * 60
    s60d = "─" * 60

    L = []
    L += [
        "```",
        " ██████╗ ██╗  ██╗██╗███████╗██╗  ██╗",
        " ██╔══██╗██║  ██║██║██╔════╝██║  ██║",
        " ██████╔╝███████║██║███████╗███████║",
        " ██╔═══╝ ██╔══██║██║╚════██║██╔══██║",
        " ██║     ██║  ██║██║███████║██║  ██║",
        " ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝",
        "",
        "  ██████╗ ███████╗███████╗████████╗██████╗  ██████╗ ██╗   ██╗",
        "  ██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔═══██╗╚██╗ ██╔╝",
        "  ██║  ██║█████╗  ███████╗   ██║   ██████╔╝██║   ██║ ╚████╔╝ ",
        "  ██║  ██║██╔══╝  ╚════██║   ██║   ██╔══██╗██║   ██║  ╚██╔╝  ",
        "  ██████╔╝███████╗███████║   ██║   ██║  ██║╚██████╔╝   ██║   ",
        "  ╚═════╝ ╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ",
        "```",
        "",
        f"# 📊 Daily Threat Intelligence Report",
        f"### {now.strftime('%B %d, %Y')} · {now.strftime('%H:%M UTC')}",
        "",
        f"> 🔗 [destroylist](https://github.com/phishdestroy/destroylist) · [phishdestroy.com](https://phishdestroy.com)",
        "",
        "```",
        s60,
        "  BLOCKLIST TOTALS",
        s60,
        f"  🛡️  Primary list    : {total_p:>9,} domains",
        f"  🤝  Community list  : {total_c:>9,} domains",
        f"  📦  Combined        : {total_p + total_c:>9,} domains",
        s60,
        "  ADDED IN LAST 24 HOURS",
        s60d,
        f"  Primary            : +{len(new_p):,}",
        f"  Community          : +{len(new_c):,}",
        f"  This week          : +{read_badge('week_added'):,}",
        f"  This month         : +{read_badge('month_added'):,}",
        s60,
        "```",
        "",
    ]

    if new_p:
        L += [f"## 🚨 New Primary Domains (+{len(new_p):,})", "", "```"]
        L += [f"  {d}" for d in new_p]
        L += ["```", ""]

    if new_c:
        L += [f"## 🤝 New Community Domains (+{len(new_c):,})", "", "```"]
        L += [f"  {d}" for d in new_c]
        L += ["```", ""]

    if not new_p and not new_c:
        L += ["## ✅ No new domains in the last 24 hours", ""]

    L += [
        "---",
        "<sub>",
        "🛡️ **PhishDestroy** — Open-source anti-phishing threat intelligence.  ",
        "Updated automatically every day · Found a phishing domain? [Submit it here](https://github.com/phishdestroy/destroylist/issues/new/choose)",
        "</sub>",
    ]

    return "\n".join(L)


def publish(content: str, now: datetime):
    filename = f"destroylist-{now.strftime('%Y-%m-%d')}.md"
    payload = json.dumps({
        "description": f"PhishDestroy Daily Report — {now.strftime('%Y-%m-%d')}",
        "public": True,
        "files": {filename: {"content": content}}
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.github.com/gists",
        data=payload, method="POST",
        headers={
            "Authorization": f"Bearer {GIST_TOKEN}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print(f"✅ Gist created: {result['html_url']}")


def main():
    now = datetime.now(timezone.utc)
    print(f"Building gist for {now.strftime('%Y-%m-%d')}...")
    publish(build_content(now), now)


if __name__ == "__main__":
    main()
