#!/usr/bin/env python3
"""Shared utilities for the destroylist pipeline."""
import ipaddress
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Set, Tuple

import tldextract

# ── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST_FILE = PROJECT_ROOT / "allow" / "allowlist.json"
APPROVED_ALLOWLIST_PATTERNS: Set[str] = {".microsoft", ".paypal.com"}

# ── Regex ────────────────────────────────────────────────────────────────────
IPV4_RE = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")
IPV6_RE = re.compile(r"^\[?[0-9a-fA-F:]{2,39}\]?$")

def _is_ip_addr(domain: str) -> bool:
    """Validate IPv4/IPv6 using the standard library."""
    try:
        ipaddress.ip_address(domain)
        return True
    except ValueError:
        return False

# ── Infrastructure providers (hosting platforms where subdomains ≠ root) ─────
PROVIDER_GROUPS: Dict[str, Set[str]] = {
    "multi_tenant_hosting": {
        "vercel.app", "netlify.app", "github.io", "render.com", "onrender.com",
        "digitaloceanspaces.com", "windows.net", "fastly.net", "cprapid.com",
        "sslip.io", "duckdns.org", "dynv6.net", "replit.dev", "replit.app",
        "surge.sh", "typedream.app", "hostingersite.com", "firebaseapp.com",
        "web.app", "pages.dev", "workers.dev", "ghost.io", "amazonaws.com",
        "cloudfront.net", "fly.dev", "fly.io", "railway.app", "herokuapp.com",
        "azurewebsites.net", "ngrok.io", "ngrok-free.app", "trycloudflare.com",
        "glitch.me", "stackblitz.io", "stackblitz.com", "codesandbox.io",
        "webcontainer.io", "gitlab.io", "bitbucket.io", "gitpod.io",
        "edgeone.dev", "edgeone.app", "r2.dev", "amplifyapp.com",
        "lovable.app", "wasmer.app", "mybluehost.me", "wpenginepowered.com",
        "tiiny.host", "hosted.app", "temporary.site", "rollout.site",
        "mdbgo.io", "onespace.app", "dora.run", "ondigitalocean.app",
        "cloudaccess.host", "cloudwaysapps.com", "deno.dev", "oraclecloud.com",
        "statuspage.io", "cloudflare.net", "scw.cloud", "sendgrid.net",
        "awstrack.me", "us.com",
    },
    "site_builders": {
        "weebly.com", "weeblysite.com", "wixsite.com", "wixstudio.com", "wordpress.com",
        "blogspot.com", "blogspot.am", "blogspot.be", "blogspot.ru", "blogspot.it",
        "blogspot.cz", "blogspot.md", "blogspot.mk", "blogspot.hk", "blogspot.in",
        "blogspot.pe", "square.site", "webflow.io",
        "godaddysites.com", "webcindario.com", "home.pl", "pineapple.page",
        "gitbook.io", "carrd.co", "framer.app", "framer.ai", "framer.media", "framer.wiki",
        "softr.app", "bubble.io", "bubbleapps.io", "strikingly.com",
        "daftpage.com", "created.app", "canva.site", "framer.website",
        "baseportal.io", "flazio.com", "odoo.com", "squarespace.com",
    },
    "decentralized_storage": {
        "ipfs.io", "cloudflare-ipfs.com", "dweb.link", "infura-ipfs.io",
        "eth.limo", "fleek.co",
        "arweave.net", "ic0.app", "ipfs.w3s.link", "4everland.app", "pinata.cloud",
    },
    "saas_platforms": {
        "jotform.com", "npoint.io", "onelink.me", "teachable.com",
        "typeform.com", "zapier.app",
    },
}
INFRA_ROOTS: Set[str] = set().union(*PROVIDER_GROUPS.values())

