# Recommendation Paper Reading

推荐系统论文阅读室。GitHub Pages 静态前端 + GitHub Actions 每日采集，Python 标准库实现，无 npm/pip 运行依赖。

**交付状态（2026-10-26）：代码与历史恢复完成；实际部署结果见 `DEPLOYMENT_STATUS.md`。仓库存在不代表网站已上线。**

## 网站包含什么

- 每日精选与日期切换、全部历史、方向过滤、关键词检索、阅读建议过滤。
- 论文与 PDF 链接、主观评分、摘要、推荐理由、最小验证实验、证据局限。
- 深色模式、移动端布局、键盘操作、本浏览器的“稍后读”书签。
- 历史 JSONL 下载和导入格式示例；不在浏览器中接收或存储 API 密钥。
- 页面区分历史恢复、摘要辅助阅读、空刊、加载失败和更新过期。

## 历史恢复与筛选偏好

优先尝试读取 `/Research/recommendation_paper_history.jsonl`。本次没有可调用的 ChatGPT Library 文件读取入口，原对话返回的附件列表也为空；`sandbox:/mnt/data/...` 仅是旧会话中的路径，不能作为当前可下载文件。

原对话声称 Library 有 18 篇，10 月 26 日合并到 20 篇但上传失败。本次从实际返回的完整日报正文恢复 **17 篇（2026-10-21 至 10-26，共 6 期）**。最早 3 篇只有数量描述，没有明细，未编造占位论文。无法保证完整 90 天历史去重。详见 `data/provenance.json`。

原始个人筛选指令没有返回。`config.json` 的 `profile` 来自历史推荐与实验建议的推断，可直接编辑：

1. 首选 GR、SID 冲突与 Prefix 负载均衡、MTP、Decision Token、用户长行为序列、GR + CF / token2tokenCF / U2I。
2. 其次工业 CTR/CVR、召回效率、Proxy/Scaling、蒸馏与训练稳定性。
3. 评分强调个人相关性 35%、技术启发 25%、摘要实验证据 20%、实验落地价值 20%。默认门槛 80 分，每日最多 4 篇，允许零篇。
4. 不把理论 FLOPs 当线上加速，不把文本检索当推荐，不把离线指标当 GMV；缺少证据必须披露。

历史摘要和评分保留原对话内容并标记“未重新核验”。仅抽查了 2610.23453 和 2610.30612 的官方摘要页面，没有重新验证全部实验结论。自动新增摘要严格标明只读了 arXiv 摘要；本项目不冒充全文研究服务。

## 部署：最短操作路径

建议仓库：`yyysyyy/recommendation-paper-reading`，站点名保留空格和大小写。

1. 在 GitHub 建立仓库，默认分支为 `main`。免费方案可选择公开仓库；实际支持范围以 GitHub 账户方案为准。
2. 将本目录所有源文件上传至仓库根目录。必须包含隐藏目录 `.github/`，不要只上传 `dist/`，也不要将外层 `recsys-daily/` 再套一层。
3. **Settings → Pages → Build and deployment → Source → GitHub Actions**。
4. **Settings → Secrets and variables → Actions → Secrets**，新增 `OPENAI_API_KEY`。
5. 可选 **Variables**：`LLM_MODEL`（默认 `gpt-4.1-mini`），`LLM_BASE_URL`（默认 `https://api.openai.com/v1`）。密钥只能放 Secret，不能放 Variable。第三方服务必须兼容 **Responses API + strict JSON schema**；仅支持 Chat Completions 的网关不能直接使用。
6. **Actions → Daily digest and Pages → Run workflow**。首次选 `collect=false`，先部署现有历史；之后选 `collect=true` 测试采集。已存在当天日报时会直接跳过，下一北京时间日期才生成新刊。
7. 等待 prepare、deploy 都成功，打开部署环境中返回的 Pages URL，并核对首页最近一期和历史数量。通常项目站点为 `https://yyysyyy.github.io/recommendation-paper-reading/`；必须以实际成功部署的 URL 为准。

每日计划是北京时间 **09:17**，工作流 cron 使用 UTC `01:17`。GitHub 的计划任务可能延迟或丢弃，不提供准点送达保证；只在默认分支运行，公开仓库长期无活动可能暂停计划任务。发现未更新时查看 Actions，必要时手动运行。参考 [GitHub 计划任务说明](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)。

