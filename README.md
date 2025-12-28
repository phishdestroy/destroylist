# 🎭 Destroylist: Phishing & Scam Domain Blacklist

![Destroyolist Illustration](scripts/destroyolist_image.png)

<p align="center">
  <a href="https://github.com/phishdestroy/destroylist">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=24&duration=3000&pause=1000&color=FF4757&center=true&vCenter=true&multiline=true&repeat=true&width=700&height=100&lines=%F0%9F%94%A5+58%2C000%2B+Phishing+Domains+Destroyed;%F0%9F%9B%A1%EF%B8%8F+Real-time+Threat+Intelligence;%F0%9F%8C%8D+Protecting+Users+Worldwide" alt="Typing SVG"/>
  </a>
</p>

<p align="center">
  <img src="https://github.com/phishdestroy/destroylist/actions/workflows/rootlist.yml/badge.svg" alt="Workflow"/>
  <img src="https://img.shields.io/badge/status-maintained-brightgreen?style=flat-square" alt="Status"/>
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License"/>
  <img src="https://img.shields.io/github/last-commit/phishdestroy/destroylist?style=flat-square" alt="Last Commit"/>
  <img src="https://img.shields.io/github/stars/phishdestroy/destroylist?style=flat-square" alt="Stars"/>
</p>

---

## ⚡ Quick Access

### Live Statistics

| Primary | Primary Live | Community | Community Live |
|:-------:|:------------:|:---------:|:--------------:|
| ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/count.json&style=for-the-badge&color=red&label=) | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/active_count.json&style=for-the-badge&label=) | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/community/count.json&style=for-the-badge&color=blue&label=) | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/community/live_count.json&style=for-the-badge&color=brightgreen&label=) |

| | Today | Week | Month |
|:--|:-----:|:----:|:-----:|
| **Primary** | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/today_added.json&style=flat-square&label=) | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/week_added.json&style=flat-square&label=) | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/month_added.json&style=flat-square&label=) |
| **Community** | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/today_community.json&style=flat-square&label=) | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/week_community.json&style=flat-square&label=) | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/month_community.json&style=flat-square&label=) |

### Data Feeds

