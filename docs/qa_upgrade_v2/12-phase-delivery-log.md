# 12. 阶段交付记录

## 目标

本文件用于把 QA Upgrade V2 的推进过程显式记录为“阶段交付”，避免后续开发只有 roadmap，没有实际落地边界。

从本轮开始，阶段记录不再只写“做了什么”，还要补齐：
- 评估结论
- 审计入口
- deferred risks
- 下一棒接力建议

---

## Phase A — 文档与架构包（已完成）

### 交付目标
把当前 QA 系统从“代码里有一些能力”整理成“可以指导开发的升级包”。

### 已交付内容
- `01-current-state-and-gap-analysis.md`
- `02-target-architecture.md`
- `03-roadmap.md`
- `04-delivery-checklist.md`
- `05-data-preparation.md`
- `06-metrics-and-evaluation.md`
- `07-development-plan.md`
- `08-schema-and-contracts.md`
- `09-implementation-spec.md`
- `10-observability-and-runbook.md`
- `11-risk-register-and-backlog.md`

### 阶段价值
这一阶段解决的是“认知与执行面”的问题：
- 现状是什么
- 缺什么
- 该先做什么
- 中间 contract 应该怎么立
- 以后如何验证是否真的变好

### 阶段验收
- 文档目录完整
- README 已串联全目录
- 相对链接自检通过

---

## Phase B — P0 稳定化第一批修复（本轮已落地）

### 交付目标
先修 3 个最影响 QA 正确性的低风险问题。

### 已落地代码改动

#### B1. Entity resolution 支持 `entity` 节点
变更文件：
- `novel_analyzer/services/entity_resolution_service.py`

改动摘要：
- 原逻辑只看 `GraphNode.node_type == 'character'`
- 现已改为兼容 `('entity', 'character')`

解决的问题：
- 与 `GraphService` 实际产出的 `entity` 节点对齐
- 恢复 alias map 的真实可用性

---

#### B2. anti-spoiler 过滤前移到 rerank 前
变更文件：
- `novel_analyzer/services/retrieval_service.py`

改动摘要：
- 原逻辑：raw retrieval → rerank → max_chapter filter
- 新逻辑：raw retrieval → `max_chapter` filter → rerank

解决的问题：
- 避免未来章节参与 rerank
- 降低防剧透模式下“高分候选都被过滤掉”的失真风险

> 注：这是 P0 的安全版修正。更彻底的 route-level filter / candidate backfill 仍在后续阶段。
> 本轮已经包含 **pre-rerank 过滤 + 一次有限扩候选回补**；后续阶段要做的是更彻底的 route-level filter / deeper candidate planning。

---

#### B3. `/api/search-branch` contract 对齐
变更文件：
- `apps/api/app/routers/pipeline.py`
- `apps/web/src/lib/risk-api.ts`

改动摘要：
- API 兼容 `q` 和 `query` 两种参数
- router 改为调用 `RetrievalService.search_branch()`
- 返回 hit 结构增加 `title / summary_text / keyword_list`
- 保留 `chunk_text` 兼容旧消费方
- `risk-api` 改为使用 `q`

解决的问题：
- 修复 service 方法名漂移
- 提高接口兼容性
- 缓解前后端 query param 漂移

---

## Phase B 验收方式

### 新增/变更测试
- `tests/test_entity_resolution_service.py`
- `tests/test_retrieval_service.py`（新增 anti-spoiler pre-rerank 测试）
- `tests/test_api_main.py`（新增 search-branch 参数兼容与返回结构测试）

### 推荐验证命令

```bash
.venv/bin/pytest \
  tests/test_entity_resolution_service.py \
  tests/test_retrieval_service.py::test_search_branch_filters_future_hits_before_rerank \
  tests/test_api_main.py::test_search_branch_endpoint_accepts_q_and_returns_retrieval_hit_shape \
  tests/test_api_main.py::test_search_branch_endpoint_accepts_legacy_query_alias \
  -q
```

### 预期效果演示

#### Demo 1：Alias 生效
输入问题包含别名，如“卫图少年为什么……”
- 以前：可能查不到 canonical
- 现在：可映射回 `卫图`

#### Demo 2：防剧透更保守
带 `max_chapter=2` 时：
- 以前：未来章节可能先参与 rerank，再被丢掉
- 现在：未来章节不再进入 rerank；如果过滤后候选不足，会做一次有限扩候选回补

#### Demo 3：search API 兼容性提升
- `/api/search-branch?...&q=卫图`
- `/api/search-branch?...&query=卫图`

两种都能返回结果。

---

## Phase C — 下一阶段建议（紧接着做）

### C1. Structured Query Plan
目标：
- 让问题先被结构化理解

