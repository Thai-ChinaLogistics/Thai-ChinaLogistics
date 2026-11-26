# SEO Change Registry / SEO 增量变更登记

## 2026-10-14 | SEO-SNIPPET-001 | REVIEW_REQUIRED
- Scope: existing `thailand-to-china-express.html`, `bangkok-to-china.html`, `phuket-to-china.html`.
- Change: shorten initial HTML meta description to concise, truthful Chinese descriptions; retain canonical, title, language-specific runtime metadata, body, URL and schema unchanged.
- Evidence: SEO Engine site-audit 2026-10-13, 17 warnings; GSC 2026-09-13..2026-10-10 with 12 query/page rows, 0 clicks.
- Constraints: no price/time guarantee, no AI-indexing or AI-citation claim; no automatic production deployment.
- Decision: REVIEW_REQUIRED pending CI/static SEO audit, PR review and 7/14/28 day observation from merge date.
- Tracking: Winner protection, cannibalization, SAFE_AUTO/REVIEW_REQUIRED/BLOCKED, AI visibility evidence tiers retained in upstream SEO Engine.

## 2026-10-15 | Review correction
- Express page reverted to baseline: its original description was already concise (50 characters); no need to optimize it.
- Active changes limited to Bangkok and Phuket initial HTML descriptions.
- Pre-merge verification: inspect multilingual runtime descriptions and CI; pending.

## 2026-10-15 | Static validation
- PASS: both pages retain exactly one title, initial description and canonical; doctype intact; runtime zh/en/th metadata retained.
- PASS: initial descriptions are 65 and 64 Chinese characters respectively.
- NOT VERIFIED: browser-rendered language switching, CI workflow, production deployment and post-merge GSC impact.
- Gate: remain REVIEW_REQUIRED; no auto-merge until required validation is available.

## 2026-11-23 | SEO/GEO fixes (FAQPage, head metadata, title/H1, robots.txt, sea-freight wording, internal links)
- Scope: `index.html`, `about.html`, `china-to-thailand.html`, all other 26 subpages (head tags only), `robots.txt`, `sitemap.xml` (lastmod for the 3 visibly changed pages only), `tools/check_homepage_inline_assets.py` (baseline), `seo-inline/pickup-slide-3.png` (deleted).
- Change: (1) homepage FAQPage JSON-LD with the 9 visible FAQs verbatim; (2) robots meta, og:type, og:locale, og:site_name, og:image and Twitter cards added where missing (all 29 indexable pages now carry the full set; existing robots values untouched, thailand-wide-shipping stays noindex); (3) zh runtime metaTitle aligned to the static title so JS no longer rewrites it; hero carousel now always writes slide titles into the H1 and never hides it (H2 removed); (4) robots.txt explicitly Allows GPTBot, ChatGPT-User, OAI-SearchBot, ClaudeBot, anthropic-ai, PerplexityBot, Google-Extended, CCBot; wildcard Allow and Sitemap kept; (5) visible phone `+66 83 976 9828` (already public in JSON-LD/about) added to the homepage contact section; (6) sea freight removed as a listed service site-wide — homepage transport card, price note and pickup-carousel slide (5→4 slides, 30s→24s cycle), about service tags/knowsAbout/description, china-to-thailand option lists; the unified wording "海运服务暂未开放" is kept as a policy statement (homepage transport desc + china-to-thailand FAQ); (7) new homepage city/service entry section linking 7 cities + 9 services (all files verified to exist).
- NOT changed (verified against source, earlier browser audit was wrong on these): sitemap filenames are already correct `*-to-china.html` (no 404s); llms.txt filenames match the sitemap; prd-enhancements.js does not rewrite title/H1 and its sea-freight copy is already correct; ai-entity.json already lists sea freight under unavailableServices. No prices, transit times, reviews, email or address were invented.
- Verification: `python3 -m unittest discover -s tests` (75 tests PASS), `scripts/check_seo_static_metadata.py` PASS, `tests/check_inline_scripts.py` PASS, `node tests/check_lead_fallback.mjs` PASS, `tools/audit_geo_service_claims.py` PASS, `tools/audit_sitemap_pages.py` PASS; FAQPage JSON-LD validated verbatim against visible FAQs; china-to-thailand zh description 52 chars (50–180) and still exactly equals TCL zh description.
- Note: `pickup-slide-3.png` (sea-freight carousel image) removed from the asset baseline per the tool's own rule for intended image changes; file deleted, recoverable from git history.
