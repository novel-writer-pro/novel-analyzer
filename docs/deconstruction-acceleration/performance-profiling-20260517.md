# 拆书性能剖析报告

**日期**：2026-05-17  
**测试分支**：`2cd9c1ff-aba2-4d92-a42e-b2e373baaab7`（雪中悍刀行，983章，229章已完成分析）  
**测试环境**：本机 CPU、ONNX embedding/rerank、PostgreSQL 本地、Gemini 2.5 Flash @ 1.5 rps

---

## 一、数据库规模（测试时）

| 表 | 记录数 |
|----|--------|
| `graph_nodes` | 1,334 |
| `graph_edges` | 45,999 |
| `fact_records` | 2,960 |
| `retrieval_documents` | 218 |
| `retrieval_chunks` | 612 |
| `chunk_embeddings` | 612 |

`graph_edges` 章节分布（集中在 ch100–200）：
```
ch0–49:    775 条
ch50–99:   3,157 条
ch100–149: 15,335 条
ch150–199: 25,598 条
ch200–249: 1,134 条
```

---

## 二、Embedding 性能（ONNX CPU）

**Provider**：`OnnxBgeEmbeddingProvider`，模型 `BAAI/bge-m3`，路径 `/home/user/migrate/bge-m3-onnx-int8`

| 场景 | 耗时 |
|------|------|
| 首次加载（warmup） | 7,994ms |
| 单文本（短文本） | 843ms |
| 单文本（900字符，典型 chunk） | **8,413ms** |
| 2 个 chunk（900字符各） | **17,488ms** |
| 10 个文本（短） | 4,078ms（408ms/text） |

**每章平均 chunk 数**：1.6（前 20 章统计：`[3,4,4,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]`）

**每章 embedding 实际耗时**：**10,000–14,000ms**

---

## 三、Rerank 性能（ONNX CPU）

**Provider**：`OnnxCrossEncoderRerankProvider`，模型 `onnx-community/bge-reranker-v2-m3-ONNX`

| 场景 | 耗时 |
|------|------|
| 首次加载（warmup） | 14,911ms |
| 5 docs rerank | **4,471ms** |
| 10 docs rerank | **6,652ms** |

影响路径：QA/搜索时触发，不影响拆书主流程。

---

## 四、PostgreSQL 上下文组装性能

### 4.1 `reasoning_snapshot` 随章节深度的增长

| upto_chapter | 单次耗时 |
|-------------|---------|
| 49 | ~221ms |
| 99 | ~210ms |
| 149 | **~1,028ms** |
| 199 | **~1,739ms** |

**根因**：`graph_edges` 仅有单列索引 `ix_graph_edges_branch_id`，查询 `WHERE branch_id=X AND chapter_first_seen <= N AND is_active=true` 需扫描全部 45,999 行再过滤。

EXPLAIN ANALYZE 关键输出：
```
Parallel Bitmap Heap Scan on graph_edges
  Filter: (is_active AND (chapter_first_seen <= 200))
  Rows Removed by Filter: 30,666
  actual time: 1.033..12.160 rows=15,333 loops=3
```

### 4.2 每章 `analyze_range` 触发 3 次 `reasoning_snapshot`

```python
graph_context_json()         → reasoning_snapshot(node=12, edge=12)   # 第1次
state_summary_json()         → reasoning_snapshot(node=12, edge=12)   # 第2次（完全重复）
adaptive_graph_context_json  → reasoning_snapshot(node=32, edge=32)   # 第3次
```

3 次合计耗时：

| 章节 | 3次合计 |
|------|--------|
| ch50 | ~413ms |
| ch100 | ~572ms |
| ch150 | **~2,279ms** |
| ch200 | **~5,677ms** |

### 4.3 完整上下文组装耗时（per chapter）

| 调用 | ch50 | ch200 |
|------|------|-------|
| `previous_summary` | 155ms | 13ms |
| `fact_context_json` | 8ms | 8ms |
| `graph_context_json` | 48ms | **1,763ms** |
| `state_summary_json` | 63ms | **2,060ms** |
| `window_summary` | 11ms | 13ms |
| `adaptive_fact_context` | 38ms | 49ms |
| `adaptive_graph_context` | 143ms | **2,111ms** |
| **合计** | **466ms** | **6,017ms** |

