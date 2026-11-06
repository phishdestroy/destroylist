[Destroylist](../README.md) / [Guides](README.md) / Integration guide

# Integration guide

Connect the feeds to your tools.

<br>

### One-Click Subscribe URLs

| Tool | Format | URL |
|:-----|:------:|:----|
| **Pi-hole** | Hosts | `https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/hosts.txt` |
| **AdGuard Home** | AdBlock | `https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/adblock.txt` |
| **uBlock Origin** | AdBlock | `https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/adblock.txt` |
| **pfSense / OPNsense (Unbound)** | Unbound | `https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/unbound.conf` |
| **BIND / Knot DNS (RPZ)** | RPZ | `https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/rpz.zone` |
| **Dnsmasq** | Dnsmasq | `https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/dnsmasq.conf` |

> **Pi-hole** — Settings > Blocklists > paste the Hosts URL<br>
> **AdGuard Home** — Filters > DNS Blocklists > Add blocklist > paste the AdBlock URL<br>
> **uBlock Origin** — Settings > Filter lists > Import > paste the AdBlock URL<br>
> **pfSense** — Services > DNS Resolver > paste the Unbound URL<br>
> **BIND/Knot** — Add the RPZ URL as a response-policy zone

### curl One-Liners

```bash
# Plain domain list
curl -fsSL https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/domains.txt -o domains.txt

# Hosts format (Pi-hole, /etc/hosts)
curl -fsSL https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/hosts.txt -o hosts_blocklist.txt

# AdBlock format (uBlock Origin, AdGuard)
curl -fsSL https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/adblock.txt -o adblock.txt

# Dnsmasq
curl -fsSL https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/dnsmasq.conf -o dnsmasq_blocklist.conf

# Unbound (pfSense / OPNsense)
curl -fsSL https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/unbound.conf -o unbound_blocklist.conf

# RPZ (BIND / Knot)
curl -fsSL https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/rpz.zone -o rpz_blocklist.zone
```

### Python
```python
import requests
blocklist = requests.get('https://raw.githubusercontent.com/phishdestroy/destroylist/main/list.json').json()
is_malicious = "suspicious-domain.com" in blocklist
```

### Bash
```bash
curl -s https://raw.githubusercontent.com/phishdestroy/destroylist/main/list.txt | grep -q "suspicious-domain.com" && echo "BLOCKED"
```


## Redis

Download [redis.txt](https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary/redis.txt) for loading with `redis-cli --pipe`. The generated loader builds a temporary set and swaps it into place.

```bash
curl -fsSL https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary/redis.txt -o redis.txt
redis-cli --pipe < redis.txt
redis-cli SISMEMBER destroylist:primary example.com
```
