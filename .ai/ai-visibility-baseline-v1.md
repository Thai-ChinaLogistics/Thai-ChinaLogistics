# AI Visibility Baseline V1 — Thai-China Logistics

Date: 2026-09-16
Status: BASELINE_STARTED

## Measurement rule

This baseline uses the frozen 50-query benchmark in `ai-visibility-benchmark-v1.json`. Results must distinguish:

1. CRAWLABLE — official page can be fetched.
2. INDEX_DISCOVERED — public search can retrieve the official domain/page for the tested query.
3. BRAND_RECOGNIZED — the system associates Thai-China Logistics / 泰中双向物流 with the official site and services.
4. CITED — an AI/search answer cites the official site.
5. RECOMMENDED — an AI answer presents the entity as a candidate for a non-brand commercial-intent query.

Never infer levels 2–5 from Schema, robots.txt, sitemap.xml, llms.txt or ai-entity.json alone.

## Initial public-search probe — 2026-09-16

Queries sampled:
- "Thai-China Logistics" / "泰中双向物流" / "Thai-ChinaLogistics"
- "泰国寄中国" + "Thai-China Logistics"
- "China to Thailand" + "Thai-China Logistics" + shipping
- "普吉岛寄中国" + "Thai-China Logistics" / "泰中双向物流"

Observed result:
- The tested public search did not return a clear official-domain result for these sampled brand/service combinations in this run.
- Therefore `INDEX_DISCOVERED` is **NOT YET VERIFIED** from this probe.
- `BRAND_RECOGNIZED`, `CITED`, and `RECOMMENDED` are also **NOT YET VERIFIED**.
- This does not mean the pages are absent from every search index or every AI provider. It only records what was actually observed in this measurement run.

## Current website-side readiness

- Canonical organization entity: READY
- About/entity fact page: READY
- `ai-entity.json`: READY
- Service → provider entity relationships: READY on audited service-page pattern
- `robots.txt` / sitemap / AI crawler access: READY from prior acceptance
- Frozen 50-query benchmark: READY

## Next optimization target

Do not create more thin keyword pages merely to increase page count. Priority order:

1. Strengthen first-party entity consistency across existing service pages.
2. Strengthen legitimate external entity evidence using existing official profiles/accounts.
3. Wait for/recheck public discovery and indexing.
4. Run the same frozen benchmark again.
5. When competitors are returned for a query, record their cited sources and compare evidence gaps before changing content.

## Pass criteria for V2

A change is counted only when the same frozen query produces a newly verifiable state transition, for example:

`NOT_DISCOVERED → INDEX_DISCOVERED → BRAND_RECOGNIZED → CITED → RECOMMENDED`

No synthetic AI Visibility percentage is allowed until enough benchmark queries have real observations.
