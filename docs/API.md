[Destroylist](../README.md) / [Guides](README.md) / Threat intelligence API

# Threat intelligence API

Endpoints, scoring and integration examples.

<p>
  <a href="https://api.destroy.tools"><img src="../assets/actions/live-api.svg" alt="Live API" width="128" height="36"/></a>
  <a href="https://api.destroy.tools/v1/stats"><img src="../assets/actions/stats.svg" alt="Stats" width="128" height="36"/></a>
</p>

### Free, open, no API key.

Real-time **domain risk scoring (0-100)** across the Primary and Community datasets · scheduled sync

**Single & bulk check (500/req)** · Keyword search · Full feeds

<details>
<summary><b>Use the API</b> · endpoints, scoring & integration examples</summary>

```mermaid
%%{init: {"themeVariables":{"background":"transparent","primaryBorderColor":"#c52237","lineColor":"#c52237","clusterBkg":"transparent","clusterBorder":"#898999","edgeLabelBackground":"transparent","fontFamily":"system-ui, sans-serif"},"flowchart":{"curve":"basis","htmlLabels":true}}}%%
flowchart LR
  Request["Client Request<br/>(Single / Bulk)"] e1@--> API["Live API<br/>api.destroy.tools"]
  API e2@--> Engine["Threat Engine<br/>(Risk Score 0-100)"]
  Engine e3@--> DB[("Destroylist DB<br/>1M+ Threats")]
  DB e4@--> Engine
  Engine e5@--> Response["JSON Response<br/>(Severity & Status)"]

  classDef client fill:transparent,stroke:#898999,stroke-width:2px;
  classDef api fill:transparent,stroke:#c52237,stroke-width:2px;
  classDef db fill:transparent,stroke:#898999,stroke-width:2px,stroke-dasharray: 5 5;
  classDef animate stroke:#c52237,stroke-width:2px,stroke-dasharray:10 5,stroke-dashoffset:900,animation:dash 22s linear infinite;
  classDef animateDark stroke:#898999,stroke-width:2px,stroke-dasharray:10 5,stroke-dashoffset:900,animation:dash 22s linear infinite;

  class Request client;
  class API,Engine,Response api;
  class DB db;
  class e1,e2,e3,e5 animate;
  class e4 animateDark;
```

### Endpoints

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| `GET` | [`/v1/check?domain=`](https://api.destroy.tools/v1/check?domain=example-phish.xyz) | Single domain check with risk score & severity |
| `POST` | `/v1/check/bulk` | Bulk check up to **500 domains** per request |
| `GET` | [`/v1/search?q=`](https://api.destroy.tools/v1/search?q=metamask) | Search blocklisted domains by keyword |
| `GET` | [`/v1/feed/{list}`](https://api.destroy.tools/v1/feed/primary) | Download full domain feeds (primary, community, active) |
| `GET` | [`/v1/stats`](https://api.destroy.tools/v1/stats) | Live statistics & domain counts |

**Per-IP quotas:** 300 data units/minute; intelligence routes have 30 units/minute and 1,000/day. Request costs vary by endpoint. On HTTP 429, respect `Retry-After`. [Current limits and response schemas](https://api.destroy.tools/openapi.json).

### Threat Scoring

Listed-domain results include a **risk score (0–100)** and the API's severity verdict. Signals include curated and community listings, DNS/HTTP liveness, multiple sources and naming patterns. Unlisted domains can return separate heuristic signals; a missing listing is not a safety guarantee.

Use the returned `threat`, `severity` and `flags` fields. The [current OpenAPI specification](https://api.destroy.tools/openapi.json) defines each response shape.

<p>
<img src="../assets/severity-critical.svg" alt="Critical severity" width="150" height="30"/>
<img src="../assets/severity-high.svg" alt="High severity" width="150" height="30"/>
<img src="../assets/severity-medium.svg" alt="Medium severity" width="150" height="30"/>
<img src="../assets/severity-low.svg" alt="Low severity" width="150" height="30"/>
</p>

### Quick Integration

**cURL**
```bash
curl "https://api.destroy.tools/v1/check?domain=suspicious-site.xyz"
```

**Python**
```python
import requests
domain = "example.com"
r = requests.get("https://api.destroy.tools/v1/check", params={"domain": domain}, timeout=30)
r.raise_for_status()
result = r.json()
if result["threat"]:
    print(f"BLOCKED: {result['severity']} (score: {result['risk_score']})")
```

**JavaScript**
```javascript
const domain = "example.com";
const r = await fetch(`https://api.destroy.tools/v1/check?domain=${encodeURIComponent(domain)}`);
if (!r.ok) throw new Error(`API returned HTTP ${r.status}`);
const data = await r.json();
if (data.threat) console.warn("PHISHING:", data.severity, data.risk_score);
```

**Bulk Check**
```bash
curl -X POST "https://api.destroy.tools/v1/check/bulk" \
  -H "Content-Type: application/json" \
  -d '{"domains":["site1.com","site2.xyz","site3.top"]}'
```

</details>
