<div align="center">

<img src="https://raw.githubusercontent.com/phishdestroy/destroylist/main/.github/banner_security.svg" alt="Security Policy" width="900"/>

<br>

[![Destroylist](https://img.shields.io/badge/destroylist-FF0000?style=flat-square&logo=github&logoColor=white)](https://github.com/phishdestroy/destroylist)
[![API](https://img.shields.io/badge/API-api.destroy.tools-000000?style=flat-square)](https://api.destroy.tools)
[![Appeals](https://img.shields.io/badge/Appeals-phishdestroy.io-FF0000?style=flat-square)](https://phishdestroy.io/appeals/)

</div>

---

## Reporting Security Issues

> [!WARNING]
> Do **not** report infrastructure vulnerabilities through public GitHub issues.

If you find a security issue in our systems, scripts, or data pipeline:

**security@phishdestroy.io** — we respond within 48 hours.

---

## Blocklist Accuracy

### Your domain was blocked by mistake

**Primary lists** (`list.json`, `dns/active_domains.json`, `dns/content_active.json`):

| Method | Link |
|:-------|:-----|
| Appeals form | [phishdestroy.io/appeals](https://phishdestroy.io/appeals/) |
| GitHub issue | [Open appeal →](https://github.com/phishdestroy/destroylist/issues/new?template=appeal.yml) |

Approved domains are added to `allow/allowlist.json` and automatically removed from all lists within the next update cycle.

**Community lists** (`community/*`):

> [!CAUTION]
> Auto-aggregated from 13+ external sources. Manual removal is not possible — report to the original feed provider and it will be removed on next sync.

### A malicious domain is missing

[Submit addition →](https://github.com/phishdestroy/destroylist/issues/new?template=blocklist-addition.yml)

---

## Data Feeds

| Feed | Frequency | Content |
|:-----|:---------:|:--------|
| `list.json` | Real-time | Curated phishing domains |
| `dns/active_domains.json` | Every 2h | DNS-verified active subset |
| `dns/content_active.json` | Every 12h | HTTP content-verified active |
| `community/blocklist.json` | Every 2h | Aggregated from 13+ sources |
| `community/live_blocklist.json` | Every 2h | DNS-verified community subset |
| `community/content_live.json` | Every 24h | Content-verified community subset |

---

## On Repository Attacks

This repository periodically receives harassment from operators of blocked scam domains — fake DMCA claims, mass-reports, star manipulation, coordinated abuse campaigns.

This is expected. It changes nothing.

Domains stay blocked. The list keeps growing. Registrars and platforms don't reverse legitimate abuse decisions because someone filed a hundred fake reports.

---

## For Victims

If you were defrauded by a domain in our list, check its addition date via [commit history](https://github.com/phishdestroy/destroylist/commits/main/) or the [Telegram channel](https://t.me/destroy_phish).

Per ICANN rules, registrars must review abuse complaints within 24 hours. If fraud occurred after the domain was listed, the registrar or hosting provider may share liability for your loss.

---

## Archive Access

Historical data: 500,000+ domains over 5+ years — available for academic and security research.

**contact@phishdestroy.io**

---

## License

MIT — free for any use with attribution.

<div align="center">

[![back](https://img.shields.io/badge/←_destroylist-FF0000?style=flat-square)](https://github.com/phishdestroy/destroylist)

</div>
