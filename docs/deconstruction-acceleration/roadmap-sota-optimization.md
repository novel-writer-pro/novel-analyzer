# Deconstruction Engine SOTA Optimization Roadmap

## Current Status: Phase 4 Complete (Full SOTA Stack)

推荐生产配置：`NOVEL_ANALYZER_USE_MERGED_STAGES=true` + `deepseek-v4-flash`

---

## Phase 1 - LLM 效率优化 (Completed)

### 1A. Adaptive Context Assembly
- **Status**: Done
- **Impact**: 长篇远距离事实召回率 +30-50%
- **Change**: `ContextService` 基于 intake 实体驱动三策略检索 (relevance + recency + foreshadowing)
- **Files**: `novel_analyzer/services/context_service.py`

### 1B. Stage Merging
- **Status**: Done
- **Impact**: LLM 调用 5→3 次，单章延迟 -40%
- **Change**: 合并 skill prompts + `_invoke_merged_stage` + `use_merged_stages` 配置
- **Files**: `novel_analyzer/services/analysis_service.py`, `novel_analyzer/agent/pipeline.py`, `skills_dir/chapter-intake-and-facts/`, `skills_dir/evidence-and-analysis/`

---

## Phase 2 - 吞吐与路由优化 (Completed)

### 2A. Foreshadowing Lifecycle Manager
- **Status**: Done
- **Impact**: 100+ 章长篇不丢失未回收伏笔
- **Change**: `ForeshadowingService` planted/reinforced/paid_off 状态机；自动注入后续章节 context
- **Files**: `novel_analyzer/services/foreshadowing_service.py`

### 2B. Chapter Complexity Router
- **Status**: Done
- **Impact**: 简单章节省成本，复杂章节提质量
- **Change**: `_score_chapter_complexity` 评分后自动路由到大/小模型
- **Files**: `novel_analyzer/services/analysis_service.py`

### 2C. Pipeline Batch Processing
- **Status**: Done
- **Impact**: 整书吞吐 +30%
- **Change**: `_runner_loop` 利用 concurrency 参数批量处理（最多 3 章/轮）
- **Files**: `novel_analyzer/application/pipeline_async.py`

---

## Phase 3 - 记忆与实体增强 (Completed)

### 3A. Entity Resolution (Coreference)
- **Status**: Done
- **Impact**: 图谱节点去重，检索精度提升
- **Change**: `EntityResolutionService` 字符级 Jaccard 聚类；adaptive retrieval 自动解析别名
- **Files**: `novel_analyzer/services/entity_resolution_service.py`

### 3B. Arc-level Memory
- **Status**: Done
- **Impact**: 第 100+ 章仍能访问第 1-5 章关键信息
- **Change**: `ArcMemoryService` 三层渐进压缩 (recent/midrange/distant)
- **Files**: `novel_analyzer/services/arc_memory_service.py`

---

## Phase 4 - 质量保证增强 (Completed)

### 4A. Causal Graph
- **Status**: Done
- **Impact**: 叙事逻辑断裂自动检测
- **Change**: `CausalGraphService` 提取因果边 + logic-break 检测
- **Files**: `novel_analyzer/services/causal_graph_service.py`

### 4B. Confidence Calibration
- **Status**: Done
- **Impact**: 事实排序更准确
- **Change**: `ConfidenceCalibrationService` 四因子加权校准
- **Files**: `novel_analyzer/services/confidence_calibration_service.py`

### 4C. Self-evaluation Loop
- **Status**: Done
- **Impact**: commit 前自动捕获质量问题
- **Change**: `SelfEvaluationService` 5 项确定性自检
- **Files**: `novel_analyzer/services/self_evaluation_service.py`

### 4D. Claim-level Grounding
- **Status**: Done
- **Impact**: 每条分析声称必须有原文锚定，无锚定自动降级
- **Change**: `ClaimGroundingService` 关键词 + bigram 多策略原文匹配；ungrounded claims 移入 ambiguous_points
- **Files**: `novel_analyzer/services/claim_grounding_service.py`

