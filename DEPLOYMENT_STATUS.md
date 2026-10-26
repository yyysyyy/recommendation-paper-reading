# 部署状态

核对日期：2026-10-26（北京时间）。

- GitHub 仓库已创建：`https://github.com/yyysyyy/recommendation-paper-reading`（public，main）。
- 当前文件记录创建时，源代码上传及 Pages 发布仍在进行；此文件不作为网站已上线的证明。
- 本地恢复 17 篇、6 期；数据验证、静态构建、17 项核心测试与 JS 语法检查通过。
- 真实 arXiv Atom API 联通测试成功，返回 2610.23453 与 2610.30612；未执行完整付费模型链路。
- 浏览器验证：历史 17 篇、Semantic ID 过滤 5 篇、OneChord 搜索 1 篇、空结果提示、日期切换 4 篇；手机宽度无横向溢出，未发现浏览器错误。
- 未取得 Library 原 JSONL，最早 3 篇缺失。已实现维护者导入，不宣称完整 20 篇去重。
- 当前环境没有 `OPENAI_API_KEY`，未进行真实付费 LLM 调用；成功的模拟响应和失败路径已测试。
- 全自动摘要需要维护者在仓库 Settings → Secrets and variables → Actions 新增 `OPENAI_API_KEY`。配置以后，次日北京时间 09:17 计划运行；GitHub 不保证准点。

最新发布结果应核对 GitHub Actions 的 deploy 成功记录与实际 Pages 页面。若仅仓库建好或工作流失败，不代表网站上线。
