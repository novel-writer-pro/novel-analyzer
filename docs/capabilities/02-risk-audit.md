# 能力线 2 — 风险检查（Risk Audit）

> **一句话定位**：9 个 checker 跨章节扫描人物 / 规则 / 时间线 / 战力 / 因果一致性，输出风险卡 + 问题簇 + 证据链，advisory-only 不阻断主提交。

**状态**：✅ 9 checker 进入 mainline，preflight + harness routing 已就绪；review workflow DB-only 模式

---

## 能解决什么问题

| 问题 | 风险检查给的答案 |
|------|-----------------|
| 100+ 章长篇人工读稿成本巨大 | 自动跨章扫 → 问题簇 + 优先级 + 证据 |
| LLM 仿写跑偏没人发现 | preflight 在写入前预检，harness 路由到对应 skill |
| 编辑没有审稿证据链 | 风险卡含 supporting / counter evidence |
| 多套衍生分支不知道哪个稳 | 分支级 audit_conclusion + risk_summary |
| 同样的问题反复跨章节出现 | review_candidate_clusters 自动聚合 |

---

## 当前能做到什么（实证）

### 9 个 checker 全部 mainline

| checker | 成熟度 | 复用 artifact 信号 |
|---------|--------|------------------|
| `character_ooc` | 高 | 角色画像基线，最稳定 |
| `world_rule_consistency` | 中 | world_rule_signals / unsupported_inferences |
| `relationship_consistency` | 中 | state_summary.stable/evolved_relations |
| `foreshadow_payoff_consistency` | 中 | new_foreshadowing / paid_off_foreshadowing |
| `setting_scope_consistency` | 中 | observed/constraining_world_rules |
| `thread_closure_consistency` | 中 | new_conflicts / escalated_conflicts |
| `plot_logic_consistency` | 中 | unsupported_inferences / state_transition_notes |
| `timeline_consistency` | 中 | timeline_signals / ambiguous_points |
| `power_scaling_consistency` | 中 | power_signals / state_transition_notes |

### 输出物

```
章节级
├─ ChapterRiskCard          # 风险明细 + supporting/counter evidence
├─ supporting_evidence
└─ counter_evidence

分支级
├─ risk_summary
├─ failed_summary
├─ review_candidate_count
├─ review_candidates_summary
├─ review_candidate_clusters   # 跨章节问题簇
└─ audit_conclusion             # 结构化审查结论

报告级
├─ branch_report.md             # Markdown 报告
├─ branch_bundle.json           # JSON bundle
└─ package 级逐章产物
```

### 跨章节问题簇字段

```json
{
  "cluster_title": "...",
  "checker_names": ["..."],
  "risk_types": ["..."],
  "chapters": [12, 18, 23],
  "chapter_count": 3,
  "first_chapter": 12,
  "last_chapter": 23,
  "max_confidence": 0.87,
  "suggested_review_action": "...",
  "review_priority": "high",
  "cluster_status": "open"
}
```

### 工程可靠性
- 最近 targeted regression：**40 passed**
- 完整链路：可测试 / 可回归 / 可重复导出

### 边界（明确不做）
- ❌ 自动修文
- ❌ 自动改 canon
- ❌ 审美 / 文风优劣判断
- ❌ "好不好看" 打分
- ❌ 阻断主提交（advisory-only 默认语义）

---

## 怎么用

### CLI（最常见）
```bash
# 风险审查（章级）
.venv/bin/python -m novel_analyzer.cli.app risk-audit <branch_id>

# 分支级总结
.venv/bin/python -m novel_analyzer.cli.app branch-report <branch_id>

# Review workflow 批量执行
.venv/bin/python -m novel_analyzer.cli.app review-batch-execute <branch_id>
```

### API
- 端点见 [api-current-surface.md](../api-current-surface.md)
- Review API 详见 [review-workflow-api.md](../review-workflow-api.md)
- 批量执行契约：[review-batch-execution-contract.md](../review-batch-execution-contract.md)

---

## 架构概览

```
canonical chapter artifact
    ↓
risk_audit_service
    ├─ checker × 9
    │   ├─ character_ooc
    │   ├─ world_rule_consistency
    │   ├─ relationship_consistency
    │   ├─ foreshadow_payoff_consistency
    │   ├─ setting_scope_consistency
    │   ├─ thread_closure_consistency
    │   ├─ plot_logic_consistency
    │   ├─ timeline_consistency
    │   └─ power_scaling_consistency
    │
    ├─ confidence-gated activation
    └─ risk aggregator
    ↓
ChapterRiskCard
    ↓
risk-aggregator-service
    ├─ review_candidates
    └─ review_candidate_clusters
    ↓
branch_report.md / branch_bundle.json
```

---

## 路线图

### Phase 1：框架成立 ✅
- 统一 checker contract / risk card / export
- 9 个 checker 全部 mainline

### Phase 1.5：artifact-signal 提质 ✅
- 各 checker 复用上游 artifact 信号
- 第一轮细粒度候选已落地：thread_state_conflict / motivation_to_action_gap / sequence_conflict_candidate / upset_without_setup …

### P1：信号质量 🔄
- 减少噪音
- 增加 cross-chapter 证据
- 提升候选可解释性

### P2：共享信号底座 🔲
- CharacterSignalRecord
- RuleSignalRecord
- EventCausalitySignal
- TimelineSignalRecord
- PowerStateSignalRecord
- → 让风险判定从"摘要提示"走向"结构化信号判断"

### P3：review lifecycle 闭环 🔲
- review_owner / review_notes
- resolved_by / resolved_at
- 人工复核回写到 DB

---

## 深入文档

### 系统总览
- [risk-audit-system-overview.md](../risk-audit-system-overview.md) — 系统总览（一页读懂）
- [risk-audit-capability.md](../risk-audit-capability.md) — 能力说明
- [risk-audit-runtime-architecture.md](../risk-audit-runtime-architecture.md) — 运行时架构
- [risk-audit-production-readiness.md](../risk-audit-production-readiness.md) — 生产就绪评估

### Checker 路线图
- [risk-audit-checker-roadmap.md](../risk-audit-checker-roadmap.md) — Checker 路线图

### Review 工作流
- [review-workflow-api.md](../review-workflow-api.md) — Review API
- [review-batch-execution-contract.md](../review-batch-execution-contract.md) — 批量执行契约

### 能力线深入
- [tracks/risk-audit/README.md](../tracks/risk-audit/README.md) — 风险审查能力线
- [tracks/review-workflow/README.md](../tracks/review-workflow/README.md) — Review workflow 能力线

### Reader Panel（读者体验子能力）
- [handoffs/reader-panel-handoff-20260516.md](../handoffs/reader-panel-handoff-20260516.md) — 4-persona × 7-dim 评估 + comfort_score soft gate
- [tracks/reader-experience/README.md](../tracks/reader-experience/README.md)

---

## 推荐对外表述

> 系统已经具备统一风险审查体系的第一阶段能力，当前正式覆盖人物 OOC 与规则一致性，并已将剧情逻辑、时间线、战力能力审查纳入统一 checker 体系。系统可输出风险卡、问题簇与结构化审查结论，适合作为作者 / 编辑的审稿辅助能力使用。

**不推荐**说法：
- ❌ 已经是完全成熟的自动审稿引擎
- ❌ 能自动判断小说好不好看
- ❌ 能直接替代人工编辑

---

返回 [capabilities/](./README.md) ｜ [文档中心](../README.md)