| Feed | Description | Update | Download |
|:-----|:------------|:------:|:--------:|
| **Primary** | Curated phishing domains | ⚡ Real-time | [![JSON](https://img.shields.io/badge/JSON-FF4757?style=flat-square&logo=json)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/list.json) [![TXT](https://img.shields.io/badge/TXT-FF6B81?style=flat-square)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/list.txt) |
| **Primary Live** | DNS verified active | 🕐 24h | [![JSON](https://img.shields.io/badge/JSON-9B59B6?style=flat-square&logo=json)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/active_domains.json) |
| **Community** | Aggregated from 35+ sources | 🕐 2h | [![JSON](https://img.shields.io/badge/JSON-3742FA?style=flat-square&logo=json)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/community/blocklist.json) |
| **Community Live** | Community DNS verified | 🕐 24h | [![JSON](https://img.shields.io/badge/JSON-2ED573?style=flat-square&logo=json)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/community/live_blocklist.json) |
| **Allowlist** | False positive protection | ✋ Manual | [![JSON](https://img.shields.io/badge/JSON-95A5A6?style=flat-square&logo=json)](https://raw.githubusercontent.com/phishdestroy/destroylist/main/allow/allowlist.json) |

> [!TIP]
> **Production:** `list.json` or `active_domains.json` · **Max coverage:** `blocklist.json` · **Firewall/DNS:** root lists

<details>
<summary><b>📁 All Download Formats</b> (TXT, Hosts, AdBlock, Dnsmasq)</summary>
<br>

| Format | Primary | Primary Live | Community | Community Live |
|:------:|:-------:|:------------:|:---------:|:--------------:|
| **TXT** | [⬇️](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary/domains.txt) | [⬇️](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/domains.txt) | [⬇️](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community/domains.txt) | [⬇️](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community_active/domains.txt) |
| **Hosts** | [⬇️](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary/hosts.txt) | [⬇️](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/hosts.txt) | [⬇️](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community/hosts.txt) | [⬇️](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community_active/hosts.txt) |
| **AdBlock** | [⬇️](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary/adblock.txt) | [⬇️](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/adblock.txt) | [⬇️](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community/adblock.txt) | [⬇️](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community_active/adblock.txt) |
| **Dnsmasq** | [⬇️](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary/dnsmasq.conf) | [⬇️](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/dnsmasq.conf) | [⬇️](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community/dnsmasq.conf) | [⬇️](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community_active/dnsmasq.conf) |

> **Hosts** → Pi-hole, /etc/hosts, Windows · **AdBlock** → uBlock Origin, AdGuard · **Dnsmasq** → DNS server

</details>

### Root Lists

> [!TIP]
> **Root domains only** — no subdomains, hosting providers excluded

| | All Roots | Live Only |
|:--|:-:|:-:|
| 🔴 **Primary** | [`active_root_domains.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/active_root_domains.json) | [`online_root_domains.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/online_root_domains.json) |
| 🟣 **Community** | [`community_root_domains.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/community_root_domains.json) | [`community_online_root_domains.json`](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/community_online_root_domains.json) |

---

## 🔭 About

> [!NOTE]
> Live data collection began on July 1, 2025

Destroylist is a powerful phishing and scam domain blocklist powered by **PhishDestroy**. Designed for firewalls, DNS resolvers, threat platforms, and security research.

<details>
<summary><b>🔧 Quick Integration Examples</b></summary>

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

### Pi-hole / AdGuard
```
https://raw.githubusercontent.com/phishdestroy/destroylist/main/dns/active_domains.json
```

</details>

---

## 🛡️ Threat Intelligence Workflow

<p align="center">
  <img src="scripts/about.png" alt="Workflow" width="700"/>
</p>

| 🔍 **DISCOVER** | 📤 **REPORT** | ⚖️ **LEGAL** | 📡 **PUBLISH** |
|:---:|:---:|:---:|:---:|
| 30+ parsers | 50+ vendors | ICANN compliance | Real-time |
| CT logs, DNS | Google, Microsoft | Abuse notifications | GitHub, Telegram |
| Social media | VirusTotal, Cloudflare | Evidence packages | Twitter, Mastodon |

<details>
<summary><b>📖 Full Workflow Details</b></summary>

### Phase 1: Discovery & Ingestion

We utilize **30+ proprietary parsers** to identify malicious domains at their earliest stage:

- **Advanced Heuristics:** Monitoring Google Ads, SEO-manipulated results, social media campaigns
- **Infrastructure Analysis:** dnstwist and typosquatting detection for look-alike domains
- **Community Intelligence:** Real-time ingestion via Telegram Bot and partner feeds

### Phase 2: Global Ecosystem Contribution

Confirmed threats are submitted to **50+ industry vendors:**

```
Cloudflare        Google Safe Browsing      Microsoft Security      VirusTotal
Netcraft          ESET                      Bitdefender             Norton Safe Web
Avira             PhishTank                 Dr.Web                  Yandex Safe Browsing
URLScan.io        PolySwarm                 SiteReview              Urlquery
```

### Phase 3: Legal & Compliance

- Formal abuse notifications to registrars and hosting providers
- Complete evidence packages with metadata, screenshots, PDF reports
- ICANN-aligned reporting standards
- Follow-up alerts if threat remains active beyond 24 hours

### Phase 4: Public Transparency

- Real-time commits to this repository
- Live monitoring at [phishdestroy.io/live](https://phishdestroy.io/live/)
- Automated social broadcasting

</details>

---

## 🚨 For Fraud Victims

<p align="center">
  <img src="scripts/abuse.png" alt="Abuse Process" width="700"/>
</p>

<details>
<summary><b>Complaints, Transparency & Registrar Accountability</b></summary>

DestroyList aims to disable malicious domains to enhance internet safety. Before a domain is added:

1. **Scan** across cybersecurity platforms for threat intelligence
2. **Report** to registrar and hosting provider via WHOIS with evidence
3. **Document** — ICANN rules require 24-hour review of abuse complaints

---

**When registrars ignore 10-30+ abuse reports for months, they become complicit.** We document this publicly so anyone can see: threats persist not because they were unnoticed, but because providers chose inaction.

---

**For victims:** Check domain addition dates via [commit history](https://github.com/phishdestroy/destroylist/commits/main/) or our Telegram/Mastodon channels. If fraud occurred after listing, the registrar's delay may indicate shared responsibility.

**Transparency policy:** Report counts available via GitHub issues only. No private email responses (legal requirement). Government/law enforcement requests handled separately.

</details>

---

## 📊 Use Cases & Historical Data

| Network Security | Automation | Threat Research | ML Training |
|:---:|:---:|:---:|:---:|
| ✅ | ✅ | ✅ | ✅ |

> [!IMPORTANT]
> **Open collaboration = Stronger security**

> [!TIP]
> **Historical Vault** (500K+ domains, 5+ years): [contact@phishdestroy.io](mailto:contact@phishdestroy.io)

---

## ⚖️ Appeals

<p align="center">
  <img src="scripts/appeal.png" alt="Appeals" width="700"/>
</p>

Wrongly listed? We prioritize accuracy.

| [![Appeals Form](https://img.shields.io/badge/📝_APPEALS_FORM-2ED573?style=for-the-badge)](https://phishdestroy.io/appeals/) | [![GitHub Issue](https://img.shields.io/badge/🐛_GITHUB_ISSUE-FF4757?style=for-the-badge)](https://github.com/phishdestroy/destroylist/issues/new) |
|:---:|:---:|

---

## 🔗 Connect

<p align="center">
  <a href="https://phishdestroy.io"><img src="https://img.shields.io/badge/🌐_WEBSITE-FF4757?style=for-the-badge" alt="Website"/></a>
  <a href="https://t.me/destroy_phish"><img src="https://img.shields.io/badge/📢_TELEGRAM-26A5E4?style=for-the-badge" alt="Telegram"/></a>
  <a href="https://t.me/PhishDestroy_bot"><img src="https://img.shields.io/badge/🤖_BOT-26A5E4?style=for-the-badge" alt="Bot"/></a>
  <a href="https://x.com/Phish_Destroy"><img src="https://img.shields.io/badge/𝕏_TWITTER-000000?style=for-the-badge" alt="Twitter"/></a>
  <a href="https://mastodon.social/@phishdestroy"><img src="https://img.shields.io/badge/🐘_MASTODON-6364FF?style=for-the-badge" alt="Mastodon"/></a>
  <a href="https://phishdestroy.medium.com"><img src="https://img.shields.io/badge/📝_MEDIUM-000000?style=for-the-badge" alt="Medium"/></a>
</p>

<p align="center">
  <a href="https://ban.destroy.tools"><img src="https://img.shields.io/badge/🚫_BAN_SERVICE-FF0000?style=for-the-badge" alt="Ban Service"/></a>
  <a href="mailto:contact@phishdestroy.io"><img src="https://img.shields.io/badge/✉️_CONTACT-8B5CF6?style=for-the-badge" alt="Email"/></a>
</p>

---

## 📄 License

**MIT** — Free, open, yours to use.

---

## 🤝 Contributing

Got ideas, sources, or improvements? We welcome:
- Detection algorithm tweaks
- Integration examples
- Fresh threat intelligence

**Drop an Issue or PR — let's crush phishing together!**

---

<p align="center">
  <img src="https://raw.githubusercontent.com/phishdestroy/destroylist/output/snake.svg" alt="Snake animation" />
</p>