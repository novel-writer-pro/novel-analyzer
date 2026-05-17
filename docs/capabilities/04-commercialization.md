# 能力线 4 — 商业化运营（Commercialization）

> **一句话定位**：从单机 dev 工具走向 B2B API 与多租户 SaaS 的演进路线，覆盖部署、可观测、用户隔离、计费、限流、版权合规。

**状态**：⚠️ 跨题材改写 B2B API 技术 ready，infra 4 周可商用；多租户 SaaS 还有 6 项 gap

---

## 能解决什么问题

| 问题 | 商业化路线给的答案 |
|------|------------------|
| 系统能力强但只能本地跑，没法卖 | v2/v3 框架（Dify + n8n + Langfuse + Helicone）+ owner_user_id 透传 |
| 多用户混用怎么隔离 | IdentityMiddleware + service 层 owner_user_id WHERE |
| LLM 主流量看不见、出问题不知道 | Helicone 透明 proxy + Langfuse trace |
| 跑完仿写没人通知 | n8n pipeline-complete webhook |
| Prompt 改一次要发版 | 路线图：Dify Prompt Studio 托管 |
| 商用前缺定价 / 限流 / fallback | 6 项 SLA gap 已列清单 |

---

## 当前能做到什么（实证）

### v2 已交付（PR #8 merged）
- ✅ Infra 三件套：Dify (8080) / n8n (5678) / Langfuse (3030) 全部 self-host docker-compose
- ✅ DB 加 `owner_user_id` 列（Alembic migration 上线）
- ✅ UI shell：`/writer/*` 与旧 Workbench 隔离
- ✅ Dify Chatbot iframe（流式 + 引用跳转）

### v3 已交付（PR #9 merged）
- ✅ IdentityMiddleware：`X-User-Id` 三层透传（middleware / service / DB）
- ✅ service 层 `owner_user_id` WHERE 子句，多用户隔离生效
- ✅ n8n pipeline-complete webhook（跑完仿写自动通知）
- ✅ Helicone LLM proxy（imitation 主流量 trace 全覆盖）
- ✅ "alice 看不到 bob 的书 + 跑完仿写 alice 收到通知" 端到端验证通过

### 跨题材改写商用就绪（B2B API 路径）
- ✅ 技术质量：170/171 pass（99.4%），1M+ 字，3 题材
- ✅ 运维能力：环境自检 3 件套 + 5 棵故障决策树 + 100+ 章后台跑批
- ✅ 接入契约：pre-v1 API contract（CLI / export / HTTP API 三入口对齐）+ versioning + 6 份 sample

详细：[cross-genre-imitation-commercial-readiness-20260515.md](../cross-genre-imitation-commercial-readiness-20260515.md)

---

## 6 项 SLA gap（商用前必须补齐）

| Gap | 现状 | 工作量 |
|-----|------|--------|
| **1. 定价模型** | ❌ 未定义 | 计费表 + Stripe 集成 ~3 天 |
| **2. 多租户隔离** | ⚠️ 有 owner_user_id 但无 tenant_id / RLS / token 映射 | ~5 天，含数据迁移 |
| **3. SLA + 限流** | ❌ 无并发控制、无 SLA 文档 | fastapi-limiter + Redis ~5 天 |
| **4. LLM provider 自动 fallback** | ⚠️ 手动 ops（nassaapi → sealos） | LLMProviderRouter + circuit breaker ~5 天 |
| **5. 版权合规** | ❌ 输入文本来源声明、商用授权链未建 | 法律 + 流程 ~2 周 |
| **6. 监控 + 计费仪表盘** | ⚠️ Helicone + Langfuse 各看一半 | OTLP forward 合并 ~1 周 |

**最低可上线方案**（B2B API 定向）：补齐 Gap 1-4 即可，约 4 周。

详细：[cross-genre-imitation-commercial-readiness-20260515.md](../cross-genre-imitation-commercial-readiness-20260515.md)

---

## 推荐计费方案（草案）

| 套餐 | 内容 | 价格 |
|------|------|------|
| 单本 | ≤ 120 章 | $60 |
| 包年 | 10 本 | $400（8 折） |
| 企业 | 自定义 | 协商 |

- 计费单位：`per-chapter`（一次成功 pass = 一章计费）
- 失败章节：**不计费**（保护用户体验）
- LLM 透传成本：~$0.10/章 → 定价 $0.50/章 留 5x 毛利覆盖运维 + retry buffer

---

## 怎么验证商业化闭环

### 一键 smoke（5 分钟端到端）
```bash
# 前置：v2/v3 docker stacks 全部 up
make v2-pickup-checklist
docker ps | grep -E 'dify|n8n|langfuse|helicone'

# 运行 6 步 smoke
docs/runbook/business-loop.md
```

### 6 步验证
1. alice 上传一本书 → 返回 `run_id` / `branch_id`
2. alice library = 1，bob library = 0（隔离生效）
3. alice 跑一次 imitation → contract_version 返回
4. n8n 收到 pipeline-complete 通知
5. Langfuse 看到 imitation trace
6. Dify 副驾发问，后端日志含 `X-User-Id: alice`

详细 runbook：[runbook/business-loop.md](../runbook/business-loop.md)

