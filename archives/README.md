<div align="center">

<img src="banner.svg" alt="Archives" width="900"/>

**Historical snapshots of the blocklist for research and analysis**

<br>

![snapshots](https://img.shields.io/badge/snapshots-weekly_%26_monthly-FF0000?style=for-the-badge)
![data](https://img.shields.io/badge/data-500K%2B_domains-000000?style=for-the-badge)

<br>

[![Destroylist](https://img.shields.io/badge/destroylist-source-FF0000?style=flat-square&logo=github)](https://github.com/phishdestroy/destroylist)
[![API](https://img.shields.io/badge/API-live-000000?style=flat-square)](https://api.destroy.tools)

</div>

---

## 📂 Structure

```
archives/
├── weekly/
│   ├── 2025-W49.json
│   ├── 2025-W50.json
│   ├── 2025-W51.json
│   └── ...
└── monthly/
    ├── 2026-01.json
    ├── 2026-02.json
    └── ...
```

| Directory | Schedule | Pattern | Details |
|:----------|:---------|:--------|:--------|
| [`weekly/`](weekly/) | Every Monday at 01:00 UTC | `YYYY-WXX.json` | ISO 8601 week number |
| [`monthly/`](monthly/) | End of each month | `YYYY-MM.json` | Monthly snapshot |

## 📋 Format

Each snapshot contains the full `list.json` state at the end of that period.

## 📊 Use Cases

- Track blocklist growth over time
- Analyze domain lifecycle
- Research phishing trends
- Train ML models on historical data

## 📩 Full Archive

For access to the complete historical archive (500K+ domains, 5+ years):

📧 **[contact@phishdestroy.io](mailto:contact@phishdestroy.io)**

---

<div align="center">

[![back](https://img.shields.io/badge/←_destroylist-FF0000?style=flat-square)](https://github.com/phishdestroy/destroylist)

</div>
