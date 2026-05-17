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
  section table { font-size: 14px; width: 100%; border-collapse: collapse; }
  section th { background: #1e3a8a; color: #fff; padding: 4px 8px; text-align: left; }
  section td { padding: 3px 8px; border-bottom: 1px solid #e5e7eb; }
  section tr:nth-child(even) td { background: #f8fafc; }
  section code { background: #f1f5f9; color: #be123c; padding: 2px 6px;
                 border-radius: 3px; font-size: 15px; }
  section strong { color: #be123c; }
  section li, section p { font-size: 16px; line-height: 1.32; margin: 2px 0; }
---

# 商业化运营 · Commercialization

> 从单机 dev 到 B2B API → 多租户 SaaS。**B2B API 4 周可商用**，SaaS 还有 6 项 SLA gap。

## 已就绪（v2 / v3 merged）

- ✅ Infra：Dify (8080) / n8n (5678) / Langfuse (3030) self-host
- ✅ Helicone LLM proxy (8585) — imitation 主流量 trace 全覆盖
- ✅ DB `owner_user_id` + IdentityMiddleware 三层透传
- ✅ "alice 看不到 bob 的书 + 跑完仿写自动通知" 端到端 6 步 smoke 通过

## 商用 6 项 SLA Gap（B2B API 路径）

| Gap | 工作量 | Gap | 工作量 |
|-----|-------|-----|-------|
| 1. 定价模型（per-chapter） | 3 天 | 4. LLM provider fallback | 5 天 |
| 2. 多租户隔离（tenant_id） | 5 天 | 5. 版权合规 | 2 周 |
| 3. SLA + 限流 | 5 天 | 6. 监控仪表盘 | 1 周 |

**最低可上线**：Gap 1-4 ≈ **4 周**

## 推荐计费方案（草案）

单本 ≤ 120 章 = **$60** ｜ 包年 10 本 = **$400** (8 折) ｜ LLM ~$0.10/章 → 定价 **$0.50/章**（5x 毛利）｜ 失败章节 **不计费**

## 不做（明确放弃）

❌ Coze SaaS（数据上云） ｜ ❌ LangFlow ｜ ❌ OpenManus 替代 LangGraph

**深入** — [capabilities/04-commercialization.md](../../capabilities/04-commercialization.md) · [strategy/writer-studio-roadmap.md](../../strategy/writer-studio-roadmap.md)
