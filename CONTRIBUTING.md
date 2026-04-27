<div align="center">

<img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Hand%20gestures/Handshake.png" width="80" />

# Contributing to Destroylist

**Thanks for helping fight phishing — every contribution matters**

<br>

![status](https://img.shields.io/badge/status-open-FF0000?style=for-the-badge)
![type](https://img.shields.io/badge/type-community_driven-000000?style=for-the-badge)

<br>

[![Destroylist](https://img.shields.io/badge/destroylist-source-FF0000?style=flat-square&logo=github)](https://github.com/phishdestroy/destroylist)
[![API](https://img.shields.io/badge/API-live-000000?style=flat-square)](https://api.destroy.tools)
[![Telegram](https://img.shields.io/badge/Telegram-bot-FF0000?style=flat-square&logo=telegram)](https://t.me/PhishDestroy_bot)

</div>

---

## 🚨 Report a Phishing Domain

**Fastest ways:**

| Method | Link | Speed |
|:-------|:-----|:-----:|
| 🤖 Telegram Bot | [@PhishDestroy_bot](https://t.me/PhishDestroy_bot) | ⚡ Instant |
| ⚡ API | [api.destroy.tools](https://api.destroy.tools) | ⚡ Instant |
| 🐛 GitHub Issue | [New Issue → Blocklist Addition](https://github.com/phishdestroy/destroylist/issues/new?template=blocklist-addition.yml) | 🕐 Reviewed |

> 💡 Include evidence when possible: screenshots, VirusTotal links, URLScan results

---

## 🛡️ Request Domain Removal (False Positive)

If a legitimate domain was listed by mistake:

| Method | Link | Speed |
|:-------|:-----|:-----:|
| 📝 Appeals Form | [phishdestroy.io/appeals](https://phishdestroy.io/appeals/) | ⚡ Fastest |
| 🐛 GitHub Issue | [New Issue → Appeal](https://github.com/phishdestroy/destroylist/issues/new?template=appeal.yml) | 🕐 Reviewed |

Approved domains are added to [`allow/allowlist.json`](allow/allowlist.json) and automatically removed from all lists.

---

## 💻 Contribute Code or Pipeline Improvements

```bash
# 1. Fork & clone
git clone https://github.com/YOUR_USERNAME/destroylist.git
cd destroylist

# 2. Create a branch
git checkout -b feature/my-improvement

# 3. Make changes

# 4. Validate locally
pip install -r requirements.txt
python scripts/validate_json.py
python scripts/validate_and_clean.py

# 5. Open a Pull Request with a clear description
```

---

## 📡 Add a New Blocklist Source

If you maintain a phishing blocklist and want it aggregated into our Community feed:

1. Open an issue with the feed URL and format (JSON array, plain text, hosts file, etc.)
2. The feed should be publicly accessible and updated regularly
3. We'll review and add it to [`scripts/smart_aggregator.py`](scripts/smart_aggregator.py)

---

## 📏 Guidelines

| Rule | Why |
|:-----|:----|
| All JSON files must be valid and sorted | Consistency & diffs |
| No IP addresses in domain lists | We block domains, not IPs |
| No duplicates across lists | Clean data |
| Respect the allowlist | Never re-add allowed domains |
| Keep PRs focused | One fix or feature per PR |

---

## 📜 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold a respectful, harassment-free environment. Spam, abuse, and fake reports will not be tolerated.

---

<div align="center">

**Drop an Issue or PR — let's crush phishing together!** 💪

[![back](https://img.shields.io/badge/←_destroylist-FF0000?style=flat-square)](https://github.com/phishdestroy/destroylist)

</div>
