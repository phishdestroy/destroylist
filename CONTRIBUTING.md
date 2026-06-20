<div align="center">

<img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Hand%20gestures/Handshake.png" width="80" />

# Contributing to Destroylist

**Every submission helps protect real people from phishing**

<br>

[![Destroylist](https://img.shields.io/badge/destroylist-FF0000?style=flat-square&logo=github&logoColor=white)](https://github.com/phishdestroy/destroylist)
[![API](https://img.shields.io/badge/API-api.destroy.tools-000000?style=flat-square)](https://api.destroy.tools)
[![Telegram](https://img.shields.io/badge/Telegram-@PhishDestroy__bot-FF0000?style=flat-square&logo=telegram)](https://t.me/PhishDestroy_bot)

</div>

---

## Report a Phishing Domain

| Method | Link | Speed |
|:-------|:-----|:-----:|
| Telegram bot | [@PhishDestroy_bot](https://t.me/PhishDestroy_bot) | Instant |
| API | [api.destroy.tools](https://api.destroy.tools) | Instant |
| GitHub issue | [Blocklist addition →](https://github.com/phishdestroy/destroylist/issues/new?template=blocklist-addition.yml) | Reviewed |

Include evidence where possible: screenshots, VirusTotal or URLScan links.

---

## Request Domain Removal (False Positive)

| Method | Link |
|:-------|:-----|
| Appeals form | [phishdestroy.io/appeals](https://phishdestroy.io/appeals/) |
| GitHub issue | [Appeal →](https://github.com/phishdestroy/destroylist/issues/new?template=appeal.yml) |

Approved domains are added to `allow/allowlist.json` and automatically cleaned from all lists.

---

## Code or Pipeline Contributions

```bash
# Fork & clone
git clone https://github.com/YOUR_USERNAME/destroylist.git
cd destroylist

# Create a branch
git checkout -b feature/my-improvement

# Install dependencies
pip install -r requirements.txt

# Validate before submitting
python scripts/validate_json.py
python scripts/validate_and_clean.py
python scripts/build_rootlist.py

# Open a Pull Request with a clear description
```

---

## Add a New Community Source

If you maintain a publicly accessible, regularly updated phishing feed and want it aggregated into the Community list:

1. Open an issue with the feed URL and format (JSON array, plain text, hosts file, etc.)
2. We'll review and add it to [`scripts/smart_aggregator.py`](scripts/smart_aggregator.py)

Current sources: MetaMask, ScamSniffer, OpenPhish, SEAL, Phishunt, Enkrypt, CryptoFirewall, DiscordPhishing, Polkadot, SPMedia, Codeesura and more.

---

## Guidelines

| Rule | Reason |
|:-----|:-------|
| JSON files must be valid and sorted | Consistency, clean diffs |
| No IP addresses in domain lists | We block domains, not IPs |
| No duplicates | Clean data |
| Respect the allowlist | Never re-add an allowed domain |
| One fix or feature per PR | Easier review |

---

<div align="center">

[![back](https://img.shields.io/badge/←_destroylist-FF0000?style=flat-square)](https://github.com/phishdestroy/destroylist)

</div>
