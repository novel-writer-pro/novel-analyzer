# novel-analyzer 全局路线图

> 4 条核心能力线的统一进度表 + 下一阶段目标。
> 每条能力线都有独立的 detail roadmap，本文是 **single source of truth** 的总进度。
> 更新节奏：每次重要里程碑（合规 / 商用 / Phase）后修订。

---

## 当前里程碑（2026-05-17）

| 能力线 | 已完成 | 进行中 | 下一阶段 |
|--------|-------|--------|---------|
| **拆书引擎** | Phase 1-4 SOTA 优化 + Phase 4.5 quick/deep 双档 + 性能剖析 | 长篇性能优化 Phase 5-Perf | RAG worldview/trope 库填充、商用基线 SLA |
| **风险检查** | 9 checker mainline + review workflow DB-only + 集群审查 | 跨章节信号底座、reduce 噪音 | review lifecycle 闭环（resolved/owner/notes） |
| **受控仿写** | 章级 harness + 整本编排 + 跨题材 mapping_pack（170/171）+ Loom Phase 1-6 | 同题材长跑验证、Phase 5 reader sim/多线 | Phase 7 Web UI 桥接、生产 LLM 长跑 |
| **商业化** | v2/v3 框架（Dify/n8n/Langfuse/Helicone）+ owner_user_id 透传 | B2B API 定价 / 限流 / fallback | 多租户 SaaS（6 项 infra gap） |

---

## 路线图视图

```
2026 Q1 ─┬─ ✅ 拆书 Phase 1-4 SOTA（adaptive context / stage merge / arc memory）
         ├─ ✅ 风险审查 9 checker mainline
         ├─ ✅ Loom Phase 1-2（memory + tension + pairwise）
         └─ ✅ Writer Studio v2（Dify + n8n + Langfuse）

2026 Q2 ─┬─ ✅ 拆书 Phase 4.5（quick/deep 双档）
         ├─ ✅ 跨题材 mapping_pack 验证（170/171 pass）
         ├─ ✅ Loom Phase 3-6（reward + style + character + project shell）
         ├─ ✅ Reader Panel（4-persona × 7-dim）
         ├─ ✅ Writer Studio v3（owner_user_id + Helicone proxy）
         ├─ 🔄 同题材 prompt 修复 Stage A/B/C 长跑
         └─ 🔄 拆书 Phase 5-Perf（embedding/rerank/reasoning_snapshot）

2026 Q3 ─┬─ 🔲 同题材整本仿写商用就绪
         ├─ 🔲 跨题材 B2B API 商用上线（Gap 1-3 解决）
         ├─ 🔲 Loom Phase 7（Web UI 桥接到 Writer Studio）
         ├─ 🔲 review workflow lifecycle 闭环
         └─ 🔲 多租户 tenant_id + 限流 + fallback

2026 Q4 ─┬─ 🔲 多租户 SaaS（计费 / 版权 / 监控全部就绪）
         ├─ 🔲 Reader 端商用化
         └─ 🔲 Prompt 资产托管 + Langfuse/Helicone trace 合并
```

图例：✅ 完成 ｜ 🔄 进行中 ｜ 🔲 计划

---

## 能力线 1 — 拆书引擎（Deconstruction）

> 详情：[capabilities/01-deconstruction.md](./capabilities/01-deconstruction.md) ｜ [deconstruction-acceleration/roadmap-sota-optimization.md](./deconstruction-acceleration/roadmap-sota-optimization.md)

### Phase 1-4 已完成（SOTA 全栈）
- adaptive context assembly（事实驱动三策略检索）
- stage merging（5→3 次 LLM 调用，单章延迟 -40%）
- foreshadowing lifecycle manager（伏笔状态机）
- chapter complexity router（自动路由大/小模型）
- entity resolution（图谱节点去重）
- arc-level memory（recent/midrange/distant 三层压缩）
- causal graph + confidence calibration + self-evaluation
- claim-level grounding + auto-repair loop
- confidence-gated checker activation

### Phase 4.5 已完成（quick/deep 双档）
- canonical chapter artifact 与 enrichment 边界
- reader isolation + stale guard + benchmark 模型
- baseline benchmark：simple R@5 = 0.81，jieba R@5 = 0.84，5 本书 587 docs

### Phase 5-Perf 进行中
- embedding 性能优化
- rerank 性能优化
- reasoning_snapshot 路径优化
- vector 路由优化
- 详细数据：[deconstruction-acceleration/performance-profiling-20260517.md](./deconstruction-acceleration/performance-profiling-20260517.md)