### 4E. Auto-repair Loop
- **Status**: Done
- **Impact**: 检测到问题后自动修复而非仅标记
- **Change**: `AutoRepairService` 4 类修复（overclaim 降级、去重、thin facts 回填、空摘要兜底）
- **Files**: `novel_analyzer/services/auto_repair_service.py`

### 4F. Confidence-gated Checker Activation
- **Status**: Done
- **Impact**: 低置信度章节加严检查，高置信度章节跳过冗余 checker
- **Change**: `ConfidenceGatedActivationService` 动态决定 checker 激活和 severity 调整；已接入 `RiskAuditService.generate_for_chapter` 主循环
- **Files**: `novel_analyzer/services/confidence_gated_activation_service.py`, `novel_analyzer/services/risk_audit_service.py`

---

## Phase 4.5 - 产品层集成 (Completed)

### 4G. QA 系统增强
- **Status**: Done
- **Impact**: QA 回答质量提升（别名扩展 + 伏笔上下文 + 因果链上下文）
- **Change**: `BranchQAService` 集成 entity resolution / foreshadowing / causal graph
- **Files**: `novel_analyzer/services/qa_service.py`

### 4H. 导出增强
- **Status**: Done
- **Impact**: 导出包含伏笔生命周期表和因果链
- **Change**: `ExportService.export_chapter_bundle` 新增 `foreshadowing_threads` + `causal_chains`
- **Files**: `novel_analyzer/services/export_service.py`

### 4I. Quality Dashboard API
- **Status**: Done
- **Impact**: 前端可消费的分支级质量仪表盘
- **Change**: `GET /api/quality-dashboard?branch_id=...` 返回置信度分布、伏笔状态、每章概要
- **Files**: `apps/api/app/main.py`

---

## Phase 5 - 性能瓶颈专项优化 (Planned)

> **背景**：2026-05-17 对雪中悍刀行 229 章已完成分支（`2cd9c1ff`）做了完整性能剖析。
> 测试环境：本机 CPU、ONNX embedding/rerank、PostgreSQL 本地、Gemini 2.5 Flash @ 1.5 rps。
> 详细数据见 [`performance-profiling-20260517.md`](./performance-profiling-20260517.md)。

### 当前单章耗时分解（ch150，已有 150 章数据积累）

| 阶段 | 耗时 | 类型 | 可优化？ |
|------|------|------|---------|
| ONNX Embedding（1.6 chunks/章） | **10,000–14,000ms** | Embedding | ✅ P0 |
| reasoning_snapshot × 3 次（无缓存） | **2,300–5,400ms** | PostgreSQL | ✅ P1 |
| LLM × 3 calls（含速率等待） | **9,000–24,000ms** | LLM | 部分可优化 |
| ONNX Rerank（QA 路径） | **4,500–6,700ms** | Rerank | ✅ P0 |
| Vector 路由（JSON + Python 余弦） | **1,325ms** | PostgreSQL | ✅ P3 |
| DB materialization（facts/graph） | ~300ms | PostgreSQL | 快，无需优化 |
| **单章总计** | **~24–39s** | — | — |

---

### 5-Perf-A. 切换 Embedding 到外部 TEI 服务（P0）

**问题**：`embedding_backend=onnx`，BGE-M3 在 CPU 上跑 ONNX 推理，单 chunk（900字符）耗时 **8,413ms**，每章平均 1.6 chunks，合计 **10–14 秒/章**。

**根因**：`OnnxBgeEmbeddingProvider` 同步阻塞，无批处理优化，CPU 推理慢。

**TEI 部署说明**：
- **CPU 部署**：比 in-process ONNX 快 2–5x（TEI 有批处理优化 + 专用进程），单 chunk 约 1,500–3,000ms，改善有限
- **GPU 部署**（推荐）：比 CPU ONNX 快 **50–200x**，单 chunk 约 **10–30ms**，是真正的量级提升
- 结论：**强烈建议 GPU 部署 TEI**；CPU TEI 只是从 8s 降到 2–3s，性价比低

