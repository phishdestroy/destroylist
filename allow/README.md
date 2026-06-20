<div align="center">

<img src="banner.svg" alt="Allowlist" width="900"/>

# Allowlist

**Curated legitimate domains — false-positive protection for crypto & Web3**

<br>

![domains](https://img.shields.io/badge/domains-verified-FF0000?style=for-the-badge)
![format](https://img.shields.io/badge/format-apex_only-000000?style=for-the-badge)

<br>

[![Destroylist](https://img.shields.io/badge/destroylist-source-FF0000?style=flat-square&logo=github)](https://github.com/phishdestroy/destroylist)
[![API](https://img.shields.io/badge/API-live-000000?style=flat-square)](https://api.destroy.tools)
[![Appeals](https://img.shields.io/badge/appeals-FF0000?style=flat-square)](https://phishdestroy.io/appeals/)

</div>

---

## Overview

This directory contains a curated allowlist of **legitimate** crypto/Web3 project domains to prevent false positives in security filters.

> [!TIP]
> Being on this list guarantees the domain will **never** appear in any Destroylist output.

## ⚠️ Format Rules

- **Apex domains only** (e.g., `example.org`)
- No subdomains
- No paths
- Lowercase only

## 📂 Contents

| File | Description |
|:-----|:------------|
| `allowlist.json` | Array of verified apex domains |

**Example:**

```json
[
  "binance.com",
  "kraken.com",
  "uniswap.org"
]
```

## ➕ Request Addition

Open an issue: [github.com/phishdestroy/destroylist/issues](https://github.com/phishdestroy/destroylist/issues)

Include:
- Project name
- Homepage URL
- Apex domain(s)
- Brief rationale

## 🙏 Credits

This dataset includes entries from [SEAL (Security Alliance)](https://github.com/security-alliance/allowlists) allowlists.

---

<div align="center">

[![back](https://img.shields.io/badge/←_destroylist-FF0000?style=flat-square)](https://github.com/phishdestroy/destroylist)

</div>