### 后续计划
- 商用基线 SLA（90 章 < 30 分钟）
- RAG worldview-dossiers / trope-library 填充

---

## 能力线 2 — 风险检查（Risk Audit）

> 详情：[capabilities/02-risk-audit.md](./capabilities/02-risk-audit.md) ｜ [risk-audit-checker-roadmap.md](./risk-audit-checker-roadmap.md)

### 已完成（9 checker mainline）
- `character_ooc`（最成熟）
- `world_rule_consistency`（含 world_rule_signals / unresolved_threads）
- `relationship_consistency`（含 trust state / hostility resolution）
- `foreshadow_payoff_consistency`（含 payoff_without_setup）
- `setting_scope_consistency`（含 constraint_scope_expansion）
- `thread_closure_consistency`（含 thread_dropped_after_escalation）
- `plot_logic_consistency`（含 thread_state_conflict / motivation_to_action_gap）
- `timeline_consistency`（含 sequence_conflict_candidate / recovery_window_insufficient）
- `power_scaling_consistency`（含 upset_without_setup / cost_constraint_missing）

### 已完成（review workflow）
- DB-only 模式
- review candidate clusters（cluster_title / status / priority / suggested_action）
- batch execute 契约
- markdown / JSON 双导出

### P1 进行中
- 减少噪音、增加 cross-chapter 证据、提升候选可解释性
- 强化 character_ooc 角色画像基线
- 强化 plot 因果链建模

### P2 / P3 计划
- P2：建设 CharacterSignalRecord / RuleSignalRecord / EventCausalitySignal 共享信号底座
- P3：review lifecycle 闭环（review_owner / review_notes / resolved_by / resolved_at）

---

## 能力线 3 — 受控仿写（Imitation）

> 详情：[capabilities/03-imitation.md](./capabilities/03-imitation.md) ｜ [loom/roadmap.md](./loom/roadmap.md) ｜ [chapter-imitation-capability-matrix.md](./chapter-imitation-capability-matrix.md)

### 章级 / 整本仿写已完成
- 章级仿写：`imitate-chapter` / `iterate-imitation` / `review-imitation`
- 全部支持 `--world-map / --character-map / --power-map / --rule-override`
- 整本编排：`writer-imitate-range`，per-chapter 增量保存
- auto-retry：thin / scaffold / action-queue 三类 contamination 实时拦截
- harness 控制：preflight + skills pipeline + risk routing

### 跨题材改写已突破（170/171 pass，99.4%）
- 卫图（古典仙侠）→ 太空科幻：102/102 ✅，mapping accuracy 98.0%
- 诛仙（古典仙侠）→ 太空科幻：58/59 ✅，mapping accuracy 97.5%
- 卫图（古典仙侠）→ 都市修真：10/10 ✅，mapping accuracy 96.1%

### Loom 上层已完成（Phase 1-6）
- Phase 1：分层记忆（working / episodic / semantic）+ 冲突代谢
- Phase 2：张力指标 + pairwise 评估（LLM-as-judge）
- Phase 3：reward model + 角色认知基（CharacterPersona）
- Phase 4：风格向量 + 节奏分析 + 对话信号
- Phase 5：reader simulation + 多线调度 + 自适应编排
- Phase 6：Author Project Shell（7 层 markdown 编译成 9 flag + 5 Loom env）

### 进行中
- 🔧 同题材整本仿写 Stage A/B/C 长跑验证（baseline prompt 修复后）
- 🔄 真实 LLM 长跑（更强模型 + max-rounds 3）

### 后续计划
- Phase 7：Web UI 桥接（项目壳 markdown 流接到 Writer Studio）
- Phase 5 实战：reader_sim_score 真实读者校准
- 多本范本叠加（多源 branch 编排）

---

## 能力线 4 — 商业化运营（Commercialization）

> 详情：[capabilities/04-commercialization.md](./capabilities/04-commercialization.md) ｜ [strategy/writer-studio-roadmap.md](./strategy/writer-studio-roadmap.md) ｜ [cross-genre-imitation-commercial-readiness-20260515.md](./cross-genre-imitation-commercial-readiness-20260515.md)

### v1（已撤回）
重自研版本，时间长、收益低，被 v2 取代。