工作流假定 `main` 是默认分支。若使用其他分支，必须同步修改触发分支、job 条件、checkout ref 和 push 目标。

### 通过终端上传

在这个目录打开终端（仓库尚未初始化时）：

```sh
git init -b main
git add .
git commit -m "Build recommendation paper reading room"
git remote add origin https://github.com/YOUR_ACCOUNT/recommendation-paper-reading.git
git push -u origin main
```

本项目不保存 GitHub token。使用 GitHub 现有登录或凭据管理器。默认 `GITHUB_TOKEN` 已用于工作流内的数据提交和 Pages 部署，不需要为每天运行创建 PAT。

## 本地查看与检查

需要 Python 3.10+（推荐 3.12）以及可用的 IANA 时区数据库。部分 Windows 安装可能额外需要 `tzdata`。Node 只用于可选的 JS 语法检查。

```sh
python3 -m unittest discover -s tests -v
python3 -m pipeline.cli validate
python3 -m pipeline.cli build
node --check site/app.js
python3 -m http.server 8765 --bind 127.0.0.1 --directory dist
```

浏览器打开 `http://127.0.0.1:8765/`，不要双击 HTML；`file://` 无法正常读取 JSON。所有前端资源均使用相对路径，支持 GitHub Pages 项目子路径，无外部字体、CDN 或跟踪脚本。

采集需将密钥以当前进程环境变量提供，再运行：

```sh
python3 -m pipeline.cli update
python3 -m pipeline.cli validate
python3 -m pipeline.cli build
```

程序不会自动加载 `.env`。请不要把真实密钥写进命令历史、源文件或截图。日常运行优先使用 GitHub Secrets。

## 抓取与去重机制

1. 按 UTC 查询 arXiv API 的 `submittedDate`，默认四个分类 cs.IR、cs.LG、cs.AI、cs.CL。覆盖近 7 天，再按原始 `published` 时间分为最近 72 小时和 72 小时至 7 天补漏。
2. 分页抓取，每页 100 条，请求间隔至少 3.1 秒。超过 2000 条时失败，要求提高 `max_fetch` 或缩小分类，不悄悄截断；API 错误页和分页异常也失败。
3. 标题/摘要关键词进行本地预筛。每天最多评估 24 篇，约 1/3 名额预留给补漏；剩余名额在两组之间复用。页面记录扫描、评估和延后数量。**这是预算内筛选，不保证发现每篇相关论文**；过期未评估论文可能漏掉，可调高预算。
4. 每篇调用一次 Responses API，要求中文结构化输出。摘要的连续原文片段必须确实出现在输入摘要中，评分、方向和建议均本地校验；这能发现格式和部分证据错误，不能证明整段摘要没有幻觉。
5. `data/history.jsonl` 是已推荐主账本，按归一化 arXiv ID 去重。`v1/v2`、abs/PDF URL、DOI URL 都归为同一 ID，保留首次推荐日期。已有记录不因新版本再次推荐。
6. 精确归一化标题、人工维护 `data/aliases.json` 以及 `data/exclusions.json` 额外排除同标题或已知跨 ID 重复。当前 OneLatent/WhisperRec 别名与显式排除继承原对话，是保守判断，未独立核验；最早历史缺失时仍会保守排除 OneLatent。跨 ID 改题/扩写没有可靠自动判重保证。
7. `data/evaluations.json` 只缓存成功评估，键包含 ID、更新时间、摘要、配置、模型和服务地址。拒选论文下次可复用；它们不进入已推荐历史。每天未入选的合格候选仍可在 7 天内补漏。
8. `data/days.json` 保存每期 ID、状态、统计、模型 token 用量；同一个北京时间日期已存在就跳过，不重复花费或重复出刊。

本次导入包含一篇原对话中的 10 月 16 日“高价值补漏”，按历史保留；自动采集不会自行扩大到 7 天以外。arXiv 的 `submittedDate` 按首次提交时间过滤，因此不覆盖早年论文的新版本，也不覆盖 arXiv 之外的论文。

## 导入原始 Library 历史