**切换方式（改配置，零代码改动）**：
```bash
# .env.local
NOVEL_ANALYZER_EMBEDDING_BACKEND=http
NOVEL_ANALYZER_EMBEDDING_API_BASE=http://tei-host:8080   # GPU TEI 地址
NOVEL_ANALYZER_EMBEDDING_API_FORMAT=tei
# NOVEL_ANALYZER_EMBEDDING_API_KEY=  # TEI 无鉴权时留空
```

**TEI GPU 启动参考**：
```bash
# BGE-M3，GPU 部署
docker run --gpus all -p 8080:80 \
  ghcr.io/huggingface/text-embeddings-inference:1.5 \
  --model-id BAAI/bge-m3 --port 80
```

**预期收益**：每章 embedding **10,000ms → 100–300ms**（GPU），节省 **~10 秒/章**。

**验证**：
```bash
make smoke-external   # 检查 TEI embed 端点
.venv/bin/python -m novel_analyzer.cli.app test-embedding
```

---

### 5-Perf-B. 切换 Rerank 到外部 TEI 服务（P0）

**问题**：`rerank_backend=onnx`，bge-reranker-v2-m3 CPU 推理，5 docs 耗时 **4,471ms**，10 docs **6,652ms**，首次加载 **14,911ms**。影响所有 QA/搜索路径。

**切换方式（改配置，零代码改动）**：
```bash
# .env.local
NOVEL_ANALYZER_RERANK_BACKEND=http
NOVEL_ANALYZER_RERANK_API_BASE=http://tei-host:8081   # GPU TEI rerank 地址
NOVEL_ANALYZER_RERANK_API_FORMAT=tei
```

**TEI GPU 启动参考**：
```bash
# bge-reranker-v2-m3，GPU 部署
docker run --gpus all -p 8081:80 \
  ghcr.io/huggingface/text-embeddings-inference:1.5 \
  --model-id BAAI/bge-reranker-v2-m3 --port 80
```

**预期收益**：QA rerank **4,500ms → 50–200ms**（GPU）。

---

### 5-Perf-C. `reasoning_snapshot` 请求级缓存（P1）

**问题**：`analyze_range` 每章对同一 `upto_chapter` 调用 `reasoning_snapshot` **3 次**，无任何缓存：

```python
# context_service.py 内，每章触发：
graph_context_json()         → reasoning_snapshot(node=12, edge=12)   # 第1次
state_summary_json()         → reasoning_snapshot(node=12, edge=12)   # 第2次（完全重复）
adaptive_graph_context_json  → reasoning_snapshot(node=32, edge=32)   # 第3次
```

**实测耗时**（同一章节 3 次合计）：
```
ch50:  ~413ms    ch100: ~572ms
ch150: ~2,279ms  ch200: ~5,677ms   ← 随 graph_edges 数量线性增长
```

**根因**：`graph_edges` 已有 45,999 条，仅有单列索引 `ix_graph_edges_branch_id`，每次 snapshot 都全表扫描后过滤。

**修复方案**：在 `analyze_range` 章节循环内加请求级 snapshot 缓存：

```python
# analysis_service.py → analyze_range 内，segment 循环开始处
_snap_cache: dict[tuple, dict] = {}

def _get_snapshot(branch_id, upto_ch, node_limit, edge_limit):
    key = (upto_ch, node_limit, edge_limit)
    if key not in _snap_cache:
        _snap_cache[key] = graph_service.reasoning_snapshot(
            branch_id, upto_chapter=upto_ch,
            node_limit=node_limit, edge_limit=edge_limit
        )
    return _snap_cache[key]
```

**预期收益**：ch150 时 3 次 → 1 次，**2,279ms → ~700ms**，节省 **~1.5 秒/章**。

**Files**：`novel_analyzer/services/analysis_service.py`、`novel_analyzer/services/context_service.py`

---

### 5-Perf-D. `graph_edges` 复合索引（P2）

**问题**：`reasoning_snapshot` 查询 `WHERE branch_id=X AND chapter_first_seen <= N AND is_active=true`，现有索引只有 `ix_graph_edges_branch_id`（单列），每次扫描全部 45,999 行再过滤。

**EXPLAIN ANALYZE 证据**：
```
Parallel Bitmap Heap Scan on graph_edges
  Filter: (is_active AND (chapter_first_seen <= 200))
  Rows Removed by Filter: 30,666 / 45,999
```

