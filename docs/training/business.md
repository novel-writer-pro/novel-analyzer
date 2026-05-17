# 培训路径 — 业务 / 产品 / 销售

> **目标读者**：要给客户讲能力、谈商业化、做 Demo 的产品 / 销售 / BD。
> **预计时长**：1 小时读懂全貌，半天能给客户做 60 分钟讲解。

---

## 30 秒电梯演讲

> **novel-analyzer 是一个面向长篇小说的 AI 内容理解 + 风险门控 + 受控生成平台**。
> 它不是 ChatGPT 帮人写小说那种通用工具，而是把小说**拆成结构化知识 + 风险检查 + 受控仿写**的端到端系统。
> 服务作家 / 编辑 / 读者 / 平台四类用户。
> 当前**跨题材改写已经验证 99.4% 通过率**，可以做 B2B API 商用上线。

---

## 1 句话 × 4 个能力线

| 能力线 | 一句话讲清 | 状态 |
|--------|-----------|------|
| **拆书** | 把 100+ 章长篇切成 facts + 图谱 + 检索向量，作为下游所有能力的真源 | ✅ 5 本书 R@5 = 0.81/0.84 锁基线 |
| **风险检查** | 9 个 checker 跨章扫人物 / 规则 / 时间线 / 战力一致性，输出问题簇 + 证据链 | ✅ 9 checker mainline |
| **仿写** | 章级 + 整本 + 跨题材三档，全程 harness 控制，可回退、可对比 | ✅ 跨题材 170/171 章 pass |
| **商业化** | v2/v3 框架就绪（owner_user_id + Helicone + n8n），4 周可商用 B2B API | ⚠️ 6 项 SLA gap 待补 |

---

## 必读 4 篇文档（业务视角）

### 1. 系统全貌（5 分钟）
- [OVERVIEW.md](../OVERVIEW.md)

### 2. 商用就绪决策表（15 分钟，最重要）
- [cross-genre-imitation-commercial-readiness-20260515.md](../cross-genre-imitation-commercial-readiness-20260515.md)
- 含：技术指标证据 + 6 项 gap + 3 条上线路径 + 推荐计费方案

### 3. 商业化路线图（10 分钟）
- [strategy/writer-studio-roadmap.md](../strategy/writer-studio-roadmap.md)
- 含：v1 / v2 / v3 / v4 演进 + 不做的事项

### 4. 全能力矩阵（10 分钟）
- [chapter-imitation-capability-matrix.md](../chapter-imitation-capability-matrix.md)
- 含：所有仿写需要的能力、当前覆盖度、下一批最值钱的能力

---

## 商业化抓手（4 类）

### 1. 拆书与知识库服务
- 给作家 / 工作室卖：自动整理人物 / 伏笔 / 规则线
- 给平台卖：知识库 API，上游对接现有阅读 App
- 实证：5 本书 587 docs，R@5 = 0.81

### 2. 风险审查 / 读者踩雷预警服务
- 给编辑 / 审校卖：减少人工只靠记忆读稿成本
- 给平台卖：审稿自动化中台
- 实证：9 checker mainline，最近 targeted regression 40 passed

### 3. 仿写与续写辅助服务
- 给作家卖：harness + Loom 信号侧栏 + AI 副驾
- 给 IP 开发团队卖：跨题材改写 mapping_pack（已商用就绪）
- 实证：跨题材 170/171 章 pass，1M+ 字，3 题材

### 4. 平台级编辑中台 / 运营中台
- 给小说平台卖：审核 + 推荐 + 防剧透 Q&A 全套
- 给 AI 内容产品集成商卖：B2B API
- 实证：v2/v3 已具备多用户隔离 + LLM trace 全覆盖

---

## 经典 Demo 脚本（60 分钟）

### 0-5 分钟：开场 + 痛点
> "传统 LLM 写小说有 3 个老问题：100+ 章后人物失格、规则乱、爽点稀释。我们做的不是改 prompt，而是把整套**拆书 → 风控 → 受控生成**做成系统。"

### 5-15 分钟：拆书 Demo
- 上传一本书（CLI 或 Workbench `/control`）
- 看 facts / graph / window 自动生成
- 在 `/qa` 问 "第 12 章那个伏笔回收了吗？" → 引用跳转

### 15-30 分钟：风险检查 Demo
- 跑 `risk-audit <branch_id>`
- 展示 ChapterRiskCard + supporting evidence
- 展示 review_candidate_clusters（跨章节问题簇）
- 强调 advisory-only 不阻断主提交

