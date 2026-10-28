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

For either route, send the domain and a short explanation. No evidence or proof of ownership is required. Screenshots and links are optional; we review the listing ourselves.

Approved appeals remove the domain from our published data. Operator-confirmed false positives are also added to `allow/allowlist.json` to prevent repeated listing. Automatic approval does not itself add a permanent allowlist entry.

**Community lists** (`community/*`):

> [!CAUTION]
Our community feeds are generated automatically. To correct a listing in our published copies, [submit an appeal](https://phishdestroy.io/appeals/); reviewed exclusions are applied through our allowlist. The original source maintains its own feed and must be contacted separately for a correction there.

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

ICANN's [RAA §3.18.1](https://www.icann.org/resources/pages/approved-with-specs-2013-09-17-en#3.18.1) requires reasonable and prompt steps to investigate and respond appropriately to abuse reports. The **24-hour review requirement** in [§3.18.2](https://www.icann.org/resources/pages/approved-with-specs-2013-09-17-en#3.18.2) applies to well-founded reports of illegal activity from the specified authorities, submitted through the registrar's dedicated contact. If fraud occurred after the domain was listed, the registrar or hosting provider may share liability for your loss.

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
