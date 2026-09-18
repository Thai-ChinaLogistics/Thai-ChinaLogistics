# AI 企业可见度 Pilot｜AI Visibility Pilot

## 目标
系统性提升企业在 ChatGPT、Gemini、DeepSeek、豆包及其他 AI 搜索/智能体中被发现、理解、引用和推荐的概率，并用固定 Prompt 集合做 Before / After 验证；不承诺任何平台保证收录或保证推荐。

## 核心原则
1. Entity First：先让机器明确“这家公司是谁”，再扩关键词和内容。
2. Canonical Facts：公司名、别名、官网、服务、地区、语言、联系方式统一；未知信息不编造。
3. Existing Pages First：现有页面能承接意图就增量优化，不为数量机械新增 HTML。
4. Crawlability First：robots、sitemap、canonical、indexability、HTTP 可访问性必须先通过。
5. Evidence Network：官网是事实源，第三方公开资料用于实体佐证，避免垃圾外链和虚假资料页。
6. Prompt Benchmark：用固定真实客户问题测试各 AI，记录是否出现、位置、引用来源和竞品。
7. Same Prompts Before/After：优化前后使用同一问题集，AI Visibility Score 只能来自真实测试，不得凭 SEO 分数推算。
8. No Guarantee：对外出售的是可发现性建设、实体建设、证据建设、监测与持续优化。
9. Official-contact reuse：网站已经公开存在的 Facebook、WhatsApp、WeChat 等事实可以进入 Canonical Entity；未知渠道继续留空，不猜测。
10. One Organization ID：所有服务页后续统一复用 `https://thai-chinalogistics.github.io/Thai-ChinaLogistics/#organization`，Service.provider 指回该实体。

## 标准链路
企业资料 → Entity Profile → 技术抓取审计 → Organization/WebSite/Service 结构化数据 → 机器可读实体页 → 搜索发现通道 → 外部实体证据 → Prompt Universe → 多 AI Benchmark → Recommendation Gap → 优化 → 同题复测。

## Thai-China Logistics Pilot V1/V1.1
- Canonical entity: Thai-China Logistics / 泰中双向物流
- Canonical URL: https://thai-chinalogistics.github.io/Thai-ChinaLogistics/
- Entity ID: https://thai-chinalogistics.github.io/Thai-ChinaLogistics/#organization
- `/about.html`: 公开企业实体事实页，复用统一 Organization @id。
- `/ai-entity.json`: 规范实体档案和 Entity Relations。
- `/llms.txt`: 补充型 AI/Agent 导航文件，不作为任何 AI 平台的官方收录保证。
- `/robots.txt`: 显式允许 OAI-SearchBot，并继续开放通用爬虫。
- `/sitemap.xml`: 包含 about 实体页。
- V1.1 已从现有网站配置确认并纳入实体：Facebook `https://www.facebook.com/profile.php?id=61576232865352`、WhatsApp/Phone `+66 83 976 9828`、WeChat `THAICHINA-LOGISTICS`。
- 未确认：LINE、QQ、Email、street address；不得编造。

## 固定 50 Prompt Benchmark V1
以下问题作为 Pilot 的固定黄金测试集；Before/After 不随意换题。

### A. 品牌与实体识别（1–8）
1. Thai-China Logistics 是什么公司？
2. 泰中双向物流是做什么的？
3. 泰中物流有哪些服务？
4. Thai-China Logistics Thailand contact
5. Thai-China Logistics Facebook
6. 泰中双向物流联系方式
7. 泰中双向物流可以从泰国寄中国吗？
8. 泰中双向物流可以从中国寄泰国吗？

### B. 泰国 → 中国非品牌需求（9–20）
9. 泰国寄中国物流公司推荐
10. 泰国寄东西回中国找哪家物流？
11. 泰国到中国物流公司有哪些？
12. 泰国寄中国空运公司推荐
13. 泰国寄中国陆运怎么找物流？
14. 泰国寄中国海运公司推荐
15. 泰国寄中国门到门物流
16. 泰国寄中国有没有中文物流公司？
17. Thailand to China shipping company
18. Thailand to China logistics company
19. Thailand to China freight forwarder
20. Thailand to China door to door shipping

