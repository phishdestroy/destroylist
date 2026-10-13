<div align="center">

<img src="banner.svg" alt="Daily changes" width="900"/>

# Daily Changes

**One small file per day: which domains entered or left the lists**

<br>

![updated](https://img.shields.io/badge/updated-daily-FF0000?style=for-the-badge)
![since](https://img.shields.io/badge/since-2026--07--21-000000?style=for-the-badge)

<br>

[![Destroylist](https://img.shields.io/badge/destroylist-source-FF0000?style=flat-square&logo=github)](https://github.com/phishdestroy/destroylist)
[![API](https://img.shields.io/badge/API-live-000000?style=flat-square)](https://api.destroy.tools)
[![Feeds](https://img.shields.io/badge/data_feeds-FF0000?style=flat-square)](https://github.com/phishdestroy/destroylist#-data-feeds)

</div>

---

## Overview

Every night the **Update Statistics** workflow (`scripts/calculate_stats.py`) compares today's lists with
yesterday's and writes the difference to `YYYY-MM/YYYY-MM-DD.json`. Files are small and never rotated, so
the full history stays in the tree.

> [!TIP]
> These files are indexed by GitHub code search. Search for a domain to see the day it was added or removed:
> [`repo:phishdestroy/destroylist path:archives/changes example.com`](https://github.com/search?q=repo%3Aphishdestroy%2Fdestroylist+path%3Aarchives%2Fchanges+example.com&type=code)

## 📋 Format

```json
{
  "date": "2026-10-07",
  "primary_added": ["24markets.com", "..."],
  "primary_removed": [],
  "primary_count": 216640,
  "community_added": ["..."],
  "community_removed": [],
  "community_count": 1115343
}
```

| Field | Meaning |
|:------|:--------|
| `primary_added` / `primary_removed` | Changes to the curated primary list (`list.json`) |
| `community_added` / `community_removed` | Changes to the aggregated community list |
| `primary_count` / `community_count` | List sizes on that day |

Full point-in-time snapshots live one level up in [`archives/`](../).
