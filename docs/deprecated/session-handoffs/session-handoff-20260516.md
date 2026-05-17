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

## 2. 进行中 🔄 → 全部完成 ✅

### LLM-1: 切 claude-haiku-4.5 + 并发节流 ✅ DONE
### DATA-1: novel_sources.source_path 修复 ✅ DONE
### Option B: 退役 WSGI fallback ✅ DONE
### Stage A 5-章 spike ✅ DONE — pass=3/5 (60%)，scaffold=2/5（JSON parse 失败，已修复）
### Reader Panel Service ✅ DONE — 4 persona × 7 dim + revise_with_panel_feedback
### T7 FActScore-lite ✅ DONE — qa_service shadow mode
### B5 Elo ✅ DONE — DB table + ORM + loom-elo CLI
### Stage B 30-章 spike ✅ DONE — pass=20/30 (66%)，scaffold=10/30 (33%)
### JSON parser fix ✅ DONE — scaffold 率预期降至接近 0%
### B2 relationship route ✅ DONE — graph_nodes/edges 接入 retrieval pipeline

---

## 3. 待办（下一棒）📋

| 优先级 | 项 | 备注 | 阻塞 |
|---|---|---|---|
| P1 | **Stage B re-run** | JSON parser 修复后重跑 30 章，验证 scaffold 率降至 <5% | ~90 min LLM |
| P1 | T2.5 Helicone 启动 | docker compose up + helicone-doctor.py | GitHub 网络不通（clone 失败）|
| P2 | Stage C 100-章全本 | 同题材整本验证 | ~5h LLM |
| P2 | retrieval-benchmark B2 delta | 对比加 relationship route 前后 R@5 | 无 |
| P3 | T5 Loom A/B | 20h LLM 预算 | runbook 已就绪 |
| P3 | T8 Persona correlation | reader_feedback 需 ≥30 行（当前 6 行）| 等 Reader Studio 积累 |

---

## 4. 本会话 commit 列表（27 commits）

| commit | 内容 |
|---|---|
| `7e1a15c` | feat(llm): claude-haiku-4.5 + shared token-bucket rate limiter |
| `2045992` | chore(data): relink novel_sources.source_path via SHA256 dedup |
| `96966a5` | docs(ops): postgres ops cheatsheet + 2026-05-16 session handoff |
| `484118a` | feat(llm): enforce 4000 max_tokens cap on deepseek-* models |
| `e5975d0` | refactor(api): retire WSGI dispatch |
| `6ca0750` | fix(tests): fix 6 pre-existing test failures + retire dead WSGI contract tests |
| `5a0eb94` | feat(imitation): add 4-persona reader panel with comfort_score soft gate |
| `62e2db2` | feat(reader-panel): 4-persona × 7-dimension LLM reader evaluation service |
| `3d78cc6` | feat(reader-panel): wire revise_with_panel_feedback into harness loop |
| `d32f19a` | feat(reader-panel): add build_panel_driven_revision_prompt |
| `fdb2489` | test(reader-panel): add tests for revise_with_panel_feedback |
| `f067d90` | feat(qa): T7 FActScore-lite shadow mode in answer_question |
| `76a3bae` | feat(db): B5 Elo — add loom_pairwise_evaluations table + ORM model |
| `ea8761b` | feat(cli): B5 Elo — add loom-elo command |
| `984c9c9` | fix(imitation): replace bare json.loads with robust JSON parser |
| `0ffa176` | fix(imitation): fix NameError in _extract_json_payload |
| `1ff9a11` | feat(retrieval): B2 — add relationship_route to retrieval pipeline |

---

## 5. 不做（理由记录）

- **Graph-aware rerank**：当前不做。章节级 retrieval rerank 已在线，graph_signals 候选量小，没有 measurable 噪音报告。上 Helicone trace 拿数据再决策。
- **Embedding INT8 → fp32 切换**：当前不做。INT8 已验证 1024 维，基线 R@5=0.81/0.84 未掉点。
- **T2.5 Helicone**：GitHub 网络不通，clone 超时。需要网络恢复后手动执行。

---

## 6. 修订记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 0.1 | 2026-05-16 | 初版，承接 5/15 final handoff |
| 0.2 | 2026-05-16 | 更新：LLM-1 / DATA-1 / Option B / Stage A / Reader Panel 全部完成 |
| 0.3 | 2026-05-16 | 更新：T7 / B5 / Stage B / JSON fix / B2 relationship route 全部完成 |

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