**修复方案**（一次性 DDL，CONCURRENTLY 不锁表）：
```sql
CREATE INDEX CONCURRENTLY ix_graph_edges_branch_chapter_active
ON graph_edges (branch_id, chapter_first_seen)
WHERE is_active = true;
```

**预期收益**：`reasoning_snapshot` 单次从 **1,700ms → 50–100ms**（避免全表扫描）。

**Files**：新增 Alembic migration

---

### 5-Perf-E. `vector_payload` 迁移到 pgvector 原生类型（P3）

**问题**：`chunk_embeddings.vector_payload` 列类型是 **`json`**（非 pgvector `vector` 类型），导致：
1. 查询时把所有 612 个 embedding（每个 ~22KB JSON）全部拉到 Python 内存
2. 在 Python 里逐个计算余弦相似度（纯 Python `_cosine_similarity`）
3. 无法使用 pgvector ANN 索引

**实测**：vector 路由耗时 **1,325ms**（612 chunks，全量拉取 + Python 计算）。

**pgvector 扩展已安装**（v0.8.2），但完全未使用。

**修复方案**：
```sql
-- 1. 添加原生 vector 列
ALTER TABLE chunk_embeddings ADD COLUMN vector_native vector(1024);

-- 2. 迁移数据（一次性）
UPDATE chunk_embeddings
SET vector_native = vector_payload::text::vector;

-- 3. 创建 HNSW ANN 索引
CREATE INDEX ON chunk_embeddings
USING hnsw (vector_native vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 4. 更新查询使用 <=> 操作符
-- retrieval_service._vector_route 改为：
-- ORDER BY e.vector_native <=> :query_vector LIMIT :limit
```

**预期收益**：vector 路由 **1,325ms → 5–20ms**（ANN 索引）。

**Files**：新增 Alembic migration、`novel_analyzer/services/retrieval_service.py`

---

### 优化后预期效果汇总

| 优化项 | 当前（ch150） | P0 后（TEI GPU） | P0+P1+P2 后 |
|--------|-------------|----------------|------------|
| Embedding/章 | ~12,000ms | ~200ms | ~200ms |
| reasoning_snapshot×3/章 | ~2,300ms | ~2,300ms | ~150ms（缓存+索引） |
| QA rerank | ~4,500ms | ~100ms | ~100ms |
| QA vector路由 | ~1,325ms | ~1,325ms | ~15ms（P3后） |
| **单章总耗时** | **~24–39s** | **~14–27s** | **~12–15s** |

> LLM 延迟（9–24s）是外部依赖，是剩余耗时的主体，无法在本地消除。
> 提升 LLM 吞吐的唯一手段是提高 `llm_requests_per_second` 或增大 `llm_max_concurrent_requests`（需 provider 支持）。

---

## Phase 5 - 未来优化方向 (Planned)

以下为 diminishing returns 区域的优化点，建议在积累 50+ 章真实运行数据后按需启动。

底座层优化已独立为专题文档：[foundation-optimization/README.md](../foundation-optimization/README.md)

### 5A. LLM-based Coreference Resolution

**问题**: 当前 `EntityResolutionService` 使用字符级 Jaccard 相似度，对于语义级别名（如"那个少年"="卫图"）无法识别。

**原因**: 纯算法方法只能处理字面相似的别名，无法理解语义等价关系。

**优化方法**:
- 在 `fact_extractor` prompt 中增加"请列出本章出现的同一人物不同称呼"指令
- 或在 entity resolution 阶段加一次轻量 LLM 调用，输入候选 pair，输出 yes/no
- 可选：使用本地 NER 模型（如 BERT-NER）做初筛，LLM 做确认

**解决的问题**:
- "那个少年"、"小子"、"卫图" 自动合并为同一节点
- 图谱节点数减少 30-50%
- adaptive retrieval 召回率进一步提升

**预期成本**: 每章 +1 次轻量 LLM 调用（~5s）
**优先级**: Medium-High（数据量大时收益明显）

---

### 5B. Arc Auto-segmentation

**问题**: 当前 `ArcMemoryService` 按固定章节数分层（5/20），不感知故事弧的自然边界。

