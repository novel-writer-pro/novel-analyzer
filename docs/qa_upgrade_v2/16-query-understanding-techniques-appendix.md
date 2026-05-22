# 16. Query Understanding Techniques Appendix

## 1. 目标

本附录用于把 Query Understanding 相关的外部常见模式，翻译成适合 novel-analyzer 当前 QA V2 路线的**可采纳技术地图**。

它不直接等同于“马上都要实现”，而是回答 4 个问题：

1. 行业内常见会做什么
2. 哪些适合我们当前阶段
3. 哪些必须等地基稳定后再做
4. 哪些看起来先进，但现在做会分散主线

---

## 2. 本轮参考模式来源（审计用途）

本附录基于当前会话已收集到的外部模式线索整理，不额外扩大成独立研究报告。

本轮直接参考到的代表性模式包括：

- `ForgeRAG`：单独的 QueryPlan / Query Understanding 阶段，把意图识别、路由与 expansion 放到 retrieval 前
- `SimpleMem`：QueryProcessor 负责 temporal filters、modality / depth preference、routing hints
- 若干 hybrid RAG / agentic search 实现：将 query understanding 视为 retrieval 的前置控制层，而不是 prompt 拼装小工具

这些模式的共同点不是“都在用 LLM”，而是：

> **都把 query 从原始字符串升级成可供下游复用的结构化控制对象。**

这与当前 [`StructuredQueryPlan`](./08-schema-and-contracts.md) 的方向一致。

---

## 3. 技术地图：Baseline / Advanced / Frontier

## 3.1 Baseline（当前阶段最该做）

这些能力最适合在现阶段投入，因为它们直接支撑 P1 gate，又不会明显打散现有主链。

### A. Intent / question_type classification
- 把问题稳定归到 relation / timeline / foreshadow / world_rule / causal_why / character_state 等桶
- 作用：避免 retrieval / rerank / answer builder 各自猜问题意图

### B. Constraint extraction
- 提取：
  - 章节范围
  - anti-spoiler 上界
  - 顺序 / “第一次” / “前20章” / “到第8章为止”
- 作用：让 spoiler-safe retrieval 和 timeline 类问题更可靠

### C. Entity grounding + alias normalization
- surface form → canonical entity
- 兼容别名、口语指代、同一人物的阶段化称呼
- 作用：降低 alias miss 对 retrieval 的连锁污染

### D. Retrieval preference inference
- query understanding 输出 `prefer_timeline / prefer_graph / prefer_causal / prefer_foreshadow`
- 作用：让 structured query plan 真正影响 retrieval lane，而不是只做展示字段

### E. Basic ambiguity flagging
- 对这些情况至少打旗标：
  - 人称/代称指向不明
  - 时间范围过宽
  - 问题目标缺失（“为什么会这样”但没主语）
- 作用：为 conservative answer 和后续 badcase taxonomy 留出口

---

## 3.2 Advanced（P1 后半段 / P2 前半段）

这些能力应建立在 Baseline 稳定之后，否则容易把问题从“没 parse 清楚”升级成“加复杂逻辑后更难 debug”。

### A. Query rewrite / canonical rewrite
- 把原问题改写成更适合 retrieval 的 canonical form
- 例如：
  - 显式补实体 canonical
  - 把口语化关系问题改成更明确的 retrieval cue
- 注意：rewrite 不应覆盖 raw question，而应保留 raw + rewritten 双轨

### B. Multi-view expansion
- 为同一个问题生成：
  - lexical-friendly rewrite
  - graph-friendly relation phrasing
  - timeline-friendly state phrasing
- 作用：提升 hybrid retrieval 命中率

### C. Implicit constraint resolution
- 识别“真正影响主线”“第一次”“逐步变化”“从埋下到兑现”这类隐式任务词
- 作用：让 query plan 不只看显式关键词

### D. Decomposition hint
- 对复杂问题只先做 lightweight decomposition：
  - single-hop
  - multi-hop
  - chain reconstruction
  - compare / trace_change
