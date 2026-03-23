#!/usr/bin/env python3
"""Shared utilities for the destroylist pipeline."""
import json
import re
import sys
from pathlib import Path
from typing import Dict, Set, Tuple

import tldextract

# ── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST_FILE = PROJECT_ROOT / "allow" / "allowlist.json"

# ── Regex ────────────────────────────────────────────────────────────────────
IPV4_RE = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")
IPV6_RE = re.compile(r"^\[?[0-9a-fA-F:]{2,39}\]?$")

# ── Infrastructure providers (hosting platforms where subdomains ≠ root) ─────
PROVIDER_GROUPS: Dict[str, Set[str]] = {
    "multi_tenant_hosting": {
        "vercel.app", "netlify.app", "github.io", "render.com", "onrender.com",
        "digitaloceanspaces.com", "windows.net", "fastly.net", "cprapid.com",
        "sslip.io", "duckdns.org", "replit.dev", "surge.sh", "typedream.app",
        "hostingersite.com", "firebaseapp.com", "web.app", "pages.dev",
        "workers.dev", "ghost.io", "amazonaws.com", "cloudfront.net",
        "fly.dev", "fly.io", "railway.app", "herokuapp.com", "azurewebsites.net",
        "ngrok.io", "ngrok-free.app", "glitch.me", "stackblitz.io",
        "gitlab.io", "bitbucket.io", "gitpod.io",
    },
    "site_builders": {
        "weebly.com", "weeblysite.com", "wixsite.com", "wordpress.com",
        "blogspot.com", "blogspot.am", "square.site", "webflow.io",
        "godaddysites.com", "webcindario.com", "home.pl", "pineapple.page",
        "gitbook.io", "carrd.co", "framer.app", "framer.ai",
        "softr.app", "bubble.io", "strikingly.com",
    },
    "decentralized_storage": {
        "ipfs.io", "cloudflare-ipfs.com", "dweb.link", "infura-ipfs.io",
        "eth.limo", "fleek.co",
    },
    "saas_platforms": {
        "teachable.com",
    },
}
INFRA_ROOTS: Set[str] = set().union(*PROVIDER_GROUPS.values())


# ── Domain parsing ───────────────────────────────────────────────────────────

def extract_domain(entry: str) -> str:
    """Strip path, query, and fragment from an entry.

    'github.com/ledger-live-download' -> 'github.com'
    """
    return entry.split("/")[0].split("?")[0].split("#")[0]


def get_root(host: str) -> str:
    """Extract registrable root domain via tldextract."""
    ext = tldextract.extract(host)
    rd = (ext.top_domain_under_public_suffix
          if hasattr(ext, "top_domain_under_public_suffix")
          else ext.registered_domain)
    return rd.lower() if rd else ""


def is_infra_root(domain: str) -> bool:
    """Check if domain is a bare infrastructure/hosting root (e.g. pages.dev).

    These must never appear in blocklists — only their subdomains are malicious.
    """
    return domain.lower() in INFRA_ROOTS


def is_valid_entry(entry: str) -> bool:
    """Check if an entry is a plausible domain.

    Rejects: empty, no dots, pure numbers, single-char/non-alpha TLD,
    bare infrastructure roots (pages.dev, vercel.app, etc.).
    Accepts Punycode TLDs (xn--*).
    """
    if not entry:
        return False
    domain = extract_domain(entry)
    if not domain or "." not in domain:
        return False
    if not any(c.isalpha() for c in domain):
        return False
    if is_infra_root(domain):
        return False
    tld = domain.rsplit(".", 1)[-1]
    if tld.startswith("xn--"):
        return len(tld) >= 6
    return len(tld) >= 2 and tld.isalpha()


def is_ip(entry: str) -> bool:
    """Check if the domain part is an IPv4 or IPv6 address."""
    domain = extract_domain(entry)
    return bool(IPV4_RE.fullmatch(domain) or IPV6_RE.fullmatch(domain))


# ── JSON I/O ─────────────────────────────────────────────────────────────────

def load_json(path: Path):
    """Load a JSON file, return parsed data or None on error."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        log(f"{path.name}: invalid JSON at line {e.lineno}: {e.msg}", "error")
        return None


def load_json_list(path: Path) -> list:
    """Load a JSON file expected to contain a flat domain list."""
    data = load_json(path)
    if data is None:
        return []
    arr = data if isinstance(data, list) else data.get("domains", [])
    out = []
    for d in arr:
        if not d:
            continue
        s = str(d).strip().lower()
        s = s.removeprefix("https://").removeprefix("http://")
        if s:
            out.append(s)
    return out


def save_json(path: Path, data, indent: int = 2):
    """Write data as JSON, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=indent, ensure_ascii=False), encoding="utf-8")


# ── Allowlist ────────────────────────────────────────────────────────────────

def load_allowlist() -> Set[str]:
    """Load allowlist as a flat set of domains."""
    data = load_json(ALLOWLIST_FILE)
    if isinstance(data, list):
        return {str(d).strip().lower() for d in data if d}
    return set()


def load_allowlist_split() -> Tuple[Set[str], Set[str]]:
    """Load allowlist split into (exact, pattern) sets.

    Pattern entries start with '.' (e.g. '.example.com').
    """
    entries = load_allowlist()
    patterns = {d for d in entries if d.startswith(".")}
    exact = entries - patterns
    return exact, patterns


def is_allowed(domain: str, exact: Set[str], patterns: Set[str]) -> bool:
    """Check if a domain matches the allowlist (exact or suffix pattern)."""
    if domain in exact:
        return True
    return any(domain.endswith(p) or domain == p[1:] for p in patterns)


# ── Badge generation ─────────────────────────────────────────────────────────

def make_badge(label: str, message, color: str = "important") -> dict:
    """Create a shields.io endpoint badge object."""
    return {
        "schemaVersion": 1,
        "label": label,
        "message": str(message),
        "color": color,
    }


# ── Logging ──────────────────────────────────────────────────────────────────

_PREFIXES = {
    "info": " ",
    "ok":   "✓",
    "warn": "!",
    "error": "✗",
    "step": "→",
}


def log(msg: str, level: str = "info"):
    """Print a consistently formatted log line."""
    prefix = _PREFIXES.get(level, " ")
    stream = sys.stderr if level == "error" else sys.stdout
    print(f"  {prefix} {msg}", file=stream, flush=True)
