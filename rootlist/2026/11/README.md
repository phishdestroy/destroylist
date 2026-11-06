[Destroylist](../../../README.md) / [rootlist](../../README.md) / [2026](../README.md) / 11

<h1>
<picture>
  <source media="(max-width: 640px)" srcset="banner-mobile.svg">
  <img src="banner.svg" alt="November 2026" width="960">
</picture>
</h1>

Monthly threat report · activity, infrastructure and detection.

[Dashboard](#dashboard) · [Analysis](#intelligence-analysis) · [Downloads](#downloads--data) · [Year overview](../)

---

![domains](https://img.shields.io/badge/domains-2%2C654-c52237?style=flat-square) ![vs prev month](https://img.shields.io/badge/daily%20avg%20vs%20prev---30%25-c52237?style=flat-square) ![kill rate](https://img.shields.io/badge/kill%20rate-26.3%25-535b69?style=flat-square) ![VT coverage](https://img.shields.io/badge/VT%20coverage-93.6%25-c52237?style=flat-square)

## Dashboard

<div align="center">

| detected | live | dead | enriched |
|:---:|:---:|:---:|:---:|
| **2,654** | **1,615** | **576** | **1,504** |

| VirusTotal | Google SB | Avg Response | Median |
|:---:|:---:|:---:|:---:|
| **2,484** (93.6%) | **82** | **37.3h** | **36h** |

</div>

<div align="center">
<img src="2026-11-activity.svg" alt="Daily Threat Detections — November 2026" width="850" />
</div>

> Peak: **2026-11-01** (1,052) &nbsp;·&nbsp; Low: **2026-11-06** (104) &nbsp;·&nbsp; Active days: **6** *(month ongoing)*

<details>
<summary><b>Daily breakdown</b></summary>

| Date | Domains | Activity |
|:-----|--------:|:---------|
| `2026-11-01` | **1,052** | `████████████████████` |
| `2026-11-02` | **326** | `██████░░░░░░░░░░░░░░` |
| `2026-11-03` | **126** | `██░░░░░░░░░░░░░░░░░░` |
| `2026-11-04` | **876** | `█████████████████░░░` |
| `2026-11-05` | **170** | `███░░░░░░░░░░░░░░░░░` |
| `2026-11-06` | **104** | `██░░░░░░░░░░░░░░░░░░` |

</details>

---

## Intelligence Analysis

### Executive Summary

November 2026 has detected **2,654** phishing and scam domains across 6 active days *(month ongoing as of 2026-11-06)*; at 442 domains per day that is a **-30%** change in daily volume from October 2026 (631 per day). The kill rate stands at **26.3%**, with 576 domains no longer serving content and 1,615 still live. VirusTotal flagged **93.6%** of the month's domains and Google Safe Browsing flagged 82. The leading registrar was Dynadot Inc with 514 domains (19.4%). Signal was the most impersonated brand (36 domains).

### Key Trends

- **Volume** — 2,654 domains in 6 days so far; daily volume -30% vs October 2026.
- **VirusTotal coverage** — 93.6% vs 97.4% the previous month.
- **Registrars** — Dynadot Inc ranked #1 with 514 domains. New in the top 10: MarkMonitor Inc., Square, Inc., MainReg Inc..
- **Domain zones** — `.com` led with 1,172 domains (44.2%), followed by `.app`, `.shop`, `.net`.
- **Brands** — top targets were Signal, Celer, Cloudflare. New in the top 10: Cloudflare, Gmail, Ups.

### Activity Patterns

Detections peaked on **2026-11-01** with 1,052 domains; the lowest day was 2026-11-06 (104). The daily average was 442 domains. Days below 10% of the peak: 1.

Crypto drainer kits identified this month: wallet_drainer (1).

### Registrar Accountability

Dynadot Inc (514, 19.4%), MarkMonitor Inc. (419, 15.8%), Spaceship, Inc. (175, 6.6%) were the three registrars with the most phishing domains this month.

Top 3 registrars account for **1,108 domains** (41.7% of threats).

### Detection Landscape

alphaMountain.ai (2,272, 85.6%), Gridinsoft (2,266, 85.4%), SOCRadar (2,100, 79.1%), VIPRE (1,993, 75.1%) were the most active VirusTotal engines. Overall, 2,484 of 2,654 domains (93.6%) had at least one VirusTotal detection.

### Recommendations

- **For Security Teams** — Subscribe to the destroylist feeds and block on VirusTotal consensus; 93.6% of this month's domains are already flagged.
- **For SOC Analysts** — Prioritise domains registered with Dynadot Inc in the `.com` zone, the highest-volume combination this month.
- **For Registrars** — Dynadot Inc and MarkMonitor Inc. hold the largest share of reported domains; faster abuse handling would have the biggest impact.
- **For Brand Owners** — Signal, Celer, Cloudflare should monitor for look-alike registrations.
- **For End Users** — Check unfamiliar crypto and login links at [api.destroy.tools](https://api.destroy.tools/v1/check?domain=example.com) before connecting a wallet.

---

## Top Registrars

| # | Registrar | Domains | Share | Trend |
|:--:|:---|------:|:---|:---:|
| **1** | Dynadot Inc | **514** | `███░░░░░░░░░░░░` 19.4% | 🔻 |
| **2** | MarkMonitor Inc. | **419** | `██░░░░░░░░░░░░░` 15.8% | 🆕 |
| **3** | Spaceship, Inc. | **175** | `█░░░░░░░░░░░░░░` 6.6% | 🔻 |
| **4** | Google LLC | **157** | `█░░░░░░░░░░░░░░` 5.9% | 🔻 |
| **5** | NICENIC INTERNATIONAL GROUP CO., LIMITED | **107** | `█░░░░░░░░░░░░░░` 4.0% | 🔻 |
| **6** | Square, Inc. | **95** | `█░░░░░░░░░░░░░░` 3.6% | 🆕 |
| **7** | MainReg Inc. | **83** | `░░░░░░░░░░░░░░░` 3.1% | 🆕 |
| **8** | GoDaddy.com, LLC | **68** | `░░░░░░░░░░░░░░░` 2.6% | 🔻 |
| **9** | Cloudflare, Inc. | **63** | `░░░░░░░░░░░░░░░` 2.4% | 🔻 |
| **10** | NameCheap, Inc. | **60** | `░░░░░░░░░░░░░░░` 2.3% | 🆕 |

> ⚠️ Top 3 registrars = **1,108** domains (41.7% of all threats)

---

## Domain Zones

| # | TLD | Domains | Share | vs Prev |
|:--:|:---|------:|------:|:---:|
| **1** | `.com` | **1,172** | 44.2% | 🔻 |
| **2** | `.app` | **399** | 15.0% | 🔻 |
| **3** | `.shop` | **154** | 5.8% | 🔻 |
| **4** | `.net` | **125** | 4.7% | 🔻 |
| **5** | `.digital` | **100** | 3.8% | 🆕 |
| **6** | `.dev` | **92** | 3.5% | 🔻 |
| **7** | `.click` | **66** | 2.5% | 🆕 |
| **8** | `.live` | **59** | 2.2% | 🔻 |
| **9** | `.pro` | **59** | 2.2% | 🆕 |
| **10** | `.io` | **39** | 1.5% | 🔻 |

---

## Registrar Geography

| # | Country | Domains | Share |
|:--:|:---|------:|------:|
| **1** | Unknown | **2,422** | 91.3% |
| **2** | US | **162** | 6.1% |
| **3** | FR | **27** | 1.0% |
| **4** | HK | **6** | 0.2% |
| **5** | SG | **5** | 0.2% |
| **6** | CY | **5** | 0.2% |
| **7** | IN | **3** | 0.1% |
| **8** | LT | **3** | 0.1% |
| **9** | ES | **3** | 0.1% |
| **10** | CN | **3** | 0.1% |

---

## Targeted Brands

| # | Brand | Domains | Share |
|:--:|:---|------:|------:|
| **1** | Signal | **36** | 1.4% |
| **2** | Celer | **34** | 1.3% |
| **3** | Cloudflare | **33** | 1.2% |
| **4** | Gmail | **27** | 1.0% |
| **5** | Google | **21** | 0.8% |
| **6** | Ups | **21** | 0.8% |
| **7** | Microsoft | **14** | 0.5% |
| **8** | Ledger | **14** | 0.5% |
| **9** | Wordpress | **14** | 0.5% |
| **10** | Base | **12** | 0.5% |

---

## Crypto Drainers & Kits

| # | Type | Domains |
|:--:|:---|------:|
| **1** | wallet_drainer | **1** |

---

## Detection Engines (VirusTotal)

| # | Engine | Detections | Coverage |
|:--:|:---|------:|------:|
| **1** | alphaMountain.ai | **2,272** | 85.6% |
| **2** | Gridinsoft | **2,266** | 85.4% |
| **3** | SOCRadar | **2,100** | 79.1% |
| **4** | VIPRE | **1,993** | 75.1% |
| **5** | Fortinet | **1,977** | 74.5% |
| **6** | G-Data | **1,879** | 70.8% |
| **7** | BitDefender | **1,859** | 70.0% |
| **8** | Sophos | **1,853** | 69.8% |
| **9** | Forcepoint ThreatSeeker | **1,841** | 69.4% |
| **10** | ESET | **1,834** | 69.1% |
| **11** | Lionic | **1,820** | 68.6% |
| **12** | DNS8 | **1,578** | 59.5% |
| **13** | CyRadar | **1,330** | 50.1% |
| **14** | Kaspersky | **1,282** | 48.3% |
| **15** | Seclookup | **1,234** | 46.5% |

> ![VT flagged](https://img.shields.io/badge/VT%20flagged-2%2C484%20%2F%202%2C654-c52237?style=flat-square) &nbsp; ![GSB flagged](https://img.shields.io/badge/GSB%20flagged-82-535b69?style=flat-square)

---

## Downloads & Data

| Format | File | Description |
|:-------|:-----|:------------|
| 📋 Report | [`README.md`](.) | This report |
| 🗃️ Threats | [`2026-11-threats.json`](2026-11-threats.json) | **2,654** threats with registrars, IPs, VT vendors |
| 📈 Chart | [`2026-11-activity.svg`](2026-11-activity.svg) | Daily detection activity graph |

> 💡 **API access**: Query any domain at [`api.destroy.tools/v1/check`](https://api.destroy.tools/v1/check?domain=example.com) — free, no API key

---

## All Reports

| Report | Domains |
|:-------|--------:|
| [January 2025](../../2025/01/) | **1** |
| [February 2025](../../2025/02/) | **13** |
| [March 2025](../../2025/03/) | **2** |
| [April 2025](../../2025/04/) | **2** |
| [May 2025](../../2025/05/) | **2** |
| [June 2025](../../2025/06/) | **4** |
| [July 2025](../../2025/07/) | **700** |
| [August 2025](../../2025/08/) | **3,788** |
| [September 2025](../../2025/09/) | **7,307** |
| [October 2025](../../2025/10/) | **8,841** |
| [November 2025](../../2025/11/) | **12,581** |
| [December 2025](../../2025/12/) | **11,773** |
| [January 2026](../../2026/01/) | **8,932** |
| [February 2026](../../2026/02/) | **18,207** |
| [March 2026](../../2026/03/) | **4,042** |
| [April 2026](../../2026/04/) | **15,633** |
| [May 2026](../../2026/05/) | **7,021** |
| [June 2026](../../2026/06/) | **8,101** |
| [July 2026](../../2026/07/) | **19,796** |
| [August 2026](../../2026/08/) | **19,782** |
| [September 2026](../../2026/09/) | **16,250** |
| [October 2026](../../2026/10/) | **19,567** |
| 📍 **November 2026** | **2,654** *(ongoing)* |

---

[**← October 2026**](../../2026/10/) &nbsp;·&nbsp; 📅 **November 2026** &nbsp;·&nbsp; *ongoing...*

---

[Destroylist](../../../README.md) · [All feeds](../../../README.md#data-feeds) · [Appeals](https://phishdestroy.io/appeals/)
