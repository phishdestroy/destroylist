<h1 align="center">Destroylist: Phishing &amp; Scam Domain Blacklist</h1>

<p align="center">
  <img src="scripts/destroylist_image.png" alt="Destroylist" width="600"/>
</p>

<p align="center">
  <a href="https://github.com/phishdestroy/destroylist">
<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=22&duration=3000&pause=1000&color=c52237&center=true&vCenter=true&multiline=false&repeat=true&width=700&height=50&lines=Continuously+Updated+Threat+Feeds;Real-time+Threat+Intelligence;Protecting+Users+Worldwide" alt="Typing SVG"/>
  </a>
</p>

<p align="center">
  <a href="#quick-start"><img src="assets/actions/quick-start.svg" alt="Quick Start" width="128" height="36"/></a>
  <a href="#data-feeds"><img src="assets/actions/data-feeds.svg" alt="Data Feeds" width="128" height="36"/></a>
  <a href="#threat-intelligence-api"><img src="assets/actions/api.svg" alt="API" width="128" height="36"/></a>
  <a href="#appeals-process"><img src="assets/actions/appeals.svg" alt="Appeals" width="128" height="36"/></a>
  <a href="https://phishdestroy.io"><img src="assets/actions/website.svg" alt="Website" width="128" height="36"/></a>
</p>

<p align="center">
<img src="https://img.shields.io/github/last-commit/phishdestroy/destroylist?style=flat-square&color=252532" alt="Last Commit"/>
<img src="https://img.shields.io/github/stars/phishdestroy/destroylist?style=flat-square&color=c52237" alt="Stars"/>
<img src="https://img.shields.io/github/forks/phishdestroy/destroylist?style=flat-square&color=252532" alt="Forks"/>
</p>


<img src="assets/readme-divider.svg" alt="" width="100%"/>

## Quick Start

**Add to Pi-hole or AdGuard Home in one click** — paste this URL into your blocklist settings:

```
https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/primary_active/hosts.txt
```

> **CDN link above is recommended** — served via jsDelivr global CDN, no rate limits.
> Raw GitHub mirror (may return 429 on heavy traffic): `https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/hosts.txt`

