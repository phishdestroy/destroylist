# 🛡️ Security Policy

---

## 🔐 Reporting Security Issues

**DO NOT** report security vulnerabilities through public GitHub issues.

If you discover a security vulnerability in our infrastructure or data processing:

📧 **security@phishdestroy.io**

We respond within 48 hours.

---

## 🎯 Blocklist Accuracy

### False Positive — Your Domain Was Blocked

**Primary Lists** (`list.json`, `dns/active_domains.json`):
- [Appeals Form](https://phishdestroy.io/appeals/) — fastest option
- [GitHub Issue](https://github.com/phishdestroy/destroylist/issues/new?template=appeal.yml) with ownership proof

**Community Lists** (`community/blocklist.json`, `community/live_blocklist.json`):
- Auto-aggregated from external sources
- Manual removal is **not possible**
- Report to the original feed → auto-removed on next sync

### Missing Malicious Domain

➕ [Submit addition request](https://github.com/phishdestroy/destroylist/issues/new?template=add-to-blocklist.yml)

---

## 🚨 A Note on Repository Attacks

Our repository periodically receives fake reports, star manipulation, and harassment from **owners of blocked scam domains**.

This is expected and changes nothing.

These individuals have no legitimate recourse — their domains are blocked for valid reasons. Instead of stopping their fraudulent activities, they resort to:

- Fake DMCA takedowns
- Mass-reporting our repository
- Coordinated manipulation attempts
- Harassment campaigns

**There is exactly one solution: stop running phishing operations.**

No amount of reporting or manipulation makes inevitable bans less inevitable. Registrars and platforms don't reverse legitimate abuse decisions because someone clicked "report" a hundred times.

We remain unaffected. The blocklist continues to grow.

---

## ⚠️ Important Warnings

### For Victims

If you were defrauded by a domain already in our list, check its addition date via [commit history](https://github.com/phishdestroy/destroylist/commits/main/) or [Telegram channel](https://t.me/destroy_phish).

Per ICANN rules, registrars must review abuse complaints within 24 hours. If fraud occurred after the domain was listed, the registrar or hosting provider may share responsibility for your financial loss.

### For Users

This blocklist is for **legitimate security purposes only**.

Prohibited uses:
- DDoS attacks against listed domains
- Censorship abuse
- Harassment campaigns
- Any malicious activity

Violators will be reported to appropriate authorities.

---

## 📊 Data Feeds

| Feed | Update | Editable |
|:-----|:------:|:--------:|
| `list.json` | Real-time | ✅ |
| `dns/active_domains.json` | Real-time | ✅ |
| `community/*` | Hourly | ❌ |

---

## 🗄️ Archive Access

Historical archive: **500,000+ domains** over **5+ years**

Available for academic and security research.

📧 **contact@phishdestroy.io**

---

## 📜 License

MIT License — Free for any use with attribution.