---

## 五、检索（QA）路径性能

### 5.1 各路由耗时

| 路由 | 命中数 | 耗时 |
|------|--------|------|
| fts | 0 | 3ms |
| similarity | 10 | 233ms |
| like | 0 | 29ms |
| keyword | 0 | 13ms |
| entity_exact | 0 | 4ms |
| relationship | 0 | 8ms |
| **vector** | 10 | **1,325ms** |

**vector 路由慢的根因**：
- `chunk_embeddings.vector_payload` 列类型是 **`json`**，非 pgvector `vector` 类型
- 查询时把全部 612 个 embedding（每个 ~22KB JSON）拉到 Python 内存
- 在 Python 里逐个计算余弦相似度（纯 Python `_cosine_similarity`）
- pgvector v0.8.2 已安装但完全未使用

### 5.2 完整 search_branch 耗时

| 阶段 | 耗时 |
|------|------|
| 多路由召回（raw） | 1,693ms |
| ONNX rerank | **18,343ms** |
| **总计** | **20,035ms** |

---

## 六、LLM 配置与速率限制

```
llm_stage_model_name   = gemini-2.5-flash
llm_fallback_model_name = claude-sonnet-4.6
llm_requests_per_second = 1.5
llm_max_bucket_size     = 3.0
llm_max_concurrent_requests = 2
use_merged_stages       = true
```

每章 LLM 调用次数（merged 模式）：3 次（intake+facts、evidence+analysis、guard）

速率限制影响：3 次调用最快需要 ~2 秒等待令牌，加上 Gemini 2.5 Flash 实际延迟 3–8s/次，**每章 LLM 总耗时 9–24 秒**。

---

## 七、单章完整耗时估算（ch150）

| 阶段 | 耗时 | 备注 |
|------|------|------|
| 上下文组装 | ~2,300ms | 3× reasoning_snapshot |
| LLM call1（intake+facts） | ~4,000–8,000ms | 含速率等待 |
| LLM call2（evidence+analysis） | ~4,000–8,000ms | 含速率等待 |
| LLM call3（guard） | ~3,000–6,000ms | 含速率等待 |
| Embedding（1.6 chunks） | ~10,000–14,000ms | ONNX CPU |
| DB materialization | ~300ms | 快 |
| Loom consolidation | ~200ms | 非阻塞 |
| **单章总计** | **~24,000–39,000ms** | **约 24–39 秒/章** |

---

## 八、现有索引清单

```
chunk_embeddings:    chunk_embeddings_pkey, ix_chunk_embeddings_chunk_id, uq_chunk_embedding_chunk
fact_records:        fact_records_pkey, ix_fact_records_branch_id
graph_edges:         graph_edges_pkey, ix_graph_edges_branch_id, uq_graph_edge_identity
graph_nodes:         graph_nodes_pkey, ix_graph_nodes_branch_id, uq_graph_node_identity
retrieval_chunks:    retrieval_chunks_pkey, ix_retrieval_chunks_document_id, uq_document_chunk_order
retrieval_documents: retrieval_documents_pkey, ix_retrieval_documents_branch_id,
                     ix_retrieval_documents_bm25_vector, uq_retrieval_document
```

**缺失的关键索引**：
- `graph_edges (branch_id, chapter_first_seen)` 复合索引（WHERE is_active=true）
- `chunk_embeddings` 上的 pgvector HNSW/IVFFlat ANN 索引（需先迁移列类型）

---

## 九、优化行动项（按优先级）

| 优先级 | 行动 | 预期收益 | 改动范围 |
|--------|------|---------|---------|
| **P0** | 切换 Embedding 到 GPU TEI | 每章 -10,000ms | 改配置 |
| **P0** | 切换 Rerank 到 GPU TEI | QA -4,000ms | 改配置 |
| **P1** | `reasoning_snapshot` 请求级缓存 | 每章 -1,500ms | 改代码 |
| **P2** | `graph_edges` 复合索引 | 每章 -1,500ms | Alembic migration |
| **P3** | `vector_payload` 迁移到 pgvector vector 类型 + HNSW 索引 | QA vector -1,300ms | Alembic + 代码 |

详细实施方案见 [`roadmap-sota-optimization.md`](./roadmap-sota-optimization.md) Phase 5-Perf 各节。
