# Contributing to Destroylist

Thanks for helping fight phishing! Here's how to contribute.

## Report a Phishing Domain

**Fastest:** use the [Telegram Bot](https://t.me/PhishDestroy_bot) or the [API](https://api.destroy.tools).

**Via GitHub:**
1. Open an [issue](https://github.com/phishdestroy/destroylist/issues/new) with the domain(s).
2. Include evidence if possible (screenshots, scan links).

## Request Domain Removal (False Positive)

If a legitimate domain was listed by mistake:

1. Use the [Appeals Form](https://phishdestroy.io/appeals/) (fastest).
2. Or open a GitHub issue with proof of legitimacy.

Approved domains are added to `allow/allowlist.json` and automatically removed from all lists.

## Contribute Code or Pipeline Improvements

1. Fork the repository.
2. Create a branch: `git checkout -b my-fix`.
3. Make your changes.
4. Run validation locally:
   ```bash
   pip install -r requirements.txt
   python scripts/validate_json.py
   python scripts/validate_and_clean.py
   ```
5. Open a Pull Request with a clear description.

## Add a New Blocklist Source

If you maintain a phishing blocklist and want it aggregated:

1. Open an issue with the feed URL and format (JSON array, plain text, hosts file, etc.).
2. The feed should be publicly accessible and updated regularly.
3. We'll review and add it to `smart_aggregator.py`.

## Guidelines

- All JSON files must be valid and sorted.
- No IP addresses in domain lists.
- No duplicates across lists.
- Respect the allowlist: never re-add allowed domains.
- Keep PRs focused: one fix or feature per PR.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold a respectful, harassment-free environment. Spam, abuse, and fake reports will not be tolerated.
