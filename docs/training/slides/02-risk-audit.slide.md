---
marp: true
paginate: false
style: |
  section { font-size: 22px; padding: 30px 50px; background: #fff;
            font-family: "Noto Sans CJK SC","Noto Sans",sans-serif; }
  section h1 { font-size: 34px; color: #1e3a8a; border-bottom: 3px solid #2563eb;
               padding-bottom: 6px; margin: 0 0 10px 0; }
  section h2 { font-size: 22px; color: #1e3a8a; border-left: 4px solid #2563eb;
               padding-left: 10px; margin: 10px 0 4px 0; }
  section blockquote { border-left: 4px solid #fbbf24; background: #fffbeb;
                       padding: 5px 10px; margin: 6px 0; font-size: 17px; }
  section table { font-size: 15px; width: 100%; border-collapse: collapse; }
  section th { background: #1e3a8a; color: #fff; padding: 4px 10px; text-align: left; }
  section td { padding: 3px 10px; border-bottom: 1px solid #e5e7eb; }
  section tr:nth-child(even) td { background: #f8fafc; }
  section code { background: #f1f5f9; color: #be123c; padding: 2px 6px;
                 border-radius: 3px; font-size: 16px; }
  section strong { color: #be123c; }
  section li, section p { font-size: 17px; line-height: 1.35; margin: 2px 0; }
---

# 风险检查 · Risk Audit

> 9 个 checker 跨章扫人物 / 规则 / 时间线 / 战力一致性，输出风险卡 + 问题簇 + 证据链。

## 9 Checker 全景（mainline）

| 类别 | Checker |
|------|---------|
| 人物 | `character_ooc`（最成熟） |
| 设定 | `world_rule_consistency` · `setting_scope_consistency` |
| 关系 | `relationship_consistency` |
| 伏笔 | `foreshadow_payoff_consistency` · `thread_closure_consistency` |
| 逻辑 | `plot_logic_consistency` · `timeline_consistency` · `power_scaling_consistency` |

## 实证 + 设计语义

- 9 checker 全部 mainline；最近 targeted regression：**40 passed**
- 输出 `ChapterRiskCard` + `review_candidate_clusters`（status / priority / suggested_action）
- **advisory-only**：不阻断主提交，只标记可疑章节
- 跨章节问题簇：自动聚合 "12 / 18 / 23 章触发同一类问题"

## 边界（不要说）

❌ "全自动审稿引擎" ｜ ❌ "判断好不好看" ｜ ❌ "100% 不漏"

**深入** — [capabilities/02-risk-audit.md](../../capabilities/02-risk-audit.md) · [risk-audit-system-overview.md](../../risk-audit-system-overview.md)
