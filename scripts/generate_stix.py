#!/usr/bin/env python3
"""
generate_stix.py — Generate STIX 2.1 bundle from PhishDestroy active domains.
Output: stix/bundle.json (all active DNS-verified domains as IoC indicators)
Uploaded to GitHub Release 'stix' to avoid repo size bloat.
"""
import json
import uuid
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

IDENTITY_ID = "identity--9a8b1427-74d5-4b3e-88a7-b4fa5be17b2c"
IDENTITY = {
    "type": "identity",
    "spec_version": "2.1",
    "id": IDENTITY_ID,
    "created": "2024-01-01T00:00:00.000Z",
    "modified": "2024-01-01T00:00:00.000Z",
    "name": "PhishDestroy",
    "identity_class": "organization",
    "description": "PhishDestroy threat intelligence — phishing and scam domain blocklist",
    "contact_information": "contact@phishdestroy.io"
}

def make_indicator(domain, ts):
    uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"phishdestroy:{domain}"))
    return {
        "type": "indicator",
        "spec_version": "2.1",
        "id": f"indicator--{uid}",
        "created_by_ref": IDENTITY_ID,
        "created": ts,
        "modified": ts,
        "name": f"Phishing domain: {domain}",
        "indicator_types": ["malicious-activity"],
        "pattern": f"[domain-name:value = '{domain}']",
        "pattern_type": "stix",
        "valid_from": ts,
        "labels": ["phishing"],
        "confidence": 85
    }

def main():
    active_file = PROJECT_ROOT / "dns" / "active_domains.json"
    if not active_file.exists():
        print("active_domains.json not found"); sys.exit(1)

    domains = json.loads(active_file.read_text())
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    objects = [IDENTITY] + [make_indicator(d, ts) for d in domains]

    bundle = {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "spec_version": "2.1",
        "objects": objects
    }

    stix_dir = PROJECT_ROOT / "stix"
    stix_dir.mkdir(exist_ok=True)

    out = stix_dir / "bundle.json"
    out.write_text(json.dumps(bundle, separators=(',', ':')))
    size_mb = out.stat().st_size / 1024 / 1024
    print(f"Generated: {len(domains)} indicators, {size_mb:.1f} MB → {out}")

if __name__ == "__main__":
    main()
