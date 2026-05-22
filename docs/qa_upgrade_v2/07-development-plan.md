# 07. 开发计划

## 1. 目标

本文件把 V2 文档进一步压缩成工程开发任务，方便直接开工。

---

## 2. 推荐代码切分

## Lane A — 稳定化与修错

### 目标
把现有主链修到“可安全迭代”。

### 任务
1. 核查并修正 alias source / node type 契约
2. 调整 anti-spoiler filter 前置
3. 对齐 `/api/search-branch` router / service / frontend contract
4. 增加 QA diagnostics trace

### 主要文件
- `novel_analyzer/services/entity_resolution_service.py`
- `novel_analyzer/services/graph_service.py`
- `novel_analyzer/services/retrieval_service.py`
- `apps/api/app/routers/pipeline.py`
- `apps/web/src/lib/api.ts`
- `apps/web/src/lib/risk-api.ts`

---

## Lane B — Query Understanding V2

### 目标
引入 `StructuredQueryPlan`。

### 任务
1. 新建 query plan schema
2. 新建 query parse service
3. 从 `qa_service` 接入 query plan
4. 增加 diagnostics 导出

### 建议新增文件
- `novel_analyzer/services/query_understanding_service.py`
- `novel_analyzer/domain/query_plan.py` 或并入 `domain/schemas.py`

### 主要修改文件
- `novel_analyzer/services/qa_service.py`
- `novel_analyzer/domain/schemas.py`

### 当前覆盖真相（2026-05-22）