# A URL path is part of the identity on these services. Bare service roots are
# not publishable/allowlistable, while an exact tenant hostname may cover paths
# on that same tenant without affecting sibling tenants.
PATH_SCOPED_HOSTS: Set[str] = {
    "npoint.io", "api.npoint.io", "pastebin.com", "hastebin.com", "paste.ee",
    "dpaste.org", "bit.ly", "tinyurl.com", "cutt.ly", "t.co", "goo.gl",
    "ow.ly", "is.gd", "v.gd", "t.me", "discord.gg", "discord.com",
    "docs.google.com", "drive.google.com", "forms.gle", "sites.google.com",
    "gist.github.com", "raw.githubusercontent.com", "ipfs.io",
    "gateway.pinata.cloud", "cloudflare-ipfs.com", "dweb.link",
    "forms.office.com", "airtable.com", "typeform.com", "jotform.com",
    "framer.app", "framer.media", "webflow.io", "carrd.co",
    "notion.site", "coda.io", "linktr.ee", "bio.link", "beacons.ai",
    "solo.to", "replit.dev", "glitch.me", "codepen.io", "jsfiddle.net",
    "codesandbox.io",
}


# ── Domain parsing ───────────────────────────────────────────────────────────

def normalize_entry(entry: str) -> str:
    """Lowercase the hostname while preserving a case-sensitive URL path."""
    s = str(entry).strip()
    lowered = s.lower()
    if lowered.startswith("https://"):
        s = s[8:]
    elif lowered.startswith("http://"):
        s = s[7:]
    if s.startswith(".") and "/" not in s:
        return "." + s[1:].rstrip(".").lower()
    host, separator, path = s.partition("/")
    host = host.strip(".").lower()
    return host + (separator + path if separator else "")


def extract_domain(entry: str) -> str:
    """Strip scheme, path, query, and fragment from an entry.

    'https://github.com/ledger-live-download' -> 'github.com'
    """
    s = normalize_entry(entry)
    return s.split("/")[0].split("?")[0].split("#")[0]


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
    if (
        is_infra_root(domain) or domain in PATH_SCOPED_HOSTS
    ) and "/" not in normalize_entry(entry):
        return False
    tld = domain.rsplit(".", 1)[-1]
    if tld.startswith("xn--"):
        return len(tld) >= 6
    return len(tld) >= 2 and tld.isalpha()


def is_ip(entry: str) -> bool:
    """Check if the domain part is an IPv4 or IPv6 address."""
    domain = extract_domain(entry)
    return _is_ip_addr(domain)


# ── JSON I/O ─────────────────────────────────────────────────────────────────

def load_json(path: Path):
    """Load a JSON file, return parsed data or None on error."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as e:
        log(f"{path.name}: read error: {e}", "error")
        return None
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
        s = normalize_entry(d)
        if s:
            out.append(s)
    return out


def save_json(path: Path, data, indent: int = 2):
    """Write data as JSON atomically, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(json.dumps(data, indent=indent, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, path)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise


# ── Allowlist ────────────────────────────────────────────────────────────────

def load_allowlist() -> Set[str]:
    """Load allowlist as a flat set of domains."""
    data = load_json(ALLOWLIST_FILE)
    if isinstance(data, list):
        return {normalize_entry(d) for d in data if d}
    return set()


def load_allowlist_split() -> Tuple[Set[str], Set[str]]:
    """Load allowlist split into (exact, pattern) sets.

    Pattern entries start with '.' (e.g. '.example.com').
    """
    entries = load_allowlist()
    patterns = {d for d in entries if d.startswith(".")}
    unknown_patterns = patterns - APPROVED_ALLOWLIST_PATTERNS
    if unknown_patterns:
        values = ", ".join(sorted(unknown_patterns))
        raise ValueError(f"unapproved allowlist suffix pattern(s): {values}")
    exact = entries - patterns
    return exact, patterns


def is_allowed(domain: str, exact: Set[str], patterns: Set[str]) -> bool:
    """Match an exact entry/host scope or an explicitly approved pattern."""
    candidate = normalize_entry(domain)
    if candidate in exact:
        return True
    host = extract_domain(candidate)
    if "/" in candidate and host in exact and host not in PATH_SCOPED_HOSTS:
        return True
    return any(host.endswith(p) or host == p[1:] for p in patterns)


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
