# novel-analyzer 系统概览

> 一页读懂：是什么、给谁、当前能做到什么、商业化走到哪。
> 详细分流：[文档中心](./README.md) ｜ 路线图：[ROADMAP.md](./ROADMAP.md) ｜ 术语：[GLOSSARY.md](./GLOSSARY.md)

---

## 1. 产品定位

novel-analyzer 是一套面向**长篇小说**的 **AI 内容理解 + 风险门控 + 受控生成 + 商业化运营**平台，**不是**通用 AI 写作器。

它解决三类问题：

| 问题 | 行业现状 | 我们的方案 |
|------|---------|-----------|
| **看不懂书** | 长篇 100+ 章，作者 / 编辑 / 读者都难以保持记忆 | 拆书 → 知识图谱 → 检索 → 防剧透 Q&A |
| **越写越乱** | LLM 直写无法保证人物/规则/时间线一致 | 9 个 risk checker + harness 控制 + Loom 信号 |
| **AI 仿写不可控** | 模型直出风格漂移、动机断裂、爽点稀释 | 章级 / 整本 harness + 跨题材 mapping_pack + 反 AI slop |

---

## 2. 服务对象

| 用户 | 核心价值 | 关键能力 |
|------|---------|---------|
| **作家 / 工作室** | 仿写辅助、连续性审查、Loom 信号反馈 | Writer Studio + 项目壳 + 整本仿写编排 |
| **编辑 / 审校** | 风险卡 + 问题簇 + 证据链 | 9 checker mainline + review workflow |
| **读者** | 流式 Q&A、引用跳转、防剧透摘要 | Reader Studio + RAG + 图谱推理 |
| **平台 / 集成方** | B2B API、跨题材改写、风险审查能力 | API surface + mapping_pack + bundle 导出 |

---

## 3. 系统全景

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          novel-analyzer 平台                                  │
│                                                                              │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│   │  导入层      │→ │  分析层      │→ │  质量层      │→ │  产品层          │   │
│   │  ingest      │  │ pipeline    │  │ risk audit  │  │ QA / Studio /   │   │
│   │  splitter    │  │ stages(3)   │  │ 9 checkers  │  │ export / API    │   │
│   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘   │
│                          │                  │                  │             │
│                          ▼                  ▼                  ▼             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │      Loom 上层：分层记忆 / 张力 / 风格 / 角色 / 评估 / 项目壳          │   │
│   │      memory · tension · style · character · reward · project shell  │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                          │                                                   │
│                          ▼                                                   │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │      仿写控制层：session → operator → action → execution → replay   │   │
│   │      章级 imitation · 整本 writer-imitate-range · mapping_pack       │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │      基础设施层                                                       │   │
│   │  PostgreSQL（pg_trgm + pgvector + pg_jieba）│ BM25 / Vector / RRF    │   │
│   │  GraphNode / GraphEdge / FactRecord │ Provider Health │ Helicone     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │      接入层                                                           │   │
│   │  Writer Studio（/writer/*）│ Reader Studio（/reader/*）│ Workbench    │   │
│   │  Dify Chatbot │ n8n hooks │ Langfuse traces │ FastAPI + CLI          │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. 四条核心能力线（一句话状态）

| 能力线 | 一句话定位 | 当前状态 | 详情入口 |
|--------|-----------|---------|---------|
| **拆书引擎**（Deconstruction） | 把长篇切成 facts / graph / window / state，喂给检索与 Q&A | ✅ Phase 4.5 完成；R@5 = 0.81/0.84（5 本书 587 docs 锁基线） | [capabilities/01-deconstruction.md](./capabilities/01-deconstruction.md) |
| **风险检查**（Risk Audit） | 9 个 checker + 集群审查 + 证据导出，advisory-only 不阻断 | ✅ 9 checker 进入 mainline，preflight + harness routing 就绪 | [capabilities/02-risk-audit.md](./capabilities/02-risk-audit.md) |
| **受控仿写**（Imitation） | 章级 + 整本 + 跨题材 mapping_pack，harness 控制全流程 | ✅ 跨题材 170/171 pass（99.4%）；🔧 同题材 prompt 修复待长跑；✅ Phase 6 项目壳完成 | [capabilities/03-imitation.md](./capabilities/03-imitation.md) |
| **商业化运营**（Commercialization） | B2B API → 多租户 SaaS，定价 / 限流 / 隔离 / 计费 | ⚠️ 技术 ready，infra 4 周可商用（6 项 SLA gap） | [capabilities/04-commercialization.md](./capabilities/04-commercialization.md) |

---

## 5. 商用就绪状态（2026-05-17）

| 维度 | 状态 | 实证 |
|------|------|------|
| **跨题材改写**（B2B API 定向） | ✅ 技术 ready | 170/171 章 verdict=pass，1M+ 字，3 题材 |
| 章节 Q&A + 引用跳转 | ✅ 可用 | R@5 0.81+ 跨 5 本书 |
| 风险审查工作流 | ✅ 可用 | 9 checker mainline，review workflow DB-only |
| 仿写辅助（作家工作台） | ⚠️ 辅助级 | harness + Loom 信号成熟；不能宣称"AI 自动写书" |
| 同题材整本仿写 | 🔧 验证中 | 0/307 → 已修复 prompt，待 Stage A/B/C 长跑 |
| 读者体验评估 | ✅ 可用 | 4-persona × 7-dim panel + comfort_score soft gate |
| 多租户 SaaS | ❌ 未就绪 | 6 项 infra gap：计费 / 限流 / fallback / 隔离 / 版权 / 监控 |

详细决策表：[capabilities/04-commercialization.md](./capabilities/04-commercialization.md) ｜ [cross-genre-imitation-commercial-readiness-20260515.md](./cross-genre-imitation-commercial-readiness-20260515.md)

---

## 6. 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python 3.11 · FastAPI · LangGraph · SQLAlchemy |
| 数据库 | PostgreSQL（pg_trgm / pgvector / pg_jieba） |
| 前端 | Next.js 15 · React 18 · Ant Design 5 |
| AI 编排 | Dify（Chatbot / Workflow / Prompt Studio） |
| 外围自动化 | n8n（通知 / 日报 / 第三方集成） |
| 可观测性 | Langfuse（Dify trace） + Helicone（LLM proxy trace） |
| Embedding | ONNX（本地） / HTTP（TEI / OpenAI / Jina） |

---

## 7. 推荐的 5 分钟入口

1. **第一次接触系统** → 本文档 + [README.md](./README.md)
2. **要部署/启动** → [runbook/deployment-and-operations-manual-20260515.md](./runbook/deployment-and-operations-manual-20260515.md)
3. **要使用 CLI** → [cli-operations-manual.md](./cli-operations-manual.md)
4. **要调用 API** → [api-current-surface.md](./api-current-surface.md)
5. **要看路线图** → [ROADMAP.md](./ROADMAP.md)
6. **要做培训 / 知识转移** → [training/](./training/README.md)

---

## 8. 设计原则（贯穿全系统）

- **章节是最小提交单元**，当前章成功后才继续下一章
- **回退采用逻辑隐藏**，默认只读 active branch
- **手工结果允许保留**，但默认 `participates_in_downstream = false`
- **拆书失败自动重试上限 5 次**，超过进入人工恢复
- **风险审查 advisory-only**，不阻断主提交
- **Loom 增量演进**，feature flag 渐进启用、可随时回滚
- **小模型 + 精准上下文 > 大模型 + 粗糙上下文**
