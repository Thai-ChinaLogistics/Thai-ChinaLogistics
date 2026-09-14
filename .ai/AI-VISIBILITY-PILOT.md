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

## 标准链路
企业资料 → Entity Profile → 技术抓取审计 → Organization/WebSite/Service 结构化数据 → 机器可读实体页 → 搜索发现通道 → 外部实体证据 → Prompt Universe → 多 AI Benchmark → Recommendation Gap → 优化 → 同题复测。

## Thai-China Logistics Pilot V1
- Canonical entity: Thai-China Logistics / 泰中双向物流
- Canonical URL: https://thai-chinalogistics.github.io/Thai-ChinaLogistics/
- Entity ID: https://thai-chinalogistics.github.io/Thai-ChinaLogistics/#organization
- `/about.html`: 公开企业实体说明页，复用现有 Organization @id。
- `/ai-entity.json`: 规范实体档案。
- `/llms.txt`: 补充型 AI/Agent 导航文件，不作为任何 AI 平台的官方收录保证。
- `/robots.txt`: 显式允许 OAI-SearchBot，并继续开放通用爬虫。
- `/sitemap.xml`: 新增 about 实体页。

## 下一阶段
1. 验证发布文件公网 200、JSON-LD、canonical、robots、sitemap。
2. 固定首批 50 条商业 Prompt。
3. 分平台记录 ChatGPT / Gemini / DeepSeek / 豆包 Baseline。
4. 找出重复出现的竞争对手和来源域名。
5. 建 Recommendation Gap 队列，只优化有证据的缺口。
6. 同题复测，形成 AI Share of Voice Before / After。
