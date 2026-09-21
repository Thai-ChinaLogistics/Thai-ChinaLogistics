# Protected routes and keyword guard — 2026-09-21

The directory is a non-Git static delivery checkout. Before any implementation, a file-level copy was created at `.ai/baseline-20260921`.

Protected primary routes are the 21 URLs listed in `sitemap.xml`. No existing HTML URL may be deleted, renamed, replaced by a duplicate primary URL, or changed to `noindex` without a separately evidenced requirement.

Protected keyword clusters from `SEO-KEYWORD-RESEARCH-2026-09-08.md` include Thailand-to-China, China-to-Thailand, Bangkok/Phuket/Chiang Mai/Pattaya city terms, luggage, Thai products, purchasing/consolidation, pickup, air/land/sea freight, price, timing, cargo eligibility and process questions. Existing primary mappings remain the source of truth; the rejected `thai-fan-merch-to-china.html` URL remains uncreated.

The utility page `thailand-wide-shipping-to-china.html` is intentionally `noindex,follow` and is not in the public sitemap. It is not treated as a missing public primary route.

External side effects held: production publish, real customer form submission, authenticated services, CAPTCHA and search-engine re-crawl.