- 作用：为 graph route、window route、answer mode 提供明确上游信号

### E. Multilingual / style variance handling
- 同一实体在中文长篇里可能有：
  - 全称
  - 昵称
  - 代称
  - 称谓变化
- 这类问题在小说场景比通用 QA 更常见，应视为核心能力，不是边角兼容

---

## 3.3 Frontier（P2+/P3+ 再考虑）

这些方向很有价值，但只有在 query plan、evidence contract、diagnostics 都稳定后才值得上。

### A. Structured multi-hop retrieval planning
- query understanding 直接输出多步计划：
  - 先找实体
  - 再找关系变化
  - 再补 timeline / causal evidence
- 风险：如果 observability 不够，会让错误定位成本暴涨

### B. Question-conditioned subgraph planning
- 按问题类型构图，而不是把整块 graph snapshot 灌给下游
- 例如：
  - relation 问题优先 relation edges
  - foreshadow 问题优先 open/payoff path
  - timeline 问题优先 follows / advances_to

### C. Answer-expectation-aware evidence budgeting
- query plan 直接控制证据预算：
  - direct_fact 少量高置信证据
  - multi_hop_explanation 更多链路证据
- 前提：`EvidenceHit` / `AnswerContextBundle` 已稳定

### D. Online feedback loop
- 把线上 badcase 自动回收到：
  - parser regression set
  - difficult query set
  - taxonomy dashboard
- 这是“可持续迭代”真正成立的标志之一

---

## 4. 对当前仓库最适合的采纳顺序

### 现在就该做
1. 稳定 question_type taxonomy
2. 稳定 entity / alias / time scope / anti-spoiler
3. 稳定 retrieval preference 输出
4. 增加 ambiguity / parse failure taxonomy

### 等 regression surface 扩大后再做
1. canonical rewrite
2. multi-view expansion
3. decomposition hint

### 等 EvidenceHit / graph typed route 成型后再做
1. multi-hop planning
2. question-conditioned subgraph planning
3. answer-budget-aware planning

---

## 5. 评估 hooks（必须与实现同时建设）

任何 query understanding 技术升级，都建议同步补以下观测点：

### Offline
- question_type accuracy
- entity grounding accuracy
- time scope accuracy
- ambiguity recall
- parse failure bucket distribution

### Online
- query plan 命中 question bucket 的分布
- rewrite 是否提升 retrieval hit rate
- parser flag 是否降低 insufficient_context 误判
- 哪类 badcase 正在持续增长

### 不要只看
- answer 是否更像人说话
- demo 是否更顺

因为这会掩盖 parser、retrieval、grounding 哪一层真正变好了。

---

## 6. 当前不建议做的事

在现阶段，不建议优先投入：

- 重 agentic planner
- 没有回归集就引入强依赖 LLM parser
- 复杂 self-reflection query understanding pipeline
- 先做模型升级，再补 parser observability

原因很简单：

> 现在最大的收益来自“让 query plan 可解释、可回归、可进 lane”，而不是让它看起来更聪明。

---

## 7. 与本项目当前状态的关系

截至当前文档状态：

- `StructuredQueryPlan` 方向已立住
- `QueryUnderstandingService` 骨架已起步
- 自动化测试只覆盖 timeline/time_scope/anti-spoiler、alias→canonical、局部 retrieval preference
- ambiguity / parse failure taxonomy / world_rule / foreshadow / diagnostics export 仍属未证明能力

因此本附录的实际用途是：

1. 帮助未来接手人判断“下一步该补哪种能力”
2. 防止团队在 P1 过早跳到 P3/P4 风格的复杂度
3. 给 badcase 回流和 regression 设计提供外部模式参照

---

## 8. 结论

对 novel-analyzer 来说，Query Understanding 的正确演进顺序不是：

> 更强模型 → 更复杂 planner → 希望结果更好

而应该是：

> 先把 query plan 变成稳定 contract，再把它变成 retrieval 控制层，最后才考虑更重的推理规划。

这也就是 QA V2 当前最值得坚持的路线。
