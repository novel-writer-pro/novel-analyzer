# Difficult Queries

用途：收纳“系统最容易做差”的问题，不追求数量，追求暴露真实短板。

建议文件：
- `ambiguous.jsonl`
- `spoiler_sensitive.jsonl`
- `multi_hop.jsonl`

典型样本特征：
- 指代不清
- 范围隐含
- 需要多章链路
- 如果 parser 理解错，下游基本无解

建议字段：
- `id`
- `branch_id`
- `question`
- `bucket`
- `risk`
- `expected_action`
- `notes`
