# 14. Demo 与 Verification

## 1. 目标

本文件把 QA Upgrade V2 当前阶段的“效果演示”和“验证命令”单独收敛出来，方便：
- 自己回归
- 给协作者演示
- 后续提测/验收

当前覆盖范围：**Phase B / P0 稳定化**。

---

## 2. 本阶段要演示什么

### Demo A：Alias 识别恢复
**要证明**：entity resolution 不再只依赖 `character` node，`entity` node 也可建立 alias map。

### Demo B：anti-spoiler 更保守
**要证明**：带 `max_chapter` 时，未来章节不会进入 rerank；如果过滤后候选不足，会做一次安全扩候选回补。

### Demo C：`/api/search-branch` contract 修复
**要证明**：
- `q` 参数可用
- `query` 参数也兼容
- endpoint 不再调用不存在的 `svc.search(...)`
- 返回结构既兼容旧消费方，也能给新消费方更多字段

---

## 3. 自动化验证命令

## 3.1 最小 targeted 验证

```bash
cd /home/user/novel-analyzer

.venv/bin/pytest -q \
  tests/test_entity_resolution_service.py \
  tests/test_retrieval_service.py::test_search_branch_filters_future_hits_before_rerank \
  tests/test_retrieval_service.py::test_search_branch_refetches_more_candidates_when_spoiler_filter_truncates \
  tests/test_retrieval_service.py::test_search_branch_with_diagnostics_filters_max_chapter_before_rerank \
  tests/test_api_main.py::test_search_branch_endpoint_accepts_q_and_returns_retrieval_hit_shape \
  tests/test_api_main.py::test_search_branch_endpoint_accepts_legacy_query_alias \
  tests/test_api_main.py::test_search_branch_endpoint_rejects_blank_query
```

### 当前期望
- `7 passed`

---

## 3.2 更强的 QA 主链回归

```bash
cd /home/user/novel-analyzer

.venv/bin/pytest -q \
  tests/test_entity_resolution_service.py \
  tests/test_qa_service.py \
  tests/test_retrieval_service.py \
  tests/e2e/test_anti_spoiler.py
```

### 当前期望
- `41 passed`

---

## 3.3 静态验证

```bash
cd /home/user/novel-analyzer

.venv/bin/python -m py_compile \
  novel_analyzer/services/entity_resolution_service.py \
  novel_analyzer/services/retrieval_service.py \
  apps/api/app/routers/pipeline.py \
  tests/test_entity_resolution_service.py \
  tests/test_retrieval_service.py \
  tests/test_api_main.py

cd apps/web
./node_modules/.bin/tsc -p tsconfig.json --noEmit --pretty false
```

### 当前期望
- Python 无输出即成功
- TypeScript 无输出即成功

---

## 4. 手工演示步骤

## 4.1 Search API 兼容演示

### 用 `q`
```bash
curl "http://127.0.0.1:8000/api/search-branch?branch_id=<branch_id>&q=%E5%8D%AB%E5%9B%BE&limit=5"
```

### 用 `query`
```bash
curl "http://127.0.0.1:8000/api/search-branch?branch_id=<branch_id>&query=%E5%8D%AB%E5%9B%BE&limit=5"
```

### 期望
两者都返回：
- `query`
- `hits[].chapter_index`
- `hits[].score`
- `hits[].title`
- `hits[].summary_text`
- `hits[].keyword_list`
- `hits[].chunk_text`（兼容字段）

---

## 4.2 blank query 错误处理演示

```bash
curl -i "http://127.0.0.1:8000/api/search-branch?branch_id=<branch_id>"
```

### 期望
- HTTP `400`
- body 含：`missing query text`

---

## 4.3 anti-spoiler 行为演示

### ask-branch-stream
```bash
curl -N -X POST "http://127.0.0.1:8000/api/ask-branch-stream" \
  -H 'Content-Type: application/json' \
  -d '{
    "branch_id": "<branch_id>",
    "question": "卫图前20章为什么要修养生功？",
    "limit": 6,
    "max_chapter": 20
  }'
```

### 期望
- SSE 可正常返回
- retrieval hits 不应包含 `chapter_index > 20`
- 最终回答中的 `used_chapters` 不应超过 20

> 注：当前 P0 主要保证“未来章节不参与 rerank”；更彻底的 route-level spoiler-safe candidate planning 是后续阶段任务。

---

## 4.4 Alias 行为演示

如果 branch 内存在：
- canonical: `卫图`
- alias: `卫图少年`

则可以手工问：

```bash
curl -X POST "http://127.0.0.1:8000/api/ask-branch" \
  -H 'Content-Type: application/json' \
  -d '{
    "branch_id": "<branch_id>",
    "question": "卫图少年为什么要修养生功？",
    "limit": 6
  }'
```

### 期望
- 能召回与 `卫图` 相关章节
- 不再因为 alias 未命中而明显失真

---

## 5. LLM 运行配置（当前指定）

见：
- [`13-llm-runtime-profile.md`](./13-llm-runtime-profile.md)

如果要做本地联调，建议先 export：

```bash
export NOVEL_ANALYZER_LLM_PROVIDER_NAME=minimax-local
export NOVEL_ANALYZER_LLM_BASE_URL=http://43.155.145.78:65432/
export NOVEL_ANALYZER_LLM_API_KEY=<set-locally>
export NOVEL_ANALYZER_LLM_MODEL_NAME=minimaxai/minimax-m2.7
export NOVEL_ANALYZER_LLM_QA_MODEL_NAME=minimaxai/minimax-m2.7
```

---

## 6. 当前阶段的效果总结

### 已确认提升
1. alias resolution 与真实 graph node 类型对齐
2. anti-spoiler 至少已推进到 pre-rerank 安全版本
3. search API 不再调用错误 service 方法
4. search API 对 `q/query` 更兼容
5. 返回结构同时兼容旧/新消费方

### 尚未完成
1. route-level anti-spoiler candidate planning
2. StructuredQueryPlan
3. EvidenceHit contract
4. graph typed routes
5. evidence-aware rerank

---

## 7. 结论

这一阶段的 demo 重点不是“问答已经非常聪明”，而是：

> **主链更正确、更稳、更可演示、更可验证。**

这正是 P0 稳定化阶段应该达成的目标。
