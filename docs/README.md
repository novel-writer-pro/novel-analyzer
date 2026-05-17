# novel-analyzer 文档中心

> **顶级导航**。按角色快速分流，按能力深入，按培训场景上手。
>
> 三秒答疑：[OVERVIEW](./OVERVIEW.md) ｜ [ROADMAP](./ROADMAP.md) ｜ [GLOSSARY](./GLOSSARY.md) ｜ [CHANGELOG](../CHANGELOG.md)

---

## 系统全景

```
┌─────────────────────────────────────────────────────────────────┐
│                        novel-analyzer                            │
├─────────────┬──────────────┬──────────────┬────────────────────┤
│   导入层    │    分析层     │    质量层     │      产品层        │
│  ingest     │  analysis    │  risk audit  │  QA / Studio /     │
│  splitter   │  stages(3)   │  9 checkers  │  export / API      │
├─────────────┼──────────────┼──────────────┼────────────────────┤
│             │              │              │                    │
│  章节切分   │ intake+facts │ claim ground │  问答 + 引用       │
│  规范化     │ evidence+    │ auto-repair  │  仿写编排           │
│             │  analysis    │ confidence   │  风险卡 / cluster  │
│             │ guard        │  gated       │  bundle 导出       │
├─────────────┴──────────────┴──────────────┴────────────────────┤
│           Loom 上层（feature flag 渐进启用）                     │
│  memory · tension · style · character · reward · project shell │
├──────────────────────────────────────────────────────────────────┤
│                     基础设施层                                    │
│  PostgreSQL（pg_trgm + pgvector + pg_jieba）│ BM25 / Vector     │
│  GraphNode / GraphEdge │ Helicone │ Langfuse │ Dify │ n8n      │
└──────────────────────────────────────────────────────────────────┘
```

详细全貌：[OVERVIEW.md](./OVERVIEW.md)

---

## 三轴导航：按角色 × 按能力 × 按深度

### 轴 1：按角色 — "我是谁，去哪？"

| 我是… | 入口 |
|-------|------|
| 🆕 **第一次接触系统** | [OVERVIEW.md](./OVERVIEW.md)（5 分钟读完） |
| 👨‍💻 **开发 / 工程师** | [training/developer.md](./training/developer.md)（Day 1-3 上手路径） |
| ✍️ **使用者 / 作家 / 创作** | [training/user.md](./training/user.md)（半天上手） |
| 🛠️ **运维 / 实施** | [training/operator.md](./training/operator.md)（部署 + 故障决策树） |
| 💼 **业务 / 产品 / 销售** | [training/business.md](./training/business.md)（60 分钟客户讲解） |
| 📦 **接入者（API / 前端）** | [roles/integrator/README.md](./roles/integrator/README.md) |
| 🔁 **维护者 / 接手人** | [handoffs/README.md](./handoffs/README.md) |

> 角色入口的细分场景：[roles/README.md](./roles/README.md)

---

### 轴 2：按能力线 — "我关心哪条线？"

| 能力线 | 一句话定位 | 状态 | 入口 |
|--------|-----------|------|------|
| **拆书引擎** | 长篇 → facts + 图谱 + 检索向量 | ✅ Phase 4.5 完成；R@5 = 0.81/0.84 | [01-deconstruction.md](./capabilities/01-deconstruction.md) |
| **风险检查** | 9 checker 跨章扫一致性，advisory-only | ✅ 9 checker mainline | [02-risk-audit.md](./capabilities/02-risk-audit.md) |
| **受控仿写** | 章级 + 整本 + 跨题材，harness 全程控制 | ✅ 跨题材 99.4%；🔧 同题材验证中 | [03-imitation.md](./capabilities/03-imitation.md) |
| **商业化运营** | B2B API → 多租户 SaaS | ⚠️ 4 周可商用 B2B；6 项 SLA gap | [04-commercialization.md](./capabilities/04-commercialization.md) |

> 能力线 landing 总览：[capabilities/README.md](./capabilities/README.md)
> 能力线 track 视图（开发者向）：[tracks/README.md](./tracks/README.md)

---

### 轴 3：按深度 — "我想看多深？"

```
Level 0: 顶级入口（本文件 + OVERVIEW + ROADMAP + GLOSSARY）
   │
   ├── Level 1: 培训路径 + 能力线 landing（30-60 分钟级）
   │   training/ × 4   capabilities/ × 4
   │
   ├── Level 2: 操作手册（半天上手级）
   │   cli-operations-manual / api-current-surface / interface-manifest
   │   runbook/ 全套 / ops-debug-manual / handoffs/
   │
   ├── Level 3: 能力线深入（专题级）
   │   deconstruction-acceleration/   foundation-optimization/
   │   loom/   risk-audit-*   review-workflow-*   cross-genre-*
   │
   ├── Level 4: 架构与策略（架构师 / 产品级）
   │   architecture/   strategy/   product/   research/   whitepaper/
   │
   └── Level 5: 历史归档（deprecated/）
       已完成的一次性报告、旧版设计文档、冻结声明
```

