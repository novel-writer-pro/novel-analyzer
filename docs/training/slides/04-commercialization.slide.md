---
marp: true
theme: a4-landscape
paginate: false
---

# 商业化运营 · Commercialization

> 从单机 dev 到 B2B API → 多租户 SaaS 的演进路线。**B2B API 4 周可商用**，SaaS 还有 6 项 SLA gap。

## 已就绪（v2 / v3 merged）

- ✅ Infra 三件套：Dify (8080) / n8n (5678) / Langfuse (3030) self-host
- ✅ Helicone LLM proxy (8585) — imitation 主流量 trace 全覆盖
- ✅ DB `owner_user_id` + IdentityMiddleware 三层透传
- ✅ "alice 看不到 bob 的书 + 跑完仿写 alice 收到通知" 端到端 6 步 smoke 通过

## 商用 6 项 SLA Gap（B2B API 路径）

| Gap | 工作量 | Gap | 工作量 |
|-----|-------|-----|-------|
| 1. 定价模型（per-chapter） | 3 天 | 4. LLM provider fallback | 5 天 |
| 2. 多租户隔离（tenant_id） | 5 天 | 5. 版权合规 | 2 周 |
| 3. SLA + 限流 | 5 天 | 6. 监控仪表盘 | 1 周 |

**最低可上线**：Gap 1-4 ≈ **4 周**

## 推荐计费方案（草案）

- 单本 ≤ 120 章 = **$60** ｜ 包年 10 本 = **$400** (8 折)
- LLM ~$0.10/章 → 定价 **$0.50/章**（5x 毛利）｜失败章节 **不计费**

## 不做（明确放弃）

❌ Coze SaaS（数据上云）｜ ❌ LangFlow（与 Dify 同质）｜ ❌ OpenManus 替代 LangGraph（控制粒度不够）

## 深入

[capabilities/04-commercialization.md](../../capabilities/04-commercialization.md) · [strategy/writer-studio-roadmap.md](../../strategy/writer-studio-roadmap.md) · [cross-genre-imitation-commercial-readiness-20260515.md](../../cross-genre-imitation-commercial-readiness-20260515.md)