基于当前已存在的 [`tests/test_query_understanding_service.py`](file:///home/user/novel-analyzer/tests/test_query_understanding_service.py)，本项目对 Query Understanding 的自动化覆盖还处在**骨架验证**阶段，而不是“功能完整阶段”。

| 能力 | 当前状态 | 证据 |
|---|---|---|
| timeline question_type | 已覆盖 | timeline query plan 测试 |
| time scope 抽取 | 已覆盖 | `前20章` 范围断言 |
| anti-spoiler constraint | 已覆盖 | `plan.constraints.anti_spoiler` 断言 |
| alias → canonical | 已覆盖 | `卫图少年 -> 卫图` 断言 |
| retrieval preference（timeline/causal） | 部分覆盖 | 仅覆盖 `prefer_timeline` / `prefer_causal` |
| ambiguity detection | 未覆盖 | 无现有测试 |
| parse failure taxonomy | 未覆盖 | 无现有测试 |
| relation intent extraction | 未覆盖 | 无现有测试 |
| world_rule extraction | 未覆盖 | 无现有测试 |
| foreshadow extraction | 未覆盖 | 无现有测试 |
| diagnostics 导出 | 未覆盖 | 无现有测试 |
| QA 主链接线一致性 | 未覆盖 | 还未进入集成覆盖 |

这意味着当前文档里所有“P1 已起步”的表述都应理解为：

> **schema 和 parser skeleton 已存在，但还没有足够的 regression surface 来支撑“query understanding 已稳定”。**

---

## Lane C — Retrieval & Evidence Contract

### 目标
引入 `EvidenceHit`，统一 retrieval 输出。

### 任务
1. 设计 `EvidenceHit` schema
2. lexical/fact/graph/vector/window 统一输出
3. graph typed route 化
4. 保留 backward compatibility

### 主要文件
- `novel_analyzer/services/retrieval_service.py`
- `novel_analyzer/services/graph_service.py`
- `novel_analyzer/services/qa_service.py`

---

## Lane D — Rerank V2

### 目标
让 rerank 能吃更细证据。

### 任务
1. rerank 输入从 chapter summary 扩展到 evidence
2. 做 question-aware rerank policy
3. 增加 rerank benchmark

### 主要文件
- `novel_analyzer/services/retrieval_service.py`
- `novel_analyzer/rerank/service.py`
- `novel_analyzer/services/retrieval_benchmark_service.py`

---

## Lane E — Answer Builder & Grounding

### 目标
结构化 answer context，增强 grounding。

### 任务
1. 新建 answer context builder
2. answer mode 分层
3. 证据桶映射
4. grounding summary 增强

### 主要文件
- `novel_analyzer/services/qa_service.py`
- `novel_analyzer/domain/schemas.py`
- `novel_analyzer/llm/prompts.py`

---

## 3. 推荐开发顺序（非常重要）

### 第 1 批 PR
- 稳定化修错
- diagnostics 补齐

### 第 2 批 PR
- `StructuredQueryPlan`
- query parse service
- qa_service 接入 plan

### 第 3 批 PR
- `EvidenceHit`
- graph typed routes
- evidence normalization

### 第 4 批 PR
- evidence-aware rerank

### 第 5 批 PR
- answer builder v2
- grounding / verification upgrade

不要倒着做。

---

## 4. 每批 PR 的最小验收

## PR1 稳定化
- alias resolution 有真实数据命中
- anti-spoiler regression 通过
- API contract 对齐

## PR2 query understanding
- query plan schema 稳定
- 至少有 20~30 条 parser regression tests

### PR2 当前缺口（新增）
建议把 `20~30` 条 parser regression tests 至少拆成以下桶：
- alias / canonical
- timeline / chapter range
- causal_why
- relation intent
- world_rule
- foreshadow
- ambiguity / underspecified question
- parse failure / fallback behavior

### 推荐把这些桶同步落到数据目录
除了测试代码，建议同时在 [`05-data-preparation.md`](./05-data-preparation.md) 约定的 `data/qa_eval/parser_regression/` 下准备同名数据桶：
- `alias_and_canonical.jsonl`
- `timeline_and_scope.jsonl`
- `relation_intent.jsonl`
- `world_rule.jsonl`
- `foreshadow.jsonl`
- `ambiguity.jsonl`
- `parse_failure_taxonomy.jsonl`

这样做的好处是：
- 单测覆盖行为边界
- 数据桶覆盖样本边界
- 以后 parser 规则 / LLM parse / rewrite 升级时能复用同一批 regression 样本

## PR3 evidence contract
- retrieval diagnostics 能输出 evidence-level objects
- graph route 可输出结构化 path

## PR4 rerank
- rerank benchmark 能证明收益或至少不退化

## PR5 answer generation
- answer grounding 结果可见
- multi-hop 问题回答质量提升

---

## 5. 推荐测试结构

建议增加：

```text
tests/
  test_query_understanding_service.py
  test_qa_query_plan.py
  test_retrieval_evidence_contract.py
  test_graph_retrieval_routes.py
  test_qa_answer_builder.py
  test_qa_grounding.py
```

并保留现有：
- `tests/test_qa_service.py`
- `tests/test_retrieval_service.py`
- `tests/test_domain_dictionary_service.py`

### 推荐先补的最小测试集（新增）

如果下一步继续做 Query Understanding，优先顺序建议是：

1. 在 `tests/test_query_understanding_service.py` 继续补：
   - relation intent
   - world_rule
   - foreshadow
   - ambiguity flag
   - parse failure taxonomy
2. 新增 `tests/test_qa_query_plan.py`：
   - 覆盖 `qa_service` 消费 query plan 的行为一致性
3. 等主链接线后，再补：
   - diagnostics export
   - anti-spoiler + query plan 联动
   - difficult query regression bucket

### 推荐执行顺序（回归资产视角）
1. 先补 `tests/test_query_understanding_service.py`
2. 再落 `data/qa_eval/parser_regression/` 的 7 个桶
3. 再让 badcase backlog 进入对应桶
4. 最后再考虑把 parser 升级成更复杂的 rewrite / decomposition / planner 体系

---

## 6. 开发时必须持续看的风险

### 风险 1：复杂度失控
如果在没有中间 contract 的情况下边改边加 route，很快会失控。

### 风险 2：线上链路变慢
graph route、evidence rerank、query parse 都会加耗时，需要明确 budget。

### 风险 3：数据坏，模型背锅
如果 keyword / entity / alias / graph 数据脏，后面再强的 query planner 也救不回来。

### 风险 4：可观测性跟不上
没有 diagnostics，你会分不清哪层在出问题。

---

## 7. 推荐第一周任务拆解

### Day 1
- 阅读本目录全部文档
- 列出现有接口 contract
- 核查 alias / search-branch 问题

### Day 2
- 修 P0 稳定化问题
- 增加 diagnostics 输出

### Day 3
- 定义 `StructuredQueryPlan`
- 写 parser schema tests

### Day 4
- 接入 `qa_service`
- 产出 query plan debug 信息

### Day 5
- 设计 `EvidenceHit`
- 起 graph typed route 的骨架

这比“直接重写 qa_service”稳得多。

---

## 8. 最终建议

V2 开发不要把它当成“调 prompt”，要把它当成一个小型检索推理系统工程。

真正的重点是这三个对象：
- `StructuredQueryPlan`
- `EvidenceHit`
- `GroundedBranchQAResult`

把这三个对象立住，后面开发会轻松很多。
