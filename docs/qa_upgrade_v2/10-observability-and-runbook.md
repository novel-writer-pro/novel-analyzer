# 10. Observability 与 Runbook

## 1. 为什么这部分必须单独建设

QA 升级很容易陷入一种假象：
- 回答看起来更聪明了
- 但没人能说清到底是 query understanding 变好了，还是 rerank 碰巧排中了

所以 V2 必须从 day 1 建 observability。

---

## 2. 推荐最小观测面

## 2.1 Query 级 Trace
每个问题至少记录：
- raw question
- structured query plan
- anti-spoiler bound
- route hits
- fused candidates
- rerank before/after
- answer mode
- grounding summary

## 2.2 Route 级指标
- lane hit_count
- lane latency_ms
- unique contribution
- skipped reason

## 2.3 Answer 级指标
- answer latency
- insufficient_context
- degraded_reason
- grounding_rate
- unsupported_claim_count

---

## 3. 建议日志对象

### Query Plan Log
```json
{
  "event": "qa.query_plan",
  "branch_id": "...",
  "question": "...",
  "question_type": "timeline",
  "entities": ["卫图"],
  "time_scope": {"chapter_end": 20}
}
```

### Retrieval Log
```json
{
  "event": "qa.retrieval",
  "branch_id": "...",
  "routes": [
    {"lane": "fts", "hit_count": 5, "latency_ms": 12.1},
    {"lane": "graph", "hit_count": 3, "latency_ms": 7.3}
  ],
  "fusion_applied": true,
  "candidate_count": 14
}
```

### Rerank Log
```json
{
  "event": "qa.rerank",
  "candidate_count": 10,
  "latency_ms": 51.8,
  "applied": true,
  "top_before": [12, 8, 7],
  "top_after": [8, 12, 7]
}
```

### Answer Log
```json
{
  "event": "qa.answer",
  "answer_mode": "multi_hop_explanation",
  "confidence": 0.71,
  "grounding_rate": 0.75,
  "insufficient_context": false
}
```

---

## 4. 推荐 Dashboard 视图

### 4.1 QA 总览
- QA request count
- p50/p95 latency
- degraded rate
- insufficient_context rate
- average grounding rate

### 4.2 Query Understanding
- question_type distribution
- ambiguity count
- anti-spoiler usage count

### 4.3 Retrieval
- lane contribution breakdown
- graph route usage & contribution
- vector route skip ratio
- rerank applied ratio

### 4.4 Answer Quality
- grounded vs unsupported
- question-type accept rate
- top badcase clusters

---

## 5. Runbook：常见问题定位

## 5.1 症状：问答完全答偏
排查顺序：
1. 看 query plan 是否解析错实体/范围
2. 看 route 是否命中正确章节
3. 看 graph lane 是否没触发
4. 看 rerank 是否把正确候选压掉
5. 看 answer builder 是否上下文裁剪错

## 5.2 症状：anti-spoiler 模式下结果很差
1. 看未来章节是否仍进入 raw route
2. 看 rerank 前是否做了章节过滤
3. 看 bounded range 后有没有补足候选

## 5.3 症状：alias 问题回答差
1. 看 alias map 是否为空
2. 看 node_type 是否错位
3. 看 canonical expansion 是否进入 query plan

## 5.4 症状：图谱题没有比 BM25 好多少
1. 看 graph typed route 是否真正触发
2. 看 graph route 是否只返回 chapter score，没返回 path
3. 看 rerank 是否吃不到 graph evidence

## 5.5 症状：rerank 很慢但收益不明显
1. 看 candidate_count 是否过大
2. 看是否仍只用 summary_text 做 rerank
3. 看 question-type bucket 下是否只有少数题型受益

---

## 6. 推荐导出物

建议新增 CLI / debug 导出能力：
- `qa-query-plan`
- `qa-evidence-dump`
- `qa-rerank-compare`
- `qa-answer-grounding`

即使先不做正式 CLI，也建议能在 service 层 dump JSON。

---

## 7. 上线观察期建议

### Day 1
- 盯 degraded rate
- 盯 anti-spoiler 请求表现
- 盯 graph route latency

### Day 2~3
- 抽 30 条 QA trace 人工检查
- 收集 alias / timeline / foreshadow badcase

### Week 1
- 做第一轮 error taxonomy：
  - parse error
  - retrieval miss
  - rerank misorder
  - grounding failure
  - insufficient_context misfire

---

## 8. 结论

V2 的可运维性不是锦上添花，而是基本盘。

如果没有 observability：
- 你会不断优化，但不知道优化的是哪一层
- 你会积累很多主观印象，但没有可复盘证据

所以推荐：**P0 就把最小 trace 打起来。**
