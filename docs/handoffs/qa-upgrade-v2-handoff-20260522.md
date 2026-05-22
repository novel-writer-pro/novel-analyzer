# Session Handoff — 2026-05-22（QA Upgrade V2 文档深化与审计治理）

## 0. 环境状态（接手即可用）
- 仓库：`/home/user/novel-analyzer`
- 主题：`docs/qa_upgrade_v2` 文档包深化，不是新功能编码冲刺
- 当前已确认进度：
  - `P0` 第一批修复已落在 [12-phase-delivery-log.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/12-phase-delivery-log.md)
  - `P1` 的 `StructuredQueryPlan` / `QueryUnderstandingService` 骨架已起步
  - `P2+` 仍以 contract、evaluation、gate 设计为主

## 1. 本会话核心交付
- 把 [QA Upgrade V2 README](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/README.md) 补成带进度快照与审计入口的导航页
- 把 [03-roadmap.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/03-roadmap.md) 从“阶段列表”升级为“阶段列表 + 当前状态 + query understanding 技术分层 + gate”
- 把 [04-delivery-checklist.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/04-delivery-checklist.md) 从功能核对表升级为带证据与审计要求的 checklist
- 把 [06-metrics-and-evaluation.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/06-metrics-and-evaluation.md) 补齐 phase gate / release gate / rollback gate
- 把 [12-phase-delivery-log.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/12-phase-delivery-log.md) 追加本轮文档治理阶段
- 新增 [15-audit-and-change-log.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/15-audit-and-change-log.md) 作为 QA V2 审计入口
- 把 [07-development-plan.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/07-development-plan.md) 补成带“当前测试覆盖真相”的开发计划
- 新增 [16-query-understanding-techniques-appendix.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/16-query-understanding-techniques-appendix.md) 作为 Query Understanding 外部模式与采纳顺序附录
- 把 [05-data-preparation.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/05-data-preparation.md) 补成带 `data/qa_eval/` 目录 contract、parser regression buckets 与 jsonl 样本规范的数据准备文档
- 把 [11-risk-register-and-backlog.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/11-risk-register-and-backlog.md) 补成包含 regression/data-contract backlog 的任务池
- 在仓库中真实创建 `data/qa_eval/` 目录骨架及各子目录 README contract（不含伪造样本）
- 新增 parser / qa_eval 两份 SOP，说明 regression case、badcase 回流、人工审核与 replay 的执行方式
- 明确 reusable RAG core 采用“默认无 graph，graph 为 optional capability，novel 为 adapter”的抽离方向
- 新增 `rag_core/` 最小代码骨架，承接 shared contracts 与 adapter protocols，作为后续代码抽离落点
- `RetrievalService` 已开始双栖复用 `rag_core` 的 `RetrievalHit` contract，证明 contract-first 抽离可行
- `RetrievalService` 的 diagnostics contract 也已双栖复用到 `rag_core`

## 2. 下一步推荐（接手人）

### P0
- 补充一份“外部 query understanding 参考模式”的本地研究附录，避免未来继续口头引用

### P1
- 把 `tests/test_query_understanding_service.py` 的当前覆盖面与 roadmap 中的 parser gate 一一对齐
- 明确哪几类 query 已经被 skeleton 支持，哪几类仍是 design-only
- 优先补 relation / world_rule / foreshadow / ambiguity / parse failure taxonomy 这五类测试桶
- 同步建立 `data/qa_eval/parser_regression/` 的同名数据桶，不要只补测试不补样本目录

