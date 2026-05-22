# QA Eval Data Skeleton

本目录承接 QA V2 的评测、回归、gold set、badcase 回流数据骨架。

当前只创建**目录 contract + README**，不填入伪造样本。

原则：

1. 真实样本优先来自：
   - 已验证测试场景
   - 人工审核问题集
   - 线上 badcase 回流
2. 未经验证的数据不要为了“看起来完整”而占位
3. `jsonl` 是默认数据格式；`README.md` 负责说明每个子目录的用途和字段 contract

目录说明：

- `query_bank_v2/`：question-type 分桶的主 query bank
- `difficult_queries/`：高失败率 / 高歧义 / 高剧透敏感问题集
- `alias_gold/`：alias → canonical 金样本
- `relation_gold/`：关系变化问题金样本
- `timeline_gold/`：阶段推进 / 主线演化金样本
- `parser_regression/`：Query Understanding 的行为边界回归集
- `answer_eval/`：grounding / insufficient_context 等回答级评测样本
- `badcase_backlog/`：线上或人工发现的问题回流入口

对应设计文档：
- [`docs/qa_upgrade_v2/05-data-preparation.md`](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/05-data-preparation.md)
- [`docs/qa_upgrade_v2/07-development-plan.md`](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/07-development-plan.md)
- [`docs/qa_upgrade_v2/16-query-understanding-techniques-appendix.md`](file:///home/user/novel-analyzer/docs/qa_upgrade_v2/16-query-understanding-techniques-appendix.md)
