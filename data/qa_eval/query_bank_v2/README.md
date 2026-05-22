# Query Bank V2

用途：承接 QA V2 的主问题集，按 `question_type` 分桶。

建议文件：
- `entity_fact.jsonl`
- `relation.jsonl`
- `timeline.jsonl`
- `world_rule.jsonl`
- `foreshadow.jsonl`
- `causal_why.jsonl`

每条样本至少建议包含：
- `id`
- `branch_id`
- `question`
- `question_type`
- `target_chapters`
- `target_entities`
- `difficulty`
- `source`

说明：
- 这是主问题集，不等同于 parser regression 集
- 可以包含 easy / medium / hard，但建议保证 question_type 分布清晰
