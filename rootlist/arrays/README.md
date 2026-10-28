<div align="center">

<img src="banner.svg" alt="Arrays" width="900"/>

# Arrays

**The primary list split into small JSON shards**


<p align="center">
<img src="https://img.shields.io/badge/shards-74-c52237?style=for-the-badge" alt="shards"/>
<img src="https://img.shields.io/badge/shard_size-3%2C000_domains-252532?style=for-the-badge" alt="size"/>
</p>


<p align="center">
<a href="https://github.com/phishdestroy/destroylist"><img src="https://img.shields.io/badge/destroylist-source-c52237?style=flat-square&logo=github" alt="Destroylist"/></a>
<a href="https://api.destroy.tools"><img src="https://img.shields.io/badge/API-live-252532?style=flat-square" alt="API"/></a>
<a href="https://github.com/phishdestroy/destroylist#data-feeds"><img src="https://img.shields.io/badge/data_feeds-c52237?style=flat-square" alt="Feeds"/></a>
</p>

</div>

---

## Overview

`part_000.json … part_NNN.json` contain the primary list (`list.json`) in sorted order, 3,000 domains per
file. They are rebuilt by `scripts/build_shards.py` whenever the list changes (rootlist, list update and
purge workflows).

> [!TIP]
> `list.json` is too large for GitHub code search; the shards are not. Search any domain across the shards:
> [`repo:phishdestroy/destroylist path:rootlist/arrays example.com`](https://github.com/search?q=repo%3Aphishdestroy%2Fdestroylist+path%3Arootlist%2Farrays+example.com&type=code)

## Format

Each shard is a JSON array of domains:

```json
[
  "0-105.com",
  "0-collab.land",
  "..."
]
```

Concatenating all shards in order gives `list.json`. For feeds in other formats see [`rootlist/formats/`](../formats/).
