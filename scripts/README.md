<p align="center">
  <img src="../image.png" width="900">
</p>

# Scripts Directory Overview

This folder contains automation, analytics, aggregation, and validation utilities used across the destroylist lifecycle.
Each script is focused on a specific operational role and is designed to run independently.

## 📌 Scripts

---

### `build_rootlist.py`

Processes full lists and extracts registrable root domains.

**Primary functions:**

* Filtering subdomains into root-only versions
* Separating infrastructure/provider platforms
* Exporting clean structured JSON outputs

Outputs include:

* `rootlist/active_root_domains.json`
* `rootlist/providers_root_domains.json`
* `rootlist/online_root_domains.json`
* Community variants

---

### `calculate_stats.py`

Analyzes additions over time and generates statistical badges.

Tracks changes for:

* last 24 hours
* weekly delta
* monthly delta

Produces:

* `dns/today_added.json`
* `dns/week_added.json`
* `dns/month_added.json`

---

### `json_to_txt.py`

Converts JSON domain lists into multiple formatted outputs.

Formats include:

* plain TXT
* hosts file format
* Adblock list format
* dnsmasq configuration

Outputs are grouped by dataset source.

---

### `smart_aggregator.py`

Pulls data from external blocklist providers, normalizes domains and merges them into a single dataset.

Features:

* SHA-256 signature tracking
* Change detection and summarization
* Multi‑source ingest framework

Generates:

* unified `community/blocklist.json`
* badge statistics
* commit update message

---

### `update_counts.py`

Generates count badges for multiple datasets:

* primary dataset
* DNS‑validated dataset
* aggregated community list
* live DNS‑validated community list

Produces files used in README badges.

---

### `validate_and_clean.py`

Cleans input domain lists using allowlist enforcement and deduplication.

Capabilities:

* root‑domain collapsing
* allow‑pattern matching
* removal of duplicates

Updates the canonical `list.json` automatically.

---

## 📂 Script Execution

Typical execution order when generating a complete pipeline:

```
validate_and_clean.py
smart_aggregator.py
build_rootlist.py
json_to_txt.py
update_counts.py
calculate_stats.py
```

Each script can run independently without dependencies on others.

## 🧪 Notes

* All scripts assume project root execution level
* Python 3.10+ required
* Output folders auto‑generated when missing