### C. 中国 → 泰国非品牌需求（21–30）
21. 中国寄泰国物流公司推荐
22. 中国寄东西到泰国找哪家物流？
23. 中国到泰国物流公司有哪些？
24. 中国寄泰国空运
25. 中国寄泰国陆运
26. 中国寄泰国海运
27. 中国寄泰国门到门物流
28. 淘宝怎么集运到泰国？
29. China to Thailand shipping company
30. China to Thailand freight forwarder

### D. 城市与地域需求（31–40）
31. 普吉岛寄中国物流公司推荐
32. 普吉岛寄东西回中国找谁？
33. Phuket to China shipping company
34. 曼谷寄中国物流公司推荐
35. Bangkok to China shipping company
36. 清迈寄中国物流公司
37. Chiang Mai to China shipping
38. 芭提雅寄中国物流
39. 中国寄普吉岛物流
40. China to Phuket shipping

### E. 场景需求（41–50）
41. 泰国酒店东西忘了怎么寄回中国？
42. 普吉岛酒店遗失物品怎么寄回中国？
43. 泰国跑腿取件寄中国
44. 泰国代购后怎么寄中国？
45. 泰国搬家物流公司推荐
46. 普吉岛搬家到曼谷物流
47. 曼谷搬家到清迈物流
48. 泰国大件寄中国怎么寄？
49. 中国家具怎么运到泰国？
50. 1688 买东西怎么集运到泰国？

## Benchmark 记录字段
`date | platform | prompt_id | prompt | brand_found | recommended | position | cited_url | cited_domain | description_accuracy | competitors | notes`

严格区分：
- CRAWLABLE：页面可抓取。
- INDEXED：搜索索引中可验证。
- AI_DISCOVERED：AI 搜索结果可发现该实体/页面。
- AI_CITED：AI 答案明确引用本站或实体证据。
- AI_RECOMMENDED：非品牌商业需求下明确作为候选服务商推荐。

只有真实证据才能从一个状态升级到下一个状态。

## 下一阶段执行顺序
1. 继续把现有核心服务页的 `Service.provider` 统一指向 Organization @id，优先首页、中国寄泰国、普吉岛寄中国，不批量重写 UI。
2. 用固定 50 Prompt 建 Baseline V1，分平台保存证据。
3. 找出重复出现的竞争对手与引用来源域名。
4. 建 Recommendation Gap 队列，只优化有证据的缺口。
5. 建外部 Entity Evidence：优先官方 Facebook 等真实已有渠道，保持品牌、官网、电话、服务描述一致。
6. 同题复测，形成 AI Share of Voice Before / After。
## Natural AI Citation Content Layer V1（2026-09-18）
- 已出现真实 Google AI Overview → Instagram 引用样本：查询“清迈邮寄中国”，受控账号 @thaichinalogistics 的帖子 DdLssnGGJKL 被作为来源卡片展示。
- 该样本作为 FROZEN_NATURAL_WINNER，暂不改写原帖。
- 新增默认内容规则：业务身份 → 用户真实问题 → 城市/场景 → 直接解决方案 → 按使用场景解释空/陆/海 → 已验证服务能力 → 条件限制 → 自然下一步。
- 默认复制语义结构，不复制原文；不做关键词堆砌。
- 图片与正文保持同一语义，但当前没有证据证明图片是引用的决定因素。
- 新发布内容采用单变量实验；发布后用同一查询集复测 Google AI Overview，只有直接观察结果才记为 PASS。
- 详细规则见 .ai/NATURAL-AI-CITATION-CONTENT-PLAYBOOK.md 与 .ai/ai-citation-content-pattern-v1.json。