### 数据资产
- 从 [`data/qa_eval/parser_regression/README.md`](file:///home/user/novel-analyzer/data/qa_eval/parser_regression/README.md) 开始填首批 regression 样本
- 从 [`data/qa_eval/badcase_backlog/README.md`](file:///home/user/novel-analyzer/data/qa_eval/badcase_backlog/README.md) 开始接 badcase 回流
- 新增样本前，先读 [`17-parser-regression-playbook.md`](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/17-parser-regression-playbook.md) 和 [`18-qa-eval-runbook.md`](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/18-qa-eval-runbook.md)

### P2
- 如果开始接 `qa_service` 主链，先要求：
  1. diagnostics schema 落地
  2. parser failure taxonomy 落地
  3. regression set 基础目录落地
  4. badcase backlog 能回流到 parser_regression / difficult_queries / gold set

### 核心解耦方向
- 优先抽 `RetrievalService` / query-plan / rerank / diagnostics 所在的 reusable core
- graph 保持 optional，不作为其他领域知识问答复用的前置依赖
- novel-specific 语义（chapter、anti-spoiler、foreshadow、world_rule、causal answer shaping）保留在 adapter

### 当前代码状态
- `rag_core/` 已存在，但目前只包含最小 contracts / protocols
- `RetrievalService` 已开始复用 shared `RetrievalHit`
- `RetrievalRouteDiagnostics` / `RetrievalSearchDiagnostics` 也已进入 shared core
- `StructuredQueryPlan / RetrievalPreferences / QueryConstraints / QueryTimeScope / PlannedEntity` 也已进入 shared core
- RRF fusion helper 也已进入 `rag_core`，`RetrievalService` 开始复用 shared mechanics
- 现有 `novel_analyzer` 服务实现整体还未迁移过去，这仍然是刻意控制风险的渐进式抽离

## 3. 已知限制
- Oracle 背景任务多次 fallback 后完成，但没有返回有效文本，不应把它当作已完成架构评审
- 本轮重点是文档治理，不代表 retrieval / rerank / grounded answer 已新增实现
- 根 [CHANGELOG.md](file:///home/user/novel-analyzer/CHANGELOG.md) 本身较长且历史重复较多，后续继续追加时要保持条目高信噪比

## 4. 标准操作手册（SOP）

### 推荐先读
1. [docs/qa_upgrade_v2/README.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/README.md)
2. [docs/qa_upgrade_v2/03-roadmap.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/03-roadmap.md)
3. [docs/qa_upgrade_v2/04-delivery-checklist.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/04-delivery-checklist.md)
4. [docs/qa_upgrade_v2/07-development-plan.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/07-development-plan.md)
5. [docs/qa_upgrade_v2/15-audit-and-change-log.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/15-audit-and-change-log.md)
6. [docs/qa_upgrade_v2/16-query-understanding-techniques-appendix.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/16-query-understanding-techniques-appendix.md)
7. [docs/qa_upgrade_v2/05-data-preparation.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/05-data-preparation.md)
8. [docs/qa_upgrade_v2/11-risk-register-and-backlog.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/11-risk-register-and-backlog.md)
9. [data/qa_eval/README.md](file:///home/user/novel-analyzer/data/qa_eval/README.md)
10. [docs/qa_upgrade_v2/17-parser-regression-playbook.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/17-parser-regression-playbook.md)
11. [docs/qa_upgrade_v2/18-qa-eval-runbook.md](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/18-qa-eval-runbook.md)
12. [docs/architecture/independent-agent-knowledge-and-retrieval.md](file:///home/user/novel-analyzer/docs/architecture/independent-agent-knowledge-and-retrieval.md)
13. [rag_core/__init__.py](file:///home/user/novel-analyzer/rag_core/__init__.py)

### 如果要继续实现 query understanding
- 先核对：`StructuredQueryPlan` 是否与 roadmap gate 一致
- 再核对：现有测试是否覆盖 alias / timeline / difficult query
- 再核对：新增能力属于 baseline / advanced / frontier 哪一层，避免过早引入重 planner
- 最后再动主链接线

## 5. 文档索引
- [QA Upgrade V2 README](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/README.md)
- [Roadmap](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/03-roadmap.md)
- [Delivery Checklist](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/04-delivery-checklist.md)
- [Development Plan](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/07-development-plan.md)
- [Data Preparation](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/05-data-preparation.md)
- [Metrics and Evaluation](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/06-metrics-and-evaluation.md)
- [Risk Register and Backlog](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/11-risk-register-and-backlog.md)
- [Phase Delivery Log](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/12-phase-delivery-log.md)
- [Audit and Change Log](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/15-audit-and-change-log.md)
- [Query Understanding Techniques Appendix](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/16-query-understanding-techniques-appendix.md)
- [Parser Regression Playbook](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/17-parser-regression-playbook.md)
- [QA Eval Runbook](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/18-qa-eval-runbook.md)
- [QA Eval Data Skeleton](file:///home/user/novel-analyzer/data/qa_eval/README.md)
- [Independent Agent Knowledge & Retrieval Architecture](file:///home/user/novel-analyzer/docs/architecture/independent-agent-knowledge-and-retrieval.md)

## 6. 本会话 commit 列表
- 本次 handoff 对应 commit 由当前会话在提交后补充到 git 历史中
