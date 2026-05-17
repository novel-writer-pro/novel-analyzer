---
marp: true
size: A4
orientation: landscape
paginate: false
---

# 风险检查 · Risk Audit

> **一句话**：9 个 checker 跨章节扫人物 / 规则 / 时间线 / 战力 / 因果一致性，输出风险卡 + 问题簇 + 证据链。

---

## 9 Checker 全景（mainline）

| 类别 | Checker |
|------|---------|
| 人物 | `character_ooc`（最成熟） |
| 设定 | `world_rule_consistency` · `setting_scope_consistency` |
| 关系 | `relationship_consistency` |
| 伏笔 | `foreshadow_payoff_consistency` · `thread_closure_consistency` |
| 逻辑 | `plot_logic_consistency` · `timeline_consistency` · `power_scaling_consistency` |

## 实证数据

- 9 个 checker 全部进入 mainline，preflight + harness routing 已就绪
- 最近 targeted regression：**40 passed**
- review workflow DB-only 模式上线
- 输出：`ChapterRiskCard` + `review_candidate_clusters`（含 `cluster_status` / `priority` / `suggested_action`）

## 设计语义

- **advisory-only** — 不阻断主提交，只标记可疑章节
- 跨章节问题簇 — 不只 "这一章有问题"，而是 "12 / 18 / 23 章都触发了同一类问题"
- 全证据链 — supporting + counter evidence 都给出来

## 边界（不要说）

- ❌ "全自动审稿引擎"
- ❌ "判断小说好不好看"
- ❌ "100% 不漏"

## 深入

[capabilities/02-risk-audit.md](../../capabilities/02-risk-audit.md) ·
[risk-audit-system-overview.md](../../risk-audit-system-overview.md) ·
[risk-audit-checker-roadmap.md](../../risk-audit-checker-roadmap.md)
