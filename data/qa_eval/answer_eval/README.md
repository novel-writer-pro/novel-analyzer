# Answer Eval

用途：承接 grounding / insufficient_context / hallucination 等回答级评测样本。

建议文件：
- `grounding_cases.jsonl`
- `insufficient_context.jsonl`

建议字段：
- `id`
- `branch_id`
- `question`
- `expected_answer_mode`
- `expected_evidence`
- `review_notes`

这个目录不替代 retrieval / parser 评测，只负责 answer 层。
