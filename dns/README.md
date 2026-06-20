<!--
  PhishDestroy DNS Intelligence
  Real-time DNS validation and active domain tracking
  https://github.com/phishdestroy/destroylist/tree/main/dns
-->

<div align="center">

<img src="banner.svg" alt="DNS Intelligence" width="900"/>

**Real-time DNS validation & active domain tracking**

<br>

![active](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/active_count.json&query=$.count&label=active%20domains&color=FF0000&style=for-the-badge)
![status](https://img.shields.io/badge/DNS_validated-live-000000?style=for-the-badge)

<br>

[![Destroylist](https://img.shields.io/badge/destroylist-source-FF0000?style=flat-square&logo=github)](https://github.com/phishdestroy/destroylist)
[![API](https://img.shields.io/badge/API-live-000000?style=flat-square)](https://api.destroy.tools)

</div>

---

## How It Works

Multithreaded DNS resolver validates every domain in the blocklist against live DNS records (A, AAAA, CNAME, MX, NS). Only domains with active infrastructure are flagged as live threats.

```mermaid
%%{init: {"theme":"base", "themeVariables": { "background": "transparent", "mainBkg": "#000000", "primaryColor": "#000000", "primaryTextColor": "#FFFFFF", "primaryBorderColor": "#FF0000", "lineColor": "#FF0000", "secondaryColor": "#111111", "tertiaryColor": "#111111", "fontFamily": "Inter, system-ui, sans-serif"}, "flowchart": {"curve": "basis", "htmlLabels": true}}}%%
flowchart LR
  Input["📥 list.json"] --> Script["⚙️ active_domains.py<br/>100 threads"]
  Script --> DNS[("🌐 DNS Resolver<br/>A / AAAA / CNAME / MX / NS")]
  DNS --> Live["✅ active_domains.json"]
  DNS --> Dead["❌ dead_domains.json"]

  classDef input fill:#000000,stroke:#333333,stroke-width:2px,color:#FFFFFF;
  classDef script fill:#000000,stroke:#FF0000,stroke-width:2px,color:#FFFFFF;
  classDef dns fill:#000000,stroke:#CC0000,stroke-width:2px,stroke-dasharray: 5 5,color:#FFFFFF;
  classDef live fill:#000000,stroke:#00CC00,stroke-width:2px,color:#FFFFFF;
  classDef dead fill:#000000,stroke:#666666,stroke-width:2px,color:#FFFFFF;

  class Input input;
  class Script script;
  class DNS dns;
  class Live live;
  class Dead dead;
```

## 📂 Data Files

| File | Description | Format |
|:-----|:------------|:------:|
| [`active_domains.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/active_domains.json) | All DNS-validated live domains | JSON |
| [`active_domains.txt`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/active_domains.txt) | Same as above, plain text | TXT |
| [`active_count.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/active_count.json) | Current active domain count | JSON |
| [`dead_domains.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/dead_domains.json) | Domains with no DNS records | JSON |
| [`content_active.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/content_active.json) | Active domains with HTTP content | JSON |
| [`content_active.txt`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/content_active.txt) | Same as above, plain text | TXT |

## ⏱️ Time-Based Feeds

| File | Description |
|:-----|:------------|
| [`today_added.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/today_added.json) | Domains added today |
| [`today_community.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/today_community.json) | Community domains added today |
| [`week_added.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/week_added.json) | Domains added this week |
| [`week_community.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/week_community.json) | Community domains this week |
| [`month_added.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/month_added.json) | Domains added this month |
| [`month_community.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/month_community.json) | Community domains this month |

## ⚙️ Script

[`active_domains.py`](active_domains.py) — Multithreaded DNS validator

- Resolves A, AAAA, CNAME, MX, NS records
- 100 concurrent threads for fast scanning
- Outputs JSON + TXT with deduplication
- Runs automatically via GitHub Actions

---

<div align="center">

[![GitHub](https://img.shields.io/badge/destroylist-FF0000?style=flat-square&logo=github)](https://github.com/phishdestroy/destroylist)
[![API](https://img.shields.io/badge/API-000000?style=flat-square)](https://api.destroy.tools)
[![Feeds](https://img.shields.io/badge/data_feeds-FF0000?style=flat-square)](https://github.com/phishdestroy/destroylist#-data-feeds)

</div>
