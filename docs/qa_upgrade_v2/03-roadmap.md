# 03. Roadmap

## 总原则

Roadmap 按“先稳定、再增强、最后拉高上限”的顺序推进。

新增一条执行纪律：**每个 phase 都必须同时产出代码推进、评估证据、审计记录、handoff 更新。**

---

## 当前状态快照（2026-05-22）

| Phase | 状态 | 当前判断 |
|---|---|---|
| P0 稳定化 | 部分完成 | 第一批正确性修复已落地，但 route-level spoiler-safe planning / 全量 diagnostics 仍未完结 |
| P1 Query Understanding V2 | 已起步 | schema + service skeleton + targeted tests 已有，尚未接入 QA 主链 |
| P2 Retrieval & Graph Fusion | 未正式启动 | contract 与 typed route 方向明确，但未进入主链集成 |
| P3 Evidence-aware Rerank | 设计中 | 目前仍以章节卡片级 rerank 为主 |
| P4 Grounded Answer | 设计中 | 现有 grounding 有 shadow 能力，但 contract 尚未系统化 |
| P5 Data & Evaluation | 初始设计完成 | 指标框架存在，但 gate、badcase 回流、审计模板不足 |

---

## Query Understanding 技术路线（新增）

### Baseline（当前应尽快达成）
- question_type taxonomy 稳定
- entity / alias / time_scope / anti_spoiler 约束稳定抽取
- retrieval preference 可进入 diagnostics
- 至少覆盖 relation / timeline / foreshadow / world_rule / causal_why / character_state

### Advanced（P1 后半段到 P2 前半段）
- ambiguity detection
- query rewrite / canonical rewrite
- implicit constraint extraction（例如“前20章”“第一次”“真正影响主线”）
- decomposition hint（复杂问题标记为 multi-hop / multi-stage）

### Frontier（P2+/P3+ 逐步吸收）
- structured multi-hop retrieval planning
- question-conditioned subgraph planning
- answer expectation aware evidence budgeting
- online badcase feedback → parser regression set 自动沉淀

详细外部模式与采纳顺序，见 [`16-query-understanding-techniques-appendix.md`](./16-query-understanding-techniques-appendix.md)。

### 不建议过早投入的方向
- 一上来引入重 agent planner
- 没有 benchmark 就接强依赖 LLM parser
- 先追求“看起来聪明”，不先把 parser contract 稳住

---

## Phase 0 — 基线稳定化（P0）

### 目标
让现有 QA 主链“可靠可开发”，避免在脏地基上继续叠逻辑。

### 任务
1. 修复 / 核查 `EntityResolutionService` 与 graph node type 对齐问题
2. 把 anti-spoiler filter 前置到 raw retrieval / route 级别
3. 校正 `/api/search-branch` 的 service 调用与参数命名一致性
4. 增加 QA trace 与 diagnostics 导出
5. 增加 keyword/entity/graph type 健康检查脚本

### 交付标准
- QA 基本路径无明显 contract 漂移
- alias expansion 有真实命中数据
- anti-spoiler 命中率不再无意义掉点
- API surface 与前端调用一致

### 推荐周期
- 2~4 天

---

## Phase 1 — Query Understanding V2（P1）

### 目标
把问题从“原始字符串”升级成“结构化查询计划”。

### 任务
1. 定义 `StructuredQueryPlan`
2. 实现 query parse service
3. 提取：
   - question_type
   - entities
   - aliases
   - relation intent
   - time scope
   - answer expectation
4. 为 QA pipeline 接入 query plan
5. 为 diagnostics 导出 query parse 结果
6. 为 ambiguity / parse failure / alias miss 建立 error taxonomy
7. 建立 parser regression set 与 badcase 回流入口

### 交付标准
- 复杂问题可被稳定分型
- 至少 80% 的测试问题可提取出正确实体与时间范围
- retrieval 与 answer 层不再各自猜问题意图
- query parse 错误能被归类到固定 taxonomy，而不是散落在人工反馈里

### 推荐周期
- 4~7 天

### Phase Gate（新增）
- `StructuredQueryPlan` schema 冻结到可供上下游复用的版本
- 至少有一批 `20~30` 条 parser regression tests
- diagnostics 可导出 query plan / parse error / ambiguity flag
- 至少有一份 alias / timeline / difficult query 的 badcase 清单

