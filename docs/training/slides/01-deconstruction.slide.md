---
marp: true
paginate: false
style: |
  section { font-size: 22px; padding: 40px 56px; background: #fff;
            font-family: "Noto Sans CJK SC","Noto Sans",sans-serif; }
  section h1 { font-size: 38px; color: #1e3a8a; border-bottom: 3px solid #2563eb;
               padding-bottom: 8px; margin: 0 0 12px 0; }
  section h2 { font-size: 24px; color: #1e3a8a; border-left: 4px solid #2563eb;
               padding-left: 10px; margin: 14px 0 6px 0; }
  section blockquote { border-left: 4px solid #fbbf24; background: #fffbeb;
                       padding: 8px 14px; margin: 10px 0; font-size: 19px; }
  section table { font-size: 17px; width: 100%; border-collapse: collapse; }
  section th { background: #1e3a8a; color: #fff; padding: 6px 10px; text-align: left; }
  section td { padding: 5px 10px; border-bottom: 1px solid #e5e7eb; }
  section tr:nth-child(even) td { background: #f8fafc; }
  section code { background: #f1f5f9; color: #be123c; padding: 2px 6px;
                 border-radius: 3px; font-size: 18px; }
  section pre { background: #0f172a; color: #e2e8f0; padding: 10px 14px;
                border-radius: 5px; font-size: 16px; }
  section pre code { background: transparent; color: inherit; padding: 0; }
  section strong { color: #be123c; }
  section li, section p { font-size: 19px; line-height: 1.45; }
---

# 拆书引擎 · Deconstruction Engine

> 把长篇小说切成 facts + 图谱 + 检索向量，作为 Q&A / 风控 / 仿写所有下游能力的统一真源。

## 解决的问题

| 痛点 | 解法 |
|------|------|
| 100+ 章长篇没人能记住 | 结构化 facts + graph + window |
| LLM prompt 装不下 | adaptive context（事实驱动三策略） |
| 中文专有名词 BM25 切错 | 自动 GraphNode → 领域词典 + pg_jieba |
| 远距离实体召回不到 | query expansion（别名 + 1-hop 图邻居） |

## 实证数据

- 检索基线：simple R@5 = 0.81，jieba R@5 = **0.84**（5 本书 587 docs 锁基线）
- 单章 LLM 调用 5→3 次（stage merging）；延迟 **-40%**；整书吞吐 **+30%**

## 边界（不要说）

❌ "AI 自动写小说" ｜ ❌ "替代编辑" ｜ ❌ "判断小说好不好看"

**深入** — [capabilities/01-deconstruction.md](../../capabilities/01-deconstruction.md) · [foundation-optimization/](../../foundation-optimization/README.md)