> More formats: [Hosts](#data-feeds) · [AdBlock](#data-feeds) · [Dnsmasq](#data-feeds) · [Unbound](#data-feeds) · [RPZ](#data-feeds) · [API](#threat-intelligence-api)

<details>
<summary><b>Table of Contents</b></summary>

- [Quick Start](#quick-start)
- [Live Statistics](#live-statistics)
- [Data Feeds](#data-feeds)
- [Root Lists](#root-lists)
- [Content-Verified Feeds](#content-verified-feeds)
- [Threat Intelligence API](#threat-intelligence-api)
- [About Destroylist](#about-destroylist)
- [Workflow & Remediation](#threat-intelligence--automated-remediation-workflow)
- [Fraud Victims Info](#key-info-for-online-fraud-victims)
- [Appeals Process](#appeals-process)
- [Connect With Us](#connect-with-us)
- [Join the Fight](#join-the-fight)

</details>

## Live Statistics

<table>
  <tr>
    <td align="center" width="280"><b>Primary</b><br/><br/><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/count.json&style=for-the-badge&color=c52237&label=" alt="Primary"/></td>
    <td align="center" width="280"><b>Primary Live</b><br/><br/><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/active_count.json&style=for-the-badge&color=c52237&label=" alt="Primary Live"/></td>
    <td align="center" width="280"><b>Primary Content</b><br/><br/><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/content_active_count.json&style=for-the-badge&color=c52237&label=" alt="Primary Content"/></td>
  </tr>
  <tr>
    <td align="center" width="280"><b>Community</b><br/><br/><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/community/count.json&style=for-the-badge&color=455268&label=" alt="Community"/></td>
    <td align="center" width="280"><b>Community Live</b><br/><br/><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/community/live_count.json&style=for-the-badge&color=455268&label=" alt="Community Live"/></td>
    <td align="center" width="280"><b>Community Content</b><br/><br/><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/community/content_active_count.json&style=for-the-badge&color=455268&label=" alt="Community Content"/></td>
  </tr>
</table>

### Today / Week / Month

<table>
  <tr><th align="left" width="210">Feed</th><th align="center" width="210">Today</th><th align="center" width="210">Week</th><th align="center" width="210">Month</th></tr>
  <tr><th align="left" scope="row" width="210">Primary</th><td align="center" width="210"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/today_added.json&style=for-the-badge&color=c52237&label=" alt="Primary added today"/></td><td align="center" width="210"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/week_added.json&style=for-the-badge&color=c52237&label=" alt="Primary added this week"/></td><td align="center" width="210"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/month_added.json&style=for-the-badge&color=c52237&label=" alt="Primary added this month"/></td></tr>
  <tr><th align="left" scope="row" width="210">Community</th><td align="center" width="210"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/today_community.json&style=for-the-badge&color=455268&label=" alt="Community added today"/></td><td align="center" width="210"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/week_community.json&style=for-the-badge&color=455268&label=" alt="Community added this week"/></td><td align="center" width="210"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/month_community.json&style=for-the-badge&color=455268&label=" alt="Community added this month"/></td></tr>
</table>

<details>
<summary>How these counts work</summary>

Badge values are exact **feed-entry counts**. The API reports normalized unique domains, so its values can be lower after URL, `www` and duplicate normalization. See the machine-readable [`dns/metrics.json`](dns/metrics.json) definitions.

</details>

## Data Feeds

<p>
  <a href="https://raw.githubusercontent.com/phishdestroy/destroylist/main/list.json"><img src="assets/actions/primary-json.svg" alt="Primary JSON" width="156" height="36"/></a>
  <a href="https://raw.githubusercontent.com/phishdestroy/destroylist/main/list.txt"><img src="assets/actions/primary-txt.svg" alt="Primary TXT" width="156" height="36"/></a>
  <a href="https://raw.githubusercontent.com/phishdestroy/destroylist/main/community/blocklist.json"><img src="assets/actions/community-json.svg" alt="Community JSON" width="156" height="36"/></a>
  <a href="https://raw.githubusercontent.com/phishdestroy/destroylist/main/community/blocklist.txt"><img src="assets/actions/community-txt.svg" alt="Community TXT" width="156" height="36"/></a>
</p>

| Feed | Description | Update | Download |
|:-----|:------------|:------:|:--------:|
| **Primary** | Curated phishing domains | Real-time | [![JSON](https://img.shields.io/badge/JSON-c52237?style=flat-square&logo=json&logoColor=white)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/list.json) [![TXT](https://img.shields.io/badge/TXT-252532?style=flat-square)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/list.txt) |
| **Primary Live** | DNS verified active | 24h | [![JSON](https://img.shields.io/badge/JSON-c52237?style=flat-square&logo=json&logoColor=white)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/active_domains.json) [![TXT](https://img.shields.io/badge/TXT-252532?style=flat-square)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/active_domains.txt) |
| **Community** | Aggregated from 13+ sources | 2h | [![JSON](https://img.shields.io/badge/JSON-c52237?style=flat-square&logo=json&logoColor=white)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/community/blocklist.json) [![TXT](https://img.shields.io/badge/TXT-252532?style=flat-square)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/community/blocklist.txt) |
| **Community Live** | Community DNS verified | 24h | [![JSON](https://img.shields.io/badge/JSON-c52237?style=flat-square&logo=json&logoColor=white)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/community/live_blocklist.json) [![TXT](https://img.shields.io/badge/TXT-252532?style=flat-square)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/community/live_blocklist.txt) |
| **Primary Content** | Curated + HTTP content verified | 12h | [![JSON](https://img.shields.io/badge/JSON-c52237?style=flat-square&logo=json&logoColor=white)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/content_active.json) [![TXT](https://img.shields.io/badge/TXT-252532?style=flat-square)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/content_active.txt) |
| **Community Content** | Aggregated + HTTP content verified | 24h | [![JSON](https://img.shields.io/badge/JSON-c52237?style=flat-square&logo=json&logoColor=white)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/community/content_live.json) [![TXT](https://img.shields.io/badge/TXT-252532?style=flat-square)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/community/content_live.txt) |
| **Allowlist** | False positive protection | Manual | [![JSON](https://img.shields.io/badge/JSON-252532?style=flat-square&logo=json&logoColor=white)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/allow/allowlist.json) |

> [!TIP]
> **Production:** `list.json` or `active_domains.json` · **Max coverage:** `blocklist.json` · **Firewall/DNS:** root lists


<details>
<summary><b>All Download Formats</b> (TXT, Hosts, AdBlock, Dnsmasq, Unbound, RPZ)</summary>

> **Getting 429 errors?** Use the jsDelivr CDN links below — they bypass GitHub rate limits.

**Via jsDelivr CDN (recommended, no rate limits):**

| Format | Primary | Primary Live | Community | Community Live |
|:------:|:-------:|:------------:|:---------:|:--------------:|
| **TXT** | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/primary/domains.txt) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/primary_active/domains.txt) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/community/domains.txt) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/community_active/domains.txt) |
| **Hosts** | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/primary/hosts.txt) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/primary_active/hosts.txt) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/community/hosts.txt) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/community_active/hosts.txt) |
| **AdBlock** | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/primary/adblock.txt) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/primary_active/adblock.txt) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/community/adblock.txt) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/community_active/adblock.txt) |
| **Dnsmasq** | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/primary/dnsmasq.conf) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/primary_active/dnsmasq.conf) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/community/dnsmasq.conf) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/community_active/dnsmasq.conf) |
| **Unbound** | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/primary/unbound.conf) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/primary_active/unbound.conf) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/community/unbound.conf) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/community_active/unbound.conf) |
| **RPZ** | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/primary/rpz.zone) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/primary_active/rpz.zone) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/community/rpz.zone) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/community_active/rpz.zone) |
| **Redis** | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/primary/redis.txt) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/primary_active/redis.txt) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/community/redis.txt) | [Download](https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/community_active/redis.txt) |

