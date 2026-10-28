<!--
  PhishDestroy DNS Intelligence
  Real-time DNS validation and active domain tracking
  https://github.com/phishdestroy/destroylist/tree/main/dns
-->

<div align="center">

<img src="banner.svg" alt="DNS Intelligence" width="900"/>

**Real-time DNS validation & active domain tracking**


<p align="center">
<img src="https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/active_count.json&query=$.count&label=active+domains&color=c52237&style=for-the-badge" alt="active"/>
<img src="https://img.shields.io/badge/DNS_validated-live-252532?style=for-the-badge" alt="status"/>
</p>


<p align="center">
<a href="https://github.com/phishdestroy/destroylist"><img src="https://img.shields.io/badge/destroylist-source-c52237?style=flat-square&logo=github" alt="Destroylist"/></a>
<a href="https://api.destroy.tools"><img src="https://img.shields.io/badge/API-live-252532?style=flat-square" alt="API"/></a>
</p>

</div>

---

## How It Works

Multithreaded DNS resolver validates every domain in the blocklist against live DNS records (A, AAAA, CNAME, MX, NS). Only domains with active infrastructure are flagged as live threats.

```mermaid
%%{init: {"themeVariables":{"background":"transparent","primaryBorderColor":"#c52237","lineColor":"#c52237","clusterBkg":"transparent","clusterBorder":"#898999","edgeLabelBackground":"transparent","fontFamily":"system-ui, sans-serif"},"flowchart":{"curve":"basis","htmlLabels":true}}}%%
flowchart LR
  Input["list.json"] --> Script["active_domains.py<br/>100 threads"]
  Script --> DNS[("DNS Resolver<br/>A / AAAA / CNAME / MX / NS")]
  DNS --> Live["active_domains.json"]
  DNS --> Dead["dead_domains.json"]

  classDef input fill:transparent,stroke:#898999,stroke-width:2px;
  classDef script fill:transparent,stroke:#c52237,stroke-width:2px;
  classDef dns fill:transparent,stroke:#c52237,stroke-width:2px,stroke-dasharray: 5 5;
  classDef live fill:transparent,stroke:#2f9d62,stroke-width:2px;
  classDef dead fill:transparent,stroke:#898999,stroke-width:2px;

  class Input input;
  class Script script;
  class DNS dns;
  class Live live;
  class Dead dead;
```

## Data Files

| File | Description | Format |
|:-----|:------------|:------:|
| [`active_domains.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/active_domains.json) | All DNS-validated live domains | JSON |
| [`active_domains.txt`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/active_domains.txt) | Same as above, plain text | TXT |
| [`active_count.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/active_count.json) | Current active domain count | JSON |
| [`dead_domains.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/dead_domains.json) | Domains with no DNS records | JSON |
| [`content_active.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/content_active.json) | Active domains with HTTP content | JSON |
| [`content_active.txt`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/content_active.txt) | Same as above, plain text | TXT |

## Time-Based Feeds

| File | Description |
|:-----|:------------|
| [`today_added.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/today_added.json) | Domains added today |
| [`today_community.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/today_community.json) | Community domains added today |
| [`week_added.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/week_added.json) | Domains added this week |
| [`week_community.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/week_community.json) | Community domains this week |
| [`month_added.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/month_added.json) | Domains added this month |
| [`month_community.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/month_community.json) | Community domains this month |

## Script

[`active_domains.py`](active_domains.py) — Multithreaded DNS validator

- Resolves A, AAAA, CNAME, MX, NS records
- 100 concurrent threads for fast scanning
- Outputs JSON + TXT with deduplication
- Runs automatically via GitHub Actions

---

<div align="center">

<p align="center">
<a href="https://github.com/phishdestroy/destroylist"><img src="https://img.shields.io/badge/destroylist-c52237?style=flat-square&logo=github" alt="GitHub"/></a>
<a href="https://api.destroy.tools"><img src="https://img.shields.io/badge/API-252532?style=flat-square" alt="API"/></a>
<a href="https://github.com/phishdestroy/destroylist#data-feeds"><img src="https://img.shields.io/badge/data_feeds-c52237?style=flat-square" alt="Feeds"/></a>
</p>

</div>