### v2 已完成（PR #8 merged）
- Infra 三件套：Dify / n8n / Langfuse 全部上线
- DB 加 `owner_user_id` 列
- UI shell：`/writer/*` 与旧 Workbench 隔离
- Dify Chatbot iframe 集成

### v3 已完成（PR #9 merged）
- IdentityMiddleware + service 层 owner_user_id WHERE
- n8n pipeline-complete webhook
- Helicone LLM proxy（imitation 主流量 trace）
- "alice 看不到 bob 的书" 隔离已验证

### v4 候选（按优先级）

**优先级 A（用户已能感受的扩展）**
- Reader 端 UI（v2/v3 都只服务作家）
- 多用户管理 UI

**优先级 B（商业化前必须）**
- B2B API 商用 6 项 SLA gap：
  - Gap 1：定价模型（per-chapter 计费 / 套餐 / 失败章节不计费）
  - Gap 2：多租户隔离（tenant_id + RLS + token 映射）
  - Gap 3：SLA + 限流（60 chapters/hour，5 concurrent runs）
  - Gap 4：LLM provider 自动 fallback（3 路 router + circuit breaker）
  - Gap 5：版权合规（输入文本来源声明 + 商用授权链）
  - Gap 6：监控 + 计费仪表盘（Helicone cost + Langfuse trace 合并）
- Prompt 资产托管（imitation prompts 从 .py 搬到 Dify Prompt Studio）
- secret 管理（Vault / SOPS / 1Password CLI）
- prod / staging 拆分（HA + backup + cost cap）

**优先级 C（内部体验）**
- FastAPI 全 surface（main.py 2503 行 → 微框架）
- 每用户配额 / 计费
- Reader 端 Letta/Mem0 长期记忆

### 不做（明确放弃）
- Coze SaaS 替代 Dify（数据上云不符合 self-host）
- LangFlow / Bisheng（与 Dify 同质）
- OpenManus 替代 LangGraph（自主性太强，imitation 需要精细控制）
- PostgreSQL Row-Level Security（v4 商业化再讨论）

---

## 决策时间线

| 日期 | 里程碑 |
|------|-------|
| 2026-05-09 | Loom Phase 1-2 完成 |
| 2026-05-11 | 拆书 Phase 4.5 双档完成 |
| 2026-05-13 | Writer Studio v2 plan 写定 |
| 2026-05-14 | v2 merged + v3 plan + v3 merged |
| 2026-05-15 | 跨题材改写 170/171 pass，商用决策表 |
| 2026-05-15 | 同题材 baseline prompt 修复（commit 9704127） |
| 2026-05-16 | Reader Panel 4-persona × 7-dim 上线 |
| 2026-05-17 | Loom Phase 6 项目壳完成（18 commits） |
| 2026-05-17 | 拆书性能剖析报告（雪中悍刀行 229 章） |

---

## 验收标准与回滚路径

每个 Phase 都有**可量化的对比实验**：

| Phase | 对比方法 | 验收指标 | 回滚方式 |
|-------|---------|---------|---------|
| Loom 记忆 | 同书连续 20 章，旧 vs Loom | character_ooc 触发率 ↓ ≥ 20% | feature flag 关闭 |
| Loom 张力 | 批量仿写 10 章，有/无张力 | plot_similarity_score 方差扩大 | 关闭 preflight 张力检查 |
| Loom 评估 | pairwise vs 现有 checker | Kendall's τ ≥ 0.5 | 回到纯规则 checker |
| Loom 文风 | 有/无 style_drift + rhythm | Pearson r ≥ 0.5；评分 5→7/10 | feature flag 关闭 |
| Loom 读者模拟 | reader_sim_score vs 真实读者 | Pearson r ≥ 0.6；评分 7→8.5/10 | 关闭 reader_simulation_service |
| 跨题材改写 | 多套源/目标题材 | full pass ≥ 95%、mapping accuracy ≥ 95% | 已达成（170/171，96-98%） |

---

## 下一棒交接

最近 4 份 session handoff 已收纳到 [handoffs/](./handoffs/README.md)：

- `session-handoff-20260517-phase6.md` — Loom Phase 6 项目壳（最新）
- `session-handoff-20260517.md` — scaffold 三层修复 + 31 commits
- `reader-panel-handoff-20260516.md` — 4-persona × 7-dim 评估
- `baseline-imitation-quality-validation-handoff-20260515.md` — 同题材 prompt 修复长跑

接手建议阅读顺序见 [README.md § 接手建议](./README.md#接手建议阅读顺序)。
