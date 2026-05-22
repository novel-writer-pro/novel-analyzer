# 05. 数据准备

## 1. 为什么数据准备是 QA V2 的核心

问答能力升级不是只改 service。它高度依赖：
- 上游抽取质量
- query bank 质量
- 图谱节点边质量
- alias 质量
- 可解释的 benchmark 数据

如果数据层没有一起建设，后面会出现：
- 你不知道是 query parse 错，还是 retrieval 错
- 你不知道 rerank 是否真的有收益
- 你不知道图谱路线到底帮了多少

---

## 2. 数据层的五类对象

## 2.1 原始内容层
- 原始章节文本
- 章节标题
- branch / chapter 元数据

## 2.2 分析产物层
- `chapter_summary`
- `key_entities`
- `key_events`
- `continuity_notes`
- facts raw output
- analysis raw output

## 2.3 检索物化层
- `retrieval_documents`
- `retrieval_chunks`
- `chunk_embeddings`
- `query_hints`
- `keyword_list`

## 2.4 图谱层
- `graph_nodes`
- `graph_edges`
- `fact_records`
- causal links
- foreshadow lifecycle state

## 2.5 QA 评测层
- query bank
- labeled difficult queries
- answer reference / evaluation notes
- route diagnostics samples

---

## 3. 现在最需要准备的数据集

## 3.1 Query Bank V2

当前自动 query bank 主要来自 `keyword_list`，这适合做 retrieval baseline，但不够支持 QA V2。

V2 建议至少分 6 桶：

1. `entity_fact`
   - 问一个人/物/地发生了什么
2. `relation`
   - 两者关系如何、何时变化
3. `timeline`
   - 某个主线/状态怎么推进
4. `world_rule`
   - 规则是什么、何时生效
5. `foreshadow`
   - 伏笔埋下/兑现链路
6. `causal_why`
   - 为什么会发生、原因链是什么

### 建议字段

```json
{
  "id": "qa-weitu-0001",
  "branch_id": "...",
  "question": "卫图为什么要修养生功？",
  "question_type": "causal_why",
  "target_chapters": [1,2,3],
  "target_entities": ["卫图", "养生功"],
  "must_have_evidence": ["卫图觉醒命格", "修行筹备"],
  "difficulty": "easy",
  "source": "manual"
}
```

---

## 3.2 Difficult Query Set

必须单独收集一批“当前系统最容易做差”的问题。

建议重点收：
- 别名问题：`卫图 / 那个少年 / 单武举弟子`
- 多章变化问题：`关系如何变化`
- 规则生效问题：`规则第一次影响主线`
- 伏笔回收问题：`哪章兑现`
- 剧透敏感问题：`前20章`

### 这批数据的价值
它们不是拿来做漂亮平均分，而是拿来发现系统真实短板。

---

## 3.3 Alias Dataset

需要专门准备一份 alias 数据，不然 entity resolution 很难评估。

建议格式：

```json
{
  "branch_id": "...",
  "canonical": "卫图",
  "aliases": ["那个少年", "卫图小子", "单武举弟子"],
  "confidence": "human_verified"
}
```

### 用途
- 测试 alias expansion
- 测试 graph node merge
- 测试 query understanding

---

## 3.4 Relation / Timeline Gold Cases

这两类问题建议做小规模人工标注。

### Relation Gold
- 主体A
- 主体B
- 关系类型
- 关系变化章节
- 关键证据章节

### Timeline Gold
- 主线名
- 起始章节
- 关键推进点
- 状态转折点
- 结束/未结束状态

这批数据不用大，前期 30~50 条就非常有价值。

---

## 4. 数据清洗优先级

## P0：先做不会错的清洗
- heuristic artifact 隔离
- `key_entities` 中章节序数剔除
- 截断词检测
- 拟声词检测
- 长句型词条剔除

## P1：再做低风险增强
- alias 人工补充
- world_rule 候选补齐
- relation phrase 清洗

## P2：再做更复杂的增强
- better entity extraction prompt
- entity disambiguation
- graph node merge policy

---

## 5. 训练/微调数据准备（未来可选）

如果未来要做 query parser / reranker 微调，建议从现在开始按 contract 留数据。

## 5.1 Query parser dataset

输入：
- question

输出：
- structured query plan

## 5.2 Rerank dataset

输入：
- question
- candidate evidence list

输出：
- relevance label / pairwise preference

## 5.3 Grounded answer dataset

输入：
- structured answer context

输出：
- answer
- claim-evidence mapping
- grounded / unsupported 标签

---

## 6. 数据构建顺序建议

### 第一步：先拿现有 branch 做半自动数据
- 从 `retrieval_documents` 自动生成 easy queries
- 从 `graph_nodes/edges` 自动生成 relation / rule / foreshadow 候选问题
- 从 `WindowArtifact` 自动生成 timeline 候选问题

### 第二步：人工筛一批 high-value set
目标不是全标，而是先做：
- 100 条 retrieval+QA 基准题
- 30 条 difficult query
- 30 条 alias / relation / timeline 金样本

