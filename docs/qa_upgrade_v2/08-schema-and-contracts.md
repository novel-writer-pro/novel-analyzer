# 08. Schema 与 Contract 设计

## 1. 为什么这一层必须先定义

QA V2 的核心不是再多加几个 route，而是把现在隐式散落在各个 service 里的中间状态，显式定义成稳定 contract。

如果没有这层，后面会持续发生：
- query understanding 和 retrieval 各自猜问题意图
- retrieval 和 rerank 对“候选对象”理解不一致
- answer generation 拿到的上下文结构不可控
- diagnostics 很难真正解释系统为什么这么答

因此建议 V2 至少先立住四个核心对象：

1. `StructuredQueryPlan`
2. `EvidenceHit`
3. `AnswerContextBundle`
4. `GroundedBranchQAResult`

---

## 2. StructuredQueryPlan

## 2.1 目标
把原始 question 解析成后续系统都能复用的结构化计划。

## 2.2 推荐字段

```json
{
  "raw_question": "卫图前20章为什么要修养生功？",
  "normalized_question": "卫图前20章为什么要修养生功",
  "question_type": "causal_why",
  "intent": "explain_reason",
  "answer_expectation": "multi_chapter_explanation",
  "entities": [
    {
      "surface": "卫图",
      "canonical": "卫图",
      "entity_type": "character",
      "confidence": 0.98
    },
    {
      "surface": "养生功",
      "canonical": "养生功",
      "entity_type": "skill",
      "confidence": 0.93
    }
  ],
  "relations": [],
  "world_rules": [],
  "events": [],
  "time_scope": {
    "mode": "bounded_range",
    "chapter_start": 1,
    "chapter_end": 20,
    "strict_upper_bound": true
  },
  "constraints": {
    "anti_spoiler": true,
    "must_cite_evidence": true,
    "prefer_multi_hop": true,
    "allow_conservative_answer": true
  },
  "retrieval_plan": {
    "lanes": ["fts", "fact", "graph", "vector", "window"],
    "prefer_graph": false,
    "prefer_timeline": true,
    "prefer_window": true,
    "prefer_causal": true,
    "prefer_foreshadow": false,
    "candidate_limit": 24,
    "final_limit": 6
  },
  "ambiguities": [],
  "diagnostic_notes": []
}
```

## 2.3 必须回答的问题
任何 query parser 至少要产出以下判断：
- 这是什么问题类型？
- 核心实体是谁？
- 有没有章节范围或顺序约束？
- 回答更需要 fact / graph / timeline / foreshadow 哪类证据？
- 如果证据不够，是否允许保守降级？

## 2.4 question_type 建议枚举

| 类型 | 含义 |
|---|---|
| `entity_fact` | 问某个实体发生了什么 |
| `relation` | 问实体之间关系/关系变化 |
| `timeline` | 问主线推进、顺序、阶段变化 |
| `world_rule` | 问世界规则 / 限制 / 设定 |
| `foreshadow` | 问伏笔埋下、回收、对应链路 |
| `causal_why` | 问原因、动机、因果 |
| `character_state` | 问人物态度/动机/状态 |
| `general` | 无法稳定归类的通用问题 |

## 2.5 intent 建议枚举
比 question_type 更细。

| intent | 示例 |
|---|---|
| `locate_fact` | “哪章发生了X” |
| `trace_change` | “关系怎么一步步变化” |
| `explain_reason` | “为什么会这样” |
| `summarize_arc` | “前20章主线如何推进” |
| `identify_rule` | “为什么不能这么做” |
| `resolve_foreshadow` | “这个伏笔什么时候兑现” |

---

## 3. EvidenceHit

## 3.1 目标
统一 retrieval / graph / fact / window / vector 的候选对象。

## 3.2 推荐字段

```json
{
  "id": "ev-branch-12-graph-003",
  "lane": "graph",
  "source_type": "graph_path",
  "branch_id": "...",
  "chapter_index": 12,
  "chapter_span": [11, 12],
  "score": 0.84,
  "raw_score": 2.4,
  "label": "卫图 --relates_to--> 单武举",
  "text": "卫图正式转为单武举弟子，关系由雇佣转为师徒。",
  "evidence": [
    "第12章：卫图正式成为单武举弟子",
    "第11章已铺垫拜师契机"
  ],
  "entities": ["卫图", "单武举"],
  "tags": ["relation", "timeline"],
  "metadata": {
    "edge_type": "relates_to",
    "path_length": 1,
    "node_types": ["entity", "relation", "entity"]
  }
}
```

## 3.3 source_type 建议枚举

