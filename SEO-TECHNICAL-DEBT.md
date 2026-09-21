# SEO Technical Debt — 2026-09-08

## Scope and status

This is a measured debt register from the REAL_BROWSER_AND_ONLINE_VERIFICATION phase for E:\SEO物流网站. It records findings only. No homepage refactor, UI redesign, source implementation, commit, push, or deployment was performed in this phase.

Current technical SEO result: **PARTIAL**  
Current final verification result: **PARTIAL**

## Open items

| Priority | Item | Evidence | User impact | Recommended follow-up |
| --- | --- | --- | --- | --- |
| P1 | Five local homepage hero-carousel assets are missing | Browser/server evidence recorded local HTTP 404 for hero-sandbox-map-china-clean-v3.png, hero-pickup-v1.png, hero-special-items-v1.png, hero-consolidation-v1.png, and hero-service-overview-v1.png. The active hero image natural size was 0 × 0. Matching approved source assets exist in E:\物流网站最后部署, not in the target project. | Homepage hero is blank in local runtime, the carousel cannot load its approved images, and image validation cannot pass. | In an authorized implementation phase, restore only the exact five approved assets, then re-run desktop and mobile browser checks. |
| P1 | Current local SEO batch is not deployed | Official GitHub Pages returns 404 for express, price, and pickup pages, while homepage returns 200. | New high-intent landing pages are not reachable online. | Review only the intended diff, then use a separately authorized commit/push/deployment process and repeat online checks. |
| P1 | Homepage canonical and schema gaps | index.html has no canonical and no JSON-LD. Sitemap includes the official homepage URL, so canonical/sitemap alignment cannot pass. | Weakens canonical clarity and structured-data coverage. | Add only approved absolute canonical and schema structures after a dedicated SEO implementation review. |
| P2 | Schema coverage is incomplete | 16 JSON-LD blocks parse validly; five pages have no JSON-LD. WebSite and BreadcrumbList are absent from current coverage. | Incomplete machine-readable entity/page context. | Define a consistent approved schema template; do not duplicate Organization entities. |
| P2 | Open Graph coverage is incomplete | OG title/description is missing on homepage, three new static pages, and thailand-wide-shipping-to-china.html. og:image is absent on all 21 HTML files. No current og:image points to a broken resource. | Social-preview metadata is inconsistent. | After image-asset approval, add only verified absolute metadata and confirm requested resources return 200. |
| P2 | New static page template lacks uniform contact and language architecture | The new three pages have no language switch or WhatsApp/Facebook/WeChat controls, while existing homepage and regional pages do. | Conversion/contact and multilingual experience vary by template. | Make a product decision before adding shared UI; do not introduce it as an unreviewed SEO-only patch. |
| P2 | Formal homepage is a large inline-heavy artifact | index.html is 4,733,842 bytes. It contains one local img, three external, and five inline-data image references, plus five local hero-carousel background references; it has no external stylesheet or script references. | Performance tuning and safe maintenance are harder to isolate and regression-test. | Plan a separately approved, screenshot-regression-protected optimization; do not rewrite the frozen homepage during a content validation task. |

## Verification guardrails for follow-up work

- Treat the current online homepage and the local project as different deployment states until the new URLs return online HTTP 200.
- Verify all five restored hero-carousel assets through a real local HTTP server and browser network evidence, not only file existence.
- Keep canonical URLs absolute and equal to the sitemap URLs for the same pages.
- Parse every JSON-LD block before release; maintain one Organization identity.
- Verify all metadata image URLs with real HTTP 200 before relying on them.
- Re-run desktop 1440 × 900 and mobile 390 × 844 tests after any source change.

## Non-claims

- This register does not state that Google has indexed any URL.
- It does not state that an external contact tracker completed successfully.
- It does not authorize deployment or any irreversible change.
