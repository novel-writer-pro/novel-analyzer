# 17. Parser Regression Playbook

## 1. 目标

本文件定义 Query Understanding 的 regression 样本如何进入仓库、如何被审核、如何被归桶、如何被后续实现消费。

目标不是“多写一些样本”，而是确保每一个 parser 样本都回答以下问题：

1. 它在守哪条 parser 行为边界？
2. 它属于哪个 bucket？
3. 它为什么值得长期回归？
4. 它会回流到测试、数据、badcase 哪一层？

---

## 2. 什么时候要新增 parser regression case

出现以下任一情况，就应考虑新增样本：

### A. 新增 parser 能力
例如：
- 新增 relation intent 抽取
- 新增 world_rule 分类
- 新增 ambiguity flag

### B. 修过 parser bug
例如：
- alias 没 canonical 化
- `前20章` 被错误解析成无范围
- “第一次真正影响主线”被错误归成 general

### C. 线上 badcase 已复现
如果问题已经在真实问答或人工复盘里出现过，就不该只修一次代码而不留回归样本。

### D. 设计 gate 需要证据
如果某项能力被写入 P1 gate，就必须能指向对应 regression bucket。

---

## 3. 样本新增流程

## Step 1：先确定 bucket

优先从现有 bucket 里选：
- `alias_and_canonical`
- `timeline_and_scope`
- `relation_intent`
- `world_rule`
- `foreshadow`
- `ambiguity`
- `parse_failure_taxonomy`

如果放不进去，再新增 bucket；不要轻易发明新名字。

## Step 2：定义“守什么边界”

每个样本要先写清楚边界，例如：
- 这题必须识别为 `relation`，不能退化成 `character_state`
- 这题可以回答不出来，但必须打 `ambiguity=true`
- 这题必须抽出 `chapter_end=20`

## Step 3：决定来源

优先级：
1. 真实 badcase
2. 人工构造但贴近真实小说问法
3. 从现有 gold set 拆出的 parser 专项样本

不要先用模板腔问题把目录填满。

## Step 4：落到 `data/qa_eval/parser_regression/`

每条样本一行 `jsonl`，字段遵循 [`data/qa_eval/parser_regression/README.md`](file:///home/user/novel-analyzer/data/qa_eval/parser_regression/README.md)。

## Step 5：决定要不要同步进测试

如果样本守的是核心行为边界，应同步进入：
- `tests/test_query_understanding_service.py`
或后续的：
- `tests/test_qa_query_plan.py`

不是所有样本都要立刻变成测试，但每个核心 bucket 必须至少有自动化覆盖。

---

## 4. 什么时候新增测试，什么时候只新增数据

### 只新增数据即可
- 还在探索该类问题是否值得长期支持
- 同一 bucket 下先收集更多样本，再决定稳定行为边界

### 数据 + 自动化测试都要加
- 已经修过线上 bug
- 已经写入 roadmap / gate / checklist
- 该行为一旦回退会直接影响 QA 主链可信度

### 先不要加的情况
- 只是语义接近，但边界尚未定义
- 还不知道期望行为到底是什么

这种情况下，应先进入 `badcase_backlog/`，不要急着进入 regression。

---

## 5. badcase → regression 的流转规则

### parser badcase
路径建议：

`badcase_backlog/parser_failures.jsonl`
→ 归因
→ 映射到 bucket
→ 进入 `parser_regression/*.jsonl`
→ 必要时进入自动化测试

### ambiguous / underspecified 问题
不是所有 ambiguous 问题都应该“答对”；很多时候正确行为是：
- 标记 ambiguity
- 触发 conservative answer
- 不假装理解清楚

因此这类样本的 expected action 可以是：
- `flag_ambiguity`
- `allow_conservative_answer`
- `do_not_force_relation_intent`

---

## 6. 样本审核 checklist

新增一个 parser regression case 前，至少确认：

- [ ] bucket 选对了
- [ ] 样本问题像真实小说问法，而不是写给机器看的提示词
- [ ] expected 行为是明确的，不是模糊感觉
- [ ] notes 能解释为什么这个样本值得长期保留
- [ ] 如果它来自 badcase，已记录来源和症状

---

## 7. 最小维护纪律

1. 不要让同类样本在测试文件、audit 文档、qa_eval 目录里用不同名字
2. 不要修 parser 而不留 regression 证据
3. 不要为了看起来“有数据”而批量制造低价值样本
4. bucket 增长前先问：能否归到现有 bucket？

---

## 8. 结论

Parser regression 的核心不是样本数量，而是：

> **每个样本都在守一条明确边界，并且能和测试、badcase、gate 对齐。**

这比“先攒一堆题”更重要。
