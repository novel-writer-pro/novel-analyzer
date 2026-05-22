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
