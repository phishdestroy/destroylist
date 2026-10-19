<div align="center">

<img src="banner.svg" alt="STIX 2.1" width="900"/>

# STIX 2.1 Bundle

**Destroylist phishing domains as STIX 2.1 indicators — ready to import into SIEM and threat-intelligence platforms**

<br>

![format](https://img.shields.io/badge/format-STIX_2.1-FF0000?style=for-the-badge)
![indicators](https://img.shields.io/badge/indicators-121%2C467-000000?style=for-the-badge)

<br>

[![Destroylist](https://img.shields.io/badge/destroylist-source-FF0000?style=flat-square&logo=github)](https://github.com/phishdestroy/destroylist)
[![API](https://img.shields.io/badge/API-live-000000?style=flat-square)](https://api.destroy.tools)
[![Feeds](https://img.shields.io/badge/data_feeds-FF0000?style=flat-square)](https://github.com/phishdestroy/destroylist#-data-feeds)

</div>

---

## Overview

`bundle.json` is a single [STIX 2.1](https://oasis-open.github.io/cti-documentation/stix/intro) bundle: one
`identity` object for PhishDestroy and one `indicator` per DNS-verified active domain from
[`dns/active_domains.json`](../dns/).

> [!NOTE]
> This bundle is a snapshot generated on **2026-08-17** and is not refreshed automatically.
> Domains cleared on appeal (listed in [`allow/allowlist.json`](../allow/allowlist.json)) were removed from it on 2026-10-19.
> For current data use the [live feeds](../dns/) or regenerate it (see below).

## 📂 Contents

| File | Description |
|:-----|:------------|
| `bundle.json` | STIX 2.1 bundle — 1 identity + 121,467 indicators (≈ 59 MB, minified) |

**Indicator example:**

```json
{
  "type": "indicator",
  "spec_version": "2.1",
  "name": "Phishing domain: example-phish.icu",
  "indicator_types": ["malicious-activity"],
  "pattern": "[domain-name:value = 'example-phish.icu']",
  "pattern_type": "stix",
  "labels": ["phishing"],
  "confidence": 85,
  "created_by_ref": "identity--9a8b1427-74d5-4b3e-88a7-b4fa5be17b2c"
}
```

## 🔌 Use it

- **OpenCTI / MISP / Microsoft Sentinel / Splunk ES** — import `bundle.json` as a STIX 2.1 file.
- **Download:** `https://raw.githubusercontent.com/phishdestroy/destroylist/main/stix/bundle.json`

## 🔄 Regenerate

```bash
python scripts/generate_stix.py   # reads dns/active_domains.json, writes stix/bundle.json
```