### 30-50 分钟：跨题材改写 Demo（核心卖点）
```bash
.venv/bin/python -m novel_analyzer.cli.app writer-imitate-range \
  <branch_id> "2:目标A" "3:目标B" \
  --output-dir output/scifi --use-llm --max-rounds 2 \
  --world-map "郑国=星际联邦" --character-map "卫图=魏拓"
```
- 实时展示生成
- 对比原文 → 改写产物，强调 mapping accuracy 96-98%
- 引用决策表："已经在 3 题材 170/171 章上跑通"

### 50-60 分钟：商业化路线
- 展示 [cross-genre-imitation-commercial-readiness-20260515.md](../cross-genre-imitation-commercial-readiness-20260515.md)
- 讲清：B2B API 4 周可商用，多租户 SaaS 还要 8 周
- 讲清：定价方案（per-chapter，$0.50 / 章，5x 毛利）

---

## FAQ（客户最常问的）

### Q1：能不能完全自动写一本书？
**A**：不能。我们的定位是**辅助工具**，不是替代品。LLM 直写做不到长篇连续性，我们的 harness + risk audit + Loom 信号能让作家**控制**仿写，不是放手让 AI 写。

### Q2：风险审查能保证 100% 不漏？
**A**：不能。当前 9 checker 是 advisory-only，给可疑提示 + 证据链，最终判断还要人工。但是**比人工只靠记忆读稿强**，问题簇能直接给到优先级清单。

### Q3：跨题材改写 99.4% 通过率是怎么算的？
**A**：在 3 套源 / 目标题材 171 章上跑，verdict=pass 的章节数 / 总章节数。失败的 1 章是诛仙某章节 mapping 边界冲突，详见决策表。

### Q4：多租户隔离做到什么程度？
**A**：v3 已经实现 service 层 owner_user_id WHERE，"alice 看不到 bob 的书" 已经端到端验证。**但是没有 RLS、没有 tenant_id、没有 token 映射**，做内部 dogfood 够，做对外 SaaS 还要补 6 项 gap。

### Q5：跟 Coze / LangFlow / OpenManus 这些比怎样？
**A**：我们**自托管 + self-host 友好**，不会数据上云；用 Dify + LangGraph 组合，比 Coze 数据安全、比 LangFlow 维护成本低、比 OpenManus 控制粒度高。详见 [research/fastgpt-vs-dify.md](../research/fastgpt-vs-dify.md)。

### Q6：定价怎么算？
**A**：推荐 per-chapter 计费，单本（≤120 章）= $60，包年 10 本 = $400 (8 折)。LLM 成本 ~$0.10/章，定价 $0.50/章 留 5x 毛利。失败章节不计费。

### Q7：商用上线还要做什么？
**A**：6 项 SLA gap：定价模型、多租户隔离、限流、LLM provider fallback、版权合规、监控仪表盘。最低可上线方案补齐 Gap 1-4，约 4 周。

---

## 不要说的话（合规边界）

- ❌ 不说 "AI 自动写书" / "AI 写小说" — 我们是辅助
- ❌ 不说 "替代编辑" — 我们是审稿辅助
- ❌ 不说 "保证 100% 通过" — 我们是 advisory-only
- ❌ 不说 "已经是成熟商用 SaaS" — 当前是 B2B API ready，SaaS 还有 6 项 gap
- ❌ 不说 "完全无 LLM 成本" — 我们透传成本，定价含 5x 毛利
- ❌ 不在 Demo 中宣称 "判断小说好不好看" — 系统不做审美判断

---

## 进阶阅读（按客户类型）

### 如果客户是**作家 / 工作室**
- [training/user.md](./user.md) — 使用者培训
- [loom/phase6/runbook-template.md](../loom/phase6/runbook-template.md) — 项目壳 SOP
- [writer-imitation-workflow.md](../writer-imitation-workflow.md) — 仿写工作流

### 如果客户是**编辑 / 平台**
- [capabilities/02-risk-audit.md](../capabilities/02-risk-audit.md)
- [risk-audit-system-overview.md](../risk-audit-system-overview.md)
- [tracks/review-workflow/README.md](../tracks/review-workflow/README.md)

### 如果客户是**AI 内容集成商 / API 用户**
- [api-current-surface.md](../api-current-surface.md)
- [cross-genre-imitation-commercial-readiness-20260515.md](../cross-genre-imitation-commercial-readiness-20260515.md)
- [strategy/writer-studio-roadmap.md](../strategy/writer-studio-roadmap.md)

### 如果客户是**投资 / 决策方**
- [whitepaper/ai-novel-system-whitepaper-v2.md](../whitepaper/ai-novel-system-whitepaper-v2.md)
- [product/ai-novel-commercialization-and-moat-20260508.md](../product/ai-novel-commercialization-and-moat-20260508.md)
- [research/competing-novel-ai-projects-20260515.md](../research/competing-novel-ai-projects-20260515.md)

---

返回 [training/](./README.md) ｜ [文档中心](../README.md)