### C2. EvidenceHit Contract
目标：
- 让检索结果从 chapter hit 升级为统一 evidence object

### C3. graph typed routes
目标：
- relation / world_rule / foreshadow / causal 分路显式化

---

## Phase C1 — Query Understanding 骨架（本轮已起步）

### 已落地内容
- `novel_analyzer/domain/schemas.py`
  - 新增 `PlannedEntity`
  - 新增 `QueryTimeScope`
  - 新增 `QueryConstraints`
  - 新增 `RetrievalPreferences`
  - 新增 `StructuredQueryPlan`
- `novel_analyzer/services/query_understanding_service.py`
  - 新增规则版 `QueryUnderstandingService`
  - 支持 question type 分类
  - 支持基础时间范围抽取（`前20章` / `第3章到第8章` / `第12章`）
  - 支持 branch 内实体/别名命中与 canonical 化
  - 支持 retrieval preference 初步规划
- `tests/test_query_understanding_service.py`
  - 覆盖 timeline query plan
  - 覆盖 alias → canonical 解析

### 这一阶段的定位
这不是最终版 query understanding，而是先把 **中间 contract 和 service 骨架** 立住。  
后续可以继续：
- 接 LLM parse
- 扩展 relation/world_rule/event 抽取
- 与 `qa_service` 真正接线

### 当前验证

```bash
.venv/bin/pytest -q tests/test_query_understanding_service.py
```

### 当前结果
- `2 passed`

---

## 当前状态总结

### 已完成
- 文档升级包
- P0 第一批正确性修复
- 基础演示与验证命令
- Query understanding V2 骨架与 schema 起步

### 正在进入
- Query understanding V2 接入主链
- Evidence contract

### 还未完成
- route-level anti-spoiler backfill
- graph-aware rerank
- grounded answer contract
- QA eval dataset 首版

---

## Phase D — 文档深化与审计治理（本轮已落地）

### 交付目标
把 QA Upgrade V2 从“有设计主线”推进到“可审计、可交接、可 gate 的执行文档包”。

### 已落地内容
- 补 current progress snapshot，明确 `P0/P1/P2+` 状态
- 补 Query Understanding 技术路线：baseline / advanced / frontier
- 补 phase gate / release gate / rollback gate
- 补 checklist 的审计通用项与证据要求
- 新增专项 audit 文件：`15-audit-and-change-log.md`
- 新增专项 handoff（见 handoff 目录）
- 根 `CHANGELOG.md` 追加 QA V2 文档治理记录

### 阶段价值
这一阶段解决的不是“功能缺失”，而是“治理缺失”：
- 下一棒如何知道当前做到了哪一步
- 哪些能力是设计完成，哪些能力是真接上主链了
- 哪些结论有验证支撑，哪些仍只是方向判断

### 阶段验收
- roadmap 能反映当前已落地进度，而不是只写理想顺序
- checklist 能支撑审计，不再只是功能核对表
- 至少有一份专项 audit 记录和一份专项 handoff 可供接手

### 风险与未完成项
- Oracle 评审任务未返回有效文字结论，因此本阶段未把“Oracle 观点”写成事实依据
- 外部研究结果未单独沉淀为研究附录，后续可视需要补 `research note`

---

## Phase E — reusable RAG core 代码抽离起步（持续推进中）

### 交付目标
从 QA V2 的架构设计推进到真实代码落点，但坚持“先 contracts / mechanics，后 adapter-heavy orchestration”。

### 已落地内容
- `rag_core/` 最小包骨架已创建
- shared contracts 已进入 `rag_core`：
  - `RetrievalHit`
  - `RetrievalRouteDiagnostics`
  - `RetrievalSearchDiagnostics`
  - `PlannedEntity`
  - `QueryTimeScope`
  - `QueryConstraints`
  - `RetrievalPreferences`
  - `StructuredQueryPlan`
- shared mechanics 已进入 `rag_core`：
  - `reciprocal_rank_fuse`
  - `apply_rerank_scores`
- 现有服务已开始双栖复用：
  - `RetrievalService` 复用 `RetrievalHit`
  - `RetrievalService` 复用 diagnostics contracts
  - `RetrievalService` 复用 RRF helper
  - `RetrievalService` 复用 rerank helper
  - `novel_analyzer.domain.schemas` 复用 query-planning contract 组

### 阶段价值
这一阶段的价值不在“已经完成核心拆包”，而在于：
- 可复用 core 已有真实代码落点
- contract 不再继续分叉
- mechanics 开始脱离 `novel_analyzer` 局部实现，证明抽离方向可行

### 当前边界
- graph 仍保持 optional capability，尚未迁移
- `BranchQAService` orchestration 仍留在 novel adapter 层
- route SQL / provider wiring / query taxonomy 仍未迁移