> **Redis one-liner** — load the full list into a Redis set (atomic swap, zero-downtime reload):
> ```
> curl -s https://cdn.jsdelivr.net/gh/phishdestroy/destroylist@main/rootlist/formats/primary/redis.txt | redis-cli --pipe
> ```
> Then check any domain in O(1): `SISMEMBER destroylist:primary evil-domain.com`

<details>
<summary>Via raw.githubusercontent.com (may return 429 under heavy traffic)</summary>

| Format | Primary | Primary Live | Community | Community Live |
|:------:|:-------:|:------------:|:---------:|:--------------:|
| **TXT** | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary/domains.txt) | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/domains.txt) | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community/domains.txt) | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community_active/domains.txt) |
| **Hosts** | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary/hosts.txt) | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/hosts.txt) | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community/hosts.txt) | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community_active/hosts.txt) |
| **AdBlock** | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary/adblock.txt) | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/adblock.txt) | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community/adblock.txt) | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community_active/adblock.txt) |
| **Dnsmasq** | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary/dnsmasq.conf) | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/dnsmasq.conf) | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community/dnsmasq.conf) | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community_active/dnsmasq.conf) |
| **Unbound** | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary/unbound.conf) | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/unbound.conf) | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community/unbound.conf) | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community_active/unbound.conf) |
| **RPZ** | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary/rpz.zone) | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/rpz.zone) | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community/rpz.zone) | [Download](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community_active/rpz.zone) |

</details>

> **Hosts** → Pi-hole, /etc/hosts, Windows · **AdBlock** → uBlock Origin, AdGuard · **Dnsmasq** → dnsmasq DNS · **Unbound** → pfSense, OPNsense · **RPZ** → BIND, Knot DNS · **Redis** → `redis-cli --pipe` bulk load

</details>

<a name="root-lists"></a>

<details>
<summary><b>Root Lists</b></summary>


> **Tip:**
> **Root domains only** — no subdomains, hosting providers excluded

| | All Roots | Live Only | Services Only |
|:--|:-:|:-:|:-:|
| **Primary** | [JSON](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/active_root_domains.json) · [TXT](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/active_root_domains.txt) | [JSON](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/online_root_domains.json) · [TXT](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/online_root_domains.txt) | [JSON](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/services_domains.json) · [TXT](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/services_domains.txt) |
| **Community** | [JSON](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/community_root_domains.json) · [TXT](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/community_root_domains.txt) | [JSON](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/community_online_root_domains.json) · [TXT](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/community_online_root_domains.txt) | [JSON](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/community_services_domains.json) · [TXT](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/community_services_domains.txt) |

> **All Roots** — clean root domains (no infra) · **Live Only** — DNS-verified active · **Services Only** — hosting platform subdomains (Vercel, Pages.dev, Netlify, etc.)

</details>

<a name="content-verified-feeds"></a>

<details>
<summary><b>Content-Verified Feeds</b></summary>


> **Note:**
> **Real HTTP content verification** — not just DNS, but actual phishing page detection


