# PostgreSQL 运维速查手册

> 给运维 / 数据 / 排障同学的「直接 SQL」速查。覆盖：连接、数据巡检、内容查询、向量检索、BM25/jieba 全文检索、Embedding 状态、维护操作、性能定位。
>
> 配套阅读：[`migration-guide.md`](./migration-guide.md) · [`bm25-jieba-reindex.md`](./bm25-jieba-reindex.md) · [`business-loop.md`](./business-loop.md)
>
> 数据库：`PostgreSQL 17.5`，启用扩展：`pg_trgm`、`vector` (pgvector)、`pg_jieba`、`pg_textsearch`

---

## 0. 连接

```bash
# 标准连接（本机 docker / 直连）
PGPASSWORD=d2pass psql -h 127.0.0.1 -p 5432 -U d2 -d novel_analyzer

# 一行执行 + 退出
PGPASSWORD=d2pass psql -h 127.0.0.1 -U d2 -d novel_analyzer -c "SELECT version();"

# 从文件执行
PGPASSWORD=d2pass psql -h 127.0.0.1 -U d2 -d novel_analyzer -f /path/to/query.sql

# 设置默认（避免每次输密码）写入 ~/.pgpass：
# 127.0.0.1:5432:novel_analyzer:d2:d2pass
# chmod 600 ~/.pgpass
```

psql 内常用反斜杠命令：

| 命令 | 用途 |
|---|---|
| `\dt` | 列出所有表 |
| `\d+ <表名>` | 表结构 + 索引 + 外键 |
| `\di+` | 索引列表（带大小） |
| `\dx` | 已安装的扩展 |
| `\df+ <函数名>` | 函数定义 |
| `\timing on` | 显示每条 SQL 耗时 |
| `\x` | 切换横/竖排显示 |
| `\copy ... TO 'file.csv' CSV HEADER` | 导出 CSV |
| `\watch 5` | 每 5 秒重跑上一条 SQL（监控用） |

---

## 1. 健康自检（90 秒）

```sql
-- 版本 + 扩展
SELECT version();
SELECT name, installed_version FROM pg_available_extensions
 WHERE name IN ('pg_trgm','vector','pg_jieba','pg_textsearch')
 ORDER BY name;

-- 文本搜索 config（中文检索依赖 jiebacfg）
SELECT cfgname FROM pg_ts_config
 WHERE cfgname IN ('simple','jiebacfg','jiebaqry');

-- alembic 当前 schema 版本
SELECT version_num FROM alembic_version;

-- 各表行数（估值，速度快）
SELECT relname AS table, n_live_tup AS rows
 FROM pg_stat_user_tables
 WHERE schemaname='public'
 ORDER BY n_live_tup DESC;

-- 数据库 / 表大小
SELECT pg_size_pretty(pg_database_size('novel_analyzer')) AS db_size;
SELECT relname, pg_size_pretty(pg_relation_size(oid)) AS size
 FROM pg_class
 WHERE relkind='r' AND relnamespace=(SELECT oid FROM pg_namespace WHERE nspname='public')
 ORDER BY pg_relation_size(oid) DESC LIMIT 15;
```

---

## 2. 业务数据导览

### 2.1 实体关系

```
novel_sources (小说原始)
    └── chapter_manifests (章节切分版本)
            ├── chapter_segments (章节起止 + hash)
            └── analysis_runs (分析运行)
                    └── run_branches (分析分支)
                            ├── chapter_jobs / chapter_job_events (执行 + 日志)
                            ├── chapter_raw_outputs (LLM 原始返回)
                            ├── chapter_artifacts (章节分析产物)
                            ├── window_artifacts (窗口摘要)
                            ├── retrieval_documents → retrieval_chunks → chunk_embeddings
                            ├── fact_records (事实库 entity/event/continuity)
                            ├── graph_nodes / graph_edges (知识图谱)
                            ├── chapter_risk_cards / gate_checker_results (风险门控)
                            ├── risk_semantic_signals / risk_signal_clusters / risk_signal_links
                            ├── cluster_review_records / cluster_review_event_records (审查工作流)
                            ├── reader_feedback_comments (读者反馈)
                            ├── pipeline_runs (流水线)
                            └── run_checkpoints (LangGraph 状态)
```

