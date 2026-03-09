<!--
  PhishDestroy DNS Intelligence
  Real-time DNS validation and active domain tracking
  https://github.com/phishdestroy/destroylist/tree/main/dns
-->

<div align="center">

<img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Travel%20and%20places/Satellite.png" width="80" />

# DNS Intelligence

**Real-time DNS validation & active domain tracking**

<br>

![active](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/active_count.json&query=$.count&label=active%20domains&color=FF0000&style=for-the-badge)
![status](https://img.shields.io/badge/DNS_validated-live-000000?style=for-the-badge)

<br>

[![Destroylist](https://img.shields.io/badge/destroylist-source-FF0000?style=flat-square&logo=github)](https://github.com/phishdestroy/destroylist)
[![API](https://img.shields.io/badge/API-live-000000?style=flat-square)](https://api.destroy.tools)

</div>

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif">

## How It Works

Multithreaded DNS resolver validates every domain in the blocklist against live DNS records (A, AAAA, CNAME, MX, NS). Only domains with active infrastructure are flagged as live threats.

```
list.json → active_domains.py → DNS resolution (100 threads) → active_domains.json
```

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif">

## Data Files

| File | Description | Format |
|:-----|:------------|:------:|
| [`active_domains.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/active_domains.json) | All DNS-validated live domains | JSON |
| [`active_domains.txt`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/active_domains.txt) | Same as above, plain text | TXT |
| [`active_count.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/active_count.json) | Current active domain count | JSON |
| [`dead_domains.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/dead_domains.json) | Domains with no DNS records | JSON |
| [`content_active.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/content_active.json) | Active domains with HTTP content | JSON |
| [`content_active.txt`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/content_active.txt) | Same as above, plain text | TXT |

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif">

## Time-Based Feeds

| File | Description |
|:-----|:------------|
| [`today_added.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/today_added.json) | Domains added today |
| [`today_community.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/today_community.json) | Community domains added today |
| [`week_added.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/week_added.json) | Domains added this week |
| [`week_community.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/week_community.json) | Community domains this week |
| [`month_added.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/month_added.json) | Domains added this month |
| [`month_community.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/month_community.json) | Community domains this month |

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif">

## Script

[`active_domains.py`](active_domains.py) — Multithreaded DNS validator

- Resolves A, AAAA, CNAME, MX, NS records
- 100 concurrent threads for fast scanning
- Outputs JSON + TXT with deduplication
- Runs automatically via GitHub Actions

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif">

<div align="center">

[![GitHub](https://img.shields.io/badge/destroylist-FF0000?style=flat-square&logo=github)](https://github.com/phishdestroy/destroylist)
[![API](https://img.shields.io/badge/API-000000?style=flat-square)](https://api.destroy.tools)
[![Feeds](https://img.shields.io/badge/data_feeds-FF0000?style=flat-square)](https://github.com/phishdestroy/destroylist#-data-feeds)

</div>