| Feed | Update | Description |
|:-----|:------:|:------------|
| [**Primary Content**](https://github.com/phishdestroy/destroylist/raw/main/dns/content_active.json) | `12h` (06:00 / 18:00 UTC) | Curated phishing with verified active content |
| [**Community Content**](https://github.com/phishdestroy/destroylist/raw/main/community/content_live.json) | `24h` (03:00 UTC) | Aggregated feeds with verified active content |

> Download links: see [Data Feeds](#data-feeds) above

> **Warning:**
> **Cloaking Alert:** Scammers use cloaking to hide phishing from bots — showing blank/fake pages to scanners. Domain **NOT** in content list ≠ safe! Use **Primary** or **Community** full lists for complete protection.

</details>

<img src="assets/readme-divider.svg" alt="" width="100%"/>

## Threat Intelligence API

<p>
  <img src="scripts/api.png" alt="API" width="680"/>
</p>

<p>
  <a href="https://api.destroy.tools"><img src="assets/actions/live-api.svg" alt="Live API" width="128" height="36"/></a>
  <a href="https://api.destroy.tools/v1/stats"><img src="assets/actions/stats.svg" alt="Stats" width="128" height="36"/></a>
</p>

### Free, open, no API key.

Real-time **domain risk scoring (0-100)** across the Primary and Community datasets · scheduled sync

**Single & bulk check (500/req)** · Keyword search · Full feeds

<details>
<summary><b>Use the API</b> · endpoints, scoring & integration examples</summary>

```mermaid
%%{init: {"themeVariables":{"background":"transparent","primaryBorderColor":"#c52237","lineColor":"#c52237","clusterBkg":"transparent","clusterBorder":"#898999","edgeLabelBackground":"transparent","fontFamily":"system-ui, sans-serif"},"flowchart":{"curve":"basis","htmlLabels":true}}}%%
flowchart LR
  Request["Client Request<br/>(Single / Bulk)"] e1@--> API["Live API<br/>api.destroy.tools"]
  API e2@--> Engine["Threat Engine<br/>(Risk Score 0-100)"]
  Engine e3@--> DB[("Destroylist DB<br/>1M+ Threats")]
  DB e4@--> Engine
  Engine e5@--> Response["JSON Response<br/>(Severity & Status)"]

  classDef client fill:transparent,stroke:#898999,stroke-width:2px;
  classDef api fill:transparent,stroke:#c52237,stroke-width:2px;
  classDef db fill:transparent,stroke:#898999,stroke-width:2px,stroke-dasharray: 5 5;
  classDef animate stroke:#c52237,stroke-width:2px,stroke-dasharray:10 5,stroke-dashoffset:900,animation:dash 22s linear infinite;
  classDef animateDark stroke:#898999,stroke-width:2px,stroke-dasharray:10 5,stroke-dashoffset:900,animation:dash 22s linear infinite;

  class Request client;
  class API,Engine,Response api;
  class DB db;
  class e1,e2,e3,e5 animate;
  class e4 animateDark;
```

### Endpoints

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| `GET` | [`/v1/check?domain=`](https://api.destroy.tools/v1/check?domain=example-phish.xyz) | Single domain check with risk score & severity |
| `POST` | `/v1/check/bulk` | Bulk check up to **500 domains** per request |
| `GET` | [`/v1/search?q=`](https://api.destroy.tools/v1/search?q=metamask) | Search blocklisted domains by keyword |
| `GET` | [`/v1/feed/{list}`](https://api.destroy.tools/v1/feed/primary) | Download full domain feeds (primary, community, active) |
| `GET` | [`/v1/stats`](https://api.destroy.tools/v1/stats) | Live statistics & domain counts |

### Threat Scoring

Every domain gets a **risk score (0-100)** based on multiple signals:

| Signal | Points | Description |
|:-------|:------:|:------------|
| Curated blocklist | **+40** | In primary destroylist |
| Community reported | **+20** | Reported by community sources |
| DNS active | **+30** | Domain currently resolves |
| Multi-source | **+10** | Confirmed by multiple feeds |
| Suspicious keywords | **+5 each** | metamask, wallet, airdrop, etc. |
| Risky TLD | **+5** | .xyz, .top, .club, .icu, etc. |

<p>
<img src="assets/severity-critical.svg" alt="Critical 70-100" width="150" height="30"/>
<img src="assets/severity-high.svg" alt="High 40-69" width="150" height="30"/>
<img src="assets/severity-medium.svg" alt="Medium 20-39" width="150" height="30"/>
<img src="assets/severity-low.svg" alt="Low 1-19" width="150" height="30"/>
</p>

### Quick Integration

**cURL**
```bash
curl "https://api.destroy.tools/v1/check?domain=suspicious-site.xyz"
```

**Python**
```python
import requests
r = requests.get(f"https://api.destroy.tools/v1/check?domain={domain}")
if r.json()["threat"]:
    print(f"BLOCKED: {r.json()['severity']} (score: {r.json()['risk_score']})")
```

**JavaScript**
```javascript
const r = await fetch(`https://api.destroy.tools/v1/check?domain=${domain}`);
const data = await r.json();
if (data.threat) console.warn("PHISHING:", data.severity, data.risk_score);
```

**Bulk Check**
```bash
curl -X POST "https://api.destroy.tools/v1/check/bulk" \
  -H "Content-Type: application/json" \
  -d '{"domains":["site1.com","site2.xyz","site3.top"]}'
```

</details>

<img src="assets/readme-divider.svg" alt="" width="100%"/>

## About Destroylist

Destroylist is a real-time threat intelligence platform by **PhishDestroy** — protecting firewalls, DNS resolvers, browser extensions, and security teams worldwide.

**Every domain is discovered, verified, reported to registrars, and published transparently.**

**Live feed counts above** · **13+** threat sources · **50+** vendor reports · **6** output formats · Free API

<sub>Live data collection began on July 1, 2025</sub>

### Data & integrations

<details>
<summary><b>Follow the data</b> · sources → checks → feeds</summary>

```mermaid
%%{init: {"themeVariables":{"background":"transparent","primaryBorderColor":"#c52237","lineColor":"#c52237","clusterBkg":"transparent","clusterBorder":"#898999","edgeLabelBackground":"transparent","fontFamily":"system-ui, sans-serif"},"flowchart":{"curve":"basis","htmlLabels":true}}}%%
flowchart TB
  subgraph Sources["Threat Sources"]
    S1[30+ Parsers]
    S2[Community Feeds]
    S3[Telegram Bot]
    S4[CT Logs / DNS]
  end

  subgraph Ingestion["Ingestion"]
    I1[smart_aggregator.py]
    I2[validate_and_clean.py]
  end

  subgraph Enrichment["Enrichment"]
    E1[DNS Validation]
    E2[HTTP Content Check]
    E3[VirusTotal / GSB]
  end

  subgraph Distribution["Distribution"]
    D1[JSON / TXT]
    D2[Hosts / AdBlock]
    D3[RPZ / Unbound]
    D4[API Feed]
  end

  Sources --> Ingestion
  Ingestion --> Enrichment
  Enrichment --> Distribution

  classDef source fill:transparent,stroke:#898999,stroke-width:2px;
  classDef ingest fill:transparent,stroke:#c52237,stroke-width:2px;
  classDef enrich fill:transparent,stroke:#c52237,stroke-width:2px;
  classDef dist fill:transparent,stroke:#c52237,stroke-width:2px,stroke-dasharray: 5 5;

  class S1,S2,S3,S4 source;
  class I1,I2 ingest;
  class E1,E2,E3 enrich;
  class D1,D2,D3,D4 dist;
```

</details>

<details>
<summary><b>Connect your tools</b> · subscribe URLs, curl, Python & Bash</summary>
<br>

### One-Click Subscribe URLs

| Tool | Format | URL |
|:-----|:------:|:----|
| **Pi-hole** | Hosts | `https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/hosts.txt` |
| **AdGuard Home** | AdBlock | `https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/adblock.txt` |
| **uBlock Origin** | AdBlock | `https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/adblock.txt` |
| **pfSense / OPNsense (Unbound)** | Unbound | `https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/unbound.conf` |
| **BIND / Knot DNS (RPZ)** | RPZ | `https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/rpz.zone` |
| **Dnsmasq** | Dnsmasq | `https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/dnsmasq.conf` |

> **Pi-hole** — Settings > Blocklists > paste the Hosts URL<br>
> **AdGuard Home** — Filters > DNS Blocklists > Add blocklist > paste the AdBlock URL<br>
> **uBlock Origin** — Settings > Filter lists > Import > paste the AdBlock URL<br>
> **pfSense** — Services > DNS Resolver > paste the Unbound URL<br>
> **BIND/Knot** — Add the RPZ URL as a response-policy zone

### curl One-Liners

```bash
# Plain domain list
curl -fsSL https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/domains.txt -o domains.txt

# Hosts format (Pi-hole, /etc/hosts)
curl -fsSL https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/hosts.txt -o hosts_blocklist.txt

# AdBlock format (uBlock Origin, AdGuard)
curl -fsSL https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/adblock.txt -o adblock.txt

# Dnsmasq
curl -fsSL https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/dnsmasq.conf -o dnsmasq_blocklist.conf

# Unbound (pfSense / OPNsense)
curl -fsSL https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/unbound.conf -o unbound_blocklist.conf

# RPZ (BIND / Knot)
curl -fsSL https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/rpz.zone -o rpz_blocklist.zone
```

### Python
```python
import requests
blocklist = requests.get('https://raw.githubusercontent.com/phishdestroy/destroylist/main/list.json').json()
is_malicious = "suspicious-domain.com" in blocklist
```

### Bash
```bash
curl -s https://raw.githubusercontent.com/phishdestroy/destroylist/main/list.txt | grep -q "suspicious-domain.com" && echo "BLOCKED"
```

</details>


### Investigations & evidence

<a name="threat-intelligence--automated-remediation-workflow"></a>

<details>
<summary><b>How we hunt</b> · discovery, reports & remediation</summary>


<p>
  <img src="scripts/about.png" alt="Workflow" width="680"/>
</p>

<br>

```mermaid
%%{init: {"themeVariables":{"background":"transparent","primaryBorderColor":"#c52237","lineColor":"#c52237","clusterBkg":"transparent","clusterBorder":"#898999","edgeLabelBackground":"transparent","fontFamily":"system-ui, sans-serif"},"flowchart":{"curve":"basis","htmlLabels":true}}}%%
flowchart LR
  Discover["DISCOVER<br/>30+ Parsers"] e1@--> Report["REPORT<br/>50+ Vendors"]
  Report e2@--> Legal["LEGAL<br/>ICANN Compliance"]
  Legal e3@--> Publish["PUBLISH<br/>Real-time Feed"]

  classDef box fill:transparent,stroke:#898999,stroke-width:2px;
  classDef animate stroke:#c52237,stroke-width:2px,stroke-dasharray:10 5,stroke-dashoffset:900,animation:dash 22s linear infinite;

  class Discover,Report,Legal,Publish box;
  
  class e1,e2,e3 animate;
```

<div>

| **DISCOVER** | **REPORT** | **LEGAL** | **PUBLISH** |
|:---:|:---:|:---:|:---:|
| 30+ parsers | 50+ vendors | ICANN compliance | Real-time |
| CT logs, DNS | Google, Microsoft | Abuse notifications | GitHub, Telegram |
| Social media | VirusTotal, Cloudflare | Evidence packages | Twitter, Mastodon |

</div>

### Phase 1: Pre-emptive Discovery & Ingestion

We utilize a distributed network of **30+ proprietary parsers** to identify malicious domains at their earliest stage:

- **Advanced Heuristics:** Continuous monitoring of Google Ads (Malvertising), SEO-manipulated search results, and trending social media campaigns on Twitter (X), YouTube, and Telegram
- **Infrastructure Analysis:** Leveraging *dnstwist* and typosquatting detection to catch look-alike domains targeting established brands
- **Community Intelligence:** Real-time ingestion of community-reported threats via our Telegram Bot and partner intelligence feeds

---

### Phase 2: Global Ecosystem Contribution

Once a threat is confirmed, we submit data to over **50 industry-leading vendors**:

```
Cloudflare        Google Safe Browsing      Microsoft Security      VirusTotal
Netcraft          ESET                      Bitdefender             Norton Safe Web
Avira             PhishTank                 Dr.Web                  Yandex Safe Browsing
URLScan.io        PolySwarm                 SiteReview              Urlquery
PhishStats        PhishReport               IsItPhish               ThreatCenter
```

---

### Phase 3: Legal Notifications & Investigation Support

- **Abuse Notifications:** Formal alerts to domain registrars and hosting providers
- **Forensic Evidence Disclosure:** Complete evidence packages including metadata, screenshots, and PDF reports
- **ICANN Compliance Support:** Reports aligned with ICANN standards
- **Conditional Re-Detection Logic:** Follow-up alerts only if threat remains active beyond 24 hours

---

### Phase 4: Public Transparency & Community Alerts

- **Open Database:** Real-time commits to this GitHub repository
- **Live Monitoring:** Visual intelligence at [phishdestroy.io/live](https://phishdestroy.io/live/)
- **Social Broadcasting:** Automated alerts on Twitter, Telegram, and Mastodon


</details>

<a name="key-info-for-online-fraud-victims"></a>

<details>
<summary><b>For fraud victims</b> · reports, evidence & provider responsibility</summary>


<p>
  <img src="scripts/abuse.png" alt="Abuse Process" width="680"/>
</p>

<br>

DestroyList aims to disable malicious domains: scams, phishing, and other illicit sites to enhance internet safety.

### Before a domain is added, we:

1. **Scan it across cybersecurity platforms** for threat intelligence.
2. **Send an official complaint to the registrar and the hosting provider** (via WHOIS), including scan results, screenshots, and a request for client investigation. The complaint also notifies them about inclusion in our public database.

ICANN's [2013 RAA §3.18.1](https://www.icann.org/resources/pages/approved-with-specs-2013-09-17-en#3.18.1) requires registrars to take **reasonable and prompt steps to investigate and respond appropriately to abuse reports**. The **24-hour review requirement** in [§3.18.2](https://www.icann.org/resources/pages/approved-with-specs-2013-09-17-en#3.18.2) applies to well-founded reports of illegal activity from law enforcement, consumer-protection and other qualifying authorities, sent to the registrar's dedicated contact.

### When reports go ignored

We work hard to eliminate threats quickly. Every malicious domain is analyzed, documented, reported, and published transparently.

However, when a domain receives **10–30+ abuse reports** and a registrar still **ignores them for months**, the situation changes: the registrar is no longer a passive party.

It effectively provides infrastructure for illegal activity.

Some registrars behave as if their internal policies somehow override ICANN requirements and national laws — as if phishing and fraud are "allowed" as long as they personally decide not to act.

> **We document this publicly so that anyone can see:** threats persist not because they were unnoticed, but because the responsible providers simply chose to do nothing.

### Requests from private individuals:

DestroyList is an open-source, non-commercial volunteer project.

Private individuals may request the number of abuse reports we have sent for a specific domain, but only through public channels:
- via GitHub issues
- via commit history: https://github.com/phishdestroy/destroylist/commits/main/

**We do not respond to private e-mail requests** from individuals about report counts.

This is a legal requirement for transparency and equal access to information.

Official government or law-enforcement requests may be answered privately.

---

**If you were defrauded by a domain already listed here,** check its addition date using the commit history or via our Telegram/Mastodon channels.

If the fraud happened after the domain was already listed, the registrar's or host's delay may indicate they share responsibility for the loss. Future potential victims can also see this negligence documented publicly.

Registrars and hosts that tolerate scam operations may reasonably be expected to assist victims or their legal representatives.


</details>

<a name="use-cases--historical-vault"></a>

<details>
<summary><b>Research the record</b> · use cases & historical vault</summary>


Network security · Threat research · AI/ML training · Trend analysis · Automation

**Point-in-time history** — every state of the list is reconstructable:

| Granularity | Where | Retention |
|:---|:---|:---|
| Every change | [Commit history](https://github.com/phishdestroy/destroylist/commits/main/) | Forever (41,000+ commits) |
| Daily added/removed diffs | [`archives/changes/`](archives/changes/) | Forever, searchable in GitHub code search |
| Weekly & monthly full snapshots | [`archives/`](archives/) → [Release assets](https://github.com/phishdestroy/destroylist/releases/tag/archives) | Recent in tree, older rotated to the permanent Release |

> **Tip:**
> **Historical Vault** (500K+ domains, 5+ years archived): [contact@phishdestroy.io](mailto:contact@phishdestroy.io)

</details>

<img src="assets/readme-divider.svg" alt="" width="100%"/>

## Appeals Process

### Wrongly listed? Fix it fast:

<p>
<a href="https://phishdestroy.io/appeals/"><img src="assets/actions/appeals-form.svg" alt="Appeals Form" width="156" height="36"/></a>
<a href="https://github.com/phishdestroy/destroylist/issues/new?template=appeal.yml"><img src="assets/actions/github-issue.svg" alt="GitHub Issue" width="156" height="36"/></a>
</p>

- [Appeals Form](https://phishdestroy.io/appeals/) — fastest option
- [GitHub Issue](https://github.com/phishdestroy/destroylist/issues/new?template=appeal.yml) — alternative option

For either route, send the domain and a short explanation. No evidence or proof of ownership is required. Screenshots and links are optional; we review the listing ourselves.

**Accuracy first!**

<details>
<summary><b>Appeals overview</b></summary>

<p>
  <img src="scripts/appeal.png" alt="Appeals" width="680"/>
</p>

</details>


## Connect With Us

**Platform**

<p>
<a href="https://phishdestroy.io"><img src="assets/actions/website.svg" alt="Website" width="128" height="36"/></a>
<a href="https://api.destroy.tools"><img src="assets/actions/api.svg" alt="API" width="128" height="36"/></a>
<a href="https://ban.destroy.tools"><img src="assets/actions/ban-service.svg" alt="Ban Service" width="128" height="36"/></a>
</p>

**Reports & contact**

<p>
<a href="https://t.me/PhishDestroy_bot"><img src="assets/actions/bot.svg" alt="Bot" width="128" height="36"/></a>
<a href="https://t.me/destroy_phish"><img src="assets/actions/telegram.svg" alt="Telegram" width="128" height="36"/></a>
<a href="mailto:contact@phishdestroy.io"><img src="assets/actions/contact.svg" alt="Contact" width="128" height="36"/></a>
</p>

**Updates**

<p>
<a href="https://mastodon.social/@phishdestroy"><img src="assets/actions/mastodon.svg" alt="Mastodon" width="128" height="36"/></a>
<a href="https://phishdestroy.medium.com"><img src="assets/actions/medium.svg" alt="Medium" width="128" height="36"/></a>
<a href="https://x.com/Phish_Destroy"><img src="assets/actions/twitter.svg" alt="Twitter" width="128" height="36"/></a>
</p>

<details>
<summary><b>All contact links</b></summary>

- **Official Website:** [phishdestroy.io](https://phishdestroy.io)
- **Telegram Report Bot:** [@PhishDestroy_bot](https://t.me/PhishDestroy_bot)
- **Telegram Channel:** [@destroy_phish](https://t.me/destroy_phish)
- **Mastodon:** [@phishdestroy](https://mastodon.social/@phishdestroy)
- **Twitter/X:** [@Phish_Destroy](https://x.com/Phish_Destroy)
- **Medium Blog:** [phishdestroy.medium.com](https://phishdestroy.medium.com)
- **Email Contact:** [contact@phishdestroy.io](mailto:contact@phishdestroy.io)
- **API Portal:** [api.destroy.tools](https://api.destroy.tools)
- **Ban Service:** [ban.destroy.tools](https://ban.destroy.tools)

</details>

<img src="assets/readme-divider.svg" alt="" width="100%"/>

## Pac-Man Contribution Graph

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/phishdestroy/destroylist/output/pacman-contribution-graph-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/phishdestroy/destroylist/output/pacman-contribution-graph.svg" />
  <img alt="pacman-contribution-graph" src="https://raw.githubusercontent.com/phishdestroy/destroylist/output/pacman-contribution-graph.svg" width="100%" />
</picture>

<a name="related-investigations--repositories"></a>

<details>
<summary><b>Related Investigations & Repositories</b></summary>


| Repository | Description |
|:-----------|:------------|
| [**namesilo-evidence**](https://github.com/phishdestroy/namesilo-evidence) | Evidence archive — NameSilo registrar abuse investigation |
| [**nicenic-evidence**](https://github.com/phishdestroy/nicenic-evidence) | Evidence archive — NiceNIC registrar abuse investigation |
| [**trustname-evidence**](https://github.com/phishdestroy/trustname-evidence) | Evidence archive — TrustName registrar abuse investigation |
| [**ScamIntelLogs**](https://github.com/phishdestroy/ScamIntelLogs) | Raw scam intelligence logs and IOC data |
| [**DestroyScammers**](https://github.com/phishdestroy/DestroyScammers) | Scammer exposure and disruption operations |

</details>

## License

![License](https://img.shields.io/badge/license-MIT-c52237?style=flat-square)

**MIT** — Free, open, yours to use!

<details>
<summary><b>Automation status</b></summary>


<p>
  <img src="https://github.com/phishdestroy/destroylist/actions/workflows/rootlist.yml/badge.svg" alt="Rootlist"/>
  <img src="https://github.com/phishdestroy/destroylist/actions/workflows/on_list_update.yml/badge.svg" alt="On List Update"/>
  <img src="https://github.com/phishdestroy/destroylist/actions/workflows/update_stats.yml/badge.svg" alt="Update Statistics"/>
  <img src="https://github.com/phishdestroy/destroylist/actions/workflows/pages.yml/badge.svg" alt="Deploy GitHub Pages"/>
</p>

</details>

## Join the Fight!

<p>
<img src="https://img.shields.io/badge/status-maintained-c52237?style=flat-square" alt="Status"/>
<img src="https://img.shields.io/badge/license-MIT-252532?style=flat-square" alt="License"/>
<img src="https://img.shields.io/badge/contributions-welcome-c52237?style=flat-square" alt="Contributions"/>
</p>

<div>

**Every star helps this project reach more security teams and protect more users.**

<p>
<a href="https://github.com/phishdestroy/destroylist"><img src="assets/actions/star-destroylist.svg" alt="Star Destroylist" width="156" height="36"/></a>
<a href="https://github.com/phishdestroy/destroylist/issues/new/choose"><img src="assets/actions/open-issue.svg" alt="Open Issue" width="156" height="36"/></a>
<a href="https://github.com/phishdestroy/destroylist/pulls"><img src="assets/actions/submit-pr.svg" alt="Submit PR" width="156" height="36"/></a>
</p>

</div>

<details>
<summary><b>We welcome contributions</b></summary>

We welcome contributions:

- Fresh threat intelligence & new blocklist sources
- Detection algorithm improvements
- Integration guides for new platforms
- Translations & documentation

</details>

### Drop an Issue or PR — let's crush phishing together!