### 2.2 关键 ID 速查

```sql
-- 全部小说（最近优先）
SELECT id, title, owner_user_id, created_at::date
 FROM novel_sources
 WHERE deleted_at IS NULL
 ORDER BY created_at DESC;

-- 某本小说的 active branch
SELECT n.title, r.id AS run_id, r.active_branch_id, b.name, b.status
 FROM novel_sources n
 JOIN analysis_runs r ON r.novel_id = n.id
 JOIN run_branches b ON b.id = r.active_branch_id
 WHERE n.title = '雪中悍刀行'
   AND n.deleted_at IS NULL
 ORDER BY r.created_at DESC;

-- 某 branch 的章节进度
SELECT chapter_index, status, attempts, last_error,
       finished_at::timestamp(0) AS finished
 FROM chapter_jobs
 WHERE branch_id = '<BRANCH_ID>'
 ORDER BY chapter_index;

-- branch 总览仪表盘
SELECT
  b.id,
  b.name,
  n.title AS novel,
  (SELECT count(*) FROM chapter_jobs WHERE branch_id=b.id) AS jobs_total,
  (SELECT count(*) FROM chapter_jobs WHERE branch_id=b.id AND status='success') AS jobs_ok,
  (SELECT count(*) FROM chapter_jobs WHERE branch_id=b.id AND status='failed') AS jobs_fail,
  (SELECT count(*) FROM chapter_artifacts WHERE branch_id=b.id) AS artifacts,
  (SELECT count(*) FROM retrieval_documents WHERE branch_id=b.id) AS rdocs,
  (SELECT count(*) FROM gate_checker_results WHERE branch_id=b.id) AS gates
 FROM run_branches b
 JOIN analysis_runs r ON r.id=b.run_id
 JOIN novel_sources n ON n.id=r.novel_id
 WHERE b.deleted_at IS NULL
 ORDER BY n.title, b.created_at DESC;
```

---

## 3. 章节内容查询

### 3.1 查某章原文（基于 segments）

```sql
-- 章节切分元数据
SELECT chapter_index, normalized_title, end_offset - start_offset AS char_len, content_hash
 FROM chapter_segments
 WHERE manifest_id = (
   SELECT m.id FROM chapter_manifests m
   JOIN novel_sources n ON n.id=m.novel_id
   WHERE n.title='雪中悍刀行' AND n.deleted_at IS NULL
   ORDER BY m.version DESC LIMIT 1
 )
 ORDER BY chapter_index
 LIMIT 20;
```

> 原文文本不在 DB 里。`source_path` 在 `novel_sources.source_path` 字段；用 `start_offset / end_offset` 配文件读出来。

### 3.2 查某章分析产物

```sql
-- chapter_artifacts.payload_json 是结构化分析结果
-- artifact_type='chapter_analysis' 是主产物
SELECT chapter_index, status, visibility,
       jsonb_pretty(payload_json::jsonb) AS analysis
 FROM chapter_artifacts
 WHERE branch_id = '<BRANCH_ID>'
   AND chapter_index = 5
   AND artifact_type = 'chapter_analysis'
   AND deleted_at IS NULL
   AND visibility = 'visible';

-- 只看摘要（payload 通常有 summary 字段）
SELECT chapter_index,
       payload_json->>'summary' AS summary,
       payload_json->'tags' AS tags
 FROM chapter_artifacts
 WHERE branch_id = '<BRANCH_ID>'
   AND artifact_type = 'chapter_analysis'
 ORDER BY chapter_index
 LIMIT 10;
```

### 3.3 章节执行日志

```sql
-- 最近 50 条事件（按章排序）
SELECT chapter_index, event_type, stage, level,
       left(message, 80) AS msg,
       created_at::timestamp(0) AS at
 FROM chapter_job_events
 WHERE branch_id='<BRANCH_ID>'
 ORDER BY created_at DESC
 LIMIT 50;

-- 失败章节诊断
SELECT j.chapter_index, j.attempts, j.failure_class, j.failure_code,
       left(j.last_error, 200) AS error
 FROM chapter_jobs j
 WHERE j.branch_id='<BRANCH_ID>' AND j.status='failed';

-- LLM 原始响应（debug 用，注意大小）
SELECT chapter_index, job_attempt, parse_status,
       length(raw_response_text) AS resp_len,
       left(parse_error, 200) AS parse_err
 FROM chapter_raw_outputs
 WHERE branch_id='<BRANCH_ID>'
   AND chapter_index=12
 ORDER BY job_attempt DESC;
```

