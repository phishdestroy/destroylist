<div align="center">

<img src="banner.svg" alt="Arrays" width="900"/>

# Arrays

**The primary list split into small JSON shards**

<br>

![shards](https://img.shields.io/badge/shards-74-FF0000?style=for-the-badge)
![size](https://img.shields.io/badge/shard_size-3%2C000_domains-000000?style=for-the-badge)

<br>

[![Destroylist](https://img.shields.io/badge/destroylist-source-FF0000?style=flat-square&logo=github)](https://github.com/phishdestroy/destroylist)
[![API](https://img.shields.io/badge/API-live-000000?style=flat-square)](https://api.destroy.tools)
[![Feeds](https://img.shields.io/badge/data_feeds-FF0000?style=flat-square)](https://github.com/phishdestroy/destroylist#-data-feeds)

</div>

---

## Overview

`part_000.json … part_NNN.json` contain the primary list (`list.json`) in sorted order, 3,000 domains per
file. They are rebuilt by `scripts/build_shards.py` whenever the list changes (rootlist, list update and
purge workflows).

> [!TIP]
> `list.json` is too large for GitHub code search; the shards are not. Search any domain across the shards:
> [`repo:phishdestroy/destroylist path:rootlist/arrays example.com`](https://github.com/search?q=repo%3Aphishdestroy%2Fdestroylist+path%3Arootlist%2Farrays+example.com&type=code)

## 📋 Format

Each shard is a JSON array of domains:

```json
[
  "0-105.com",
  "0-collab.land",
  "..."
]
```

Concatenating all shards in order gives `list.json`. For feeds in other formats see [`rootlist/formats/`](../formats/).