### Rollback Gate（新增）
以下任一出现则不应把 P1 视为完成：
- parser 接入后 retrieval recall 明显退化且无法解释
- anti-spoiler 约束被 parser 接线破坏
- 实体 canonical 化不稳定，导致 alias 问题回退

---

## Phase 2 — Retrieval & Graph Fusion V2（P2）

### 目标
先把 retrieval 核心 contract 立稳，再把图谱作为可选增强层接入。

### 任务
1. 定义 `EvidenceHit`
2. 先把 lexical/fact/vector/window 输出统一成 evidence objects
3. graph retrieval typed route 化（optional capability）：
   - relation route
   - world_rule route
   - foreshadow route
   - causal route
4. 让 fact lane 扩展到更多 fact_type
5. lane diagnostics 标准化

### 交付标准
- core retrieval 在 graph 关闭时仍可稳定工作
- graph lane 不只是 chapter score，而能输出 path / node / edge evidence
- timeline / foreshadow / relation 类问题召回显著稳定
- retrieval 输出变成可 rerank、可 answer、可 debug 的统一结构

### 推荐周期
- 1~2 周

---

## Phase 3 — Evidence-aware Rerank（P3）

### 目标
把 rerank 从章节卡片级，升级到证据级。

### 任务
1. rerank 输入支持 chunk / fact / graph path / window
2. 设计 lane 内排序 + lane 间统一排序
3. 对不同 question type 做 question-aware rerank 模板
4. 增加 rerank effect benchmark

### 交付标准
- rerank 不再只依赖 summary 质量
- rerank 对复杂问题的排序收益可被 benchmark 证明
- rerank latency 仍可控

### 推荐周期
- 5~8 天

---

## Phase 4 — Grounded Answer Generation（P4）

### 目标
把回答从“会说”升级到“受证据约束地说”。

### 任务
1. 结构化 answer context builder
2. answer mode 显式化：
   - direct_fact
   - multi_hop_explanation
   - conservative_insufficient_context
3. 每条 claim 绑定 evidence bucket
4. 扩展 grounding / verification 输出

### 交付标准
- 回答的证据来源更清晰
- insufficient_context 更可靠
- hallucination / unsupported claim 可观察下降

### 推荐周期
- 1 周

---

## Phase 5 — Data & Evaluation System（P5）

### 目标
让 QA 升级不靠感觉，而靠数据闭环。

### 任务
1. 建标准 query bank
2. 建 question-type 分桶评测集
3. 建 retrieval / rerank / answer 三层指标
4. 建线上 trace 抽样回放机制
5. 为未来训练留出 dataset contract

### 交付标准
- 每次改动都能回答“到底变好没”
- 能区分是 query understanding 问题、retrieval 问题，还是 generation 问题

### Release Gate（新增）
- 没有 regression set，不允许宣称“query understanding 已稳定”
- 没有 retrieval / rerank / answer 三层拆分指标，不允许宣称“QA V2 整体提升”
- 没有 badcase 回流机制，不允许宣称“进入可持续迭代状态”
- 没有专项 audit / handoff 记录，不允许宣称“可持续接力开发”

### 推荐周期
- 与 P1~P4 并行推进，首版 3~5 天起步

---

## 推荐执行顺序

### 最稳顺序
1. P0
2. P1
3. P2
4. P3
5. P4
6. P5 持续并行

### 为什么不是先做 rerank
因为当前最大瓶颈不是“候选排得不够好”，而是：
- 问题没被结构化理解
- 图谱证据没有进入统一中间层
- 上下游 contract 不够清晰

---

## 里程碑定义

### M1 — 稳定可开发
完成 P0

### M2 — 可理解复杂问题
完成 P1

### M3 — 图谱真正进召回主链
完成 P2

### M4 — 可证明排序收益
完成 P3

### M5 — 可证明回答可信度提升
完成 P4 + P5 首版

---

## 建议第一批开发任务（本周就能做）

### 本周必须做
- [ ] alias resolution 对齐核查
- [ ] anti-spoiler filter 前置
- [ ] `/api/search-branch` contract 修正
- [ ] 设计 `StructuredQueryPlan`
- [ ] 写 query parse mock / schema / tests
- [ ] 建立 QA V2 审计记录入口
- [ ] 建立专项 handoff

### 下周开始做
- [ ] `EvidenceHit` contract
- [ ] core retrieval evidence contract（graph 可关闭）
- [ ] graph typed routes（optional）
- [ ] answer context builder v2

这套顺序能保证你后面开发不是返工式推进。