---

## 4. 检索 / Embedding 查询

### 4.1 检索物化状态

```sql
-- 每章是否物化了检索文档
SELECT
  d.chapter_index,
  d.materialization_status AS mat_status,
  length(d.bm25_text)        AS bm25_len,
  d.bm25_vector IS NOT NULL  AS has_tsv,
  (SELECT count(*) FROM retrieval_chunks c WHERE c.document_id=d.id) AS chunks
 FROM retrieval_documents d
 WHERE d.branch_id='<BRANCH_ID>'
 ORDER BY d.chapter_index;

-- Embedding 状态分布
SELECT c.embedding_status, count(*)
 FROM retrieval_chunks c
 JOIN retrieval_documents d ON d.id=c.document_id
 WHERE d.branch_id='<BRANCH_ID>'
 GROUP BY 1;

-- 找出未生成 embedding 的 chunk
SELECT d.chapter_index, c.id AS chunk_id, c.chunk_order, c.embedding_status
 FROM retrieval_chunks c
 JOIN retrieval_documents d ON d.id=c.document_id
 WHERE d.branch_id='<BRANCH_ID>' AND c.embedding_status<>'ready'
 LIMIT 50;
```

### 4.2 Embedding 向量检视

```sql
-- chunk_embeddings 用 json 存向量（vector_payload），不是 pgvector 类型
-- 检查向量维度 / 模型一致性
SELECT model_name, vector_dim, status, count(*)
 FROM chunk_embeddings
 GROUP BY 1,2,3;

-- 取一个向量看长度（确认 1024 维 bge-m3）
SELECT chunk_id, model_name, vector_dim,
       json_array_length(vector_payload) AS arr_len,
       l2_norm
 FROM chunk_embeddings
 LIMIT 3;

-- 如果未来切到 pgvector 列，余弦相似度查询模板（参考）：
-- SELECT id, 1 - (embedding <=> '[0.01,0.02,...]'::vector) AS sim
--  FROM chunk_embeddings_v2
--  ORDER BY embedding <=> '[0.01,...]'::vector
--  LIMIT 10;
```

### 4.3 BM25 / jieba 全文检索

`retrieval_documents.bm25_vector` 是 `tsvector`，用 `jiebacfg` 索引。这是中文 BM25 主路径。

```sql
-- 查 jieba 分词效果（debug 用）
SELECT to_tsvector('jiebacfg', '路朝歌养生功龟息养气功');

-- 标准 BM25 检索（plainto_tsquery 自动分词 + AND）
SELECT chapter_index,
       title,
       ts_rank_cd(bm25_vector, plainto_tsquery('jiebacfg', :query)) AS score
 FROM retrieval_documents
 WHERE branch_id = '<BRANCH_ID>'
   AND bm25_vector @@ plainto_tsquery('jiebacfg', :query)
 ORDER BY score DESC, chapter_index
 LIMIT 10;

-- 实例：搜「龟息功」
SELECT chapter_index, title,
       ts_rank_cd(bm25_vector, plainto_tsquery('jiebacfg', '龟息功')) AS score
 FROM retrieval_documents
 WHERE branch_id='<BRANCH_ID>'
   AND bm25_vector @@ plainto_tsquery('jiebacfg', '龟息功')
 ORDER BY score DESC LIMIT 5;

-- 多关键词（OR 用 to_tsquery + |）
SELECT chapter_index, title
 FROM retrieval_documents
 WHERE branch_id='<BRANCH_ID>'
   AND bm25_vector @@ to_tsquery('jiebacfg', '徐凤年 | 北凉');
```

### 4.4 Trigram 模糊匹配（人名 / 别名）

```sql
-- pg_trgm 适合"长得像"的字符串模糊查找
SELECT label, similarity(label, '徐风年') AS sim
 FROM graph_nodes
 WHERE branch_id='<BRANCH_ID>'
   AND node_type='entity'
   AND label % '徐风年'        -- % 是 trgm 操作符
 ORDER BY sim DESC LIMIT 10;
```

---