| source_type | 含义 |
|---|---|
| `chapter_summary` | 章节摘要卡片 |
| `chunk` | 原始 chunk 文本 |
| `fact` | FactRecord 级证据 |
| `graph_node` | 单节点图谱证据 |
| `graph_path` | 图路径证据 |
| `window` | 多章窗口摘要 |
| `causal_chain` | 因果链证据 |
| `foreshadow_thread` | 伏笔链路证据 |

## 3.4 lane 建议枚举
- `fts`
- `similarity`
- `like`
- `keyword`
- `fact`
- `graph`
- `vector`
- `window`
- `causal`
- `foreshadow`

## 3.5 为什么要 chapter_span
因为很多问题不是“某一章”，而是“某几章共同构成一条链”。

---

## 4. EvidenceBundle

## 4.1 目标
把 `EvidenceHit` 分层组织，供 rerank 和 answer builder 使用。

## 4.2 推荐结构

```json
{
  "query_plan": {},
  "chapter_hits": [],
  "fact_hits": [],
  "graph_hits": [],
  "window_hits": [],
  "causal_hits": [],
  "foreshadow_hits": [],
  "merged_hits": [],
  "diagnostics": {
    "route_counts": {},
    "latency_ms": {},
    "fusion_applied": true,
    "rerank_applied": false
  }
}
```

## 4.3 设计原则
- retrieval 层输出“找到了什么”
- answer builder 再决定“哪些要放进回答上下文”
- 不要在 retrieval service 里过早把所有证据压成字符串

---

## 5. AnswerContextBundle

## 5.1 目标
作为 LLM 生成回答前的最终结构化上下文。

## 5.2 推荐结构

```json
{
  "question": "...",
  "query_plan": {},
  "answer_mode": "multi_hop_explanation",
  "top_evidence": [],
  "chapter_evidence": [],
  "fact_evidence": [],
  "graph_paths": [],
  "window_evidence": [],
  "causal_evidence": [],
  "foreshadow_threads": [],
  "state_summary": {},
  "diagnostic_notes": []
}
```

## 5.3 answer_mode 建议枚举
- `direct_fact`
- `multi_hop_explanation`
- `timeline_summary`
- `relation_trace`
- `rule_explanation`
- `foreshadow_resolution`
- `conservative_insufficient_context`
- `degraded`

---

## 6. GroundedBranchQAResult

## 6.1 目标
在当前 `BranchQAResult` 基础上增加调试、评估、前端消费都能复用的字段。

## 6.2 推荐结构

```json
{
  "answer": "...",
  "answer_mode": "multi_hop_explanation",
  "confidence": 0.72,
  "insufficient_context": false,
  "used_chapters": [10, 11, 12],
  "evidence": [],
  "chapter_evidence": [],
  "window_evidence": [],
  "graph_evidence": [],
  "reasoning_paths": [],
  "graph_signals": [],
  "query_plan": {},
  "top_evidence": [],
  "retrieval_diagnostics": {},
  "grounding_summary": {
    "claim_count": 4,
    "grounded_claim_count": 3,
    "grounding_rate": 0.75,
    "unsupported_claims": ["..."]
  },
  "failure_reason": null,
  "degraded_reason": null
}
```

## 6.3 与现有 `BranchQAResult` 的兼容策略
建议：
- 先做 **向后兼容追加字段**
- 不要立刻破坏现有 API 消费方
- 旧前端无感，新前端可增量消费

---

## 7. Diagnostics Contract

建议 diagnostics 也有统一 schema，不要散在 print / logs 里。

```json
{
  "query": "...",
  "query_plan": {},
  "routes": [
    {"lane": "fts", "hit_count": 8, "latency_ms": 11.2},
    {"lane": "graph", "hit_count": 4, "latency_ms": 6.8}
  ],
  "fusion": {
    "applied": true,
    "candidate_count": 18
  },
  "rerank": {
    "applied": true,
    "candidate_count": 10,
    "latency_ms": 52.3
  },
  "top_evidence_ids": ["..."],
  "answer_mode": "multi_hop_explanation"
}
```

---

## 8. Contract 演进顺序建议

### 第一步
先定义 schema，不一定一次性全部用上。

### 第二步
让 `qa_service` 能产出 `query_plan` 和 `retrieval_diagnostics`。

### 第三步
让 `retrieval_service` 增量产出 `EvidenceHit`。

### 第四步
让 answer builder 从结构化 bundle 生成 prompt。

---

## 9. 最小落地版本

如果想压缩开发量，V2 第一版至少做：
- `StructuredQueryPlan`
- `EvidenceHit`
- `GroundedBranchQAResult.query_plan`
- `GroundedBranchQAResult.retrieval_diagnostics`

这四个做出来，整个系统的开发抓手就会强很多。