---

## 架构概览

```
作家 / 集成方
    ↓ X-User-Id
┌─────────────────────────────────┐
│  IdentityMiddleware (FastAPI)    │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  Service 层（owner_user_id WHERE） │
│  ImportService / ImitationService │
│  RetrievalService / QAService     │
└─────────────────────────────────┘
    ↓                    ↓
┌──────────────┐    ┌─────────────────────┐
│ PostgreSQL   │    │ LLM 调用            │
│ owner_user_id│    │   ↓                 │
└──────────────┘    │ Helicone (8585)    │
                    │   ↓ trace           │
                    │ LLM Provider        │
                    │ (DeepSeek/Claude)   │
                    └─────────────────────┘
                              ↓
                    ┌─────────────────────┐
                    │ Dify (8080)         │
                    │  Chatbot            │
                    │  Prompt Studio      │
                    │  Workflow           │
                    │  ↓ trace            │
                    │ Langfuse (3030)     │
                    └─────────────────────┘

        n8n (5678) ← pipeline-complete webhook
```

---

## 路线图

### v1（已撤回）
重自研版本，被 v2 取代。

### v2 ✅（2026-05-14）
infra + DB + UI shell。

### v3 ✅（2026-05-14）
IdentityMiddleware + n8n + Helicone。"alice 看不到 bob 的书" 验证通过。

### v4 候选

**优先级 A — 用户已能感受**
- 🔲 Reader 端 UI
- 🔲 多用户管理 UI

**优先级 B — 商业化前必须**
- 🔲 6 项 SLA gap 补齐（定价 / 隔离 / 限流 / fallback / 版权 / 监控）
- 🔲 Prompt 资产托管（Dify Prompt Studio）
- 🔲 secret 管理（Vault / SOPS / 1Password CLI）
- 🔲 prod / staging 拆分（HA + backup + cost cap）
- 🔲 Langfuse + Helicone trace 合并

**优先级 C — 内部体验**
- 🔲 FastAPI 全 surface（main.py 2503 行 → 微框架）
- 🔲 每用户配额 / 计费
- 🔲 Reader 端长期记忆（Letta / Mem0）

详细：[strategy/writer-studio-roadmap.md](../strategy/writer-studio-roadmap.md)

### 不做（明确放弃）
- ❌ Coze SaaS 替代 Dify（数据上云不符合 self-host 约束）
- ❌ LangFlow / Bisheng（与 Dify 同质，引入二个 framework 维护成本）
- ❌ OpenManus 替代 LangGraph（自主性太强，imitation 需要精细控制）
- ❌ PostgreSQL Row-Level Security（v4 商业化再讨论）

---

## 深入文档

### 路线图与策略
- [strategy/writer-studio-roadmap.md](../strategy/writer-studio-roadmap.md) — 商业化整体路线图
- [strategy/external-integration-roadmap-20260514.md](../strategy/external-integration-roadmap-20260514.md) — 外部集成路线图
- [strategy/external-integration-checklist-20260514.md](../strategy/external-integration-checklist-20260514.md) — 外部集成 checklist
- [strategy/kernel-sota-gap-assessment-20260514.md](../strategy/kernel-sota-gap-assessment-20260514.md) — 与 SOTA 的差距评估
- [strategy/ai-novel-system-benchmark.md](../strategy/ai-novel-system-benchmark.md) — 行业基准对比

### 商用就绪决策
- [cross-genre-imitation-commercial-readiness-20260515.md](../cross-genre-imitation-commercial-readiness-20260515.md) — 跨题材改写商用就绪报告（6 项 gap + 3 条上线路径）

### 产品策略
- [product/ai-novel-product-strategy.md](../product/ai-novel-product-strategy.md) — 产品战略
- [product/ai-novel-capability-map.md](../product/ai-novel-capability-map.md) — 能力地图
- [product/ai-novel-capability-scorecard.md](../product/ai-novel-capability-scorecard.md) — 能力评分卡
- [product/ai-novel-commercialization-and-moat-20260508.md](../product/ai-novel-commercialization-and-moat-20260508.md) — 商业化与护城河

### 运维 runbook
- [runbook/business-loop.md](../runbook/business-loop.md) — v3 端到端 6 步 smoke
- [runbook/v3-pickup-checklist.md](../runbook/v3-pickup-checklist.md) — v3 pickup 步骤清单
- [runbook/helicone-enable.md](../runbook/helicone-enable.md) — Helicone 启用
- [runbook/migration-guide.md](../runbook/migration-guide.md) — 迁移指南

### 可观测性与选型
- [observability/helicone-vs-langfuse.md](../observability/helicone-vs-langfuse.md) — observability 评估
- [research/fastgpt-vs-dify.md](../research/fastgpt-vs-dify.md) — 框架选型决策
- [research/competing-novel-ai-projects-20260515.md](../research/competing-novel-ai-projects-20260515.md) — 竞品研究

### 白皮书
- [whitepaper/ai-novel-system-whitepaper-v2.md](../whitepaper/ai-novel-system-whitepaper-v2.md) — 白皮书 v2

---

返回 [capabilities/](./README.md) ｜ [文档中心](../README.md)
