# 11. 风险清单与任务 Backlog

## 1. 风险登记表

| 风险 | 级别 | 现象 | 影响 | 建议应对 |
|---|---|---|---|---|
| alias source 与 graph node type 错位 | 高 | alias map 常为空 | query understanding 半失效 | P0 优先核查并修复 |
| anti-spoiler 过滤过晚 | 高 | 剧透模式候选无意义丢失 | 用户体验差、可信度下降 | 前置过滤 |
| API surface 漂移 | 中 | router/service/frontend 参数不一致 | 接入成本高，潜在线上 bug | P0 对齐 contract |
| keyword/entity 噪声污染 | 高 | retrieval benchmark / keyword route 失真 | 难以优化、图谱质量下降 | 建健康检查与清洗 |
| rerank 粒度过粗 | 中 | 排序收益有限 | complex query 提升受限 | evidence-aware rerank |
| graph route 只给 chapter score | 中 | 图谱价值发挥不出来 | relation/timeline 问题不稳 | 输出 path evidence |
| 新链路耗时变高 | 高 | p95 latency 升高 | 产品可用性下降 | 做 budget + observability |
| contract 改动破坏现有前端 | 中 | 前端消费失败 | 影响上线节奏 | 采用追加字段策略 |

---

## 2. P0 Backlog（必须先做）

### QA-STAB-001
**标题**：核查 alias resolution 对真实 graph node 是否生效
- 类型：bug / correctness
- 优先级：P0
- 输出：诊断结论 + 修复方案 + regression test

### QA-STAB-002
**标题**：把 anti-spoiler 过滤前置到 retrieval early stage
- 类型：bug / product correctness
- 优先级：P0
- 输出：route-level filter + tests

### QA-STAB-003
**标题**：修复 `/api/search-branch` router/service/frontend contract 漂移
- 类型：bug / integration
- 优先级：P0
- 输出：统一参数和调用方式

### QA-STAB-004
**标题**：补齐 QA request trace 与 diagnostics 导出
- 类型：observability
- 优先级：P0
- 输出：query plan / route / rerank / answer log

### QA-STAB-005
**标题**：新增 keyword/entity/graph 健康检查脚本
- 类型：data quality
- 优先级：P0
- 输出：巡检脚本 + 文档

---

## 3. P1 Backlog（Query Understanding）

### QA-PLAN-001
定义 `StructuredQueryPlan` schema

### QA-PLAN-002
实现 `QueryUnderstandingService`

### QA-PLAN-003
抽取章节范围 / anti-spoiler 约束

### QA-PLAN-004
抽取实体 / 关系 / 规则 / 因果意图

### QA-PLAN-005
query parse diagnostics 导出

### QA-PLAN-006
建立 parser regression buckets（alias / timeline / relation / world_rule / foreshadow / ambiguity / parse failure）

### QA-PLAN-007
建立 parser badcase → regression bucket 回流流程

---

## 4. P2 Backlog（Retrieval & Graph Fusion）

### QA-RET-001
定义 `EvidenceHit` schema

### QA-RET-002
新增 `search_evidence()` service 接口

### QA-RET-003
graph typed routes：relation / world_rule / foreshadow / causal

### QA-RET-004
fact lane 扩到 continuity / relation / conflict / world_rule

### QA-RET-005
window / timeline lane 明确化

---

## 5. P3 Backlog（Rerank）

### QA-RR-001
evidence-aware rerank text builder

### QA-RR-002
question-aware rerank policy

### QA-RR-003
rerank benchmark & latency budget

---

## 6. P4 Backlog（Answer & Grounding）

### QA-ANS-001
定义 `AnswerContextBundle`

### QA-ANS-002
answer builder v2

### QA-ANS-003
answer mode 分层

### QA-ANS-004
claim-evidence mapping 输出

### QA-ANS-005
grounding summary contract

---

## 7. P5 Backlog（Data & Eval）

### QA-DATA-001
建立 Query Bank V2

### QA-DATA-002
建立 difficult query set

### QA-DATA-003
建立 alias gold set

### QA-DATA-004
建立 relation / timeline / foreshadow gold set

### QA-DATA-005
建立 QA eval report contract

### QA-DATA-006
建立 `data/qa_eval/` 目录 contract 与 jsonl 样本规范

### QA-DATA-007
建立 badcase backlog 样本格式与状态流转字段

---

## 8. 推荐看板顺序

### 当前冲刺建议只放：
- QA-STAB-001
- QA-STAB-002
- QA-STAB-003
- QA-PLAN-001
- QA-PLAN-002

### Query Understanding 继续演进时，下一批优先放：
- QA-PLAN-006
- QA-PLAN-007
- QA-DATA-006

### 下一冲刺再放：
- QA-RET-001
- QA-RET-003
- QA-ANS-001

不要一次把 backlog 全开。

---

## 9. 任务验收模板

每个任务建议统一按以下模板验收：

### 目标
这项任务解决什么问题？

### 变更点
改了哪些文件 / 哪些 contract？

### 验证
- 单测
- 集成测试
- 手工样例
- diagnostics 截图/JSON

### 风险
- 性能风险
- 回归风险
- 接口风险

### 下一步
这项任务完成后应该衔接什么？

---

## 10. 结论

这个 backlog 的核心思想是：

> 先做“修正系统认知和 contract”的任务，再做“增强模型和排序”的任务。

这样后面开发才不会一直返工。
