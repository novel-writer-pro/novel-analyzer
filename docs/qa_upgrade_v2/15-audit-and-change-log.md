# 15. Audit 与 Change Log

## 1. 目标

本文件用于把 QA Upgrade V2 的评估、修改、验证、风险接受统一沉淀成**可追溯审计轨**。

它不是替代根 [CHANGELOG](file:///home/user/novel-analyzer/CHANGELOG.md)，而是补齐 QA V2 专项开发最需要的四类记录：

1. 评估记录：这次为什么改
2. 修改记录：具体改了哪些文档/contract
3. 验证记录：如何证明没有空转
4. 风险记录：哪些问题被延后、为什么延后

---

## 2. 审计原则

### 2.1 任何“结论”都要能回溯到证据
- 文档评估要指向具体文件
- 进度判断要指向实际已落地的 schema / service / test
- 后续建议要注明优先级与前置条件

### 2.2 任何“修改”都要回答 4 个问题
1. 为什么现在改？
2. 改了什么？
3. 怎么验证？
4. 还没解决什么？

### 2.3 任何“未完成项”都不能只写 TODO
必须写清：
- 当前状态
- 阻塞原因
- 下一步建议
- 推荐接手入口

---

## 3. 统一审计模板

后续每次评估/修改建议都按下面模板追加：

```markdown
## Audit Entry — YYYY-MM-DD HH:MM（主题）

### Trigger
- 这次为什么要评估/修改

### Inputs Reviewed
- 文档：...
- 代码/测试：...
- 外部参考：...

### Findings
- 发现 1
- 发现 2

### Decisions
- 决策 1
- 决策 2

### Files Changed
- path/to/file.md — 为什么改

### Verification
- 命令 / 人工检查 / 诊断证据

### Deferred Risks
- 暂不处理的项与原因

### Next Owner Notes
- 下一棒优先做什么
```

---

## 4. 审计条目

## Audit Entry — 2026-05-22 继续推进（QA Upgrade V2 文档深化与治理）

### Trigger
- 用户要求系统审阅 `docs/qa_upgrade_v2`，提升 QA 升级方案
- 用户明确要求：扩展 query understanding 技术路线，跟进开发进度，完善 roadmap / handoff / checklist / changelog，并对每次评估与修改做充分记录和审计

### Inputs Reviewed
- 文档主包：
  - [README](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/README.md)
  - [01-current-state-and-gap-analysis.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/01-current-state-and-gap-analysis.md)
  - [02-target-architecture.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/02-target-architecture.md)
  - [03-roadmap.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/03-roadmap.md)
  - [04-delivery-checklist.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/04-delivery-checklist.md)
  - [05-data-preparation.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/05-data-preparation.md)
  - [06-metrics-and-evaluation.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/06-metrics-and-evaluation.md)
  - [07-development-plan.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/07-development-plan.md)
  - [08-schema-and-contracts.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/08-schema-and-contracts.md)
  - [09-implementation-spec.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/09-implementation-spec.md)
  - [10-observability-and-runbook.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/10-observability-and-runbook.md)
  - [11-risk-register-and-backlog.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/11-risk-register-and-backlog.md)
  - [12-phase-delivery-log.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/12-phase-delivery-log.md)
  - [14-demo-and-verification.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/14-demo-and-verification.md)
- 项目交接与变更基线：
  - [docs/handoffs/README.md](file:///home/user/novel-analyzer/docs/handoffs/README.md)
  - [CHANGELOG.md](file:///home/user/novel-analyzer/CHANGELOG.md)
- 代码/测试进度证据：
  - `tests/test_query_understanding_service.py`
  - `tests/test_entity_resolution_service.py`
- 外部模式线索：检索到 query-understanding / QueryPlan / routing / query processor 相关开源实现，用于确认“结构化 query plan + route-aware retrieval”是行业常见演进路径

### Findings
- 文档包已有完整架构主线，但 query understanding 仍偏“对象定义”而不是“技术路线 + 失败模式 + 评估闭环”
- roadmap 已写阶段顺序，但缺少 phase gate / release gate / rollback gate
- checklist 已写交付项，但缺少“证据要求 / 审计要求 / badcase 回流要求”
- delivery log 能记录阶段落地，但缺少统一审计模板，难以支撑下一棒直接接手
- changelog 已较长且局部重复，新增 QA 记录时必须更结构化，避免继续堆叠噪音

### Decisions
- 新增 QA V2 专项 audit 文件，作为后续评估、修改、验证、风险接受的统一入口
- 强化 roadmap，显式补 query understanding 的 baseline / advanced / frontier 分层与 gate
- 强化 checklist，使其不只是开发核对表，而是上线与回归的审计清单
- 新增专项 handoff，单独承接 QA V2 当前状态、下一步与验证入口
- 在根 changelog 增加一条高质量文档治理记录，而不是把细节散落到多个地方

### Files Changed
- [README.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/README.md) — 补当前进度快照与审计入口
- [03-roadmap.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/03-roadmap.md) — 补阶段状态、query understanding 分层、gate
- [04-delivery-checklist.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/04-delivery-checklist.md) — 补审计通用项与证据要求
- [06-metrics-and-evaluation.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/06-metrics-and-evaluation.md) — 补 gate 设计
- [12-phase-delivery-log.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/12-phase-delivery-log.md) — 记录本轮文档治理阶段
- [15-audit-and-change-log.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/15-audit-and-change-log.md) — 新建专项审计轨
- [qa-upgrade-v2-handoff-20260522.md](file:///home/user/novel-analyzer/docs/handoffs/qa-upgrade-v2-handoff-20260522.md) — 新建专项交接

### Verification
- 文档内容与当前已有 Phase B / C1 进度交叉比对
- 所有新增判断均基于已读文档和测试文件，不依赖未读代码猜测

### Deferred Risks
- Oracle 评审任务未返回有效文字结果，因此本轮不把“Oracle 建议”写成事实结论
- 外部研究结果未单独入库为参考附录，本轮仅将其作为设计方向校正，不扩成单独研究报告

### Next Owner Notes
- 下一棒优先继续把 roadmap / checklist / handoff / changelog 的治理补齐
- 每次新增阶段性结论时，都应继续往本文件追加 audit entry，而不是覆盖历史

---

## Audit Entry — 2026-05-22 继续推进（Query Understanding 覆盖面校准）

### Trigger
- 用户要求继续推进和演进 QA V2
- 上一轮文档治理完成后，需要进一步把“已实现 vs 设计中”的边界写实，避免 roadmap 高估 query understanding 完成度

### Inputs Reviewed
- [tests/test_query_understanding_service.py](file:///home/user/novel-analyzer/tests/test_query_understanding_service.py)
- [07-development-plan.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/07-development-plan.md)
- [08-schema-and-contracts.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/08-schema-and-contracts.md)
- [09-implementation-spec.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/09-implementation-spec.md)

### Findings
- 当前自动化测试只明确覆盖了 timeline/time_scope/anti-spoiler、alias→canonical、局部 retrieval preference
- 仍未覆盖 ambiguity、parse failure taxonomy、relation/world_rule/foreshadow 抽取、diagnostics 导出、主链接线一致性
- 因此“P1 已起步”成立，但“P1 接近稳定”不成立

### Decisions
- 在开发计划中增加“当前覆盖真相”矩阵
- 在测试建议中明确最小下一批 regression buckets
- 后续所有 query understanding 进度判断，都以测试桶而不是口头表述为准

### Files Changed
- [07-development-plan.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/07-development-plan.md) — 增加测试覆盖真相、缺口与最小补测顺序
- [15-audit-and-change-log.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/15-audit-and-change-log.md) — 记录本轮覆盖面校准

### Verification
- 逐行比对现有测试内容与 roadmap / development plan 中对 P1 的要求
- 仅记录已读文件能证明的覆盖项，不推断未见代码行为

### Deferred Risks
- relation / world_rule / foreshadow 可能在实现中已有部分逻辑，但在当前已读测试面中未被证明，故本轮仍按“未覆盖”处理

### Next Owner Notes
- 继续扩 query-understanding regression surface 时，优先补“意图/失败模式/边界条件”，再补更多 happy-path 样例

---

## Audit Entry — 2026-05-22 继续推进（Query Understanding 技术附录落地）

### Trigger
- 在完成覆盖面校准后，需要把 query understanding 的外部模式收敛成可供仓库持续使用的 appendix，避免后续讨论反复停留在口头层

### Inputs Reviewed
- [README.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/README.md)
- [03-roadmap.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/03-roadmap.md)
- [07-development-plan.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/07-development-plan.md)
- 当前会话已收集到的外部模式线索（如 QueryPlan / QueryProcessor / pre-retrieval query understanding 结构）

### Findings
- 当前主文档已定义 `StructuredQueryPlan`，但缺一个单独说明“为什么这样分层、什么该现在做、什么不该现在做”的技术附录
- 如果没有附录，后续很容易再次跳到“先上更重 planner / 更强 parser”而忽略 regression 和 observability 地基

### Decisions
- 新增 Query Understanding appendix
- 用 baseline / advanced / frontier + evaluation hooks + do-not-do-now 组织内容
- 只写适配 novel-analyzer 当前阶段的采纳顺序，不把附录写成泛泛研究综述

### Files Changed
- [16-query-understanding-techniques-appendix.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/16-query-understanding-techniques-appendix.md) — 新增技术附录
- [README.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/README.md) — 加入附录索引
- [03-roadmap.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/03-roadmap.md) — 连接技术路线与附录

### Verification
- 附录内容与当前 repo 的 `StructuredQueryPlan` / roadmap / development plan 用词保持一致
- 不把外部模式直接当作“本项目已实现能力”写入

### Deferred Risks
- 外部模式仍未沉淀成独立 research note；如果未来需要更强引用链，可再拆单独研究文档

### Next Owner Notes
- 后续如果引入 rewrite / decomposition / planner，先回看本附录的采纳顺序，再决定是否推进

---

## Audit Entry — 2026-05-22 继续推进（Regression buckets 与 qa_eval 目录 contract）

### Trigger
- 用户继续要求推进和演进
- 在补完覆盖真相与技术附录后，下一步最该固化的是 regression buckets 与 qa_eval 数据目录 contract，否则“下一步怎么补测试/数据”仍然停留在口头建议

### Inputs Reviewed
- [05-data-preparation.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/05-data-preparation.md)
- [07-development-plan.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/07-development-plan.md)
- [11-risk-register-and-backlog.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/11-risk-register-and-backlog.md)

### Findings
- 当前文档已知道需要 query bank / difficult set / gold set，但还没有把 parser_regression / badcase_backlog 写成显式目录 contract
- 如果不把 regression bucket 名称与数据桶名称固定下来，后续测试和数据很容易各说各话

### Decisions
- 在数据准备文档中显式加入 `data/qa_eval/` 推荐层级
- 为 `parser_regression/`、`difficult_queries/`、`badcase_backlog/` 补样本字段 contract
- 在开发计划和 backlog 中同步把 regression buckets 升级为明确任务

### Files Changed
- [05-data-preparation.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/05-data-preparation.md) — 增加 `data/qa_eval/` 目录与 jsonl contract
- [07-development-plan.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/07-development-plan.md) — 增加 regression buckets 与数据桶联动要求
- [11-risk-register-and-backlog.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/11-risk-register-and-backlog.md) — 把 regression/data contract 升级为显式 backlog 项

### Verification
- regression bucket 命名与当前开发计划中的 PR2 当前缺口保持一致
- 数据目录设计与当前 query bank / difficult set / gold set 的既有文档方向保持兼容

### Deferred Risks
- 本轮只定义 contract，不创建真实 `data/qa_eval/` 样本文件，避免凭空制造伪数据

### Next Owner Notes
- 如果下一步开始补真实样本，优先从 alias、timeline、ambiguity、world_rule 这四桶落首批 jsonl

---

## Audit Entry — 2026-05-22 继续推进（qa_eval 目录骨架落库）

### Trigger
- 前一轮已经定义了 `data/qa_eval/` contract，但目录还不存在
- 用户继续要求持续优化，因此需要把 contract 进一步变成真实仓库骨架，降低下一棒落样本的摩擦成本

### Inputs Reviewed
- [05-data-preparation.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/05-data-preparation.md)
- [07-development-plan.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/07-development-plan.md)

### Findings
- 只有文档 contract、没有真实目录时，后续接手人仍要先自行建立结构，容易再次偏离命名和分层
- 但如果现在直接创建空 `jsonl` 样本文件，会制造没有来源保证的伪资产

### Decisions
- 创建真实 `data/qa_eval/` 目录骨架
- 每个子目录只放 `README.md` contract，不放占位样本
- 让 README contract 成为未来填入真实数据的唯一入口说明

### Files Changed
- [data/qa_eval/README.md](file:///home/user/novel-analyzer/data/qa_eval/README.md)
- [data/qa_eval/query_bank_v2/README.md](file:///home/user/novel-analyzer/data/qa_eval/query_bank_v2/README.md)
- [data/qa_eval/difficult_queries/README.md](file:///home/user/novel-analyzer/data/qa_eval/difficult_queries/README.md)
- [data/qa_eval/alias_gold/README.md](file:///home/user/novel-analyzer/data/qa_eval/alias_gold/README.md)
- [data/qa_eval/relation_gold/README.md](file:///home/user/novel-analyzer/data/qa_eval/relation_gold/README.md)
- [data/qa_eval/timeline_gold/README.md](file:///home/user/novel-analyzer/data/qa_eval/timeline_gold/README.md)
- [data/qa_eval/parser_regression/README.md](file:///home/user/novel-analyzer/data/qa_eval/parser_regression/README.md)
- [data/qa_eval/answer_eval/README.md](file:///home/user/novel-analyzer/data/qa_eval/answer_eval/README.md)
- [data/qa_eval/badcase_backlog/README.md](file:///home/user/novel-analyzer/data/qa_eval/badcase_backlog/README.md)
- [05-data-preparation.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/05-data-preparation.md)

### Verification
- 目录命名与上一轮文档 contract 一致
- 未创建伪造样本文件，只创建 README contract

### Deferred Risks
- 真实样本仍未入库；这一步只降低未来样本落地摩擦，不替代真实数据准备

### Next Owner Notes
- 下一步若开始填样本，优先从 `parser_regression/` 和 `badcase_backlog/` 开始，而不是先追求 query_bank 全量化

---

## Audit Entry — 2026-05-22 继续推进（Parser / qa_eval SOP 落地）

### Trigger
- `qa_eval` 目录骨架已经落库，但仍缺少“怎么新增样本、怎么审核、怎么回流、怎么 replay”的操作说明
- 用户继续要求持续优化，因此需要把这套骨架推进成可执行 SOP，而不只是静态目录说明

### Inputs Reviewed
- [data/qa_eval/README.md](file:///home/user/novel-analyzer/data/qa_eval/README.md)
- [data/qa_eval/parser_regression/README.md](file:///home/user/novel-analyzer/data/qa_eval/parser_regression/README.md)
- [05-data-preparation.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/05-data-preparation.md)
- [07-development-plan.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/07-development-plan.md)

### Findings
- 目录和 contract 已经存在，但缺操作层指导时，后续贡献者仍可能不知道：
  - 什么时候新增 regression case
  - 什么时候只记 badcase 不进 regression
  - 什么时候样本必须同步进入自动化测试

### Decisions
- 新增 parser regression playbook
- 新增 qa_eval runbook
- 让 SOP 和现有目录 contract、开发计划、handoff 一起工作，而不是各自独立

### Files Changed
- [17-parser-regression-playbook.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/17-parser-regression-playbook.md)
- [18-qa-eval-runbook.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/18-qa-eval-runbook.md)
- [README.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/README.md)

### Verification
- SOP 内容与现有 bucket 命名、qa_eval 目录、audit 逻辑保持一致
- 不扩展为新的产品需求，仅补执行层指导

### Deferred Risks
- 当前仍未引入真实样本；SOP 只能降低未来样本接入成本，不能替代真实数据建设

### Next Owner Notes
- 当首批真实样本入库时，优先使用本 SOP 检查 bucket、来源、expected 行为、回流路径是否一致

---

## Audit Entry — 2026-05-22 继续推进（Reusable RAG Core / Optional Graph 方案）

### Trigger
- 用户希望继续优化 QA，并进一步判断是否能解耦出可复用的核心 RAG 体系，供其他领域知识问答复用
- 用户新增约束：graph 很重，应该可以启动或不启动

### Inputs Reviewed
- [docs/architecture/independent-agent-knowledge-and-retrieval.md](file:///home/user/novel-analyzer/docs/architecture/independent-agent-knowledge-and-retrieval.md)
- [docs/architecture/novel-assistant-system-architecture.md](file:///home/user/novel-analyzer/docs/architecture/novel-assistant-system-architecture.md)
- [docs/qa_upgrade_v2/02-target-architecture.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/02-target-architecture.md)
- [docs/qa_upgrade_v2/03-roadmap.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/03-roadmap.md)
- [docs/qa_upgrade_v2/08-schema-and-contracts.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/08-schema-and-contracts.md)
- [docs/qa_upgrade_v2/09-implementation-spec.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/09-implementation-spec.md)
- [novel_analyzer/services/qa_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/qa_service.py)
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [novel_analyzer/services/query_understanding_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/query_understanding_service.py)
- Oracle 架构评估：建议先抽 hybrid retrieval + query-plan + rerank/fusion，再把 graph 留在 adapter/capability 层

### Findings
- `RetrievalService` 已经具备较强的 reusable-core 候选形态：多路召回、RRF、rerank、diagnostics、anti-spoiler 前置过滤
- `QueryUnderstandingService` 的结构化 contract 也可复用，但其 taxonomy 仍有小说 domain bias
- `BranchQAService` 当前把窗口/伏笔/因果/世界规则/回答 orchestration 混在一起，是主要耦合点
- graph 若被视为必选核心层，会显著抬高复用门槛

### Decisions
- 定义一个默认不依赖 graph 的 reusable RAG core
- 把 graph 降为 optional capability，而不是 core 必选项
- 把 novel-specific 语义（chapter/spoiler/foreshadow/world_rule/causal answer shaping）留在 adapter 层

### Files Changed
- [docs/architecture/independent-agent-knowledge-and-retrieval.md](file:///home/user/novel-analyzer/docs/architecture/independent-agent-knowledge-and-retrieval.md)
- [docs/qa_upgrade_v2/02-target-architecture.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/02-target-architecture.md)
- [docs/qa_upgrade_v2/03-roadmap.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/03-roadmap.md)
- [docs/qa_upgrade_v2/08-schema-and-contracts.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/08-schema-and-contracts.md)
- [docs/qa_upgrade_v2/09-implementation-spec.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/09-implementation-spec.md)

### Verification
- 方案与当前代码边界一致：core 候选、optional graph、adapter 语义不再混说
- “graph 可关闭”已正式写入设计，而不是只停留在聊天约定

### Deferred Risks
- 当前仍是架构/文档层演进，尚未开始代码抽离；后续需要结合实际耦合映射决定 PR 顺序

### Next Owner Notes
- 真正开始代码抽离时，优先顺序应是：contract → retrieval core → adapters → optional graph capability

---

## Audit Entry — 2026-05-22 继续推进（rag_core 首步代码抽离）

### Trigger
- 架构方向已经明确为 reusable core + optional graph + novel adapter
- 用户要求继续开发，不停在纯文档层
- 为避免过早误拆 novel-specific 逻辑，先从 shared contracts 和 adapter protocols 的最小代码骨架开始

### Inputs Reviewed
- [docs/architecture/independent-agent-knowledge-and-retrieval.md](file:///home/user/novel-analyzer/docs/architecture/independent-agent-knowledge-and-retrieval.md)
- [docs/qa_upgrade_v2/08-schema-and-contracts.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/08-schema-and-contracts.md)
- [docs/qa_upgrade_v2/09-implementation-spec.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/09-implementation-spec.md)
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [novel_analyzer/domain/schemas.py](file:///home/user/novel-analyzer/novel_analyzer/domain/schemas.py)

### Findings
- 当前最安全的第一步不是移动 `BranchQAService` 或 graph 逻辑，而是先引入一个可导入的 `rag_core` 包骨架
- 这一步只要承接 shared contracts 和 protocol 边界，就能为后续抽离留出稳定落点，同时不破坏现有 novel 代码路径

### Decisions
- 先新增 `rag_core` 包
- 只包含：shared contract + `CorpusAdapter` / `GraphAdapter` protocol
- 不在这一步移动现有 `novel_analyzer` 服务实现
- 使用 TDD：先让 `rag_core` 导入测试失败，再补最小实现

### Files Changed
- [rag_core/__init__.py](file:///home/user/novel-analyzer/rag_core/__init__.py)
- [rag_core/contracts.py](file:///home/user/novel-analyzer/rag_core/contracts.py)
- [rag_core/protocols.py](file:///home/user/novel-analyzer/rag_core/protocols.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Verification
- RED：`.venv/bin/python -m pytest tests/test_rag_core_contracts.py -q` 先因 `ModuleNotFoundError: No module named 'rag_core'` 失败
- GREEN：同一测试在补完最小实现后通过（`3 passed`）
- Manual QA：通过 `.venv/bin/python` 直接导入 `rag_core`，实例化 contract 并打印输出成功

### Deferred Risks
- 这一步尚未实现真正的 retrieval core 迁移，只是给后续迁移创造落点

### Next Owner Notes
- 下一步应优先考虑让 `RetrievalHit` / query-plan contract 在现有服务中逐步双栖，再决定是否迁移 `RetrievalService` 的纯核心部分

---

## Audit Entry — 2026-05-22 继续推进（RetrievalHit 双栖共享 contract）

### Trigger
- `rag_core` 最小骨架已经落库，需要验证现有服务是否能逐步改用 shared contract，而不是保留平行的第二套类型定义

### Inputs Reviewed
- [rag_core/contracts.py](file:///home/user/novel-analyzer/rag_core/contracts.py)
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Findings
- `RetrievalService` 原本仍保留自己的 `RetrievalHit` dataclass，会让 core 与现有服务继续平行演化
- 这是最适合先做 contract 双栖验证的一步，因为它只影响类型绑定，不影响 route、SQL、graph 或 rerank 行为

### Decisions
- 让 `novel_analyzer.services.retrieval_service.RetrievalHit` 直接复用 `rag_core.RetrievalHit`
- 用 TDD 锁定“两个 import 实际引用同一个类对象”

### Files Changed
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Verification
- RED：`test_retrieval_service_reuses_rag_core_hit_contract` 先因类型不相同失败
- GREEN：同一测试在切换为 shared contract 后通过（`4 passed`）
- Manual QA：直接导入并打印 `same_object=True`

### Deferred Risks
- 这一步仍只覆盖 `RetrievalHit`，尚未开始双栖 `StructuredQueryPlan` 或其他 contract

### Next Owner Notes
- 下一步可优先评估 `StructuredQueryPlan` 是否也适合类似双栖，再考虑提炼 `RetrievalSearchDiagnostics` 或纯 fusion/rerank 核心

---

## Audit Entry — 2026-05-22 继续推进（Retrieval diagnostics contract 双栖）

### Trigger
- `RetrievalHit` 已经双栖共享到 `rag_core`
- 下一步最稳妥的延伸是让 retrieval diagnostics 也进入 shared core，而不提前移动 retrieval mechanics

### Inputs Reviewed
- [rag_core/contracts.py](file:///home/user/novel-analyzer/rag_core/contracts.py)
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Findings
- `RetrievalRouteDiagnostics` / `RetrievalSearchDiagnostics` 与 `RetrievalHit` 一样，本质是纯 contract，不携带 graph 或 novel 语义
- 如果继续留在 `retrieval_service.py` 本地定义，会拖慢后续把 pure retrieval core 往 `rag_core` 迁移的节奏

### Decisions
- 把两个 diagnostics contract 提升到 `rag_core.contracts`
- 让 `RetrievalService` 直接复用 shared diagnostics types
- 继续维持 contract-first、小步迁移策略

### Files Changed
- [rag_core/contracts.py](file:///home/user/novel-analyzer/rag_core/contracts.py)
- [rag_core/__init__.py](file:///home/user/novel-analyzer/rag_core/__init__.py)
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Verification
- RED：`rag_core` 先无法导出 diagnostics contract，测试失败
- GREEN：同一测试在提升 contract 后通过（`6 passed`）
- Manual QA：直接导入并打印 `route_same_object=True`、`search_same_object=True`

### Deferred Risks
- 仍未开始迁移 `_apply_rerank`、RRF、route 逻辑本体；这一拍只处理 contract

### Next Owner Notes
- 下一步若继续抽代码，优先考虑纯函数/纯 mechanics（例如 fusion 或 rerank 逻辑），而不是先碰 novel adapter orchestration

---

## Audit Entry — 2026-05-22 继续推进（Query-planning contract 双栖）

### Trigger
- `RetrievalHit` 和 retrieval diagnostics contract 已进入 `rag_core`
- 下一步若继续让 core contract 变完整，最合适的是把 query-planning contract 也统一，而不是保留 `novel_analyzer.domain.schemas` 的平行定义

### Inputs Reviewed
- [rag_core/contracts.py](file:///home/user/novel-analyzer/rag_core/contracts.py)
- [novel_analyzer/domain/schemas.py](file:///home/user/novel-analyzer/novel_analyzer/domain/schemas.py)
- [novel_analyzer/services/query_understanding_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/query_understanding_service.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Findings
- `StructuredQueryPlan` 不能只迁一半；它与 `PlannedEntity / QueryTimeScope / QueryConstraints / RetrievalPreferences` 是一组 contract
- 如果只共享其中一部分，会让现有 `QueryUnderstandingService` 依赖结构断裂

### Decisions
- 一次性把整组 query-planning contract 提升到 `rag_core`
- 让 `novel_analyzer.domain.schemas` 直接复用 shared types
- 继续保持 contract-first、小步迁移，而不触碰 query understanding 的 novel taxonomy 或 graph 语义

### Files Changed
- [rag_core/contracts.py](file:///home/user/novel-analyzer/rag_core/contracts.py)
- [rag_core/__init__.py](file:///home/user/novel-analyzer/rag_core/__init__.py)
- [novel_analyzer/domain/schemas.py](file:///home/user/novel-analyzer/novel_analyzer/domain/schemas.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Verification
- RED：测试先证明 `novel_analyzer.domain.schemas` 还未复用 shared types
- GREEN：同一测试在迁移整组 contract 后通过（`8 passed`）
- Manual QA：直接导入并打印 `prefs_same_object=True`、`plan_same_object=True`、`constraints_same_object=True`

### Deferred Risks
- 这一步仍只迁移 contract，不迁移 `QueryUnderstandingService` 的实现本体

### Next Owner Notes
- 下一步若继续抽代码，可优先考虑把纯 retrieval mechanics（RRF / rerank helper）移入 `rag_core`，而不是先碰 query taxonomy 或 graph augmentation

---

## Audit Entry — 2026-05-22 继续推进（RRF fusion mechanics 进入 rag_core）

### Trigger
- contract 层已经共享到 `rag_core`
- 下一步最合适的不是继续抽 adapter-heavy 逻辑，而是开始把纯 retrieval mechanics 中最安全的一块提升进去

### Inputs Reviewed
- [rag_core/contracts.py](file:///home/user/novel-analyzer/rag_core/contracts.py)
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Findings
- `_fuse_recall_lists` 是纯 RRF fusion helper，不依赖 DB、graph、novel taxonomy 或 adapter 语义
- 它刚好处于 contract-first 抽离后的下一拍：contract 已共享，现在 mechanics 也能开始共享

### Decisions
- 新增 `rag_core/fusion.py`
- 把 `reciprocal_rank_fuse` 提升为 shared helper
- 让 `RetrievalService._fuse_recall_lists` 直接复用 shared helper，而不改其他 retrieval 行为

### Files Changed
- [rag_core/fusion.py](file:///home/user/novel-analyzer/rag_core/fusion.py)
- [rag_core/__init__.py](file:///home/user/novel-analyzer/rag_core/__init__.py)
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Verification
- RED：测试先因 `rag_core` 还没有 fusion helper 而失败
- GREEN：同一测试在抽出 helper 后通过（`10 passed`）
- Manual QA：直接导入并打印 `same_object=True`

### Deferred Risks
- 这一步只迁移 fusion，不迁移 rerank helper 或 route 收集逻辑

### Next Owner Notes
- 如果继续抽 retrieval mechanics，下一拍优先考虑 `_apply_rerank` 或纯 diagnostics helper，而不是 route SQL 本体

---

## Audit Entry — 2026-05-22 继续推进（Rerank helper 进入 rag_core）

### Trigger
- shared contracts 与 RRF fusion helper 已经进入 `rag_core`
- 下一步最自然的纯 mechanics seam 是 rerank 的 score→hit 重排逻辑

### Inputs Reviewed
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [rag_core/fusion.py](file:///home/user/novel-analyzer/rag_core/fusion.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Findings
- `_apply_rerank` 里混合了两层逻辑：
  1. provider 调用
  2. score→hit 的纯重排 mechanics
- 第 2 层可安全抽离到 core，而不需要提前迁移 provider 调用边界

### Decisions
- 新增 `rag_core/rerank.py`
- 提升 `apply_rerank_scores` 为 shared helper
- 让 `RetrievalService` 只保留 provider 调用与 fallback 控制，纯重排逻辑委托给 shared helper

### Files Changed
- [rag_core/rerank.py](file:///home/user/novel-analyzer/rag_core/rerank.py)
- [rag_core/__init__.py](file:///home/user/novel-analyzer/rag_core/__init__.py)
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Verification
- RED：测试先因 `rag_core` 还没有 rerank helper 而失败
- GREEN：同一测试在提升 helper 后通过（`12 passed`）
- Manual QA：直接导入并打印 `same_object=True`

### Deferred Risks
- 这一步仍未迁移 provider 调用、route SQL 或 graph-aware rerank

### Next Owner Notes
- 如果继续抽 mechanics，下一步应优先考虑 provider-agnostic 的 text builder 或 diagnostics aggregation，再决定是否拆 provider orchestration

---

## Audit Entry — 2026-05-22 继续推进（Rerank text helper 进入 rag_core）

### Trigger
- shared rerank score application 已进入 `rag_core`
- 下一步最贴近它的纯 helper 是 rerank 文本构造逻辑 `_hit_rerank_text`

### Inputs Reviewed
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [rag_core/rerank.py](file:///home/user/novel-analyzer/rag_core/rerank.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Findings
- `_hit_rerank_text` 本质上是纯 formatting helper，不依赖 provider、graph、SQL 或 adapter 语义
- 它非常适合和 `apply_rerank_scores` 一起进入 shared rerank/text helper 层

### Decisions
- 新增 `rag_core/text.py`
- 提升 `build_rerank_text` 为 shared helper
- 让 `RetrievalService` 复用 shared helper，但仍由本地常量控制 `char_limit`

### Files Changed
- [rag_core/text.py](file:///home/user/novel-analyzer/rag_core/text.py)
- [rag_core/__init__.py](file:///home/user/novel-analyzer/rag_core/__init__.py)
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Verification
- RED：测试先因 `rag_core` 还没有 `build_rerank_text` 而失败
- GREEN：同一测试在提升 helper 后通过（`14 passed`）
- Manual QA：直接导入并打印 `same_object=True`，并观察未超长文本不应被强制加省略号

### Deferred Risks
- 这一步仍未迁移 provider 调用、graph-aware rerank 或 route-level text policy

### Next Owner Notes
- 如果继续抽 pure helper，下一步应优先考虑 `_coerce_keywords` / keyword normalization 这类无 provider 依赖的小块，再决定是否切更大的 retrieval text/materialization seam

---

## Audit Entry — 2026-05-22 继续推进（Keyword normalization helper 进入 rag_core）

### Trigger
- shared rerank text helper 已进入 `rag_core`
- 下一步最小纯 helper 目标是 `_coerce_keywords`，因为它无 DB、无 provider、无 graph 依赖，且在 retrieval 路径里复用频繁

### Inputs Reviewed
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Findings
- `_coerce_keywords` 是稳定的 payload-normalization helper，适合和其他 retrieval utilities 一起沉到 shared 层
- 这一步不改变任何 retrieval 语义，只统一 helper 所在位置

### Decisions
- 新增 `rag_core/keywords.py`
- 提升 `coerce_keywords` 为 shared helper
- 让 `RetrievalService` 直接复用 shared implementation

### Files Changed
- [rag_core/keywords.py](file:///home/user/novel-analyzer/rag_core/keywords.py)
- [rag_core/__init__.py](file:///home/user/novel-analyzer/rag_core/__init__.py)
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Verification
- RED：测试先因 `rag_core` 还没有 keyword normalizer 而失败
- GREEN：同一测试在提升 helper 后通过（`16 passed`）
- Manual QA：直接导入并打印 `same_object=True`，并验证 list / JSON string / scalar 输入输出一致

### Deferred Risks
- 这一步仍未触及更大的 materialization / payload-shaping seam

### Next Owner Notes
- 如果继续抽 retrieval pure helper，下一步可考虑 `_normalize_keywords` / `_query_hints` / `_bm25_text` 这些更接近 materialization 的边界，但要先确认它们是否已经进入 domain adapter 区域

---

## Audit Entry — 2026-05-22 继续推进（Cosine similarity helper 进入 rag_core）

### Trigger
- 已经把 contract、RRF、rerank score application、rerank text builder、keyword normalization 逐步提升到 `rag_core`
- 下一步最合适的 vector 纯 helper 是 `_cosine_similarity`

### Inputs Reviewed
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Findings
- `_cosine_similarity` 是纯数值 helper，不依赖 retrieval route、graph、DB 或 provider
- 它很适合作为 reusable vector helper 进入 `rag_core`

### Decisions
- 新增 `rag_core/vector.py`
- 提升 `cosine_similarity` 为 shared helper
- 让 `RetrievalService` 直接复用 shared implementation

### Files Changed
- [rag_core/vector.py](file:///home/user/novel-analyzer/rag_core/vector.py)
- [rag_core/__init__.py](file:///home/user/novel-analyzer/rag_core/__init__.py)
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Verification
- RED：测试先因 `rag_core` 还没有 cosine helper 而失败
- GREEN：同一测试在提升 helper 后通过（`18 passed`）
- Manual QA：直接导入并打印 `same_object=True`，并验证 self-sim/orthogonal/empty 三种结果

### Deferred Risks
- 这一步仍未迁移更大的 vector route 逻辑，只迁移底层数值 helper

### Next Owner Notes
- 如果继续抽 vector 相关 mechanics，下一步应优先看 `_coerce_vector_payload`，再决定是否往上触及 `_vector_route`

---

## Audit Entry — 2026-05-23 继续推进（Vector payload coercion helper 进入 rag_core）

### Trigger
- 已完成 `cosine_similarity` 抽离，vector mechanics 仍有一个相邻且纯净的 helper：`_coerce_vector_payload`
- 上一拍审计已把它标为下一优先候选

### Inputs Reviewed
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)
- [docs/qa_upgrade_v2/09-implementation-spec.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/09-implementation-spec.md)

### Findings
- `_coerce_vector_payload` 只负责把 DB / JSON 载荷正规化为 float list
- 它不依赖 graph、route orchestration、provider 调度或会话状态
- 它与 `cosine_similarity` 同属 reusable vector mechanics，适合进入 shared core

### Decisions
- 在 `rag_core/vector.py` 中新增 shared `coerce_vector_payload`
- 通过 `rag_core/__init__.py` 导出该 helper
- 让 `RetrievalService` 通过静态方法别名复用 shared implementation

### Files Changed
- [rag_core/vector.py](file:///home/user/novel-analyzer/rag_core/vector.py)
- [rag_core/__init__.py](file:///home/user/novel-analyzer/rag_core/__init__.py)
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Verification
- RED：新增测试先因 `rag_core` 尚未导出 `coerce_vector_payload` 而失败（`2 failed, 18 passed`）
- GREEN：最小实现后同一测试集通过（`20 passed`）
- Manual QA：验证 `same_object=True`，并确认 list / JSON string / invalid JSON-object 输入分别得到 `[1.0, 2.5]` / `[1.0, 2.5]` / `[]`

### Deferred Risks
- 这一步依然只迁移 vector payload normalization，不触及 `_vector_route` 本身的查询与候选聚合逻辑

### Next Owner Notes
- 如果继续沿 vector lane 抽离，优先评估 `_embedding_norm` 是否值得进入 shared core；若收益不足，再等待更大的 vector route seam 一起设计

---

## Audit Entry — 2026-05-23 继续推进（Embedding norm helper 进入 rag_core）

### Trigger
- 已完成 `coerce_vector_payload` 抽离，当前 vector lane 剩余最小的纯 helper 是 `_embedding_norm`
- 上一拍审计已把它列为下一优先候选

### Inputs Reviewed
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Findings
- `_embedding_norm` 只计算 dense vector 的 L2 norm
- 它不依赖 graph、DB、provider 或 route orchestration
- 它与 `coerce_vector_payload`、`cosine_similarity` 同属 reusable vector mechanics

### Decisions
- 在 `rag_core/vector.py` 中新增 shared `embedding_norm`
- 通过 `rag_core/__init__.py` 导出该 helper
- 让 `RetrievalService` 通过静态方法别名复用 shared implementation

### Files Changed
- [rag_core/vector.py](file:///home/user/novel-analyzer/rag_core/vector.py)
- [rag_core/__init__.py](file:///home/user/novel-analyzer/rag_core/__init__.py)
- [novel_analyzer/services/retrieval_service.py](file:///home/user/novel-analyzer/novel_analyzer/services/retrieval_service.py)
- [tests/test_rag_core_contracts.py](file:///home/user/novel-analyzer/tests/test_rag_core_contracts.py)

### Verification
- RED：新增测试先因 `rag_core` 尚未导出 `embedding_norm` 而失败（`2 failed, 20 passed`）
- GREEN：最小实现后同一测试集通过（`22 passed`）
- Manual QA：验证 `same_object=True`，并确认 `[3.0, 4.0] -> 5.0`、`[] -> 0.0`

### Deferred Risks
- 这一步仍只迁移 vector math primitive，不触及更高层的 chunk materialization / vector route seam

### Next Owner Notes
- 如果继续沿 vector lane 抽离，优先重新评估 `_embedding_inputs_for_chunks` 是否仍足够“纯”；若不够纯，就暂停 vector lane，转向 materialization helper 候选