---

## 核心文档清单（必读）

按"接手优先级"排序：

| 文档 | 说明 | 适合谁 |
|------|------|--------|
| **[OVERVIEW.md](./OVERVIEW.md)** | **系统一页读懂** | **所有人** |
| **[ROADMAP.md](./ROADMAP.md)** | **4 条能力线统一路线图** | **所有人** |
| **[GLOSSARY.md](./GLOSSARY.md)** | **全局术语表** | **所有人**（按需查阅） |
| **[runbook/deployment-and-operations-manual-20260515.md](./runbook/deployment-and-operations-manual-20260515.md)** | **从零部署 + 日常运维总章（1038 行）** | **接手人 / 运维优先读** |
| **[ops-debug-manual-20260514.md](./ops-debug-manual-20260514.md)** | **scenario-first 故障速查（5 棵决策树）** | **运维 / 调试** |
| **[runbook/postgres-ops-cheatsheet.md](./runbook/postgres-ops-cheatsheet.md)** | **PostgreSQL 运维速查** | **运维 / 数据 / 排障** |
| **[cross-genre-imitation-commercial-readiness-20260515.md](./cross-genre-imitation-commercial-readiness-20260515.md)** | **跨题材改写 99.4% pass + 6 项 SLA gap + 3 条上线路径** | **业务 / PM** |
| **[handoffs/session-handoff-20260517-phase6.md](./handoffs/session-handoff-20260517-phase6.md)** | **最新会话交接（Loom Phase 6 完成）** | **接手人** |
| [cli-operations-manual.md](./cli-operations-manual.md) | CLI 命令真相源 | 使用者 |
| [api-current-surface.md](./api-current-surface.md) | 当前 API 端点清单 | 接入者 |
| [interface-manifest.md](./interface-manifest.md) | 稳定接口结构 | 后端 |
| [chapter-imitation-capability-matrix.md](./chapter-imitation-capability-matrix.md) | 仿写全能力矩阵 + 当前覆盖度 | 产品 / 架构 |
| [novel-ingest-input-spec.md](./novel-ingest-input-spec.md) | 小说输入规范（novel.txt 格式） | 使用者 |

---

## 4 条能力线深入文档

### 拆书引擎
| 文档 | 说明 |
|------|------|
| [capabilities/01-deconstruction.md](./capabilities/01-deconstruction.md) | landing |
| [deconstruction-acceleration/README.md](./deconstruction-acceleration/README.md) | 专题入口 |
| [deconstruction-acceleration/architecture.md](./deconstruction-acceleration/architecture.md) | Quick / Deep 双档架构 |
| [deconstruction-acceleration/roadmap-sota-optimization.md](./deconstruction-acceleration/roadmap-sota-optimization.md) | SOTA 路线图 + benchmark |
| [deconstruction-acceleration/handoff-sota-optimization.md](./deconstruction-acceleration/handoff-sota-optimization.md) | 交付文档 |
| [deconstruction-acceleration/user-manual.md](./deconstruction-acceleration/user-manual.md) | 用户使用说明 |
| [deconstruction-acceleration/performance-profiling-20260517.md](./deconstruction-acceleration/performance-profiling-20260517.md) | 雪中悍刀行 229 章性能剖析 |
| [foundation-optimization/README.md](./foundation-optimization/README.md) | 底座优化六层 |

### 风险检查
| 文档 | 说明 |
|------|------|
| [capabilities/02-risk-audit.md](./capabilities/02-risk-audit.md) | landing |
| [risk-audit-system-overview.md](./risk-audit-system-overview.md) | 系统总览 |
| [risk-audit-capability.md](./risk-audit-capability.md) | 能力说明 |
| [risk-audit-runtime-architecture.md](./risk-audit-runtime-architecture.md) | 运行时架构 |
| [risk-audit-checker-roadmap.md](./risk-audit-checker-roadmap.md) | Checker 路线图 |
| [risk-audit-production-readiness.md](./risk-audit-production-readiness.md) | 生产就绪评估 |
| [review-workflow-api.md](./review-workflow-api.md) | Review API |
| [review-batch-execution-contract.md](./review-batch-execution-contract.md) | 批量执行契约 |

