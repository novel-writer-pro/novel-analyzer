# Badcase Backlog

用途：作为线上 / 人工 / 回归复盘中发现问题的统一回流入口。

建议文件：
- `retrieval_miss.jsonl`
- `rerank_misorder.jsonl`
- `parser_failures.jsonl`
- `answer_hallucination.jsonl`

建议通用字段：
- `id`
- `observed_at`
- `branch_id`
- `question`
- `failure_layer`
- `failure_type`
- `symptom`
- `next_bucket`
- `status`

维护规则：
1. badcase 先进入 backlog，再决定回流到 parser_regression / difficult_queries / gold set
2. 不要让 badcase 只存在聊天记录或临时笔记里
