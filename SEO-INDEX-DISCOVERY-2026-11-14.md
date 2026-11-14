# Google URL Inspection：核心页面发现问题（2026-11-14）

## 实际证据

- 官方数据：Google Search Console URL Inspection API，SEO 自动分析工作流 #74，GitHub Actions run `43566932332`。
- 官网首页、中国寄泰国、普吉岛寄中国、行李寄回国的 Google `indexStatusResult.verdict` 为 `PASS`；`thailand-to-china-express.html` 为 `NEUTRAL`，`coverageState: URL is unknown to Google`，无 Google 最后抓取时间。
- 网站技术审计显示该页面 `indexable=true`、绝对 canonical 正确、Sitemap 包含网址、无断链、站内入链 `5`、无 robots 屏蔽；不是孤岛页。
- 2026-10-04 代码提交 `60b19b623d2281b35133b061886107e2bebc71a4` 修改了该页面（包含结构化数据/链接相关的 SEO/GEO 修复），但 `sitemap.xml` 中该 URL 的 `lastmod` 仍为 `2026-09-08`，比已确认的显著更新早。

## 安全修改范围

只把该 URL 的 Sitemap `lastmod` 修改为已确认的 **2026-10-04**，不擅自改成今天、不批量刷新其他 URL 日期、不添加新网页或改动既定网站 UI/业务承诺。修改后重新解析 XML，确认目标条目恰好一条，并执行网站已有 SEO CI；通过后回读线上 Sitemap。

Google 官方说明：`lastmod` 应反映上次显著内容/结构化数据/链接变化，不应无变化而更新日期。见 https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap 。

## 不能作出的推断

修复旧日期并不证明该因素就是 Google 尚未发现 URL 的根本原因，也不保证立刻爬取或建立索引。需持续使用现有 GSC URL Inspection 每日只读检查，观察 `UNKNOWN/NEUTRAL → PASS` 是否实际发生。百度、豆包等中国智能体需独立验证。
