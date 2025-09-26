# Active Domains Liveness (`active/`)

Short module that **checks DNS liveness** of domains from our main list and keeps a cached, fast‑to‑use split of **active** vs **dead**.

[IMPORTANT] **Apex domains only** (lowercase). DNS‑resolvable ≠ legitimate — use allowlists separately for exceptions.

---

## What this folder contains

* `active_domains.py` — liveness checker (parallel + cache)
* `active_domains.json` — current **live** domains
* `dead_domains.json` — current **inactive** domains (NXDOMAIN/timeout/no‑answer)
* `active_count.json` — Shields‑style badge JSON with live count
* `dns_check_cache.json` — local DNS cache (TTL 24h)

---

## How it works

1. **Fetch** source domains from our repo list:
   [https://github.com/phishdestroy/destroylist/raw/main/list.json](https://github.com/phishdestroy/destroylist/raw/main/list.json)
2. **Merge** with previous `active_domains.json` to avoid regressions.
3. **Resolve in parallel** (A/AAAA, custom resolvers `1.1.1.1`, `8.8.8.8`, `9.9.9.9`),
   with per‑query timeout **2s** and up to **500 workers**.
4. **Cache** per‑domain result in `dns_check_cache.json` for **86400s**
   to speed up subsequent runs.
5. **Write outputs**: live/dead lists + `active_count.json` summary.
6. **CI outputs** (for GitHub Actions): `added_count`, `removed_count`, `has_changes`.

---

## Quick start (Windows)

```powershell
# Python 3.11+
py -m venv .venv
. .venv\Scripts\activate
pip install -r requirements.txt
py active\active_domains.py          # uses cache
py active\active_domains.py --no-cache  # ignore cache this run
```

**requirements.txt**

```
requests==2.32.3
 dnspython==2.6.1
 tldextract==5.1.2
 tqdm==4.66.5
```

---

## JSON formats

* `active_domains.json` / `dead_domains.json`: sorted array of domains
* `active_count.json`:

```json
{"schemaVersion":1,"label":"Active Phishing Domains","message":"1234","color":"purple"}
```

* `dns_check_cache.json` (example entry):

```json
{"example.org":{"status":"live","timestamp":1727347200}}
```

---

## Notes

* Resolver/timeouts/workers are configurable inside the script: `CUSTOM_RESOLVERS`, `DNS_TIMEOUT`, `MAX_WORKERS`.
* Liveness stats are logged; unexpected JSON from source is handled safely.
* Source list URL (full): [https://github.com/phishdestroy/destroylist/raw/main/list.json](https://github.com/phishdestroy/destroylist/raw/main/list.json)
