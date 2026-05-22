# QA Upgrade V2

## 目标

本目录用于承接 novel-analyzer 当前问答能力的下一轮系统升级，目标不是只做“回答更像”，而是把问答链路从“可用”推进到“可持续迭代、可评估、可运维、可扩展开发”的状态。

当前系统已经具备：
- 多路召回：`fts / similarity / like / keyword / entity_exact / relationship / vector`
- 召回融合：`RRF`
- 候选重排：`rerank`
- 图谱补充：`graph / foreshadow / causal / window`
- 结果生成：LLM based answer generation
- 基础评估：`retrieval-benchmark`、`search-branch-diagnostics`

但它仍存在几个关键短板：
- query understanding 过于轻量，复杂问题理解不足
- 图谱在 query-time 的利用还偏浅
- rerank 粒度偏粗，证据消费偏弱
- 上游 `key_entities / keyword_list` 数据质量对效果影响过大
- anti-spoiler、防漂移、grounding、API surface 一致性仍需系统治理

因此本升级包聚焦 6 件事：
1. 稳定现有 QA 主链
2. 提升 query understanding
3. 重做 retrieval × graph fusion 的中间层
4. 强化 answer generation 的证据约束
5. 建立可用的数据准备与评估闭环
6. 给后续开发留出清晰 roadmap / checklist / 验收标准

---

## 推荐阅读顺序

1. [`01-current-state-and-gap-analysis.md`](./01-current-state-and-gap-analysis.md)
2. [`02-target-architecture.md`](./02-target-architecture.md)
3. [`03-roadmap.md`](./03-roadmap.md)
4. [`04-delivery-checklist.md`](./04-delivery-checklist.md)
5. [`05-data-preparation.md`](./05-data-preparation.md)
6. [`06-metrics-and-evaluation.md`](./06-metrics-and-evaluation.md)
7. [`07-development-plan.md`](./07-development-plan.md)
8. [`08-schema-and-contracts.md`](./08-schema-and-contracts.md)
9. [`09-implementation-spec.md`](./09-implementation-spec.md)
10. [`10-observability-and-runbook.md`](./10-observability-and-runbook.md)
11. [`11-risk-register-and-backlog.md`](./11-risk-register-and-backlog.md)
12. [`12-phase-delivery-log.md`](./12-phase-delivery-log.md)
13. [`13-llm-runtime-profile.md`](./13-llm-runtime-profile.md)
14. [`14-demo-and-verification.md`](./14-demo-and-verification.md)
15. [`15-audit-and-change-log.md`](./15-audit-and-change-log.md)
16. [`16-query-understanding-techniques-appendix.md`](./16-query-understanding-techniques-appendix.md)

---

## 与现有代码的直接对应

核心实现文件：
- `novel_analyzer/services/qa_service.py`
- `novel_analyzer/services/retrieval_service.py`
- `novel_analyzer/services/graph_service.py`
- `novel_analyzer/services/entity_resolution_service.py`
- `novel_analyzer/services/causal_graph_service.py`
- `novel_analyzer/services/domain_dictionary_service.py`
- `novel_analyzer/services/analysis_service.py`
- `novel_analyzer/services/retrieval_benchmark_service.py`
- `apps/api/app/routers/pipeline.py`

关联文档：
- `docs/architecture/independent-agent-knowledge-and-retrieval.md`
- `docs/foundation-optimization/entity-extraction-noise-diagnosis-20260513.md`
- `docs/foundation-optimization/pg-jieba-userdict-ops.md`
- `docs/interface-manifest.md`
- `docs/loom/handoff.md`

---

## 本目录输出物说明

| 文件 | 用途 |
|---|---|
| `01-current-state-and-gap-analysis.md` | 当前 QA 主链的真实实现、问题清单、优先风险 |
| `02-target-architecture.md` | V2 目标架构与分阶段设计 |
| `03-roadmap.md` | 分期路线图、里程碑、依赖顺序 |
| `04-delivery-checklist.md` | 开发 checklist / 上线前 checklist / 回归 checklist |
| `05-data-preparation.md` | 数据准备、标注、query bank、训练/评测集建议 |
| `06-metrics-and-evaluation.md` | 指标、实验设计、离线/在线验证方法 |
| `07-development-plan.md` | 面向工程开发的落地任务拆解 |
| `08-schema-and-contracts.md` | V2 的中间对象与 API/结果 contract 设计 |
| `09-implementation-spec.md` | 基于现有代码的实现规格与改造建议 |
| `10-observability-and-runbook.md` | 观测面、trace、排障路径、上线观察期 |
| `11-risk-register-and-backlog.md` | 风险清单、任务池、冲刺建议 |
| `12-phase-delivery-log.md` | 阶段交付记录、效果演示与验证命令 |
| `13-llm-runtime-profile.md` | 当前指定 LLM 运行配置与联调建议 |
| `14-demo-and-verification.md` | 当前阶段的效果演示、验证命令与手工 demo 步骤 |
| `15-audit-and-change-log.md` | QA V2 的专项评估、修改、验证与风险审计入口 |
| `16-query-understanding-techniques-appendix.md` | Query understanding 的外部模式、采纳顺序与评估 hooks |

---

## 先做什么

如果现在就要开始开发，建议顺序是：

1. 先做 `P0 稳定化`：修掉 alias / anti-spoiler / stale API / observability 问题
2. 再做 `P1 query understanding`：至少引入 query parse + structured retrieval plan
3. 再做 `P2 retrieval & graph fusion`：把图谱从“补充层”升级为“显式召回维度”
4. 最后做 `P3 answer generation & grounding`

一句话：**先补地基，再卷模型。**

---

## 当前开发进度快照（2026-05-22）

- `P0`：第一批正确性修复已落地，见 [`12-phase-delivery-log.md`](./12-phase-delivery-log.md)
- `P1`：`StructuredQueryPlan` schema 与 `QueryUnderstandingService` 骨架已起步，已有针对性测试
- `P2+`：仍以 contract、eval、observability、handoff、gate 设计为主，尚未完成主链接线

当前最需要补的不是“再加一个 route”，而是：
- query understanding 的技术分层与失败模式
- phase gate / release gate / rollback gate
- badcase 回流到 query bank / regression set 的机制
- 评估、修改、验证、handoff 的持续审计轨
