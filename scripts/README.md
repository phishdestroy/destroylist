# ⚙️ Scripts

<div align="center">
<img src="banner.svg" alt="Scripts" width="900"/>
</div>

Automation, analytics, and validation utilities for the destroylist pipeline.

Each script runs independently.

---

## 📜 Script Reference

### `validate_json.py`

Pre-pipeline JSON integrity checks.

- Validates syntax, structure, duplicates
- Checks for empty entries, IPs, invalid domains
- Runs before and after pipeline steps

**Targets:** `list.json`, `allow/allowlist.json`, `community/blocklist.json`, `community/live_blocklist.json`, `community/content_live.json`, `dns/active_domains.json`, `dns/content_active.json`

---

### `validate_and_clean.py`

Cleans and validates domain lists.

- Root-domain collapsing
- Allowlist enforcement
- Invalid entry and IP removal
- Duplicate removal

**Output:** Updated `list.json`, `community/blocklist.json`, `community/live_blocklist.json`, `community/content_live.json`, `dns/active_domains.json`, `dns/content_active.json`

---

### `smart_aggregator.py`

Aggregates external blocklist sources.

- SHA-256 change tracking
- Multi-source ingestion (13+ feeds)
- Normalization and deduplication
- Allowlist filtering

**Output:** `community/blocklist.json` + `community/state.json`

---

### `build_rootlist.py`

Extracts registrable root domains.

- Filters subdomains to roots only
- Separates infrastructure providers
- DNS validation

**Output:** `rootlist/*.json`, `rootlist/*.txt` (root domains, services, provider analytics)

---

### `json_to_txt.py`

Converts JSON lists to multiple formats.

- Plain TXT
- Hosts file (`0.0.0.0 domain.com`)
- AdBlock Plus (`||domain.com^`) with subscription headers
- Dnsmasq config (`address=/domain.com/0.0.0.0`)
- Unbound config (`local-zone: "domain.com" always_nxdomain`)
- RPZ zone (`domain.com CNAME .`)

**Output:** `rootlist/formats/` (6 formats x 4 datasets), `list.txt`, `dns/*.txt`, `community/*.txt`

---

### `build_shards.py`

Splits the primary list into array chunks.

- 3,000 domains per shard
- Auto-creates output directory

**Output:** `rootlist/arrays/part_000.json` ... `part_NNN.json`

---

### `update_counts.py`

Generates badge count files.

- Primary, DNS-validated, community counts
- Content-verified counts

**Output:** `count.json`, `dns/active_count.json`, `dns/content_active_count.json`, `community/count.json`, `community/live_count.json`, `community/content_active_count.json`

---

### `calculate_stats.py`

Tracks additions over time via git history.

- Last 24 hours, weekly, monthly deltas
- Weekly and monthly archive snapshots

**Output:** `dns/today_added.json`, `dns/week_added.json`, `dns/month_added.json`, `archives/`

---

### `update_gist.py`

Updates a GitHub Gist with current statistics.

- Reads all badge files
- Pushes formatted markdown to Gist
- Requires `GIST_TOKEN` and `GIST_ID` env vars

---

## 🔄 Execution Order

Full pipeline:

```
1. validate_json.py       (pre-check)
2. smart_aggregator.py    (fetch sources)
3. validate_and_clean.py  (clean all lists)
4. validate_json.py       (post-check)
5. update_counts.py       (badge counts)
6. json_to_txt.py         (format conversion)
7. build_rootlist.py      (root domains)
8. build_shards.py        (array splitting)
9. calculate_stats.py     (time-period stats)
```

---

## 📋 Requirements

- Python 3.10+
- Dependencies: `pip install -r requirements.txt`
- Run from project root
- Output folders auto-created