### 受控仿写
| 文档 | 说明 |
|------|------|
| [capabilities/03-imitation.md](./capabilities/03-imitation.md) | landing |
| [writer-imitation-workflow.md](./writer-imitation-workflow.md) | 完整工作流 |
| [chapter-imitation-capability-matrix.md](./chapter-imitation-capability-matrix.md) | 全能力矩阵 |
| [imitation-control-plane-glossary.md](./imitation-control-plane-glossary.md) | 控制层术语表 |
| [loom/README.md](./loom/README.md) | Loom 总入口（5 份 canonical） |
| [loom/overview.md](./loom/overview.md) | 完整架构图 + SOTA 对比 |
| [loom/handoff.md](./loom/handoff.md) | Loom 当前状态 |
| [loom/roadmap.md](./loom/roadmap.md) | Phase 1-6 路线图 |
| [loom/phase6/README.md](./loom/phase6/README.md) | Author Project Shell |

### 商业化
| 文档 | 说明 |
|------|------|
| [capabilities/04-commercialization.md](./capabilities/04-commercialization.md) | landing |
| [strategy/writer-studio-roadmap.md](./strategy/writer-studio-roadmap.md) | 商业化整体路线图 |
| [cross-genre-imitation-commercial-readiness-20260515.md](./cross-genre-imitation-commercial-readiness-20260515.md) | B2B 商用决策表（必读） |
| [strategy/external-integration-roadmap-20260514.md](./strategy/external-integration-roadmap-20260514.md) | 外部集成路线图 |
| [runbook/business-loop.md](./runbook/business-loop.md) | v3 端到端 6 步 smoke |
| [runbook/v3-pickup-checklist.md](./runbook/v3-pickup-checklist.md) | v3 pickup 步骤 |

---

## 接入与运维（横向）

### API 与接口
| 文档 | 说明 |
|------|------|
| [api-current-surface.md](./api-current-surface.md) | 当前 API 端点 |
| [api-contract.md](./api-contract.md) | API 合同（稳定字段） |
| [interface-manifest.md](./interface-manifest.md) | 稳定接口结构 |

### Runbook（按场景）
| 文档 | 场景 |
|------|------|
| [runbook/deployment-and-operations-manual-20260515.md](./runbook/deployment-and-operations-manual-20260515.md) | 从零部署 + 日常运维 |
| [runbook/business-loop.md](./runbook/business-loop.md) | v3 端到端 smoke |
| [runbook/v3-pickup-checklist.md](./runbook/v3-pickup-checklist.md) | v3 pickup 步骤 |
| [runbook/helicone-enable.md](./runbook/helicone-enable.md) | Helicone proxy 启用 |
| [runbook/loom-ab-experiment.md](./runbook/loom-ab-experiment.md) | Loom A/B 实验 |
| [runbook/migration-guide.md](./runbook/migration-guide.md) | 迁移指南 |
| [runbook/bm25-jieba-reindex.md](./runbook/bm25-jieba-reindex.md) | BM25 + jieba 重建 |
| [runbook/postgres-ops-cheatsheet.md](./runbook/postgres-ops-cheatsheet.md) | PostgreSQL 速查 |
| [ops-debug-manual-20260514.md](./ops-debug-manual-20260514.md) | 故障速查（5 棵决策树） |

### 可观测性
| 文档 | 说明 |
|------|------|
| [observability/helicone-vs-langfuse.md](./observability/helicone-vs-langfuse.md) | observability 工具对比与决策 |

---

## 架构与战略（深度向）

### 架构
| 文档 | 说明 |
|------|------|
| [architecture/README.md](./architecture/README.md) | 架构专题入口 |
| [architecture/ai-novel-system-blueprint.md](./architecture/ai-novel-system-blueprint.md) | 系统蓝图 |
| [architecture/novel-assistant-system-architecture.md](./architecture/novel-assistant-system-architecture.md) | 系统架构详解 |
| [architecture/novel-assistant-business-architecture.md](./architecture/novel-assistant-business-architecture.md) | 业务架构 |
| [architecture/independent-agent-knowledge-and-retrieval.md](./architecture/independent-agent-knowledge-and-retrieval.md) | Agent 知识与检索 |
| [architecture/chapter-imitation-harness-architecture.md](./architecture/chapter-imitation-harness-architecture.md) | 章节仿写 Harness |
| [architecture/external-integration-architecture-20260514.md](./architecture/external-integration-architecture-20260514.md) | 外部集成架构 |

