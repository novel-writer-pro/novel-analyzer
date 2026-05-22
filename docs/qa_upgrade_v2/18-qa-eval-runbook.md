# 18. QA Eval Runbook

## 1. 目标

本 runbook 用来说明 QA V2 的评测样本如何被接收、整理、审核、回放与沉淀。

它关注的是流程，不是模型细节：
- 样本从哪来
- 放到哪里
- 谁来判断是否有效
- 什么时候进入 regression / gold / badcase backlog

---

## 2. 三种入口

## 2.1 测试驱动入口

来源：
- 新增测试时发现需要稳定样本
- 修 bug 时需要补 regression asset

适合进入：
- `parser_regression/`
- `query_bank_v2/`

## 2.2 人工审核入口

来源：
- 人工设计高价值问题
- 复盘时提炼出的典型问题

适合进入：
- `difficult_queries/`
- `relation_gold/`
- `timeline_gold/`
- `alias_gold/`

## 2.3 线上 / 回归 badcase 入口

来源：
- retrieval miss
- parser failure
- rerank misorder
- answer hallucination

适合先进入：
- `badcase_backlog/`

先不要直接跳到 gold set，先归因。

---

## 3. 样本 intake 流程

### Step 1：先判断 failure layer
- parser
- retrieval
- rerank
- answer

### Step 2：决定目录
- parser 行为边界 → `parser_regression/`
- 高价值难题 → `difficult_queries/`
- 已明确正确答案与关键章节 → `*_gold/`
- 还没归因清楚 → `badcase_backlog/`

### Step 3：写最小必要字段
- 问题
- bucket / failure_type
- 期望行为
- 来源
- notes

### Step 4：决定是否需要自动化跟进
- 若影响 gate，则要补测试
- 若只是收集探索样本，可先留在数据目录

---

## 4. 人工审核规则

### 4.1 什么样本值得保留
- 能暴露真实系统短板
- 能代表一类稳定边界
- 能在未来升级时复用

### 4.2 什么样本先不要进主集合
- 过度模板化
- 问题表达过于奇怪，和真实用户不相似
- 还不知道期望行为是什么

### 4.3 审核时要避免的误区
- 把“很难答对”误当成“高价值样本”
- 把“模型输出不好看”误当成 parser 问题
- 把一时灵感问题塞进长期 regression 集

---

## 5. replay / 回放建议

当某一类 badcase 增多时，建议这样回放：

1. 先按 `failure_layer` 聚类
2. 再按 `bucket` 聚类
3. 看是否已经有同类 regression 样本
4. 没有的话，补一个高代表性样本
5. 已有的话，检查是否测试面不够 / gate 不够 / diagnostics 不够

重点不是“全量重跑一遍所有东西”，而是：

> **确认 badcase 是否已经被现有资产覆盖。**

---

## 6. 目录职责边界

### `query_bank_v2/`
主问题集，用于 question-type 维度覆盖

### `parser_regression/`
parser 行为边界守卫，不追求海量，只追求边界清楚

### `difficult_queries/`
系统最容易做差的问题集，偏发现短板

### `*_gold/`
人工确认后的金样本，适合做高置信评测

### `badcase_backlog/`
问题回流入口，不是最终归宿

---

## 7. 推荐每周最小节奏

如果开始进入持续优化阶段，建议每周至少做：

1. 新增 1~3 个 parser regression 样本
2. 清理 1 批 badcase backlog，完成归因
3. 从 backlog 中提升 1~2 个高价值样本到 regression 或 gold set
4. 更新一次 audit / handoff 中的“当前新增桶”说明

---

## 8. 什么时候算这套 qa_eval 机制开始真正工作

至少满足：

- 有真实目录骨架
- 有可解释的 bucket
- 有 badcase 回流路径
- 有至少一批人工审核样本
- 有样本被测试或评测消费

当前状态：
- 目录骨架已存在
- bucket 已定义
- 回流路径已文档化
- 真实样本仍待后续逐步填充

---

## 9. 结论

qa_eval 机制的核心不是“把目录建出来”，而是：

> **让每个样本知道自己为什么存在、归谁管理、如何被复用。**

做到这一点，后续 QA V2 的持续优化才不会再次退化成零散经验。
