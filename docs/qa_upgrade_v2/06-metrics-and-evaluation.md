# 06. 指标与评估设计

## 1. 评估原则

QA V2 不能只看一个总分。至少要拆三层：

1. Query understanding
2. Retrieval / rerank
3. Answer quality / grounding

否则会出现：
- retrieval 提升了，但答案没提升
- answer 写得更顺了，但 grounding 变差了
- graph route 很贵，但实际没贡献

---

## 2. Query Understanding 指标

## 2.1 结构化解析正确率
建议统计：
- question_type accuracy
- entity extraction accuracy
- relation intent accuracy
- time scope extraction accuracy
- ambiguity detection recall

## 2.2 Plan usefulness
比起 parser 本身，更重要的是它是否让 downstream 变好：
- retrieval hit rate 提升多少
- graph route 是否更精准触发
- answer mode 是否更合理

---

## 3. Retrieval 指标

## 3.1 基础指标
- Recall@1 / @3 / @5 / @10
- MRR
- hit by question_type

## 3.2 分路指标
对每条 route 分开看：
- hit_count
- contribution_rate
- unique_contribution_rate
- latency_ms

特别需要看：
- graph route 的独立贡献
- vector route 的真实贡献
- keyword route 是否被噪声污染

## 3.3 anti-spoiler 指标
- spoiler-safe recall@k
- 过滤前后命中损失
- filtered-away top-hit ratio

---

## 4. Rerank 指标

## 4.1 排序收益
- top1 improve ratio
- top3 improve ratio
- MRR delta before/after rerank
- question_type bucket delta

## 4.2 代价指标
- rerank latency p50 / p95
- candidate_count avg / p95
- rerank skipped ratio

## 4.3 证据级收益
如果 V2 引入 `EvidenceHit`，还应统计：
- chunk evidence promoted ratio
- graph path evidence promoted ratio
- fact evidence promoted ratio

---

## 5. Answer 指标

## 5.1 基础质量
- answer accept rate
- insufficient_context precision
- insufficient_context recall
- degraded answer rate

## 5.2 grounding 质量
- claim grounding rate
- unsupported claim ratio
- evidence coverage ratio
- answer-evidence consistency

## 5.3 类型专项指标
### relation
- 是否能回答关系类型
- 是否能给出变化章节

### timeline
- 是否能覆盖关键推进节点
- 是否顺序正确

### foreshadow
- 是否区分“埋下”和“兑现”
- 是否能给出章节链路

### world_rule
- 是否给出规则内容
- 是否给出规则影响主线的具体章节/事件

---

## 6. 推荐评测矩阵

| 维度 | easy | medium | hard |
|---|---:|---:|---:|
| entity_fact | ✓ | ✓ | - |
| relation | ✓ | ✓ | ✓ |
| timeline | - | ✓ | ✓ |
| foreshadow | - | ✓ | ✓ |
| world_rule | ✓ | ✓ | ✓ |
| causal_why | ✓ | ✓ | ✓ |

---

## 7. 实验设计建议

## 7.1 单变量实验
不要一次改很多层。

### 推荐顺序
1. 只开 query plan
2. 只开 graph typed route
3. 只开 evidence-aware rerank
4. 只开 grounded answer mode

分别看收益。

## 7.2 A/B 维度
- old QA vs new QA
- with query plan vs without
- with graph route v2 vs old relationship route
- chapter-level rerank vs evidence-level rerank

## 7.3 回归集
固定一批 regression queries：
- alias
- relation
- timeline
- foreshadow
- anti-spoiler
- insufficient context

每次改动都必须过。

---

## 8. Gate 设计（新增）

## 8.1 Phase Gate

### P0 Gate
- alias / anti-spoiler / API contract 三类 correctness 问题有回归验证
- diagnostics 至少能看到 query → route → rerank → answer 基本链路

### P1 Gate
- parser regression set 可稳定运行
- 至少可统计 entity / time scope / question_type 三项准确度
- ambiguity / parse failure 不再只留在人工备注里

### P2 Gate
- `EvidenceHit` / evidence bundle 已能稳定导出
- graph lane 贡献可单独评估

### P3 Gate
- rerank 收益可被证明，且 latency 不突破预算

### P4 Gate
- grounded answer 指标提升，unsupported claim 不恶化

## 8.2 Release Gate

以下任一不满足，不应把 QA V2 对外视为“进入稳定升级态”：
- 没有固定 regression queries
- 没有 question-type bucket 指标
- 没有 badcase taxonomy
- 没有至少一份 handoff / audit / delivery log 可供下一棒追溯

## 8.3 Rollback Gate

以下任一出现，应阻止继续放量或宣称阶段完成：
- parser 接线导致 spoiler-safe recall 显著下降
- rerank 提升不成立且 latency 明显上升
- answer grounding rate 下降但未被 observability 抓到根因

---

## 9. 推荐产出物

### 离线
- `qa_query_parse_eval.json`
- `qa_retrieval_eval.json`
- `qa_rerank_eval.json`
- `qa_answer_eval.json`

### 在线/诊断
- 每个问题的 query plan
- lane diagnostics
- fused evidence snapshot
- rerank before/after
- answer grounding summary

---

## 10. 最小可用验收标准

建议先设一个现实目标，而不是一步到位。

### M1
- P0 完成
- diagnostics 稳

### M2
- complex query retrieval recall 有明显提升
- relation / timeline / foreshadow 题型不再明显崩

### M3
- answer grounding rate 提升
- insufficient_context 误判下降

---

## 11. 结论

V2 成不成功，不是看 demo 时回答多自然，而是看以下三个问题能不能稳定回答：

1. 问题理解是否更准？
2. 检索证据是否更对？
3. 回答是否更可证明？

所以评估体系必须围绕这三层建设。
