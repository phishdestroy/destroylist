# Security Policy

## Reporting Security Issues

**DO NOT** report security vulnerabilities through public GitHub issues.

If you discover a security vulnerability in our infrastructure or data processing:

📧 **security@phishdestroy.io**

We respond within 48 hours.

## Blocklist Accuracy

### False Positive (Your Domain Blocked)

1. **Primary List** (list.json, dns/active_domains.json):
   - Use [Appeals Form](https://phishdestroy.io/appeals/)
   - Or create [GitHub Issue](https://github.com/phishdestroy/destroylist/issues/new?template=appeal.yml) with evidence

2. **Community Lists** (community/blocklist.json, community/live_blocklist.json):
   - These are auto-aggregated from external sources
   - Manual removal is NOT possible
   - Report to the original source feed
   - Will be auto-removed on next sync

### Missing Malicious Domain

[Submit addition request](https://github.com/phishdestroy/destroylist/issues/new?template=add-to-blocklist.yml)

## ⚠️ Important Warnings

### For Victims
If you were defrauded by a domain already in our list, check its addition date via [commit history](https://github.com/phishdestroy/destroylist/commits/main/) or [Telegram channel](https://t.me/destroy_phish). 

Per ICANN rules, registrars must review complaints within 24 hours. If fraud occurred after listing, the registrar/host may share responsibility for your loss.

### For Users
This blocklist is for **legitimate security purposes only**. Prohibited uses:
- DDoS attacks
- Censorship abuse  
- Harassment
- Any malicious activity

Violators will be reported to authorities.

## Data Feeds

| Feed | Update Frequency | Manual Edits |
|------|------------------|--------------|
| list.json | Real-time | ✅ Yes |
| dns/active_domains.json | Real-time | ✅ Yes |
| community/* | Hourly | ❌ No (auto-sync) |

## Archive Access

Historical archive (500k+ domains, 5+ years) available for research.

Contact: **phishdestroy.io**

## License

MIT License - Free for any use with attribution.
