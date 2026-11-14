# IndexNow 事件驱动 URL 更新通知（2026-11-14）

## 用途

在泰中物流官网的 HTML 页面实际新增或更新后，通知支持 IndexNow 协议的搜索系统有 URL 发生变化。**提交回执不等于抓取、建立索引、排名提升或 AI 助手推荐**。Google、百度、豆包没有被这条通知证明接入。

## 所有权验证与目录边界

实际官方页面前缀是 `https://thai-chinalogistics.github.io/Thai-ChinaLogistics/`，并非 `https://thai-chinalogistics.github.io/` 的根目录。IndexNow 选择官方文档的 `keyLocation` 方式，把随机 32 位十六进制密钥文件直接放在受控仓库顶层，在正式 GitHub Pages 部署后验证该文件通过 HTTP 200 返回完全一致的字节。该文件只对 `/Thai-ChinaLogistics/` 下的 URL 授权；绝不通知同一共享主机上的其他路径。

## 事件与安全约束

- 重用已有 `SEO content safety check` GitHub Actions 的 `push main` 事件，不新增定时任务；仅检测本次 commit 的 added/modified 根级公开 HTML 文件。
- 有真实新旧 Git diff 时才计算变更 URL；不对每次 CI 重新发送整个站点、不通知 admin/Google 验证文件或跨域路径。
- 仅在所有权密钥文件 **已经公开可验证** 时通知 IndexNow；部署尚未完成则返回 `KEY_NOT_PUBLIC`，不能假报成功。
- 每次不超过 25 个页面；联网仅发送到 `https://api.indexnow.org/indexnow`，HTTP 200 视为收到、202 视为等待验证；失败、限流或超时原样记录但不破坏网站内容安全测试。
- 公开 CI 只输出 URL 数量和状态，不打印密钥，不把第三方收录等同于已验证。
- 可用 `--changed-files` 文本文件进行手工有依据的首批通知；只选提交来源可核验的实际公开页面。
- 网站技术 SEO 校验以及用户业务内容审批保持独立。

官方文档：https://www.indexnow.org/documentation
