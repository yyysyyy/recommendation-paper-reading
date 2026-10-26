# 部署状态

核对日期：2026-10-26（北京时间）。

- 公开仓库：[yyysyyy/recommendation-paper-reading](https://github.com/yyysyyy/recommendation-paper-reading)，main。
- 网站已上线：[Recommendation Paper Reading](https://yyysyyy.github.io/recommendation-paper-reading/)。实际 HTTP200，线上 data.json 为17篇、6期，最新2026-10-26；已用浏览器打开核对。
- 首次成功部署：[Actions run 40266519888](https://github.com/yyysyyy/recommendation-paper-reading/actions/runs/40266519888)，prepare 和 deploy 成功。后续版本以仓库最新 Actions 对应 SHA 为准。
- 用户选择 Codex 定时维护，不配置 API。已在本地 Codex 创建并核对 ACTIVE 的“推荐论文日报网站维护”，每天本地北京时间09:17，绑定原任务；下次计划为2026-10-27。电脑在线、应用运行、登录额度和 GitHub 授权需有效。尚未经历第一次未来定时运行，不能将创建成功当作次日一定更新的保证。
- GitHub workflow 已改为提交后检查/部署，没有云端 schedule；可选 API collector 默认关闭，需要手动启用开关与 Secret。没有发起真实付费模型调用。
- 无 API 的候选导出、完整审核批次导入、快照过期/缺项/错误证据拒绝、版本去重及失败安全共22项测试通过；validate、静态 build 与 JS 语法检查通过。
- 真实完整7天 arXiv 抓取成功：扫描2080条、关键词与历史筛选后162篇、导出24篇候选。测试只读未发布，不覆盖已有10月26日日报。之前也验证了两个真实 arXiv Atom ID。
- 浏览器验证：历史17篇、Semantic ID过滤5篇、OneChord搜索1篇、空结果提示、日期切换4篇；手机宽度无横向溢出，未发现浏览器错误。
- Library 原始 JSONL 未取得；从原对话日报恢复17篇（10月21日至26日），最早3篇缺失，不宣称完整20篇去重。支持维护者 import-history 补齐。
- 历史摘要与评分未全面重新核验；未来自动摘要也只依据 arXiv 摘要。个性化 profile 是历史推断，保留编辑入口。