### 战略
| 文档 | 说明 |
|------|------|
| [strategy/writer-studio-roadmap.md](./strategy/writer-studio-roadmap.md) | 商业化路线图 |
| [strategy/ai-novel-system-benchmark.md](./strategy/ai-novel-system-benchmark.md) | 行业基准对比 |
| [strategy/kernel-sota-gap-assessment-20260514.md](./strategy/kernel-sota-gap-assessment-20260514.md) | 与 SOTA 差距评估 |
| [strategy/external-integration-roadmap-20260514.md](./strategy/external-integration-roadmap-20260514.md) | 外部集成路线图 |
| [strategy/external-integration-checklist-20260514.md](./strategy/external-integration-checklist-20260514.md) | 外部集成 checklist |

### 产品
| 文档 | 说明 |
|------|------|
| [product/ai-novel-product-strategy.md](./product/ai-novel-product-strategy.md) | 产品战略 |
| [product/ai-novel-capability-map.md](./product/ai-novel-capability-map.md) | 能力地图 |
| [product/ai-novel-capability-scorecard.md](./product/ai-novel-capability-scorecard.md) | 能力评分卡 |
| [product/ai-novel-commercialization-and-moat-20260508.md](./product/ai-novel-commercialization-and-moat-20260508.md) | 商业化与护城河 |

### 研究 & 白皮书
| 文档 | 说明 |
|------|------|
| [research/competing-novel-ai-projects-20260515.md](./research/competing-novel-ai-projects-20260515.md) | 竞品研究 |
| [research/fastgpt-vs-dify.md](./research/fastgpt-vs-dify.md) | 框架选型 |
| [research/heuristic-scorer-validation-findings-20260515.md](./research/heuristic-scorer-validation-findings-20260515.md) | heuristic scorer 验证 |
| [whitepaper/ai-novel-system-whitepaper-v2.md](./whitepaper/ai-novel-system-whitepaper-v2.md) | 白皮书 v2 |
| [whitepaper/ai-novel-system-whitepaper.md](./whitepaper/ai-novel-system-whitepaper.md) | 白皮书 v1 |

---

## 历史归档（Level 5）

`docs/deprecated/` 目录保留以下历史文档，**不再活跃**但保留完整内容供查阅：

- 一次性评估报告（manual-eval / stage-evaluation / real-run-evaluation）
- 已冻结的 API 版本声明（freeze-evidence / api-versioning）
- 旧版设计文档（phase2-design / persistence-strategy）
- 模板文件（review-template / rewrite-brief-template）
- 已完成的 checklist（phase-completion / doc-consistency）
- 早期 session handoff（[deprecated/session-handoffs/](./deprecated/session-handoffs/)）
- 早期 whole-book imitation 报告（[deprecated/whole-book-reports/](./deprecated/whole-book-reports/)）

如需查阅，直接进入 [`docs/deprecated/`](./deprecated/)。

---

## 当前推荐运行配置

```bash
NOVEL_ANALYZER_LLM_BASE_URL=http://34.97.18.233:65432/v1
NOVEL_ANALYZER_LLM_MODEL_NAME=claude-haiku-4.5
NOVEL_ANALYZER_LLM_STAGE_MODEL_NAME=claude-haiku-4.5
NOVEL_ANALYZER_LLM_REQUESTS_PER_SECOND=1.5
NOVEL_ANALYZER_USE_MERGED_STAGES=true
NOVEL_ANALYZER_LOOM_MEMORY_MODE=ab
NOVEL_ANALYZER_LOOM_PAIRWISE_ENABLED=true
```

完整环境变量见根 [README.md § 环境变量](../README.md#环境变量)。

---

## 接手建议阅读顺序

1. [OVERVIEW.md](./OVERVIEW.md) — 5 分钟读懂系统
2. [handoffs/session-handoff-20260517-phase6.md](./handoffs/session-handoff-20260517-phase6.md) — 最新会话交接
3. [ROADMAP.md](./ROADMAP.md) — 4 条能力线进度
4. [training/developer.md](./training/developer.md) — Day 1-3 开发上手路径（按需）
5. [runbook/deployment-and-operations-manual-20260515.md](./runbook/deployment-and-operations-manual-20260515.md) — 部署
6. 选择能力线深入：[capabilities/](./capabilities/README.md)

---

## 文档贡献规则

- 新文档**必须**归类到一个能力线（capabilities）或一个层（runbook / architecture / strategy / product）
- 新增 handoff 放到 `handoffs/`，遵循 [handoffs/README.md § 模板](./handoffs/README.md#写新交接的模板给下一棒)
- 一次性报告 / 已完成 checklist 完成使命后移到 `deprecated/`
- 所有 markdown 链接用相对路径，验证不断链
- 中文文档用全角标点，避免半角
- 顶级 README 不超过 280 行（本文件），细节下沉到子 README