**原因**: 故事弧的起止点（如"修炼弧"、"复仇弧"）需要语义理解，固定窗口无法捕捉。

**优化方法**:
- 基于 continuity_notes 和 state_transition_notes 的变化幅度检测弧边界
- 当连续 N 章的主要角色/冲突/场景发生显著切换时，标记为新弧起点
- 每个弧维护独立摘要，按弧而非按章组织 distant tier

**解决的问题**:
- 跨 50 章的故事弧有完整摘要，不会被固定窗口截断
- distant tier 质量从"前 N 句拼接"提升为"弧级语义摘要"
- QA 回答"这条主线怎么发展的"类问题质量大幅提升

**预期成本**: 零额外 LLM 调用（纯确定性检测）
**优先级**: Medium（200+ 章时收益明显）

---

### 5C. Multi-language Causal Markers

**问题**: 当前 `CausalGraphService` 的因果关键词仅覆盖中文（导致/因此/所以/于是/使得/引发/触发/迫使/逼得）。

**原因**: 系统设计为中文小说拆书，但如果扩展到英文/日文小说需要多语言支持。

**优化方法**:
- 将 causal_markers 抽取为配置化的 language profile
- 增加英文 markers: because, therefore, causing, leading to, resulting in
- 增加日文 markers: ため、から、ので、結果

**解决的问题**:
- 支持多语言小说的因果链提取
- 为国际化拆书打基础

**预期成本**: 纯配置变更
**优先级**: Low（当前只做中文小说）

---

### 5D. Streaming Analysis with Early Abort

**问题**: 当前每个 LLM stage 必须完整返回后才能判断质量，低质量响应浪费全部等待时间。

**原因**: `_invoke_with_retry` 是同步阻塞调用，无法在流式输出中途判断质量。

**优化方法**:
- 使用 LangChain streaming 接口
- 在前 200 token 内检测明显格式错误（非 JSON、乱码、重复）
- 检测到问题立即 abort 并重试，节省 60-80% 的等待时间

**解决的问题**:
- 低质量响应的重试延迟从 ~60s 降至 ~10s
- 整体 retry 场景的耗时大幅减少

**预期成本**: 改造 `_invoke_with_retry` 为 streaming 模式
**优先级**: Medium（retry 频率高时收益明显）

---

### 5E. Parallel Stage Execution (True Pipelining)

**问题**: 当前 merged stages 仍是串行（先 intake+facts，再 evidence+analysis，再 guard），无法重叠。

**原因**: evidence+analysis 依赖 facts 结果，guard 依赖 analysis 结果，存在真实数据依赖。

**优化方法**:
- 将 materialization（retrieval/fact/graph/window）移到独立线程
- 在 materialization 运行的同时，开始下一章的 intake（intake 只依赖 previous_summary，不依赖 materialization）
- 使用 `concurrent.futures.ThreadPoolExecutor` 管理重叠

**解决的问题**:
- 多章连续运行时，materialization 延迟被隐藏
- 预期整书吞吐再提升 15-20%

**预期成本**: pipeline_async 重构为 2-stage overlap
**优先级**: Medium-Low（当前 batch processing 已部分解决）

---

### 5F. Adaptive Context Budget

**问题**: 当前 adaptive context 的 token 预算是固定的（ADAPTIVE_FACT_LIMIT=30, node_limit=16），不感知模型的实际 context window。

**原因**: 不同模型 context window 差异大（4K-128K），固定预算要么浪费要么溢出。

**优化方法**:
- 根据 `llm_stage_model_name` 自动推断 context window 大小
- 动态调整 fact_limit / node_limit / arc_memory 各 tier 的 max_chars
- 大 context window 模型可以注入更多历史信息

**解决的问题**:
- 大模型充分利用 context window，分析质量进一步提升
- 小模型不会因 context 过长导致截断或质量下降

**预期成本**: Settings 增加 model_context_window 配置 + ContextService 动态计算
**优先级**: Low（当前 deepseek-v4-flash 的 context window 足够）

---

## Benchmark Summary

