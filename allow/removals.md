`allowlist.json` contains explicit exceptions. `removals.json` records executed
appeal decisions and accepted source withdrawals, without declaring a domain
safe or granting an unconditional allowlist exception. Each record names the
exact host, decision time and original appeal or issue.

All current feeds and derived formats must apply both files. A stale external
feed entry is not a new assessment and cannot undo a recorded removal.
The exact host and its `www` form are covered; sibling tenants and other
subdomains are not. Shared service roots are prohibited.

To relist a removed host, a reviewer must document the source/report, observation
date and specific URL or behavior in the original appeal discussion, then remove
only the corresponding record in a reviewed commit. Do not lift removals merely
because an upstream feed still contains the hostname. Historical Git commits
remain available as evidence; current community lists are consumable blocklists.
