---
marp: true
size: A4
orientation: landscape
paginate: false
---

# 拆书引擎 · Deconstruction Engine

> **一句话**：把长篇小说切成 facts + 图谱 + 检索向量，作为 Q&A / 风控 / 仿写所有下游能力的统一真源。

---

## 解决的问题

| 痛点 | 解法 |
|------|------|
| 100+ 章长篇没人能记住 | 结构化 facts + graph + window |
| LLM prompt 装不下 | adaptive context（事实驱动三策略） |
| 中文专有名词 BM25 切错 | 自动 GraphNode → 领域词典 + pg_jieba |
| 远距离实体召回不到 | query expansion（别名 + 1-hop 图邻居） |

## 实证数据

- **检索基线**：simple R@5 = 0.81，jieba R@5 = **0.84**
- 跨 **5 本书 587 docs** 验证，已锁基线
- 单章 LLM 调用：5 → 3 次（stage merging）
- 单章延迟：**-40%**，整书吞吐 **+30%**

## 怎么用

```bash
.venv/bin/python -m novel_analyzer.cli.app \
  auto-run /path/to/novel.txt --max-chapters 0
```
→ 拿到 `branch_id`，下游全部能力都基于它工作。

## 边界（不要说）

- ❌ "AI 自动写小说"
- ❌ "替代编辑"
- ❌ "判断好不好看"

## 深入

[capabilities/01-deconstruction.md](../../capabilities/01-deconstruction.md) ·
[deconstruction-acceleration/architecture.md](../../deconstruction-acceleration/architecture.md) ·
[foundation-optimization/README.md](../../foundation-optimization/README.md)
