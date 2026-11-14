# 百度搜索资源平台接入准备与证据边界（2026-11-14）

## 当前已真实确认

- 实际公开主站：https://thai-chinalogistics.github.io/Thai-ChinaLogistics/ （2026-11-14，从已连接电脑 HTTP 200）。
- 域名根目录：https://thai-chinalogistics.github.io/ （同次 HTTP 404）。
- 项目内 robots.txt 可以 HTTP 200 获取，但域名根级 robots.txt 当前 HTTP 404。
- 百度站点所有权：**尚未获得百度账户内“验证通过”的证据**；没有站长平台签发的专用验证码，不得以占位代码或其他站点的验证码冒充。

## 官方验证方式与本网站的现实差异

百度官方说明：文件验证要求网站根目录放置文件；HTML 标签验证要求站点首页 head 内插入由平台提供的专用 meta 验证代码。站点验证是进一步使用站点数据与资源提交工具的前置条件。

目前网站运行于 GitHub Pages **项目路径** /Thai-ChinaLogistics/，而域名根目录 404。因此不能把项目仓库下的文件误认为域名根目录验证文件。建议**优先尝试 HTML 标签验证**，但百度是否接受当前项目路径作为注册站点，以及其验证程序实际请求什么主页，必须通过登录后的真实界面确认。不要根据此文擅自宣称根目录文件验证或 HTML 标签验证已成功。

百度官方：
- 网站验证 https://ziyuan.baidu.com/college/articleinfo?id=267&page=1
- 站点验证图文详解 https://ziyuan.baidu.com/college/articleinfo?id=1003
- AI流量分析公告 https://ziyuan.baidu.com/college/articleinfo?id=3519

百度在 2026-09-15 发布的 AI 流量分析公告称，数据能力分阶段开放，**当时尚未正式启用完整数据服务**；因此即使验证成功，也不能保证立即获得 AI 引用/曝光/点击完整记录。

## 一次性账号侧必要动作

1. 使用您有权管理的百度账号访问 https://ziyuan.baidu.com/site/index ，进入“站点管理”，尝试注册上述**完整网站地址**；把平台是否接受子路径的实际结果保留为截图或审计记录。
2. 如果允许进入验证方式，选择 **HTML 标签验证**，只从百度实际页面复制完整的 meta 标签或其中 content 值。验证码应与站点一一对应；请勿用此文中的任何示例生成假的验证码。
3. 验证码到手后，让 Codex 在本网站主仓库创建**单一安全 PR**，使用现成脚本（推荐从本地 PowerShell 调用）：
   `python scripts/baidu_verification.py --root . --code "<百度实际发放的content>" --apply`
   脚本会拒绝注入、畸形、重复或覆盖另一个所有者的标签；只在项目首页 head 中插入对应 meta，不改业务页面、Canonical、Sitemap。
4. 必须等待该 PR 的网页 CI 通过、获准合并并完成 GitHub Pages 发布。再执行
   `python scripts/baidu_verification.py --code "<同一验证码>" --check-live`
   检查线上首页是否真的出现签发的 meta，且报告不在日志中打印验证码。
5. 回到**百度实际登录的站点管理**点击“完成验证”，保留账号侧“验证成功”的截图或官方响应。仅当这条真实平台证据存在，才可改内部状态为 VERIFIED。
6. 若百度不接受此项目路径，或 HTML 标签验证仍只读取 404 的域名根目录，应停止重试与提交：评估在有实际 DNS 控制权、可提供站点根目录的独立域名/托管下实施迁移方案。**禁止**自动购域名、改 DNS、迁移现有生产站或制造绕过所有权验证的文件。

## 接通后才开始的数据闭环

- 验证通过后查看百度资源提交（Sitemap/普通收录）、抓取诊断、索引量、流量与关键词；只把百度官方实测值写入状态记录。不能把 Google GSC 索引视为百度索引。
- 如 AI 流量分析在本账户内实际可用，再记录百度官方引用、曝光、点击；若功能不可用，保留 NOT_AVAILABLE，不编造 0。
- 豆包、元宝、千问、Kimi、DeepSeek 等消费者端仍需要各自**真实联网搜索回答及可核实引用来源**。搜索 API 返回网页不能充当消费者端推荐证明；当前 GEO 的 135 组平台注册提问仍是 NOT_TESTED。

## 命令当前的安全结果

- `python scripts/baidu_verification.py --root .`：检查本地标签状态；未配置时应返回 `ACCOUNT_TOKEN_REQUIRED`，脚本 exit 0（不阻塞其他网站更新）。
- `python scripts/baidu_verification.py --check-live`：实时检查网站首页及根目录的 HTTP 和可见验证标签，**不调用百度平台验证接口**。
- `--apply` 必须有真实百度验证码；当前不会执行。