## 5. 知识图谱查询

### 5.1 节点 / 边

```sql
-- 节点类型分布（典型：entity / event / continuity / relation / foreshadow / conflict / world_rule）
SELECT node_type, count(*)
 FROM graph_nodes WHERE branch_id='<BRANCH_ID>'
 GROUP BY 1 ORDER BY 2 DESC;

-- 重要度排名（importance_score）
SELECT label, node_type, occurrence_count, importance_score
 FROM graph_nodes
 WHERE branch_id='<BRANCH_ID>' AND node_type='entity'
 ORDER BY importance_score DESC LIMIT 20;

-- 某实体的所有关系
WITH src AS (
  SELECT id FROM graph_nodes
   WHERE branch_id='<BRANCH_ID>' AND label='徐凤年'
   LIMIT 1
)
SELECT e.edge_type, n.label AS target,
       e.weight, e.chapter_first_seen, e.chapter_last_seen
 FROM graph_edges e
 JOIN graph_nodes n ON n.id=e.target_node_id
 WHERE e.source_node_id=(SELECT id FROM src)
   AND e.is_active = true
 ORDER BY e.weight DESC LIMIT 20;
```

### 5.2 事实库（fact_records）

```sql
-- 实体 / 事件 / 连续性（episodic_status: active / archived）
SELECT fact_type, episodic_status, count(*)
 FROM fact_records
 WHERE branch_id='<BRANCH_ID>'
 GROUP BY 1,2;

-- 某章节的所有事实
SELECT fact_type, label, confidence, importance_score, episodic_status
 FROM fact_records
 WHERE branch_id='<BRANCH_ID>' AND chapter_index=5
   AND deleted_at IS NULL
 ORDER BY importance_score DESC;

-- 高置信度连续性事实（用于 carry-over）
SELECT chapter_index, label, confidence, importance_score
 FROM fact_records
 WHERE branch_id='<BRANCH_ID>'
   AND fact_type='continuity'
   AND confidence >= 0.8
   AND episodic_status='active'
 ORDER BY chapter_index DESC LIMIT 30;
```

---

## 6. 风险审查 / Gate Checker

### 6.1 Checker 结果

9 个 mainline checker：`character_ooc` / `world_rule_consistency` / `plot_logic_consistency` / `power_scaling_consistency` / `relationship_consistency` / `setting_scope_consistency` / `thread_closure_consistency` / `timeline_consistency` / `foreshadow_payoff_consistency`。

```sql
-- 全 branch checker 通过率
SELECT checker_name,
       count(*) FILTER (WHERE status='pass')      AS pass,
       count(*) FILTER (WHERE status='fail')      AS fail,
       count(*) FILTER (WHERE status='warn')      AS warn,
       round(100.0 * count(*) FILTER (WHERE status='pass') / count(*), 1) AS pass_rate
 FROM gate_checker_results
 WHERE branch_id='<BRANCH_ID>' AND visibility='visible'
 GROUP BY 1 ORDER BY 1;

-- 某章哪些 checker 报警
SELECT checker_name, status, jsonb_pretty(payload_json::jsonb) AS detail
 FROM gate_checker_results
 WHERE branch_id='<BRANCH_ID>' AND chapter_index=12 AND status<>'pass';
```

### 6.2 Risk Cards / Semantic Signals

```sql
-- 章节风险卡
SELECT chapter_index, status, jsonb_pretty(payload_json::jsonb)
 FROM chapter_risk_cards
 WHERE branch_id='<BRANCH_ID>' AND chapter_index=12 AND visibility='visible';

-- 信号类型分布（thread / transition / unsupported / checker:* 等）
SELECT signal_type, status, count(*)
 FROM risk_semantic_signals
 WHERE branch_id='<BRANCH_ID>'
 GROUP BY 1,2 ORDER BY 3 DESC;

-- 集群审查工作流状态
SELECT cluster_status, review_result, count(*)
 FROM cluster_review_records
 WHERE branch_id='<BRANCH_ID>' AND deleted_at IS NULL
 GROUP BY 1,2;

-- 审查事件流（who / when / what）
SELECT cluster_key, event_type, review_actor, review_result,
       resolved_at_text, created_at::timestamp(0) AS at
 FROM cluster_review_event_records
 WHERE branch_id='<BRANCH_ID>'
 ORDER BY created_at DESC LIMIT 20;
```

