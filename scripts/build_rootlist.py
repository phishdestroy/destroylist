import json
import os
from pathlib import Path
from typing import Iterable, Set

import dns.resolver
import tldextract

ROOT = Path(__file__).resolve().parents[1]

SOURCE_DNS_ACTIVE = ROOT / "dns" / "active_domains.json"

OUT_DIR = ROOT / "rootlist"
OUT_ACTIVE = OUT_DIR / "active_root_domains.json"
OUT_INVALID = OUT_DIR / "invalid_root_domains.json"

INFRA_ROOTS: Set[str] = {
    "ipfs.io", "cloudflare-ipfs.com", "dweb.link", "infura-ipfs.io", "eth.limo",
    "vercel.app", "netlify.app", "github.io", "render.com", "onrender.com",
    "digitaloceanspaces.com", "windows.net", "fastly.net", "cprapid.com",
    "sslip.io", "duckdns.org", "replit.dev", "surge.sh", "typedream.app",
    "hostingersite.com", "firebaseapp.com", "web.app", "pages.dev", "workers.dev",
    "weebly.com", "weeblysite.com", "wixsite.com", "wordpress.com",
    "blogspot.com", "blogspot.am", "webcindario.com", "home.pl",
    "square.site", "webflow.io", "godaddysites.com", "pineapple.page",
    "gitbook.io",
    "fleek.co",
    "teachable.com",
}


def load_domains(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        arr = data.get("domains", [])
    else:
        arr = data
    out = []
    for v in arr:
        if isinstance(v, str):
            d = v.strip().strip(".").lower()
            if d:
                out.append(d)
    return out


def get_root(host: str) -> str | None:
    ext = tldextract.extract(host)
    return ext.registered_domain.lower() if ext.registered_domain else None


def dns_ok(domain: str) -> bool:
    resolver = dns.resolver.Resolver()
    resolver.timeout = 3
    resolver.lifetime = 3
    for r in ("A", "AAAA", "CNAME", "MX", "NS"):
        try:
            ans = resolver.resolve(domain, r, raise_on_no_answer=False)
            if ans.rrset:
                return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            return False
        except dns.exception.DNSException:
            continue
    return False


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    fqdn_list = load_domains(SOURCE_DNS_ACTIVE)

    root_candidates = set()
    for fqdn in fqdn_list:
        rd = get_root(fqdn)
        if not rd:
            continue
        if rd in INFRA_ROOTS:
            continue
        root_candidates.add(rd)

    valid = set()
    invalid = set()

    for rd in root_candidates:
        if dns_ok(rd):
            valid.add(rd)
        else:
            invalid.add(rd)

    OUT_ACTIVE.write_text(
        json.dumps(
            {
                "meta": {
                    "name": "destroylist root-only dataset",
                    "dns_validated": True,
                    "infra_excluded": True,
                },
                "domains": sorted(valid),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    OUT_INVALID.write_text(
        json.dumps(
            {
                "meta": {
                    "name": "destroylist root-only dataset (invalid DNS)",
                },
                "domains": sorted(invalid),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("[OK] rootlist generated")
    print("valid:", len(valid))
    print("invalid:", len(invalid))


if __name__ == "__main__":
    main()
