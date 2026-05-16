# Session Handoff — 2026-05-16

> 本会话进度跟踪 + 待办 checklist。每完成一项立即勾选，落 CHANGELOG + commit。
> 上一棒：[`session-handoff-20260515-final.md`](./session-handoff-20260515-final.md)

---

## 0. 本会话上下文

| 项 | 值 |
|---|---|
| 分支 | `build` |
| 数据库 | PostgreSQL 17.5 @ 127.0.0.1:5432 / d2 / novel_analyzer |
| 数据 | 43 novels / 40 branches / 363k graph_edges / 17k segments / 2695 chunks (1024 维 bge-m3) |
| LLM 网关 | `http://34.97.18.233:65432/v1` · 8 个模型 · claude-haiku-4.5 / claude-sonnet-4.6 / deepseek-v4-flash / deepseek-v4-pro 等 |
| Embedding | ONNX bge-m3 INT8 · `/home/user/migrate/bge-m3-onnx-int8/model_quantized.onnx` (544 MB) |
| Rerank | ONNX bge-reranker-v2-m3 · `.cache/rerank-models/` 已就绪 |
| 原始小说 | `/home/user/migrate/novels/` · 9 个 txt · 40 MB |

---

## 1. 已完成 ✅

### 环境恢复（5/15 → 5/16 衔接）

- [x] PG dump 恢复（`/home/user/migrate/novel_analyzer.sql.gz` → 27 张表全数据，关 FK 跑 COPY 解决跨版本恢复问题）
- [x] `.env.local` LLM 切到外部网关 `http://34.97.18.233:65432/v1`
- [x] `.env.local` Embedding `MODEL_PATH=/home/user/migrate/bge-m3-onnx-int8`
- [x] Rerank ONNX provider runtime 验证（OnnxCrossEncoderRerankProvider，scores 正常）
- [x] Embedding ONNX provider runtime 验证（1024 维真实向量）
- [x] `make smoke-external` 全绿
- [x] 后端 `/health` 200 OK，`tmux novel-api` session 在跑

### 文档

- [x] [`docs/runbook/postgres-ops-cheatsheet.md`](./runbook/postgres-ops-cheatsheet.md) · PG 运维速查 14 章
- [x] [`docs/README.md`](./README.md) 必读列表挂入

---

## 2. 进行中 🔄

### LLM-1: 切 claude-haiku-4.5 + 并发节流 ✅ DONE

commit `7e1a15c feat(llm): claude-haiku-4.5 + shared token-bucket rate limiter`

- [x] `config/settings.py` 加 `llm_max_concurrent_requests` / `llm_requests_per_second` / `llm_check_every_n_seconds` / `llm_max_bucket_size`
- [x] `llm/client.py` 用 `InMemoryRateLimiter` 包 `ChatOpenAI`（`lru_cache` 共享 bucket）
- [x] `.env.local` 切到 `claude-haiku-4.5` + 设默认节流（rps=1.5 / bucket=3 / concurrent=2）
- [x] `tests/test_llm_client.py` 4 个测试全 pass
- [x] runtime smoke：`build_chat_model().invoke(...)` 3.8s 返回真实输出
- [x] CHANGELOG / commit

### DATA-1: novel_sources.source_path 修复 ✅ DONE

commit `chore(data): relink novel_sources.source_path via SHA256 dedup`

- [x] 写 `scripts/dev/relink_novel_sources.py`（dry-run 默认 + `--apply` 才写库）
- [x] 匹配规则：SHA256 only（标题不可信）
- [x] dry-run 报告：20 already-OK / 7 will-relink / 16 unmatched
- [x] apply 成功 7 行（青华系列 4 / 诛仙-fixed 1 / 魔师 2）
- [x] 16 unmatched 故意保留 → 哈希不同强换会导致章节 offset 错位
- [x] CHANGELOG / commit

---

## 3. 待办（下一项进行中）📋

| 优先级 | 项 | 备注 | 阻塞 |
|---|---|---|---|
| P0 | LLM-1 (本会话进行中) | 切 haiku + 节流 | 无 |
| P0 | DATA-1 (本会话进行中) | source_path relink | 无 |
| P1 | **Option B**: 退役 WSGI fallback | `apps/api/app/main.py` 删 `/api/review-batch-execute` dispatch 块 + drop `application` callable + drop `make api-wsgi-legacy` | 无 |
| P1 | T2.5 Helicone 启动 | docker compose up + helicone-doctor.py | 4-5 GB RAM + 10-15 GB 磁盘 commit |
| P2 | 同题材 Stage A/B/C 长跑 | prompt 修复已上线，待验证 | ~7h × $13.5 LLM 预算 |
| P2 | T7 FActScore-lite | qa_service shadow 模式 | v5 `prompts.py` freeze 决策 |
| P3 | B5 Elo wiring | `pairwise_eval_service` | DB schema 决策 |
| P3 | T5 Loom A/B | 20h LLM 预算 | runbook 已就绪 |

---

## 4. 不做（理由记录）

- **Graph-aware rerank**：当前不做。理由：
  - 章节级 retrieval rerank 已在线（bge-reranker-v2-m3，候选 limit×2，cap 10）
  - graph_signals/fact_records 候选量小（≤6/≤12），用 importance/degree 排序合理
  - 没有 measurable 噪音报告；上 Helicone trace 拿数据再决策
  - 详细分析：本会话答复

- **Embedding INT8 → fp32 切换**：当前不做。理由：
  - INT8 模型已加载验证 ✅，1024 维与 DB 现存 2695 chunks 完全兼容
  - 基线 R@5=0.81/0.84 已锁，没掉点报告
  - 切 fp32 = 1.1 GB 模型 + 2-3× 推理延迟，ROI 不清晰
  - 监控掉点再考虑

---

## 5. 修订记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 0.1 | 2026-05-16 | 初版，承接 5/15 final handoff |