从原会话或 Library 下载实际 JSONL 后，放在本地安全位置，先备份账本，再运行：

```sh
python3 -m pipeline.cli import-history /absolute/path/recommendation_paper_history.jsonl
python3 -m pipeline.cli validate
python3 -m pipeline.cli build
```

每行一个 JSON 对象。必需字段：`id` / `arxiv_id` / `url` / `paper_url` 之一，以及 `recommended_on` / `first_recommended_date` / `recommendation_date` / `date` 之一（YYYY-MM-DD）。其他字段可缺省，`score` 必须是 0–100 整数或 null；方向用 `topics` 字符串数组。参考 `docs/import-example.jsonl`。

导入会归一化版本主键、保留已有详细内容、以较早日期作为首次推荐时间，重建每日 ID 映射。无效行会中止整批，重复执行不会产生新记录。核对后将 `data/history.jsonl` 和 `data/days.json` 一并提交。`data/provenance.json` 是人工审计记录，确认补齐后更新缺失数量与说明，不应只因数字达到 20 就宣称补齐正确。

## 失败安全与恢复

- API key 缺失、arXiv 限流/错误、超出抓取上限、模型拒绝/截断/格式或证据校验失败：返回非零，不写入这次生成的数据，不发布“伪零篇”。任一候选失败会中止整期。
- 真正抓取成功但没有合格论文：保存 `empty` 空刊，保留全部历史。
- HTTP 429 / 5xx 最多重试 3 次；不确定是否已送达的模型网络超时不自动重试，避免额外计费。服务端 5xx 后重试仍可能重复计费。
- 全部抓取与摘要成功后才写数据；每个文件使用临时文件 + 原子替换。**多文件一致性的持久事务边界是 Git commit**，不是文件系统数据库事务。Actions 中检查或进程失败的临时 checkout 会丢弃；本地若恰在多个文件替换之间被终止，运行 validate，必要时从上次 Git 提交恢复三个数据文件再重跑，不要提交不一致状态。
- 提交前先 validate + build。普通非强制 push 若碰到别人更新会失败，不自动覆盖或重写历史；下一次运行基于新主分支重算。保护分支拒绝机器人直推时，需给机器人配置精确 bypass 或改成维护者审核的数据 PR 流程；不能直接启用宽泛绕过。
- 采集、数据提交、Pages 上传和部署在同一条工作流中显式衔接，避免机器人 push 不触发另一个工作流的问题。并发任务按同一组排队，旧的半成品不会覆盖新的任务。
- Pages 部署失败时上一版仍可访问。若数据已经提交但部署失败，重跑同一工作流即可，日幂等会跳过 LLM，再构建部署。
- 失败记录保存在 Actions job 状态和摘要；是否收到 GitHub 邮件取决于你的 Actions 通知设置。本项目没有额外发送邮件、Slack 或聊天通知。
- 如需更正已出刊内容，直接在账本中更正文案并提交；默认不开放同日强制重采集开关。

## 安全与费用

详细说明见 [docs/SECURITY_AND_COST.md](docs/SECURITY_AND_COST.md)。静态站点与其下载的数据会被访问者读取，公开仓库也会公开筛选 profile 和全部提交历史。请仅放可分享的论文笔记，不要放公司内部实验数据或账号资料。

## 文件说明

```text
.github/workflows/daily.yml   每日抓取、校验、提交、发布
.github/workflows/check.yml   PR 检查，无密钥
config.json                  筛选标准、方向、预算与模型配置
data/history.jsonl           已推荐主账本
data/days.json               每期索引与运行统计
data/evaluations.json        已评估候选缓存
data/aliases.json            人工跨 ID 去重别名
data/exclusions.json         人工排除（含原因）
data/provenance.json         恢复来源与完整性边界
pipeline/                    标准库 Python 流程
site/                        静态页面源文件
tests/                       失败安全与核心逻辑测试
dist/                        本地构建产物（不提交）
```

## 官方参考

- [arXiv API：时间过滤、分页与请求间隔](https://info.arxiv.org/help/api/user-manual.html)
- [GitHub Pages 自定义 Actions 工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [GPT-4.1 mini 模型与价格页](https://developers.openai.com/api/docs/models/gpt-4.1-mini)
