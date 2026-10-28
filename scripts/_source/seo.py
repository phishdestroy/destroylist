"""Generate public metadata from the same source registry as the visible page."""
import json,re
from datetime import date
from html import escape
from pathlib import Path
from community_tools import TOOLS,reference_text,write_registry
from xml.etree import ElementTree as ET
BASE='https://phishdestroy.github.io/destroylist/scripts/'
# Metadata files are published at the site root (see .github/workflows/pages.yml)
SITE='https://phishdestroy.github.io/destroylist/'
TITLE='DestroyList — Community Phishing & Scam Blocklists'
DESCRIPTION='Free community phishing and scam blocklists for AdGuard, uBlock Origin, Pi-hole and DNS. Transparent sources, public threat intelligence API and free appeals.'
def write_json(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def enhance_and_write(root,html,sources,active_sources,feeds,formats,raw,repo):
    out=root/'dist';today=date.today().isoformat()
    html=re.sub(r'<title>.*?</title>','<title>'+escape(TITLE)+'</title>',html,count=1)
    html=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="'+escape(DESCRIPTION,quote=True)+'">',html,count=1)
    html=re.sub(r'<meta property="og:title" content="[^"]*">','<meta property="og:title" content="'+escape(TITLE,quote=True)+'">',html,count=1)
    html=re.sub(r'<meta property="og:description" content="[^"]*">','<meta property="og:description" content="'+escape(DESCRIPTION,quote=True)+'">',html,count=1)
    html=html.replace('name="twitter:card" content="summary_large_image"','name="twitter:card" content="summary"')
    extra=f'''<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1"><meta property="og:site_name" content="DestroyList"><meta name="twitter:title" content="{escape(TITLE,quote=True)}"><meta name="twitter:description" content="{escape(DESCRIPTION,quote=True)}"><link rel="alternate" type="application/ld+json" href="../dataset-catalog.jsonld" title="Dataset catalog"><link rel="alternate" type="text/plain" href="../overview.txt" title="Readable project reference"><link rel="sitemap" type="application/xml" href="../sitemap.xml">'''
    organization={'@type':'Organization','@id':'https://phishdestroy.io/#organization','name':'PhishDestroy','url':'https://phishdestroy.io/','description':'Independent, non-commercial maintainer of DestroyList.','sameAs':['https://github.com/phishdestroy']}
    source_rows=[{'name':name,'category':cat,'description':desc,'project_url':url,'feed_url':feed or None,'relationship':'configured_upstream' if name in active_sources else 'community_credit'}for name,cat,desc,url,feed in sources]
    source_doc={'name':'DestroyList source directory','reviewed_at':today,'canonical_url':BASE+'#sources','configuration_url':repo+'/blob/main/scripts/smart_aggregator.py','notes':['Configured upstream entries are taken from SOURCES_CONFIG.','Community credits do not imply current ingestion, endorsement or a partnership.','Source data and logos retain their own rights and licenses.'],'sources':source_rows}
    upstream=[r['feed_url'] for r in source_rows if r['relationship']=='configured_upstream']
    definitions={
      'primary':'Curated phishing and scam indicators maintained by the project. This is the full published feed, not a count of active sites or confirmed takedowns.',
      'primary_dns':'The subset of the primary feed whose entries resolve in DNS at the latest published check. DNS resolution alone does not prove malicious content.',
      'community':'Indicators aggregated from configured public upstream feeds and the primary list. Source licenses remain applicable, and an entry may appear in more than one feed.',
      'community_dns':'The DNS-resolving subset of the community dataset at the latest published check. A domain missing from this subset is not established as safe.',
      'primary_content':'Primary indicators passing additional HTTP content checks. Cloaking and changing content can limit coverage; use the full feed when broader coverage is needed.',
      'community_content':'Community indicators passing additional HTTP content checks. This is a checked subset, not a comprehensive record of every phishing domain.'}
    parent={'primary_dns':'primary','primary_content':'primary','community_dns':'community','community_content':'community'}
    datasets=[];catalog_rows=[]
    for name,desc,cadence,path,key in feeds:
        distributions=[{'@type':'DataDownload','name':name+' '+ext.upper(),'encodingFormat':mime,'contentUrl':raw+path+'.'+ext}for ext,mime in [('json','application/json'),('txt','text/plain')]]
        ds={'@type':'Dataset','@id':BASE+'#dataset-'+key,'url':BASE+'#dataset-'+key,'name':'DestroyList '+name,'description':definitions[key],'publisher':{'@id':organization['@id']},'inLanguage':'en','isAccessibleForFree':True,'keywords':['phishing','scam domains','threat intelligence','domain blocklist'],'includedInDataCatalog':{'@id':BASE+'#catalog'},'usageInfo':BASE+'#reuse','distribution':distributions,'variableMeasured':'Published domain indicators'}
        if key=='community':ds['isBasedOn']=[raw+'list.json']+upstream
        elif key in parent:ds['isBasedOn']={'@id':BASE+'#dataset-'+parent[key]}
        if key.startswith('primary'):ds['license']=repo+'/blob/main/LICENSE'
        datasets.append(ds);catalog_rows.append({'id':key,'name':name,'description':definitions[key],'documented_update_schedule':cadence,'landing_url':ds['url'],'files':{ext:raw+path+'.'+ext for ext in ['json','txt']}})
    allow={'@type':'Dataset','@id':BASE+'#dataset-allowlist','url':BASE+'#dataset-allowlist','name':'DestroyList Allowlist','description':'Reviewed domains cleared from false-positive listings. Maintained manually to support corrections and avoid repeated false-positive inclusion.','publisher':{'@id':organization['@id']},'isAccessibleForFree':True,'includedInDataCatalog':{'@id':BASE+'#catalog'},'usageInfo':BASE+'#reuse','license':repo+'/blob/main/LICENSE','distribution':[{'@type':'DataDownload','encodingFormat':'application/json','contentUrl':raw+'allow/allowlist.json'}]}
    datasets.append(allow);catalog_rows.append({'id':'allowlist','name':'Allowlist','description':allow['description'],'documented_update_schedule':'Manual review','landing_url':allow['url'],'files':{'json':raw+'allow/allowlist.json'}})
    roots=[('Primary roots','active_root_domains','primary','Root-domain projection of the primary dataset; subdomains and shared hosting infrastructure are excluded.'),('Primary live roots','online_root_domains','primary_dns','DNS-active root-domain projection of the primary dataset; shared hosting infrastructure is excluded.'),('Primary service subdomains','services_domains','primary','Individual hosting-platform subdomains from the primary dataset. These should not be treated as a listing of the entire shared hosting provider.'),('Community roots','community_root_domains','community','Root-domain projection of the community dataset; subdomains and shared hosting infrastructure are excluded.'),('Community live roots','community_online_root_domains','community_dns','DNS-active root-domain projection of the community dataset; shared hosting infrastructure is excluded.'),('Community service subdomains','community_services_domains','community','Individual hosting-platform subdomains from the community dataset. These should not be treated as a listing of the entire shared hosting provider.')]
    for name,path,parent_key,desc in roots:
        ds={'@type':'Dataset','@id':BASE+'#dataset-root-'+path,'url':BASE+'#dataset-root-'+path,'name':'DestroyList '+name,'description':desc,'isAccessibleForFree':True,'publisher':{'@id':organization['@id']},'includedInDataCatalog':{'@id':BASE+'#catalog'},'isBasedOn':{'@id':BASE+'#dataset-'+parent_key},'usageInfo':BASE+'#reuse','distribution':[{'@type':'DataDownload','encodingFormat':mime,'contentUrl':raw+'rootlist/'+path+'.'+ext}for ext,mime in [('json','application/json'),('txt','text/plain')]]}
        datasets.append(ds);catalog_rows.append({'id':'root-'+path,'name':name,'description':desc,'landing_url':ds['url'],'files':{ext:raw+'rootlist/'+path+'.'+ext for ext in ['json','txt']}})
    catalog={'@type':'DataCatalog','@id':BASE+'#catalog','name':'DestroyList public threat intelligence catalog','description':'Public phishing and scam domain datasets, activity-checked subsets, root-domain projections and a false-positive allowlist. Compiled from project research and credited community sources.','url':BASE+'#downloads','publisher':{'@id':organization['@id']},'isAccessibleForFree':True,'dataset':[{'@id':d['@id']}for d in datasets]}
    website={'@type':'WebSite','@id':BASE+'#website','url':BASE,'name':'DestroyList','description':DESCRIPTION,'inLanguage':'en','publisher':{'@id':organization['@id']}}
    webpage={'@type':'WebPage','@id':BASE+'#webpage','url':BASE,'name':TITLE,'description':DESCRIPTION,'inLanguage':'en','dateModified':today,'isPartOf':{'@id':website['@id']},'mainEntity':{'@id':catalog['@id']},'publisher':{'@id':organization['@id']}}
    tool_list={'@type':'ItemList','@id':BASE+'#tool-directory','url':BASE+'#community-tools','name':'Community phishing investigation and reporting tools','description':'Independently operated scanners, reputation checks, infrastructure research and phishing reporting routes used by the maintainers. Non-exhaustive; access conditions vary.','itemListOrder':'https://schema.org/ItemListUnordered','numberOfItems':len(TOOLS),'itemListElement':[{'@type':'ListItem','position':i+1,'name':t['name'],'url':BASE+'#tool-'+t['id'],'item':{'@type':'WebPage','name':t['name'],'url':t['url'],'description':t['description']}}for i,t in enumerate(TOOLS)]}
    webpage['mentions']={'@id':tool_list['@id']}
    graph={'@context':'https://schema.org','@graph':[organization,website,webpage,catalog,tool_list]+datasets}
    jsonld=json.dumps(graph,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    html=html.replace('</head>',extra+'<script type="application/ld+json">'+jsonld+'</script></head>')
    resource_block='''<div class="research-resources" id="research-resources"><div><h3>For researchers and integrations.</h3><p>Readable project facts, direct download metadata and the complete source registry. The API remains the reference for current checks and feed availability.</p></div><div class="resource-links"><a href="../overview.txt">Project overview <span>TXT ↗</span></a><a href="../datasets.json">Download catalog <span>JSON ↗</span></a><a href="../sources.json">Source registry <span>JSON ↗</span></a><a href="../tools.json">Community tool directory <span>JSON ↗</span></a><a href="../llms.txt">Agent reading guide <span>TXT ↗</span></a></div></div>'''
    html=html.replace('<section id="faq"', '<section id="research" class="wrap">'+resource_block+'</section><section id="faq"')
    overview=f'''# DestroyList: community phishing and scam blocklists

Canonical page: {BASE}
Maintainer: PhishDestroy — https://phishdestroy.io/
Reference reviewed: {today}

DestroyList is an independent, non-commercial public resource for sharing phishing and scam domain indicators. It combines project research with configured upstream feeds and credits the wider community. Public data, API access and appeals are free. Listings and corrections follow evidence; there are no paid delistings.

## One shared mission: stop phishing

The common objective is to help people avoid phishing through shared observations, analysis and defensive intelligence. Published indicators are starting points for investigation, filtering, detection rules and further research. Counts describe files; they do not measure the total work behind them or downstream protection. The page's animated network illustrates this idea; it is not live attack telemetry.

MetaMask publishes Web3 phishing indicators at https://github.com/MetaMask/eth-phishing-detect . Other defenders can study and reuse this public work under its source license: https://github.com/MetaMask/eth-phishing-detect/blob/main/LICENSE . DestroyList's configured upstream sources include MetaMask; see the aggregation configuration linked below. Attribution is not a claim of sponsorship or endorsement.

## Finding the right starting point

Start with {BASE}#start for three routes: add a blocklist to a compatible client, investigate or report a link, or integrate the public API. Listings can be appealed at {BASE}#appeals . The subscription selector at {BASE}#subscription explains primary/community and full/live datasets. Its copyable setup link preserves the chosen dataset and format.

Source and tool directories are alphabetical. Their initial view is compact; search and filters cover every entry, and Show all reveals the complete directory. All entries remain present in the generated HTML. Individual tool links open their cards even when outside the initial view.

## Scope and interpretation

The primary feed contains project-curated indicators. Community feeds aggregate public sources and the primary list. DNS-active subsets reflect resolving entries, not proof of malicious content. Content-verified subsets add HTTP checks and can miss cloaking. An unlisted domain is not a safety certificate. The project submits evidence to providers; registrars and hosts decide enforcement.

Published feed-entry counts and API normalized unique-domain counts are different measures. Lists overlap. Counts are not confirmed takedowns. Use the timestamp returned with the metrics, not the date a reader opens the page.

Live feed metrics: {raw}dns/metrics.json
API statistics: https://api.destroy.tools/v1/stats

## Downloads

Primary and community lists are available in JSON and plain text. DNS-oriented formats include Hosts, AdBlock for AdGuard and uBlock Origin, Dnsmasq, Unbound and RPZ, with Redis output for application use. Root projections and hosting-platform subdomains are separate datasets. Inspect file scope before blocking an entire parent domain.

Download selector: {BASE}#downloads
Dataset catalog: {SITE}datasets.json
Schema.org catalog: {SITE}dataset-catalog.jsonld

## Public API

Documentation: https://api.destroy.tools/
OpenAPI contract: https://api.destroy.tools/openapi.json
Base URL: https://api.destroy.tools

GET /v1/check?domain=example.com — a domain check
POST /v1/check/bulk — at most 500 domains per request
GET /v1/search?q=example — substring search
GET /v1/feed/{{list}} — a complete feed
GET /v1/stats — counts and synchronization
GET /v1/health — service health and freshness
GET /v1/feeds — available files and checksums
GET /v1/feed/{{list}}/delta — incremental additions and removals

No API key is required. Handle errors, timeouts and rate limits. Missing risk fields and failed requests do not mean zero risk. Current API behavior and limits are documented at the API origin.

## Source attribution and reuse

Configured upstream feeds: {len(active_sources)}.
Credited source and community projects: {len(sources)}.
Current configuration: {repo}/blob/main/scripts/smart_aggregator.py
Complete source directory: {SITE}sources.json

Configured upstreams are marked separately from broader community credits. Attribution, logos and public maintainer avatars do not imply endorsement or a formal partnership. The repository declares MIT; upstream data may have separate conditions. Reuse must respect those conditions. Community intelligence is shared for defensive cooperation, not claimed as an exclusive discovery.

Repository license: {repo}/blob/main/LICENSE
Reuse notes: {BASE}#reuse

## Community investigation tools

The maintainers use and credit independently operated scanners, reputation checks, infrastructure research services and reporting channels. Many basic functions are free and work without registration. This is not universal: PhishTank submissions require a free account, PolySwarm has limited anonymous access, and other services apply their own quotas or paid tiers. Public submissions can help other defenders, but visibility and sharing vary by provider. Public scans may expose URLs; check the selected visibility before sharing private links. This directory is non-exhaustive and is distinct from configured upstream feeds.

Tool directory: {BASE}#community-tools
Machine-readable directory and provider references: {SITE}tools.json

## Appeals and corrections

Submit or track: https://phishdestroy.io/appeals/
Public issue: {repo}/issues/new?template=appeal.yml

Appeals are free. Both the official form and GitHub issues accept a domain and a short explanation. No evidence or proof of ownership is required; screenshots and links are optional. The official form also works without an account. The official policy describes its 48-hour review window and auto-approval when no reviewer confirms the listing in time. Refer to that page for current timing and rules. External services control their own refresh schedules.

## Distribution, archives and community

Repository: {repo}
Archives: {repo}/tree/main/archives
Daily changes: {repo}/tree/main/changes
Public commits: {repo}/commits/main/
Dataset distribution: https://huggingface.co/datasets/phishdestroy/destroylist
OTX pulses: https://otx.alienvault.com/user/phishdestroy/pulses
Toolkit: https://destroy.tools/
Domain analyzer: https://analyze.destroy.tools/
URL scanner: https://ban.destroy.tools/
Threat reports: https://t.me/PhishDestroy_bot
Alerts: https://t.me/destroy_phish
Contact: contact@phishdestroy.io

Older snapshots: {repo}/releases/tag/archives
'''
    guide=f'''# DestroyList

> A non-commercial community resource for open phishing and scam blocklists, credited sources, public API access and free appeals. Maintained by PhishDestroy.

Canonical page: {BASE}

## Project references

- [Readable overview]({SITE}overview.txt): scope, definitions, methods, limits, reuse and appeals.
- [Full reference]({SITE}llms-full.txt): the overview plus dataset downloads and source attribution.
- [Dataset catalog]({SITE}datasets.json): exact download URLs and documented refresh schedules.
- [Structured datasets]({SITE}dataset-catalog.jsonld): Schema.org metadata matching the visible page.
- [Source registry]({SITE}sources.json): configured upstreams distinguished from wider community credits.
- [Community tools]({SITE}tools.json): scanners, investigation and reporting routes, with individual access notes and provider references.

## Current services

- [API reference](https://api.destroy.tools/): authoritative endpoints, limits and response semantics.
- [OpenAPI description](https://api.destroy.tools/openapi.json): the API's published contract.
- [Feed metrics]({raw}dns/metrics.json): dated feed-entry counts.
- [Repository]({repo}): source, license and change history.
- [Official appeals](https://phishdestroy.io/appeals/): submission, tracking and current review policy.

## Interpretation

The shared objective is to stop phishing through open observations, analysis and defensive reuse. Feed size is not an impact score; an animated illustration is not live telemetry. Unlisted does not mean safe. DNS-active does not prove malicious content. HTTP checks can miss cloaking. Feed counts overlap and differ from API normalized-domain totals. Listings and reports are not confirmed takedowns. Source attribution does not imply a partnership. Upstream licenses remain applicable. The reference contains no live-domain safety guarantee.
'''
    downloads={'name':'DestroyList download catalog','canonical_url':BASE,'metadata_reviewed_at':today,'counts_url':raw+'dns/metrics.json','api_catalog_url':'https://api.destroy.tools/v1/feeds','license_notes':'Repository MIT license; upstream data can retain separate conditions. See source registry and project license.','datasets':catalog_rows,'format_subscriptions':[{'dataset':key,'format':name,'url':raw+'rootlist/formats/'+key+'/'+file}for key in ['primary','primary_active','community','community_active']for _,name,file,_,_ in formats]}
    write_registry(root,BASE)
    write_json(out/'datasets.json',downloads);write_json(out/'sources.json',source_doc);write_json(out/'dataset-catalog.jsonld',graph)
    (out/'overview.txt').write_text(overview);(out/'llms.txt').write_text(guide)
    full=overview+'\n## Dataset download directory\n\n'+'\n'.join('### '+d['name']+'\n'+d['description']+'\n'+'\n'.join(f'- {fmt.upper()}: {url}'for fmt,url in d['files'].items())+'\n'for d in catalog_rows)
    full+='\n## Complete source directory\n\n'+'\n'.join(f"- {r['name']} ({r['relationship']}): {r['project_url']}"+(' | Feed: '+r['feed_url']if r['feed_url']else'')for r in source_rows)+'\n'
    full+=reference_text()
    (out/'llms-full.txt').write_text(full)
    sitemap=(root/'assets/original-sitemap.xml').read_text()
    ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9');doc=ET.fromstring(sitemap);ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    for node in doc.findall('s:url',ns):
        if node.find('s:loc',ns).text==BASE:node.find('s:lastmod',ns).text=today
    (out/'sitemap.xml').write_bytes(ET.tostring(doc,encoding='utf-8',xml_declaration=True))
    (out/'robots.txt').write_text((root/'assets/original-robots.txt').read_text())
    return html