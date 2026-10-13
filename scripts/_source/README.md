# DestroyList community site

Static, self-contained landing page plus machine-readable reference files for the GitHub Pages site (https://phishdestroy.github.io/destroylist/scripts/). Run `python build.py` (Python standard library only). Build sources: build.py, style.css, app.js, seo.py, mission.py, mission.css, mission.js, community_tools.py, community-tools.css, usability.py, usability.css, directory.js and the attributed local assets directory.

## Publishing

Copy dist/index.html to scripts/index.html and the companion metadata/reference files in dist/ to scripts/meta/. The Pages workflow (.github/workflows/pages.yml) builds Jekyll from the repository and publishes scripts/meta/ at the site root, so their URLs stay the same. The repository root stays the rendered README; the platform page lives under /scripts/.

The generated sitemap retains the existing docs and archive pages. Only the homepage modification date is changed. Existing robots policy remains unchanged.

## Public data and attribution

Thirty credited source projects, twelve configured upstream feeds, thirteen described datasets and twenty-eight formatted subscriptions. All original destinations are retained except the corrected MetaMask branch and Inversion DNSBL repository link. Unavailable historical release links remain labeled and current archive buttons use the existing repository directory.

Logos/public maintainer avatars are embedded with provenance in assets/logo-manifest.json. A dated metrics snapshot is visible before network requests; failures retain an explicit snapshot label. Feed-entry counts are distinguished from API normalized-domain counts and takedowns.

## Motion and discoverability

The mission-led hero contains a rotating canvas network sphere, flowing SVG signals and a static SVG fallback. The sphere is an illustration, not live telemetry. Canvas rendering is capped at about 30 FPS and device pixel ratio 1.75, stops outside the viewport or in a hidden tab, and respects reduced motion. Pointer movement produces a small bounded change in the viewing angle. Both the hero and footer offer synchronized motion controls.

Scroll reveals use the Web Animations API and IntersectionObserver when available; base content stays visible. Hover effects are bounded. Motion follows prefers-reduced-motion and a persistent user toggle. Changes to counts fade into their actual values; no intermediate domain totals are invented.

Server-rendered metadata includes a canonical URL, descriptive title/snippet, social metadata and a Schema.org graph with DataCatalog and thirteen Dataset entries. The graph matches visible links and descriptions. Structured data contains no unsupported ratings, fabricated identifier or promise of search inclusion. Machine-readable references are generated from the same source registry as the page. llms.txt is optional documentation for integrators, not a ranking mechanism.

The opening follows observations through analysis and open publication to defensive use. MetaMask’s public repository is a sourced example of reusable intelligence beyond one wallet, with its own license linked. Counts are preserved in an operational disclosure and in the feed tables; they are not presented as an impact ranking. Machine-readable descriptions reflect the same meaning.

## Verification

JavaScript syntax; H1 and canonical uniqueness; anchor and ID integrity; thirteen dataset schema objects with visible distribution links; complete source/format coverage; valid JSON and sitemap XML; companion reference paths; unchanged upstream attribution. Browser animation/layout testing and Search Console indexing verification were unavailable.

## Community tools directory

The directory credits 21 independently operated services, retaining all 22 supplied destinations (the phish.report analysis and main site share one card). Filters select checking, research or reporting and can be combined with text search. All entries and primary links are server-rendered and readable without JavaScript. Access notes distinguish public/guest functions, free accounts, quotas and paid features; PhishTank submission is explicitly marked as requiring sign-in. Tools are not automatically designated upstream feeds or partners.

The directory is also published as tools.json and an unordered Schema.org ItemList; llms-full.txt includes descriptions and access notes. Provider references are linked from each card. Site icons are embedded from provider-declared assets, with provenance in assets/tool-logo-manifest.json; neutral functional icons stand in where a declared icon was not available.

## Task paths and directory behavior

A Start section offers three routes: subscriptions, investigation tools and the public API, with direct reporting/correction links. The subscription builder appears before the format gallery, explains dataset scope and supports allowlisted `feed` and `format` URL parameters. Copy setup link produces a bookmarkable configuration without propagating unrelated query parameters.

Directories show the first nine source projects and six services alphabetically after JavaScript initializes. Show all, category filters and search still cover the full catalogs. All content is present without scripts. Deep links reveal a hidden tool and open containing disclosures. Header navigation indicates the current section; a back-to-top control appears farther down the page. Source cards use a readable single-column mobile layout.

Behavior checks verified compact catalogs, searching entries outside the initial view, category/task filtering, clearing, expansion/collapse, zero results, direct links to hidden cards and disclosures, and configuration links with allowlisted values. Generated HTML retains every external link and all source/tool records. These checks do not replace browser layout or accessibility testing, which remained unavailable.