---
marp: true
paginate: false
style: |
  section { font-size: 22px; padding: 40px 56px; background: #fff;
            font-family: "Noto Sans CJK SC","Noto Sans",sans-serif; }
  section h1 { font-size: 38px; color: #1e3a8a; border-bottom: 3px solid #2563eb;
               padding-bottom: 8px; margin: 0 0 12px 0; }
  section h2 { font-size: 24px; color: #1e3a8a; border-left: 4px solid #2563eb;
               padding-left: 10px; margin: 12px 0 5px 0; }
  section blockquote { border-left: 4px solid #fbbf24; background: #fffbeb;
                       padding: 6px 12px; margin: 8px 0; font-size: 18px; }
  section table { font-size: 16px; width: 100%; border-collapse: collapse; }
  section th { background: #1e3a8a; color: #fff; padding: 5px 10px; text-align: left; }
  section td { padding: 4px 10px; border-bottom: 1px solid #e5e7eb; }
  section tr:nth-child(even) td { background: #f8fafc; }
  section code { background: #f1f5f9; color: #be123c; padding: 2px 6px;
                 border-radius: 3px; font-size: 17px; }
  section strong { color: #be123c; }
  section li, section p { font-size: 18px; line-height: 1.4; }
---

# 受控仿写 · Imitation

> 章级 / 整本 / 跨题材三档，全程 harness 控制（preflight + skills pipeline + risk routing），可回退、可对比、已商用。

## 三档能力

- **章级**：`imitate-chapter` / `iterate-imitation` / `review-imitation`
- **整本**：`writer-imitate-range` — per-chapter 增量保存，进程被杀不丢章节
- **跨题材**：mapping_pack（world / character / power / rule）

## 跨题材改写已商用就绪

| 测试 | 章数 | full pass | mapping accuracy |
|------|-----:|-----------|------------------|
| 卫图 → 太空科幻 | 102 | **102/102 (100%)** | 98.0% |
| 诛仙 → 太空科幻 | 59 | **58/59 (98.3%)** | 97.5% |
| 卫图 → 都市修真 | 10 | **10/10 (100%)** | 96.1% |
| **合计 1M+ 字** | **171** | **170 / 99.4%** | **96-98%** |

## Loom 上层（feature flag 渐进启用）

memory · tension · style · character · reward · **Phase 6 项目壳**（7 层 markdown）

## 边界（不要说）

❌ "AI 自动写一本书" ｜ ❌ "完全替代作家" ｜ ❌ 同题材整本仿写仍在长跑验证

**深入** — [capabilities/03-imitation.md](../../capabilities/03-imitation.md) · [loom/README.md](../../loom/README.md)
