# 会话交接（Session Handoffs）

> 每一棒接手人留下的状态总结。按时间倒序列出，最近的在最上面。
> 接手新会话时，从最上面一份开始读，逐份回溯 2-3 棒即可建立完整心智模型。

---

## 最近交接（按时间倒序）

| 日期 | 主题 | 交接文档 |
|------|------|---------|
| **2026-05-22** | **QA Upgrade V2 文档深化 + 审计治理** | [qa-upgrade-v2-handoff-20260522.md](./qa-upgrade-v2-handoff-20260522.md) |
| **2026-05-17** | **Loom Phase 6 完成 — Author Project Shell（18 commits）** | [session-handoff-20260517-phase6.md](./session-handoff-20260517-phase6.md) |
| 2026-05-17 | scaffold 三层修复 + 31 commits 总结 | [session-handoff-20260517.md](./session-handoff-20260517.md) |
| 2026-05-16 | Reader Panel — 4-persona × 7-dim 阅读体验评估 + comfort_score soft gate | [reader-panel-handoff-20260516.md](./reader-panel-handoff-20260516.md) |
| 2026-05-15 | 同题材 baseline prompt 修复后 Stage A/B/C 长跑验证步骤 | [baseline-imitation-quality-validation-handoff-20260515.md](./baseline-imitation-quality-validation-handoff-20260515.md) |

---

## 接手建议阅读顺序（30 分钟建立完整心智模型）

1. **本目录最新一份** — 看上一棒做完了什么、留了什么坑
2. [docs/OVERVIEW.md](../OVERVIEW.md) — 系统全貌（5 分钟）
3. [docs/ROADMAP.md](../ROADMAP.md) — 4 条能力线进度（5 分钟）
4. [training/developer.md](../training/developer.md) — 开发路径（如果你是工程师）
5. [runbook/deployment-and-operations-manual-20260515.md](../runbook/deployment-and-operations-manual-20260515.md) — 从零部署
6. [CHANGELOG.md](../../CHANGELOG.md) — 最近变更记录

---

## 历史交接

更早的 session handoff 已收纳到：
- [deprecated/session-handoffs/](../deprecated/session-handoffs/) — 2026-05-14 ~ 2026-05-15 期间的 handoff 归档

包含但不限于：
- session-handoff-20260514.md
- session-handoff-20260514-kernel-and-integration.md
- session-handoff-20260515-final.md
- session-handoff-20260516.md
- writer-studio-v3-handoff.md
- imitation-next-dev-handoff.md
- release-handoff-brief.md

---

## 写新交接的模板（给下一棒）

写新 handoff 时，建议覆盖以下章节：

```markdown
# Session Handoff — YYYY-MM-DD（主题）

## 0. 环境状态（接手即可用）
- 分支、最新 commit、DB、LLM、feature flag 状态、测试通过数

## 1. 本会话核心交付
- 新增能力（CLI / API / service / skill）
- 验证数据 / benchmark
- 关键变更点

## 2. 下一步推荐（接手人）
- P0 / P1 / P2 优先级清单

## 3. 已知限制
- 未解决的问题、临时绕过、性能瓶颈

## 4. 标准操作手册（SOP）
- 复现本会话产物的命令清单

## 5. 文档索引
- 相关文档链接

## 6. 本会话 commit 列表
- git log --oneline 摘要
```

---

返回 [文档中心](../README.md)
