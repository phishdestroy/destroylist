# ⚙️ Scripts

![Scripts Banner](image.png)

Automation, analytics, and validation utilities for the destroylist pipeline.

Each script runs independently.

---

## 📜 Script Reference

### `validate_and_clean.py`

Cleans and validates domain lists.

- Root-domain collapsing
- Allowlist enforcement
- Duplicate removal
- Updates `list.json` automatically

---

### `smart_aggregator.py`

Aggregates external blocklist sources.

- SHA-256 change tracking
- Multi-source ingestion
- Normalization and deduplication

**Output:** `community/blocklist.json` + stats

---

### `build_rootlist.py`

Extracts registrable root domains.

- Filters subdomains → roots only
- Separates infrastructure providers
- DNS validation

**Output:** `rootlist/*.json` files

---

### `json_to_txt.py`

Converts JSON lists to multiple formats.

- Plain TXT
- Hosts file (`0.0.0.0 domain.com`)
- AdBlock (`||domain.com^`)
- Dnsmasq config

**Output:** `rootlist/formats/`

---

### `update_counts.py`

Generates badge count files.

- Primary dataset count
- DNS-validated count
- Community counts

**Output:** `count.json`, `dns/active_count.json`, etc.

---

### `calculate_stats.py`

Tracks additions over time.

- Last 24 hours
- Weekly delta
- Monthly delta

**Output:** `dns/today_added.json`, `dns/week_added.json`, `dns/month_added.json`

---

## 🔄 Execution Order

Full pipeline:

```
1. validate_and_clean.py
2. smart_aggregator.py
3. build_rootlist.py
4. json_to_txt.py
5. update_counts.py
6. calculate_stats.py
```

---

## 📋 Requirements

- Python 3.10+
- Run from project root
- Output folders auto-created