---

## 7. 流水线 / 状态

```sql
-- 最近 pipeline 运行
SELECT id, mode, status, target_from_chapter, target_to_chapter,
       concurrency, started_at::timestamp(0), finished_at::timestamp(0)
 FROM pipeline_runs
 WHERE branch_id='<BRANCH_ID>'
 ORDER BY created_at DESC LIMIT 10;

-- LangGraph checkpoint（恢复用）
SELECT chapter_index, langgraph_thread_id, langgraph_checkpoint_id,
       is_inherited, visibility
 FROM run_checkpoints
 WHERE branch_id='<BRANCH_ID>'
 ORDER BY chapter_index DESC LIMIT 5;

-- 窗口摘要（chunk-level memory）
SELECT window_type, window_start_chapter, window_end_chapter, status
 FROM window_artifacts
 WHERE branch_id='<BRANCH_ID>'
 ORDER BY window_start_chapter LIMIT 10;
```

---

## 8. 维护 / 性能

### 8.1 表 / 索引体积

```sql
-- 表 + TOAST + 索引总占用
SELECT
  c.relname AS table,
  pg_size_pretty(pg_table_size(c.oid))     AS table_size,
  pg_size_pretty(pg_indexes_size(c.oid))   AS index_size,
  pg_size_pretty(pg_total_relation_size(c.oid)) AS total
 FROM pg_class c
 JOIN pg_namespace n ON n.oid=c.relnamespace
 WHERE n.nspname='public' AND c.relkind='r'
 ORDER BY pg_total_relation_size(c.oid) DESC LIMIT 15;

-- 每个索引大小
SELECT schemaname, relname AS table, indexrelname AS index,
       pg_size_pretty(pg_relation_size(indexrelid)) AS size,
       idx_scan AS scans
 FROM pg_stat_user_indexes
 WHERE schemaname='public'
 ORDER BY pg_relation_size(indexrelid) DESC LIMIT 20;

-- 没用过的索引（可能可删）
SELECT relname AS table, indexrelname AS index,
       pg_size_pretty(pg_relation_size(indexrelid)) AS size
 FROM pg_stat_user_indexes
 WHERE schemaname='public' AND idx_scan=0
 ORDER BY pg_relation_size(indexrelid) DESC;
```

### 8.2 死元组 / Vacuum

```sql
-- 高死元组比 → 该 vacuum 了
SELECT relname,
       n_live_tup AS live,
       n_dead_tup AS dead,
       round(100.0*n_dead_tup/nullif(n_live_tup+n_dead_tup,0), 1) AS dead_pct,
       last_vacuum, last_autovacuum
 FROM pg_stat_user_tables
 WHERE schemaname='public'
 ORDER BY n_dead_tup DESC LIMIT 10;

-- 单表手动 vacuum（不阻塞读写）
VACUUM (VERBOSE, ANALYZE) public.graph_edges;

-- 全库（生产慎用，会扫所有表）
VACUUM ANALYZE;
```

### 8.3 索引重建

```sql
-- 单索引重建（CONCURRENTLY 不锁表）
REINDEX INDEX CONCURRENTLY public.ix_retrieval_documents_bm25_vector;

-- 全表重建
REINDEX TABLE CONCURRENTLY public.retrieval_documents;

-- BM25 列重建（jieba 字典更新后必做）
-- 用 CLI：.venv/bin/python -m novel_analyzer.cli.app bm25-vector-reindex --confirm
-- 详见 docs/runbook/bm25-jieba-reindex.md
```

### 8.4 软删除清理

业务侧大多数表有 `deleted_at`，是软删除。**默认所有查询应该带 `WHERE deleted_at IS NULL`**。

```sql
-- 检查软删除积压
SELECT 'fact_records' AS tbl, count(*) FILTER (WHERE deleted_at IS NOT NULL) AS soft_deleted, count(*) AS total
 FROM fact_records
UNION ALL
SELECT 'chapter_artifacts', count(*) FILTER (WHERE deleted_at IS NOT NULL), count(*)
 FROM chapter_artifacts
UNION ALL
SELECT 'graph_nodes', count(*) FILTER (WHERE deleted_at IS NOT NULL), count(*) FROM graph_nodes
UNION ALL
SELECT 'graph_edges', count(*) FILTER (WHERE deleted_at IS NOT NULL), count(*) FROM graph_edges;

-- 物理清理（高危！先备份）
-- DELETE FROM fact_records WHERE deleted_at < now() - interval '30 days';
```

