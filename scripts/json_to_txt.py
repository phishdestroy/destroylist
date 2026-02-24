#!/usr/bin/env python3
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Set

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
FORMATS_DIR = PROJECT_ROOT / "rootlist" / "formats"
ALLOWLIST_FILE = PROJECT_ROOT / "allow" / "allowlist.json"

SOURCES = {
    "primary": PROJECT_ROOT / "list.json",
    "primary_active": PROJECT_ROOT / "dns" / "active_domains.json",
    "community": PROJECT_ROOT / "community" / "blocklist.json",
    "community_active": PROJECT_ROOT / "community" / "live_blocklist.json",
}

IPV4_RE = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")


def load_allowlist() -> Set[str]:
    """Load allowlist domains for filtering at output generation time."""
    if not ALLOWLIST_FILE.exists():
        return set()
    try:
        data = json.loads(ALLOWLIST_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return {str(d).strip().lower() for d in data if d}
    except Exception:
        pass
    return set()


def load_domains(filepath: Path, allowlist: Set[str]) -> list:
    if not filepath.exists():
        return []
    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
        domains = data if isinstance(data, list) else data.get("domains", [])
        clean = set()
        for d in domains:
            d = str(d).strip().lower().replace("https://", "").replace("http://", "").split("/")[0].split("?")[0]
            if not d or "." not in d:
                continue
            # Skip IP addresses — this is a domain blacklist
            if IPV4_RE.fullmatch(d):
                continue
            # Skip entries without alphabetic characters (numeric garbage like '0.512752')
            if not any(c.isalpha() for c in d):
                continue
            # Skip domains that are in the allowlist (handles path-based entries
            # like 'github.com/something' where the extracted domain 'github.com'
            # is a legitimate allowlisted domain)
            if d in allowlist:
                continue
            clean.add(d)
        return sorted(clean)
    except Exception:
        return []


def header(name: str, count: int, fmt: str, c: str = "#") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"{c} Destroylist - {name} | {fmt} | {count} domains | {ts}\n{c} https://github.com/phishdestroy/destroylist\n\n"


def write(path: Path, content: str):
    path.write_text(content, encoding="utf-8")


def main():
    FORMATS_DIR.mkdir(parents=True, exist_ok=True)
    allowlist = load_allowlist()

    for name, src in SOURCES.items():
        domains = load_domains(src, allowlist)
        if not domains:
            continue

        out = FORMATS_DIR / name
        out.mkdir(exist_ok=True)
        n = name.replace("_", " ").title()

        write(out / "domains.txt", header(n, len(domains), "plain") + "\n".join(domains) + "\n")
        write(out / "hosts.txt", header(n, len(domains), "hosts") + "\n".join(f"0.0.0.0 {d}" for d in domains) + "\n")
        write(out / "adblock.txt", header(n, len(domains), "adblock", "!") + "[Adblock Plus]\n" + "\n".join(f"||{d}^" for d in domains) + "\n")
        write(out / "dnsmasq.conf", header(n, len(domains), "dnsmasq") + "\n".join(f"address=/{d}/0.0.0.0" for d in domains) + "\n")

        print(f"{name}: {len(domains)}")

    primary = load_domains(SOURCES["primary"], allowlist)
    if primary:
        write(PROJECT_ROOT / "list.txt", "\n".join(primary) + "\n")


if __name__ == "__main__":
    main()