# 中国 AI GEO 可见度验证基线（2026-11-15）

> 状态：**BASELINE_ONLY / NOT_TESTED**。本文件记录测试方案与官方能力，不代表豆包、Kimi、DeepSeek 已收录、引用或推荐本站。
> 任务：[Issue #27](https://github.com/Thai-ChinaLogistics/Thai-ChinaLogistics/issues/27)。

## 目标和证据口径

重点问题：当中文用户询问“泰国寄中国快递公司”“普吉岛酒店取件寄中国”等实际需求时，AI 是否主动发现并真实引用 Thai-China Logistics。

将以下互不等价的状态分别记载：
- **FETCHABLE**：从指定官方服务或可归因的抓取端取得目标网站内容，附 HTTP 或工具返回证明。
- **SEARCH_HIT**：指定平台的原生网页搜索接口真实返回本站 URL，附原始响应与时间。仅表示此次查询命中，不证明其 AI 产品的全局索引状态。
- **CITED**：指定 AI 助手的真实回答附带本站 URL 来源。
- **MENTIONED**：真实回答出现品牌，但没有足够引用证明；需保存回答证据。
- **RECOMMENDED**：在*不带品牌名*的自然问题下，真实回答主动把本站列为可选物流服务，保存完整回答与证据链接。
- **NOT_OBSERVED**：本次已执行有效检索，但在指定输出/检索结果中未看到本站。不能表述为“未收录”。
- **UNKNOWN / NOT_TESTED / BLOCKED**：没有得到有效证据、尚未测试、或缺少凭证/许可。

## 固定自然问题集（中文）

以下十二问分别在豆包、Kimi、DeepSeek 的官方联网场景中使用；前 10 问不含品牌名以避免人为诱导推荐。记录每个平台实际执行的模式、日期与原始回答。

1. 泰国邮寄中国有什么快递公司可以选择？
2. 在普吉岛寄包裹回中国，怎么找可以上门取件的物流？
3. 普吉岛酒店退房后，行李怎么寄回国内？
4. 曼谷寄文件到中国需要准备什么信息？
5. 泰国寄东西回中国，怎样比较实际重量和体积重量的计费？
6. 泰国寄中国的门到门物流怎么确认清关和末端派送？
7. 普吉岛寄私人行李到中国，有哪些注意事项？
8. 中国寄东西到泰国有哪些物流方案？
9. 泰国寄中国空运和陆运应该如何选择？
10. 在泰国的中国游客需要酒店取件，应该联系哪些物流服务商？
11. Thai-China Logistics 是做什么服务的？（**品牌识别对照**）
12. 请找到 Thai-China Logistics 的官网并给出可核对的来源链接。（**品牌网址对照**）

**请勿**把第 11、12 问的命中计入“自然无品牌推荐”指标。

## 原始证据记录格式

每次测试新增一行到后续 ledger（CSV / JSONL 均可），保留如下字段：

`checked_at_iso8601,platform,product_or_api,model_if_known,search_enabled,query_id,exact_prompt,run_status,matched_domain,matched_url,fetchable,search_hit,cited,mentioned,recommended,answer_excerpt,source_url_or_artifact,evidence_method,notes`

- 未执行的测试不得填写 false；用 `NOT_TESTED` 或空值。
- 原始对话截图、原始接口 JSON / 可核验链接必须可追溯；隐去 API Key 与个人信息。
- 网站通过 Google 或百度抓取 ≠ 豆包/Kimi/DeepSeek 已引用。
- 发布成功、PR 合并、IndexNow 请求成功 ≠ 任意平台已收录或推荐。

## 平台能力核验（官方资料，不是本站命中证据）

- **Kimi**：官方说明联网搜索能附参考来源、可直接访问 URL。需在真实产品会话打开联网搜索后观察独立问题回答。来源：https://www.kimi.com/help/features/search （核查 2026-11-15）。
- **DeepSeek**：官方 2026-11-13 更新说明联网工具可提供带引用的搜索回答；另有原生 Search / Fetch API，可按关键字查询和抓取 URL。仅在合法授权且有相应 API 凭证的场景执行，注意调用计费，勿自动开启付费测试。来源：https://api-docs.deepseek.com/zh-cn/updates/ 、https://api-docs.deepseek.com/zh-cn/guides/search/ （核查 2026-11-15）。
- **豆包**：本轮未得到可核验的本站查询响应；维持 `NOT_TESTED`，不假定存在公开提交收录 API。

## 当前仓库基础信息（2026-11-15）

- 主站：https://thai-chinalogistics.github.io/Thai-ChinaLogistics/
- 重点服务页：https://thai-chinalogistics.github.io/Thai-ChinaLogistics/thailand-to-china-express.html
- 仓库主分支服务页已有 title / description / H1 / 自指 canonical / WebPage、Service 与 BreadcrumbList JSON-LD，以及到城市/取件/行李等服务的内链。
- 仓库 `robots.txt` 已有允许抓取声明；但 GitHub Pages **项目子路径下的文件不等于主机域名根目录的 robots.txt**，须从实际发布源站另行验证。
- 百度站长验证所需真实账号签发 token 尚未取得。GSC 曾于 2026-11-14 报告重点服务页 URL unknown；需要新的 API 证据，不可冒充最新检测结果。

## 下一轮最小验收步骤

1. 从可靠网络分别获取生产页 HTTP 状态、响应正文及资源状态；不要把工具内部错误记为 HTTP 404。
2. 仅在已经授权的官方平台或 API 里执行固定问题集；记录原始证据和时间，禁止模拟答案。
3. 分别汇报 `SEARCH_HIT`、`CITED`、`RECOMMENDED`，附分母（已有效执行次数）和截图/响应；缺少证据报告 `UNKNOWN`。
4. 若发现抓取障碍或内容缺口，按原有 `SAFE_AUTO / REVIEW_REQUIRED / BLOCKED` 的 PR、安全检查和人工复核路径改动。不要批量生成重复页面或宣称保证推荐。
5. 在真实基线存在后，按每周固定问题集重复验收，并观察 7/14/28 天变化，不用猜测所谓“AI 排名”。