---

## 9. 性能定位

### 9.1 慢查询 / 实时活动

```sql
-- 当前正在跑的 query
SELECT pid, now()-query_start AS dur, state, wait_event_type, wait_event,
       left(query, 120) AS query
 FROM pg_stat_activity
 WHERE state<>'idle' AND datname='novel_analyzer'
 ORDER BY query_start;

-- kill 长查询（确认 pid 后）
-- SELECT pg_cancel_backend(<pid>);   -- 优雅取消
-- SELECT pg_terminate_backend(<pid>); -- 强制断连接
```

### 9.2 pg_stat_statements（已启用）

```sql
-- Top 10 累计耗时
SELECT calls, round(total_exec_time::numeric, 1) AS ms_total,
       round(mean_exec_time::numeric, 2) AS ms_avg,
       rows, left(query, 150) AS query
 FROM pg_stat_statements
 ORDER BY total_exec_time DESC LIMIT 10;

-- Top 平均最慢
SELECT calls, round(mean_exec_time::numeric, 2) AS ms_avg,
       round(max_exec_time::numeric, 2) AS ms_max, left(query, 150)
 FROM pg_stat_statements
 WHERE calls > 5
 ORDER BY mean_exec_time DESC LIMIT 10;

-- 重置统计
SELECT pg_stat_statements_reset();
```

### 9.3 EXPLAIN

```sql
-- 看执行计划（不执行）
EXPLAIN SELECT * FROM retrieval_documents
 WHERE branch_id='<BRANCH_ID>'
   AND bm25_vector @@ plainto_tsquery('jiebacfg', '徐凤年');

-- 看真实执行（执行 + 时间）
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
```

---

## 10. 备份 / 恢复

```bash
# 全库备份（custom format，建议日常用）
PGPASSWORD=d2pass pg_dump -h 127.0.0.1 -U d2 -d novel_analyzer \
  -Fc -f /tmp/novel_analyzer_$(date +%Y%m%d).dump

# 纯 SQL 备份（gzip 压缩，便于 grep）
PGPASSWORD=d2pass pg_dump -h 127.0.0.1 -U d2 -d novel_analyzer \
  | gzip > /tmp/novel_analyzer_$(date +%Y%m%d).sql.gz

# 单表导出
PGPASSWORD=d2pass pg_dump -h 127.0.0.1 -U d2 -d novel_analyzer \
  -t public.fact_records -Fc -f /tmp/fact_records.dump

# 恢复（custom format）— 需要 pg_restore 版本 ≥ 源端
PGPASSWORD=d2pass pg_restore -h 127.0.0.1 -U d2 -d novel_analyzer \
  --no-owner --no-privileges -j 4 /tmp/novel_analyzer_xxx.dump

# 恢复（plain SQL）— 任何版本 psql 都行，遇到约束冲突可关 FK
zcat /tmp/novel_analyzer_xxx.sql.gz \
  | PGPASSWORD=d2pass psql -h 127.0.0.1 -U d2 -d novel_analyzer

# 仅恢复数据（schema 已存在时常用）— 关 FK，只跑 COPY
zcat /tmp/x.sql.gz | python3 -c "
import sys
print('SET session_replication_role = replica;')
in_copy=False
for ln in sys.stdin:
    if ln.startswith('COPY '): in_copy=True; sys.stdout.write(ln)
    elif ln.strip()=='\\.' and in_copy: sys.stdout.write(ln); in_copy=False
    elif in_copy: sys.stdout.write(ln)
print('SET session_replication_role = DEFAULT;')
" | PGPASSWORD=d2pass psql -h 127.0.0.1 -U d2 -d novel_analyzer
```

> **版本注意**：dump 由 PG 17 生成时，`pg_restore` 必须 ≥ 17。本机 `pg_restore --version` 验证。

---

## 11. 常用排障 SQL 集

### 11.1 Embedding 全链路自检