| 配置 | 单章耗时 | vs 基线 | LLM 调用 | 质量增强 |
|------|---------|---------|----------|---------|
| 原始基线 | 330.4s | - | 5 | 无 |
| Phase 1 (merged only) | 254.0s | -23% | 3 | adaptive context |
| Phase 3 (entity + arc) | 136.0s | -59% | 5 | + 实体消解 + 弧记忆 |
| Phase 4 non-merged | 241.3s | -27% | 5 | + 因果图 + 校准 + 自评估 |
| **Phase 4 merged (推荐)** | **170.2s** | **-48%** | **3** | **全部** |

Provider: deepseek-v4-flash @ https://api.deepseek.com/v1
Novel: 775 chapters, ~5.2MB

---

## Risk Controls (Implemented)

| 风险 | 控制措施 | 级别 |
|------|---------|------|
| 后处理 service 静默失败 | 所有 exception handler 改为 logger.warning/debug | 已实现 |
| LLM provider rate-limit (429) | 指数退避 5s*attempt，最多 3 次 | 已实现 |
| LLM provider 503 | 指数退避 3s*attempt，最多 3 次 | 已实现 |
| Provider 持续降级 | provider_health 记录每次调用结果，degraded 时 warning | 已实现（观察模式） |
| Materialization 慢/卡死 | 耗时监控，>60s 发出 warning | 已实现 |
| Merged stage 返回格式异常 | 自动降级到非合并路径（分别调用） | 已实现 |
| Artifact persist 后 materialization 失败 | restore_previous_active_artifact 回滚 | 已有 |
| Job 长时间无心跳 | fail_stalled_jobs 自动标记超时 | 已有 |
| 章节重试超限 | chapter_failure_retry_limit (默认 5) 后标记 pipeline failed | 已有 |

### 未来风险控制演进

| 风险 | 建议措施 | 优先级 |
|------|---------|--------|
| Provider 持续降级自动熔断 | degraded_events >= 10 时自动切换 fallback provider | Medium |
| Materialization 硬超时 | 120s 后强制中断 + rollback | Medium |
| 单章 LLM 总耗时超限 | 全链路 timeout budget（如 300s），超时走 heuristic fallback | Low |
| 并发章节间的 DB 锁竞争 | batch_size > 1 时监控 session 锁等待时间 | Low |
| 置信度校准的 N+1 查询 | 批量查询替代逐 fact 查询 | Low |

---

## Configuration Reference

```bash
# 推荐生产配置
NOVEL_ANALYZER_LLM_PROVIDER_NAME=deepseek
NOVEL_ANALYZER_LLM_BASE_URL=https://api.deepseek.com/v1
NOVEL_ANALYZER_LLM_MODEL_NAME=deepseek-v4-flash
NOVEL_ANALYZER_LLM_STAGE_MODEL_NAME=deepseek-v4-flash
NOVEL_ANALYZER_LLM_FALLBACK_MODEL_NAME=deepseek-v4-flash
NOVEL_ANALYZER_USE_MERGED_STAGES=true
```

## Architecture Overview

```
chapter_content
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Stage 1: intake + fact_extractor (merged)          │
│  - 章节预处理 + 事实提取 (1 LLM call)               │
└─────────────────────────────────────────────────────┘
    │
    ├── complexity_score → model routing
    ├── adaptive_fact_context (entity-resolved queries)
    ├── adaptive_graph_context (relevance-ranked nodes)
    ├── arc_memory (3-tier progressive compression)
    ├── open_foreshadowing_threads
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Stage 2: evidence_binder + analysis_generator      │
│  - 证据绑定 + 分析生成 (1 LLM call)                 │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Stage 3: anti_fabrication_guard (1 LLM call)       │
│  + state_summary_guard (deterministic)              │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Post-processing (all deterministic, zero LLM cost) │
│  - self_evaluation → quality_gate                   │
│  - artifact persist                                 │
│  - materialization (retrieval/fact/graph/window)    │
│  - foreshadowing lifecycle update                   │
│  - entity resolution (alias map rebuild)            │
│  - causal graph extraction + logic-break detection  │
│  - confidence calibration                           │
│  - loom memory consolidation                        │
└─────────────────────────────────────────────────────┘
```
