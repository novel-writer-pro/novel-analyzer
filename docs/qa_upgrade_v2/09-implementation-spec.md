# 09. 实现规格说明

## 1. 文档目标

本文件不只讲“做什么”，而是讲“建议怎么在现有代码上落”。

---

## 2. 推荐新增/修改的代码模块

## 2.1 新增 `query_understanding_service.py`

### 目标
提供统一的 query parse 入口。

### 建议接口

```python
class QueryUnderstandingService:
    def build_query_plan(
        self,
        branch_id: str,
        question: str,
        *,
        max_chapter: int | None = None,
    ) -> StructuredQueryPlan:
        ...
```

### 内部建议分层
- `_classify_question_type()`
- `_extract_time_scope()`
- `_extract_entities()`
- `_expand_aliases()`
- `_infer_retrieval_preferences()`
- `_detect_ambiguities()`

### 第一期可以怎么做
- 规则优先
- 必要时可加轻量 LLM parse，但建议先不开强依赖

---

## 2.2 在 `domain/schemas.py` 增 schema

建议增加：
- `StructuredQueryPlan`
- `PlannedEntity`
- `TimeScope`
- `RetrievalPreferences`
- `EvidenceHit`
- `AnswerContextBundle`
- `GroundingSummary`

### 原则
- 先建轻量 schema
- 与当前 `BranchQAResult` 向后兼容

---

## 2.3 修改 `qa_service.py`

### 建议重构方式
把 `answer_question()` 按阶段拆开：

```python
answer_question()
  -> build_query_plan()
  -> retrieve_evidence()
  -> rerank_evidence()
  -> build_answer_context()
  -> generate_answer()
  -> verify_answer()
  -> finalize_result()
```

### 建议新增私有方法
- `_build_query_plan()`
- `_retrieve_evidence()`
- `_rerank_evidence()`
- `_build_answer_context()`
- `_generate_grounded_answer()`
- `_verify_grounding()`

### 为什么这么拆
因为现在 `answer_question()` 已经承担太多职责，继续往里堆会越来越难维护。

---

## 2.4 修改 `retrieval_service.py`

### 目标
从“返回 `RetrievalHit`”逐步升级到“能返回 `EvidenceHit`”。

### 建议策略
不要一次推翻。

#### Step 1
保留原 `search_branch()`，新增：

```python
def search_evidence(
    self,
    branch_id: str,
    query_plan: StructuredQueryPlan,
    *,
    limit: int = 8,
) -> EvidenceBundle:
    ...
```

#### Step 2
把现有 route 包进 `EvidenceHit`。

#### Step 3
新增 graph typed routes。

---

## 2.5 graph typed routes 建议

### 当前问题
`relationship_route()` 太单一，图谱能力没有按问题类型打开。

### 建议新增方法
- `_relation_route()`
- `_world_rule_route()`
- `_foreshadow_route()`
- `_causal_route()`
- `_timeline_route()`

### 每条 route 的职责

#### `_relation_route()`
- 从 query entities 找 relation nodes / relates_to edges
- 返回 `graph_path` 型 evidence

#### `_world_rule_route()`
- 查 `world_rule` nodes
- 找 `constrains` / related events

#### `_foreshadow_route()`
- 查 open foreshadow nodes
- 查 `pays_off_as` path

#### `_causal_route()`
- 查 `causes / enables / triggers / prevents / blocks`
- 返回因果链

#### `_timeline_route()`
- 查 `follows / advances_to / evolves_to / escalates_to`
- 输出阶段链路

---

## 2.6 anti-spoiler 实现建议

### 当前问题
`max_chapter` 在 rerank 后过滤，太晚。

### 建议改法
在这些地方尽早生效：
- SQL route 查询条件
- graph route 章节展开条件
- vector route 候选文档筛选
- evidence merge 前

### 最低要求
任何未来章节不应参与最终 rerank。

---

## 2.7 alias resolution 修复建议

### 当前风险
`EntityResolutionService` 看起来主要依赖 `character` node，而 `graph_service` 更常写 `entity`。

### 建议改法
二选一：

#### 方案 A（推荐）
让 `EntityResolutionService` 支持：
- `node_type in ('entity', 'character')`

#### 方案 B
统一 graph 生产逻辑，引入明确 `character` node。

### 为什么先推荐 A
侵入小，回归风险低，先验证 alias map 是否恢复更实际。

---

## 2.8 rerank 升级建议

### 当前问题
rerank 只看 title + summary + keywords。

### 第一版建议
新增 evidence text builder：

```python
def _evidence_rerank_text(hit: EvidenceHit) -> str:
    ...
```

按 source_type 选择不同模板：
- `chunk`: chunk_text + title
- `fact`: label + evidence_list
- `graph_path`: path + supporting text
- `window`: window summary

### 第二版建议
做 question-aware rerank template。

---

## 2.9 answer builder 建议

### 当前问题
LLM 上下文是大字符串拼接，可控性一般。

### 建议新增
`answer_context_builder.py` 或在 `qa_service.py` 内先收敛为一个 builder 类：

```python
class AnswerContextBuilder:
    def build(
        self,
        query_plan: StructuredQueryPlan,
        evidence_bundle: EvidenceBundle,
    ) -> AnswerContextBundle:
        ...
```

### 职责
- 选 top evidence
- 控制 context budget
- 分类放进 chapter/fact/graph/window/causal/foreshadow
- 输出 answer mode

---

## 3. 推荐测试策略

## 3.1 单元测试
优先覆盖：
- query parse
- anti-spoiler
- graph typed routes
- evidence normalization
- answer mode selection

## 3.2 集成测试
至少要有：
- relation 问题
- timeline 问题
- foreshadow 问题
- anti-spoiler 问题
- alias 问题

## 3.3 回归测试
保留现有 `tests/test_qa_service.py`，再增加新的 V2 test 文件。

---

## 4. 推荐 PR 切法

### PR1
- 修 alias / anti-spoiler / stale API

### PR2
- 加 `StructuredQueryPlan` + query parse service

### PR3
- 加 `EvidenceHit` + retrieval evidence path

### PR4
- graph typed routes

### PR5
- answer context builder + result contract 扩展

### PR6
- evidence-aware rerank

不要一口气全改。

---

## 5. 风险控制

### 风险 1：性能变差
应新增：
- query parse latency
- graph route latency
- rerank latency
- total answer latency

### 风险 2：结果更复杂但不更好
必须绑定 benchmark。

### 风险 3：接口破坏前端
优先做追加字段，不破老接口。

---

## 6. 第一批建议直接实现的函数

如果现在就进入开发，建议优先写这些：

1. `QueryUnderstandingService.build_query_plan`
2. `RetrievalService.search_evidence`
3. `BranchQAService._build_answer_context`
4. `RetrievalService._relation_route / _world_rule_route / _foreshadow_route / _causal_route`

这四块是 V2 主骨架。