### 第三步：持续回收线上 badcase
每次真实 QA 出现：
- 检索 miss
- rerank 错排
- answer 幻觉
- insufficient_context 误判

都进入 dataset backlog。

---

## 7. 推荐目录结构

建议未来在仓库里补：

```text
runs/qa_eval/
  query_bank_v2/
  difficult_queries/
  alias_gold/
  relation_gold/
  timeline_gold/
  answer_eval/
```

如果不想放 `runs/`，也可以单独建：

```text
data/qa_eval/
```

当前仓库已建议落下真实目录骨架：
- [`data/qa_eval/README.md`](file:///home/user/novel-analyzer/data/qa_eval/README.md)
- [`data/qa_eval/parser_regression/README.md`](file:///home/user/novel-analyzer/data/qa_eval/parser_regression/README.md)
- [`data/qa_eval/badcase_backlog/README.md`](file:///home/user/novel-analyzer/data/qa_eval/badcase_backlog/README.md)

这样后续接手人不需要先猜“数据应该放哪”，可以直接按 README contract 开始补真实样本。

### 推荐采用的仓库内布局（新增）

为了让 regression、gold set、badcase 回流、人工备注能长期共存，建议在 `data/qa_eval/` 下进一步明确为：

```text
data/qa_eval/
  query_bank_v2/
    README.md
    entity_fact.jsonl
    relation.jsonl
    timeline.jsonl
    world_rule.jsonl
    foreshadow.jsonl
    causal_why.jsonl
  difficult_queries/
    README.md
    ambiguous.jsonl
    spoiler_sensitive.jsonl
    multi_hop.jsonl
  alias_gold/
    aliases.jsonl
  relation_gold/
    relation_changes.jsonl
  timeline_gold/
    timeline_arcs.jsonl
  parser_regression/
    README.md
    alias_and_canonical.jsonl
    timeline_and_scope.jsonl
    relation_intent.jsonl
    world_rule.jsonl
    foreshadow.jsonl
    ambiguity.jsonl
    parse_failure_taxonomy.jsonl
  answer_eval/
    grounding_cases.jsonl
    insufficient_context.jsonl
  badcase_backlog/
    retrieval_miss.jsonl
    rerank_misorder.jsonl
    parser_failures.jsonl
    answer_hallucination.jsonl
```

这里最关键的是 `parser_regression/`：
- 它是 Query Understanding P1 gate 的直接证据面
- 它不等同于 query bank，而是专门用来守 parser 行为边界
- 它的桶划分应与 [`07-development-plan.md`](./07-development-plan.md) 中的 regression buckets 对齐

---

## 7.1 推荐文件 contract（新增）

建议统一使用 `jsonl`，每行一个样本，便于：
- 增量追加
- 人工 diff
- 按桶抽样
- CLI / notebook / 脚本复用

### parser regression 样本建议字段

```json
{
  "id": "parser-rel-0001",
  "branch_id": "...",
  "question": "卫图和单武举的关系是怎么一步步变化的？",
  "bucket": "relation_intent",
  "expected": {
    "question_type": "relation",
    "intent": "trace_change",
    "entities": ["卫图", "单武举"],
    "time_scope": null,
    "ambiguity": false
  },
  "difficulty": "medium",
  "source": "manual",
  "notes": "要求识别为关系变化，不是普通人物状态问题"
}
```

### difficult query 样本建议字段

```json
{
  "id": "difficult-amb-0003",
  "branch_id": "...",
  "question": "他为什么后来不再信任她？",
  "bucket": "ambiguous",
  "risk": ["missing_subject", "missing_object", "needs_context"],
  "expected_action": "flag_ambiguity",
  "notes": "重点不在答对，而在不要假装理解清楚"
}
```

### badcase backlog 样本建议字段

```json
{
  "id": "badcase-parser-0012",
  "observed_at": "2026-05-22",
  "branch_id": "...",
  "question": "这个规则第一次真正影响主线是什么时候？",
  "failure_layer": "parser",
  "failure_type": "world_rule_scope_miss",
  "symptom": "被误分类为 general，未触发 world_rule preference",
  "next_bucket": "world_rule",
  "status": "open"
}
```

---

## 8. 数据准备的验收标准

- [ ] easy query bank 可自动生成
- [ ] difficult queries 有人工筛选集合
- [ ] alias dataset 可用于回归测试
- [ ] 至少有 relation / timeline / foreshadow 三类 gold set
- [ ] 数据可版本化、可复跑、可增量扩展
- [ ] parser regression buckets 已和 query understanding gate 对齐
- [ ] badcase backlog 能回灌到 parser_regression / difficult_queries / gold set

---

## 9. 结论

V2 不缺“更多 query”，缺的是：
- **结构更好的 query**
- **更可靠的 gold cases**
- **能支撑图谱问答升级的数据集**

一句话：

> 先把 dataset contract 建起来，后面的 query understanding、retrieval fusion、rerank、grounding 才有真正的优化抓手。
