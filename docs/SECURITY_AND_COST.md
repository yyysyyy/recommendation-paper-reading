# 安全与费用

## 密钥和可见性

- `OPENAI_API_KEY` 只放 GitHub Actions Secret。前端不调用 LLM，不包含 API 密钥，访问者不能触发付费调用。
- `GITHUB_TOKEN` 使用 GitHub 自动签发的工作流凭据。默认只读；准备 job 仅增加 contents:write，部署 job 仅 pages:write 与 id-token:write。PR 检查没有任何密钥，避免使用 `pull_request_target` 执行外来代码。
- Python 网络请求只接受 HTTPS 模型地址，拒绝含密码、查询参数的 base URL，禁止自动跳转携带 Authorization。更换 LLM_BASE_URL 会将密钥和论文输入发给该域名，只能配置你信任的提供商。
- 论文只作为不可信数据交给模型，无工具权限；模型不能执行代码、改配置、查密钥或生成外部链接。页面使用 textContent 构造论文内容、固定生成 arXiv 链接，避免将模型 HTML 注入页面。CSP 限制到本站资源，无第三方分析脚本。
- `store:false` 禁止按默认方式保存 Responses 以供后续查询，但不等于对所有服务商保证零保留；以实际提供商条款为准。
- 公开 Pages 不是朋友访问控制系统。知道地址的人均可查看；公开仓库更会暴露源配置、论文笔记和历史提交。不要发布内部模型指标、个人身份信息或公司资料。网站书签只保存在当前浏览器，不跨设备同步。
- GitHub 官方 Actions 已按 2026-10-26 实际解析的上游标签固定为完整提交 SHA，并配置 Dependabot 月度检查。不要无审核自动合并依赖更新。
- 账本和评估缓存没有秘密信息；站点产物只复制 site 资源、公开 data.json 和下载历史，不复制工作流、测试、环境文件或原始聊天。

## 成本控制

默认每次最多 **24 个逻辑评估请求**，每个请求最多输出 **1800 tokens**。每篇最多发送 12000 个摘要字符，加上标题、作者、固定 profile 和 schema；字符上限不是严格 token 上限。429 / 5xx 重试最多 3 次，因此最坏可能出现 72 次 HTTP POST。程序不读取余额，也没有美元级硬断路器。

已出刊日期再次运行直接跳过；已评估且输入与配置不变的候选复用缓存。失败中止的评估结果不会持久化，因此重跑失败批次可能再次付费。周末可能没有新稿，历史去重也能减少调用。

估算公式（不含缓存优惠、税与重试）：

`月成本 ≈ 30 × 每日实际新评估篇数 × (每篇输入 tokens × 输入单价 + 每篇输出 tokens × 输出单价) / 1,000,000`

**仅作预算示例，不是报价：** 假设输入每百万 tokens $0.40、输出 $1.60，每篇输入 2500、输出 900 tokens，24 篇/日约 **$0.059/日、$1.76/30日**；如果所有输出用满 1800 tokens、输入仍为 2500，则约 $2.79/月。真实价格、输入长度、失败重试、供应商账单会改变结果，首次启用请在提供商后台设置预算提醒/可用额度，并先把 `max_candidates` 与 `max_calls_per_run` 都设为 4 观察账单。

定价应以 [实际模型官方价格页](https://developers.openai.com/api/docs/models/gpt-4.1-mini) 和提供商控制台为准，不能把 ChatGPT 订阅当作 API 余额。`data/days.json` 按日记录成功响应的 input/output token 数，方便核算；网络失败或被拒绝的请求可能已计费但无法取得 usage。

GitHub Pages 与 Actions 是否免费、私有仓库是否可用、分钟数和存储额度取决于账户方案与政策；参照 [Pages 支持范围](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。本项目没有启用付费套餐、域名购买或其他订阅。

## 维护建议

- 查看 Actions 失败记录和账单；未收到 GitHub 邮件不能说明任务成功。
- 每月核对 Secrets、模型可用性、依赖更新和历史恢复说明。
- 更换 profile 或模型会使候选缓存失效，增加新的评估费用。
- 需要零新增调用时手动运行 `collect=false`；需要暂停每日采集时停用该 workflow。
