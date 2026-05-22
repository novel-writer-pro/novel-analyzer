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
