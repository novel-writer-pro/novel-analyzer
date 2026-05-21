# 03. Roadmap

## 总原则

Roadmap 按“先稳定、再增强、最后拉高上限”的顺序推进。

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

### 交付标准
- 复杂问题可被稳定分型
- 至少 80% 的测试问题可提取出正确实体与时间范围
- retrieval 与 answer 层不再各自猜问题意图

### 推荐周期
- 4~7 天

---

## Phase 2 — Retrieval & Graph Fusion V2（P2）

### 目标
让图谱从“辅助上下文”升级成“显式召回维度”。

### 任务
1. 定义 `EvidenceHit`
2. graph retrieval typed route 化：
   - relation route
   - world_rule route
   - foreshadow route
   - causal route
3. 让 fact lane 扩展到更多 fact_type
4. 把 chunk/fact/graph/window 统一成 evidence objects
5. lane diagnostics 标准化

### 交付标准
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

### 下周开始做
- [ ] graph typed routes
- [ ] `EvidenceHit` contract
- [ ] answer context builder v2

这套顺序能保证你后面开发不是返工式推进。
