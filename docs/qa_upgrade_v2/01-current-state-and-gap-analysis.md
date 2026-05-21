# 01. 当前状态与差距分析

## 1. 当前 QA 实际链路

当前 `BranchQAService.answer_question()` 的主路径如下：

1. 问题分类：`relation / world_rule / foreshadow / timeline / character / general`
2. 别名扩展：尝试把问题中的 alias 扩成 canonical name
3. 走检索：`RetrievalService.search_branch()`
4. 问题类型补排序：基于关键词 overlap 调整 hit 顺序
5. 组装上下文：
   - chapter hits
   - `WindowArtifact`
   - `GraphService.reasoning_snapshot()`
   - open foreshadowing
   - causal edges
6. 调用 LLM 生成 `BranchQAResult`
7. fallback 时走 degraded answer
8. shadow 跑 `factscore_lite`

---

## 2. 当前系统的优点

### 2.1 已经是一个可用的 Hybrid RAG / GraphRAG
不是单一路径的 BM25 QA，也不是只靠图谱的 GraphQA，而是：
- lexical retrieval
- vector retrieval
- fact retrieval
- graph-assisted retrieval
- graph-assisted context
- LLM answer generation

### 2.2 检索层做得比普通 RAG 更细
当前已具备路由：
- `fts`
- `similarity`
- `like`
- `keyword`
- `entity_exact`
- `relationship`
- `vector`

而且有：
- `RRF fusion`
- rerank
- diagnostics (`raw/reranked/route/latency`)

### 2.3 图谱不是摆设，已经进主链
图谱当前在两个地方参与：
1. `relationship_route` 直接补召回
2. `reasoning_snapshot / foreshadow / causal` 直接补回答上下文

### 2.4 数据物化链已经成型
上游 `analysis_service` 在 artifact 落盘后会连续调用：
- `RetrievalService.materialize_for_artifact()`
- `FactService.materialize_for_artifact()`
- `GraphService.materialize_for_artifact()`
- `DomainDictionaryService.update_from_chapter()`

这说明“分析 → 结构化 → 检索 / 图谱 / 词典”这条数据通路是存在的。

---

## 3. 当前最关键的问题

## 3.1 Query understanding 太弱

当前只做了：
- heuristics 问题分类
- alias expansion
- hit overlap 二次排序

没有做：
- query rewrite
- query decomposition
- constraint extraction（时间、人物、关系、范围）
- ambiguity detection
- multi-hop retrieval planning

### 直接后果
复杂问题无法被拆成清晰的检索任务。例如：
- “A 为什么在前20章对 B 的态度逐步改变？”
- “这个世界规则第一次真正影响主线是在什么时候？”
- “这条伏笔从埋下到兑现的完整链路是什么？”

这类问题本质不是“搜一个词”，而是“先解析意图，再做多段检索，再拼证据”。

---

## 3.2 图谱在 query-time 的利用偏浅

当前图谱主要用法：
- `GraphNode.label LIKE %query%`
- 1-hop 边展开
- snapshot 作为上下文注入

还没有做到：
- multi-hop graph retrieval
- path-constrained retrieval
- graph-aware rerank
- question-type specific subgraph construction
- 结构化 path evidence 输出

### 直接后果
图谱更像“补上下文层”，还不是“显式推理层”。

---

## 3.3 Rerank 粒度偏粗

当前 rerank 输入主要是：
- title
- summary_text
- keyword_list

不是：
- chunk-level evidence
- graph path
- fact evidence list
- source sentence span

### 直接后果
- summary 写得不好的章节可能被错杀
- 真正关键的证据句没有进入 rerank
- rerank 更像“章节卡片重排”，不是“证据重排”

---

## 3.4 上游实体/关键词噪声会污染整条链

已知问题见：
- `docs/foundation-optimization/entity-extraction-noise-diagnosis-20260513.md`

典型噪声：
- 动词短语
- 拟声词
- 章节序数
- 截断残词

它会污染：
- `keyword_list`
- BM25 query bank
- domain dictionary
- retrieval benchmark
- graph node quality

这属于“上游脏一层，下游全脏”。

---

## 3.5 alias resolution 存在高风险实现错位

当前代码有一个很值得优先核查的问题：
- `GraphService` 产出的角色相关节点主类型是 `entity`
- `EntityResolutionService` 却主要查 `GraphNode.node_type == 'character'`

如果线上没有额外写入 `character` 节点，那么：
- alias map 可能经常是空的
- `_resolve_entities_in_question()` 实际不生效

这不是“效果优化项”，而是“功能可能半失效”的风险项。

---

## 3.6 anti-spoiler 过滤时机不理想

当前 `search_branch()` 是：
1. raw retrieval
2. rerank
3. 最后按 `max_chapter` 过滤

问题在于：
- 未来章节参与了 rerank
- 被过滤后不会补回过去章节候选
- 会导致防剧透模式下可用候选变少

应改成：**route-level filter 或 raw hit filter 前置。**

---

## 3.7 API surface 有漂移风险

已看到两处值得检查：
- `/api/search-branch` router 调用方式与 `RetrievalService` 当前公开方法名不一致
- 前端有一处参数叫 `query=`，router 期望 `q=`

这类问题短期不一定炸，但会导致：
- 文档与实现不一致
- 新功能接入成本变高
- debug 成本上升

---

## 4. 当前系统的结构判断

一句话判断：

> 当前 QA 已经拥有“不错的检索地基”和“有潜力的图谱层”，但还缺一层真正把 query understanding、retrieval planning、graph reasoning、grounded generation 串起来的中控层。

也就是说，V2 不应该只是继续加 route，而应该引入：
- structured query plan
- evidence object model
- retrieval-stage contracts
- answer grounding contract

---

## 5. V2 的设计原则

1. **先稳定现有主链，再增强智能性**
2. **query understanding 必须结构化，不再只靠关键词 heuristics**
3. **图谱必须从“补充上下文”升级为“显式召回和推理维度”**
4. **rerank 必须吃更细的证据粒度**
5. **answer generation 必须受证据约束，而不是只看 prompt 拼装质量**
6. **数据准备与评估要从 day 1 一起建设**

---

## 6. P0 优先处理的问题清单

这些问题建议在大改前先修：

### 功能正确性
- [ ] 核查 `EntityResolutionService` 与 `GraphService` 的 node_type 对齐
- [ ] anti-spoiler 过滤前置到 raw retrieval 之前
- [ ] 检查 `/api/search-branch` service 调用与参数一致性

### 可观测性
- [ ] QA 请求级 trace：query → routes → fused hits → rerank → answer
- [ ] graph route hit count / latency / contribution 单独暴露
- [ ] answer grounding rate 和 insufficient_context 进 dashboard

### 数据健康
- [ ] 把 heuristic artifact 与 llm artifact 的消费隔离再复核一遍
- [ ] 为 `keyword_list` / `key_entities` 建健康检查脚本
- [ ] 为 graph node / edge 的类型分布建统计视图

这批做完，才适合进入 V2 主开发。
