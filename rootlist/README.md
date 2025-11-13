<p align="center">
  <img src="image.png" alt="PhishDestroy Rootlist Banner" width="950">
</p>

# destroylist: root-only domain list

A minimal, DNS-validated list of **registrable root domains**, designed for consumers who block at the domain level.

## Contents

- `active_root_domains.json`  
  - Derived from `dns/active_domains.json`  
  - Reduced to registrable domains using `tldextract`  
  - Hosting / infrastructure platforms are removed  
  - DNS-validated (A/AAAA/CNAME/MX/NS)

- `invalid_root_domains.json`  
  - Candidates that did not return any DNS records

## Excluded (infra / hosting)

Root domains that should **never** be blocked globally, including but not limited to:

- **multi-tenant app hosting:**  
  `vercel.app`, `netlify.app`, `github.io`, `render.com`, `onrender.com`,  
  `firebaseapp.com`, `web.app`, `pages.dev`, `workers.dev`, `cprapid.com`,  
  `windows.net`, `fastly.net`, `sslip.io`, `duckdns.org`, `replit.dev`,  
  `surge.sh`, `typedream.app`, `hostingersite.com`

- **website builders / shared platforms:**  
  `weebly.com`, `weeblysite.com`, `wixsite.com`,  
  `wordpress.com`, `blogspot.com`, `blogspot.am`,  
  `webflow.io`, `square.site`, `godaddysites.com`,  
  `webcindario.com`, `home.pl`, `pineapple.page`, `gitbook.io`

- **decentralized / web3 gateways:**  
  `ipfs.io`, `cloudflare-ipfs.com`, `dweb.link`,  
  `infura-ipfs.io`, `eth.limo`

- **SaaS / course hosts:**  
  `teachable.com`

## Generation

This list is produced by scripted reduction of the main dataset, removing  
non-registrable and infrastructure roots, and validating active records.
