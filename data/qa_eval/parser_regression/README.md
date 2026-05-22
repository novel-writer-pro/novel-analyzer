# Parser Regression

用途：这是 Query Understanding P1 gate 的直接证据面。

它与 `query_bank_v2/` 的区别：
- `query_bank_v2/` 关心主问题覆盖
- `parser_regression/` 关心 parser 行为边界是否被破坏

建议文件：
- `alias_and_canonical.jsonl`
- `timeline_and_scope.jsonl`
- `relation_intent.jsonl`
- `world_rule.jsonl`
- `foreshadow.jsonl`
- `ambiguity.jsonl`
- `parse_failure_taxonomy.jsonl`

建议通用字段：
- `id`
- `branch_id`
- `question`
- `bucket`
- `expected`
- `difficulty`
- `source`
- `notes`

维护规则：
1. 新增 parser 行为时，优先补本目录，再宣称能力进入 P1 稳定范围
2. 线上 parser badcase 应优先回流到这里或 `difficult_queries/`
3. bucket 名称必须和 [`docs/qa_upgrade_v2/07-development-plan.md`](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/07-development-plan.md) 对齐