```sql
WITH x AS (
  SELECT '<BRANCH_ID>'::varchar AS bid
)
SELECT
  (SELECT count(*) FROM retrieval_documents WHERE branch_id=(SELECT bid FROM x)) AS rdoc,
  (SELECT count(*) FROM retrieval_chunks c JOIN retrieval_documents d ON d.id=c.document_id
    WHERE d.branch_id=(SELECT bid FROM x)) AS chunks,
  (SELECT count(*) FROM retrieval_chunks c JOIN retrieval_documents d ON d.id=c.document_id
    WHERE d.branch_id=(SELECT bid FROM x) AND c.embedding_status='ready') AS chunks_ready,
  (SELECT count(*) FROM chunk_embeddings e
    WHERE e.chunk_id IN (
      SELECT c.id FROM retrieval_chunks c
       JOIN retrieval_documents d ON d.id=c.document_id
       WHERE d.branch_id=(SELECT bid FROM x))
      AND e.status='ready') AS embeddings_ok;
```

### 11.2 卡住的章节 job

```sql
-- 心跳超过 10 分钟未更新且仍 running
SELECT branch_id, chapter_index, worker_id, status,
       now()-heartbeat_at AS stale, attempts, current_stage
 FROM chapter_jobs
 WHERE status IN ('running','pending')
   AND heartbeat_at < now() - interval '10 minutes'
 ORDER BY stale DESC LIMIT 20;
```

### 11.3 owner 隔离自检（多租户）

```sql
-- novel_sources / analysis_runs / run_branches 都有 owner_user_id
SELECT owner_user_id, count(*)
 FROM novel_sources WHERE deleted_at IS NULL
 GROUP BY 1 ORDER BY 2 DESC;

-- 跨用户泄漏检查（理应为空）
SELECT b.id AS branch, b.owner_user_id AS branch_owner,
       n.id AS novel,  n.owner_user_id AS novel_owner
 FROM run_branches b
 JOIN analysis_runs r ON r.id=b.run_id
 JOIN novel_sources n ON n.id=r.novel_id
 WHERE b.owner_user_id <> n.owner_user_id;
```

### 11.4 时间范围统计

```sql
-- 今天的执行量
SELECT count(*) FILTER (WHERE status='success') AS ok,
       count(*) FILTER (WHERE status='failed')  AS fail
 FROM chapter_jobs
 WHERE finished_at >= current_date;

-- 最近 7 天每天的产物
SELECT created_at::date AS day, count(*) AS artifacts
 FROM chapter_artifacts
 WHERE created_at >= current_date - 7
 GROUP BY 1 ORDER BY 1 DESC;
```

---

## 12. 反模式 / 注意事项

| 反模式 | 替代 |
|---|---|
| `SELECT *` 查 `chapter_artifacts` | `SELECT chapter_index, payload_json->>'summary'`，payload 经常 100 KB+ |
| 不带 `deleted_at IS NULL` 查业务表 | 默认软删除模型，会带出已删除记录 |
| 不带 `branch_id=` 查 `chapter_*` / `fact_records` | 跨 branch 数据混在一起 |
| `LIKE '%xxx%'` 查长文本 | 用 `bm25_vector @@ plainto_tsquery('jiebacfg', ...)` |
| `pg_dump` 大库不加 `-Fc` | 用 custom format + `pg_restore -j N` 并行恢复 |
| 直接 `DELETE FROM graph_edges` | 209 MB 大表，先 `VACUUM` 后 `DELETE`，分批 + 限速 |
| `psql` 一次性 `\i large.sql` | 大文件用 `pg_restore`，会自动分阶段 + 索引延后创建 |

---

## 13. 配套 CLI

很多查询封装在 CLI 里：

```bash
# 健康
.venv/bin/python -m novel_analyzer.cli.app db-health
.venv/bin/python -m novel_analyzer.cli.app db-capabilities

# 检索基线
.venv/bin/python -m novel_analyzer.cli.app retrieval-benchmark <branch_id>

# 重建 BM25 列（jieba 字典变更后）
.venv/bin/python -m novel_analyzer.cli.app bm25-vector-reindex --confirm

# Smoke 探针（DB / LLM / Embedding / Rerank）
make smoke-external
```

---

## 14. 修订记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0 | 2026-05-16 | 首版,基于 PG 17.5 + 当前 27 张业务表的真实 schema |
