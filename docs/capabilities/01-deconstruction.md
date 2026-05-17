# 能力线 1 — 拆书引擎（Deconstruction）

> **一句话定位**：把一本长篇小说切成结构化的事实、图谱、状态、检索向量，喂给检索 / Q&A / 风控 / 仿写所有下游能力。

**状态**：✅ Phase 4.5 完成；P0 锁基线 R@5 = 0.81 / 0.84（5 本书 587 docs）

---

## 能解决什么问题

| 问题 | 拆书引擎给的答案 |
|------|-----------------|
| 100+ 章长篇，作者/编辑/读者记不住前文 | 结构化 facts + graph + window，可检索可回看 |
| LLM 直问长篇，prompt 装不下 | adaptive context（事实驱动三策略）+ arc memory（三层渐进压缩） |
| 中文专有名词 BM25 切错 | 自动从 GraphNode 收集领域词典 + pg_jieba |
| 远距离实体召回不到 | query expansion（别名 + 1-hop 图邻居） |
| 长篇下游：风险审查、仿写、Q&A 没有可靠上下文源 | canonical chapter artifact 作为统一真源 |

---

## 当前能做到什么（实证）

### 检索基线
- **simple R@5 = 0.81**，**jieba R@5 = 0.84**
- 跨 5 本书 587 docs 验证（domain dict + pg_jieba + bm25_vector 三件套已固化）
- 详细：[deconstruction-acceleration/benchmark-baseline-20260511.md](../deconstruction-acceleration/benchmark-baseline-20260511.md)

### LLM 效率
- 单章 LLM 调用：5 → 3 次（stage merging）
- 单章延迟：-40%
- 整书吞吐：+30%（pipeline batch processing）

### 质量保证
- 每条分析声称必须有原文锚定（claim grounding）
- 检测到问题自动修复（auto-repair 4 类）
- confidence-weighted 动态压缩，挤掉低价值上下文

### 边界（明确不做）
- ❌ 不写小说
- ❌ 不评判好不好看
- ❌ 不替代人工编辑
- ❌ 不自动修文

---

## 怎么用

### CLI 一键导入
```bash
.venv/bin/python -m novel_analyzer.cli.app auto-run /path/to/novel.txt --max-chapters 0
# 记录返回的 branch_id，作为后续所有命令的入参
```

### 检索基准测试
```bash
.venv/bin/python -m novel_analyzer.cli.app retrieval-benchmark <branch_id>
```

### Workbench UI
```
http://127.0.0.1:4173/control     # 导入 + 启动 + 恢复
http://127.0.0.1:4173/quality     # 质量仪表盘
```

### 推荐运行配置
```bash
NOVEL_ANALYZER_LLM_BASE_URL=http://34.97.18.233:65432/v1
NOVEL_ANALYZER_LLM_MODEL_NAME=claude-haiku-4.5
NOVEL_ANALYZER_LLM_STAGE_MODEL_NAME=claude-haiku-4.5
NOVEL_ANALYZER_LLM_REQUESTS_PER_SECOND=1.5
NOVEL_ANALYZER_USE_MERGED_STAGES=true
```

---

## 架构概览

```
原始小说 .txt
    ↓
ingest + chapter splitter
    ↓
manifest / segments
    ↓
chapter analysis pipeline （3 stage merged）
    ├─ chapter_intake + fact_extractor
    ├─ evidence_binder + analysis_generator
    └─ writer_learning_lens + anti_fabrication_guard
    ↓
canonical chapter artifact
    ├─ facts        → FactRecord
    ├─ graph        → GraphNode / GraphEdge
    ├─ window       → WindowArtifact
    ├─ state        → state_summary
    └─ embeddings   → ChunkEmbedding (pgvector)
    ↓
下游消费者
    ├─ Retrieval Service（BM25 / vector / RRF）
    ├─ ContextService（adaptive context for LLM）
    ├─ Risk Audit（9 checker）
    ├─ Imitation harness（章级 / 整本）
    └─ Q&A（流式 RAG + 图谱推理）
```

---

## 路线图

| 阶段 | 状态 | 内容 |
|------|------|------|
| **Phase 1**：LLM 效率 | ✅ | adaptive context + stage merging |
| **Phase 2**：吞吐与路由 | ✅ | foreshadowing manager + complexity router + batch processing |
| **Phase 3**：记忆与实体 | ✅ | entity resolution + arc memory |
| **Phase 4**：质量保证 | ✅ | causal graph + confidence calibration + self-eval + claim grounding + auto-repair + confidence-gated checker |
| **Phase 4.5**：双档拆书 | ✅ | quick / deep canonical / enrichment 边界 |
| **Phase 5-Perf**：性能优化 | 🔄 | embedding / rerank / reasoning_snapshot / vector 路由 |

---

## 深入文档

### 入口
- [deconstruction-acceleration/README.md](../deconstruction-acceleration/README.md) — 拆书加速专题入口
- [deconstruction-acceleration/architecture.md](../deconstruction-acceleration/architecture.md) — Quick / Deep 双档架构
- [deconstruction-acceleration/user-manual.md](../deconstruction-acceleration/user-manual.md) — 用户使用说明

### 路线图与交付
- [deconstruction-acceleration/roadmap-sota-optimization.md](../deconstruction-acceleration/roadmap-sota-optimization.md) — SOTA 路线图
- [deconstruction-acceleration/handoff-sota-optimization.md](../deconstruction-acceleration/handoff-sota-optimization.md) — 交付文档
- [deconstruction-acceleration/critical-open-points.md](../deconstruction-acceleration/critical-open-points.md) — 剩余关键风险

### 性能与基线
- [deconstruction-acceleration/performance-profiling-20260517.md](../deconstruction-acceleration/performance-profiling-20260517.md) — 雪中悍刀行 229 章实测
- [deconstruction-acceleration/benchmark-baseline-20260511.md](../deconstruction-acceleration/benchmark-baseline-20260511.md) — canonical 默认读路径基线

### 底座优化（互补能力线）
- [foundation-optimization/README.md](../foundation-optimization/README.md) — 分词 / Embedding / Prompt / Context / Calibration / Cache 六层
- [foundation-optimization/embedding-rerank-dictionary-guide.md](../foundation-optimization/embedding-rerank-dictionary-guide.md) — Embedding/Rerank 微调
- [foundation-optimization/p0-maintenance-checklist.md](../foundation-optimization/p0-maintenance-checklist.md) — P0 维护清单

### 输入规范
- [novel-ingest-input-spec.md](../novel-ingest-input-spec.md) — 小说输入规范
- [novel-ingest-chapter-standard.md](../novel-ingest-chapter-standard.md) — 章节切分标准

---

## 上下游关系

| 上游 | 下游 |
|------|------|
| 原始小说 .txt | Retrieval / Q&A |
| 用户输入约束 | Risk Audit |
|  | Imitation harness |
|  | Loom memory 层 |

---

返回 [capabilities/](./README.md) ｜ [文档中心](../README.md)
