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

唯一真源：`.ai/ai-visibility-benchmark-v1.json`。

本文件不再复制维护另一份 50 Prompt 文本清单，避免 Prompt 漂移。任何 Agent、Codex、自动审计器、Before/After 验收都必须读取该 JSON 中的冻结 Prompt IDs 与原文；如文档与 JSON 冲突，以该 JSON 为准。

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


## Codex GEO Site Auditor V1（2026-09-18）

机器可执行规格：`.ai/codex-geo-site-auditor-v1.json`。后续自动审计/修复优先读取该文件，本节作为人类可读说明。

定位：这是 `ai-visibility-growth-engine｜AI 搜索收录与推荐增长引擎` 的站内自动审计与修复模块，不是独立重复产品。

### 输入
- 企业官网 URL
- 可选：代码仓库 / 本地项目
- 可选：核心业务、目标国家/城市、已验证企业事实
- 固定 Prompt Universe（若已有）

### 自动审计链路
URL / Repo
→ Crawlability Audit
→ Entity Audit
→ Schema Audit
→ Canonical Audit
→ Internal Link Graph
→ Answer Extraction Audit
→ Performance / Crawl Efficiency
→ Content / Intent Gap
→ Prompt-to-Page Mapping
→ GEO Fix Plan
→ Codex Incremental Patch
→ Before / After Validation

### 审计项
1. Crawlability：robots、sitemap、canonical、indexability、HTTP 状态、重复/孤立页面。
2. Entity：企业名称、别名、官网、服务、地区、语言、联系方式是否统一；未知字段保持 UNKNOWN。
3. Schema：仅在页面语义真实匹配时使用 Organization、WebSite、WebPage、Service、BreadcrumbList、Product 等类型；禁止“为了 Schema 数量而加 Schema”。
4. FAQ / Answer Layer：FAQ 即使没有专用 Schema，也必须做到问题明确、答案可直接抽取、事实可验证。普通企业 FAQ 不机械套用不适用的 QAPage。
5. Internal Link Priority：核心实体页、核心服务页、核心路线页具有清晰优先级，避免抓取入口和语义权重混乱。
6. Answer Extraction：页面首段优先给出可直接回答用户问题的结论；随后提供属性、流程、适用场景、限制与下一步。
7. Performance / Crawl Efficiency：检查影响抓取与渲染的明显问题，但不把 Core Web Vitals 或速度分数伪装成 AI Citation 证明。
8. Prompt Mapping：每个核心页面映射到真实需求 Prompt；优先修补已有页面，不制造薄内容重复页。
9. Evidence Boundary：站内代码优化不能代替外部 Entity Evidence；E1/E2/E3 仍需真实公开来源。
10. Validation：Google Search 与 AI 平台双轨验收；相同 Prompt 做 Before / After，只有直接观察才允许升级 CITED / RECOMMENDED。

### 决策规则
- Existing Pages First：现有页能承接意图，就增量修复。
- Entity First：先解决“是谁”，再扩展“回答什么”。
- Evidence First：未经验证的地址、仓库、价格、时效、资质、媒体、合作方、评价不得写入。
- Applicable Schema Only：Schema 类型必须与页面真实语义匹配。
- No SEO-to-AI Inference：Google 排名提升不能自动推导为 ChatGPT / Gemini / DeepSeek / 豆包已引用或推荐。
- No 24h Guarantee：不承诺 24/48 小时排名、收录、引用或推荐结果。
- Freeze Real Wins：已经真实 PASS 的页面结构、引用样本或运行链路默认冻结，除非发现明确缺陷。

### 自动修复输出
`page | issue | severity | evidence | fix | changed_files | validation | status`

状态仅使用：
- `PASS_REAL`
- `PASS_REAL_PARTIAL`
- `NEEDS_IMPROVEMENT`
- `BLOCKED_EXTERNAL`
- `NOT_YET_VERIFIED`

### 双轨验收
Track A — Search:
- 页面是否可抓取
- 是否被索引
- 核心查询是否出现
- 排名/摘要/富结果是否发生真实变化

Track B — AI:
- 是否识别品牌
- 是否正确描述
- 是否引用本站或外部证据
- 是否在非品牌需求中列为候选
- 引用 URL / 来源域名 / 竞品

### Gap Audit
Required / Needs Improvement:
- 自动 Crawl + Schema + Entity + Internal Link + Answer Extraction 审计
- Prompt-to-Page Mapping
- Before / After 验收
- 外部 Evidence 与站内 GEO 分层
- 真实状态机，禁止假 PASS

Optional / Recommended:
- Lighthouse / CWV 接入
- 搜索控制台数据接入
- 自动截图与证据归档
- 多站点批量模式

Not Needed by Default:
- 为每个 Prompt 建独立页面
- 为所有页面强塞 Product Schema
- 机械添加 FAQ/QAPage Schema
- 大量低质量目录提交
- 以 llms.txt 作为收录或排名开关
