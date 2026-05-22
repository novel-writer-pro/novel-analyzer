# 04. Delivery Checklist

> 本清单不是只给开发者自检，也用于评审、提测、上线前 gate、以及 handoff 审计。

---

## 0. 审计通用项（新增）

### 每个阶段都要补齐
- [ ] 已记录本轮目标、输入文档、关键发现
- [ ] 已记录本轮修改文件与修改原因
- [ ] 已记录验证命令 / 验证方式 / 观察结论
- [ ] 已记录 deferred risks 与下一棒建议
- [ ] 已更新 handoff / delivery log / changelog 中至少一个对应入口

### 每个“完成”结论都必须附带证据
- [ ] 有测试 / 命令 / demo / diagnostics 支撑
- [ ] 有明确的 pass / fail / unknown 判断
- [ ] 没有把“设计已写”误报为“能力已上线”

## 1. P0 稳定化 Checklist

### 功能正确性
- [ ] `EntityResolutionService` 能在真实 branch 上产出非空 alias map
- [ ] `GraphService` 与 alias source 的 node_type 契约明确
- [ ] `max_chapter` 在 retrieval 早期生效，而不是 rerank 后再裁
- [ ] `/api/search-branch` service 方法与 router 参数一致
- [ ] 前端调用参数命名与 router 一致

### 可观测性
- [ ] diagnostics 可看到每个 route 的 hit_count / latency
- [ ] diagnostics 可看到 vector route 是否被 skip
- [ ] diagnostics 可看到 rerank 是否 applied
- [ ] QA 结果带 answer_mode / insufficient_context / degraded_reason

### 数据健康
- [ ] heuristic artifact 不污染 retrieval / graph / benchmark
- [ ] keyword_list 质量有巡检脚本
- [ ] graph node_type / edge_type 有分布统计

---

## 2. Query Understanding Checklist

- [ ] 已定义 `StructuredQueryPlan` schema
- [ ] 已定义 question_type taxonomy
- [ ] 已支持实体抽取
- [ ] 已支持时间范围抽取
- [ ] 已支持关系/规则/伏笔/因果意图抽取
- [ ] 已支持 ambiguity 标记
- [ ] 已支持 parse failure taxonomy（至少区分 entity miss / scope miss / ambiguity / unsupported type）
- [ ] 已支持 badcase 回流到 regression set
- [ ] 已有 baseline / advanced / frontier 能力边界说明
- [ ] query parse 结果可进入 diagnostics
- [ ] 复杂 query 有回归样例

### Query Understanding 审计证据
- [ ] 至少一份 query plan JSON 示例
- [ ] 至少一份 parse 失败案例及归因
- [ ] 至少一份 alias / timeline / foreshadow difficult query 回放记录

---

## 3. Retrieval & Graph Fusion Checklist

- [ ] 已定义 `EvidenceHit` schema
- [ ] lexical / fact / graph / vector / window 五类 evidence 可统一输出
- [ ] graph retrieval 有 typed route
- [ ] graph route 可输出 path 或结构化证据
- [ ] fact route 不再只局限于 entity/event
- [ ] retrieval 输出可直接供 rerank / answer builder 使用

---

## 4. Rerank Checklist

- [ ] rerank 支持 chunk-level evidence
- [ ] rerank 支持 fact-level evidence
- [ ] rerank 支持 graph path evidence
- [ ] rerank 输入长度有控制策略
- [ ] rerank latency 有预算
- [ ] rerank effect 有离线 benchmark
- [ ] rerank 失败时有清晰 fallback

---

## 5. Answer Generation Checklist

- [ ] answer context 结构化
- [ ] answer mode 分层
- [ ] direct_fact / multi_hop / conservative 都有样例
- [ ] claim grounding 仍能跑
- [ ] unsupported claim 有降级策略
- [ ] evidence bucket 能映射回 top answer

---

## 6. 数据准备 Checklist

- [ ] query bank 有 question_type 分桶
- [ ] retrieval test set 不只依赖 keyword_list 自动生成
- [ ] 至少有一批人工核查问题集
- [ ] difficult queries 单独收集
- [ ] alias / relation / timeline / foreshadow 各自有样本
- [ ] 数据版本可追踪
- [ ] badcase 有回流入口，不再只靠人工记忆
- [ ] query bank / gold set / manual notes 的来源字段可追踪

---

## 7. 评估 Checklist

### Retrieval
- [ ] Recall@k
- [ ] MRR
- [ ] route contribution
- [ ] graph route contribution

### Rerank
- [ ] rerank delta@k
- [ ] top1 improve ratio
- [ ] latency budget

### Answer
- [ ] grounded answer rate
- [ ] insufficient_context precision
- [ ] unsupported claim ratio
- [ ] human accept rate

### Gate / Audit
- [ ] 本阶段的通过线已明示
- [ ] 本阶段的阻塞条件已明示
- [ ] 本阶段的结果已写入 delivery log 或专项 audit log

---

## 8. 上线前 Checklist

- [ ] 新旧链路可灰度
- [ ] 配置开关可回滚
- [ ] diagnostics 对比新旧版本
- [ ] 至少 1 个真实 branch 跑完回归
- [ ] anti-spoiler 场景专测
- [ ] API contract 文档已更新

---

## 9. 上线后 Checklist

- [ ] 记录 query parse 错误样例
- [ ] 记录 retrieval miss 样例
- [ ] 记录 rerank 错排样例
- [ ] 记录 answer hallucination 样例
- [ ] 每周补充一批 regression queries
- [ ] 每周更新一次错误 taxonomy 分布
- [ ] 每周把新增 badcase 归档到 query bank / difficult set / gold set backlog

---

## 10. 不要做的事

- [ ] 不要先换 embedding 再说
- [ ] 不要先上重 agent planner 再说
- [ ] 不要没有 benchmark 就改主链
- [ ] 不要把 graph 当成 prompt 附件而不进 retrieval contract
- [ ] 不要让 QA 评估继续只依赖自动 query bank
