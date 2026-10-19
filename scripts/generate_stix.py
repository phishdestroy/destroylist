#!/usr/bin/env python3
"""
generate_stix.py — Generate STIX 2.1 bundle from PhishDestroy active domains.

One identity, one indicator per DNS-verified active domain
(dns/active_domains.json, minus allow/allowlist.json), and a revoked copy of
every earlier indicator whose domain has since been allowlisted, so platforms
that imported a false positive retract it instead of keeping it forever.

Pass the previously published bundle with --previous: an unchanged domain then
keeps its object (same id, created, valid_from), as STIX requires for the same
object id. Published as the 'stix' GitHub Release asset by
.github/workflows/stix.yml, not committed, to avoid repo size bloat.
"""
import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from utils import PROJECT_ROOT, is_allowed, load_allowlist_split

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
PATTERN = re.compile(r"\[domain-name:value = '([^']+)'\]")
# Refuse to publish if the source shrank this much: a truncated
# active_domains.json must not wipe the feed.
MIN_ACTIVE_RATIO = 0.5


def make_indicator(domain, ts, salt=""):
    uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"phishdestroy:{domain}{salt}"))
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


def load_previous(path):
    """Map domain -> (live indicator or None, revoked indicators)."""
    previous = {}
    if not path:
        return previous
    for obj in json.loads(Path(path).read_text(encoding="utf-8"))["objects"]:
        match = PATTERN.fullmatch(obj.get("pattern", "")) if obj.get("type") == "indicator" else None
        if not match:
            continue
        entry = previous.setdefault(match.group(1), [None, []])
        if obj.get("revoked"):
            entry[1].append(obj)
        else:
            entry[0] = obj
    return previous


def build(domains, previous, exact, patterns, ts):
    active = sorted({d.strip().lower() for d in domains if d.strip()})
    active = [d for d in active if not is_allowed(d, exact, patterns)]
    active_set = set(active)

    indicators, revoked_count = [], 0
    for domain in active:
        live, revoked = previous.get(domain, (None, []))
        if live:
            indicators.append(live)
        else:
            # A revoked id can never become valid again; a re-listed domain
            # gets a new object.
            indicators.append(make_indicator(domain, ts, f":{ts}" if revoked else ""))

    for domain in sorted(previous):
        if domain in active_set or not is_allowed(domain, exact, patterns):
            continue
        live, revoked = previous[domain]
        if live:
            revoked = revoked + [dict(live, modified=ts, revoked=True)]
        indicators.extend(revoked)
        revoked_count += len(revoked)

    bundle = {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "objects": [IDENTITY] + indicators
    }
    return bundle, len(active), revoked_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--previous", type=Path, help="last published bundle.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    domains = json.loads((PROJECT_ROOT / "dns" / "active_domains.json").read_text(encoding="utf-8"))
    if not isinstance(domains, list):
        sys.exit("active_domains.json must be a JSON array")
    previous = load_previous(args.previous)
    exact, patterns = load_allowlist_split()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    bundle, active, revoked = build(domains, previous, exact, patterns, ts)
    previous_active = sum(1 for live, _ in previous.values() if live)
    if previous_active and active < previous_active * MIN_ACTIVE_RATIO:
        sys.exit(f"refusing to publish: {active} active indicators, previous bundle had {previous_active}")

    args.output.write_text(json.dumps(bundle, separators=(',', ':')), encoding="utf-8")
    size_mb = args.output.stat().st_size / 1024 / 1024
    print(f"Generated: {active} indicators, {revoked} revoked, {size_mb:.1f} MB → {args.output}")


if __name__ == "__main__":
    main()
