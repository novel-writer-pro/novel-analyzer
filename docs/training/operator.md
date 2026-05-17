# 培训路径 — 运维 / 实施

> **目标读者**：负责部署、自检、排障、生产长跑监控的工程师 / SRE。
> **预计时长**：第 1 天部署起、第 2-3 天熟悉故障决策树。

---

## Day 1：部署起来（4-6 小时）

### 1. 关键文档先读
- [runbook/deployment-and-operations-manual-20260515.md](../runbook/deployment-and-operations-manual-20260515.md) — **从零部署 + 日常运维总章（1038 行，必读）**
- [ops-debug-manual-20260514.md](../ops-debug-manual-20260514.md) — scenario-first 故障速查（自检 / 常见操作 / 故障决策树 / 反模式）
- [runbook/postgres-ops-cheatsheet.md](../runbook/postgres-ops-cheatsheet.md) — PostgreSQL 运维速查

### 2. 环境就绪
按根 [README.md § 快速启动](../../README.md#快速启动) 选路径：

**路径 A（推荐生产）**：DB / TEI Embedding / TEI Rerank 都在外部主机
**路径 B**：本地一体化（含本地 ONNX embedding）

### 3. 一键探针
```bash
make smoke-external
```
预期 4 个 ✓：
- DB 连通 + 扩展（pg_trgm + vector + pg_jieba）
- LLM `/models`
- TEI embed
- TEI rerank

失败时脚本会打印具体修复提示。

### 4. PostgreSQL 扩展
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_jieba;   -- 可选，中文检索 R@5 +0.03
```

### 5. 启动顺序
```bash
# 后端
make api-dev                                    # :8011

# 前端
cd apps/web && npm install && npm run dev       # :4173

# 可选 infra
make v2-up-all                                  # Dify + n8n + Langfuse
cd infra/helicone/upstream && docker compose up -d   # Helicone :8585
```

### 6. 健康检查
- 后端：`curl http://localhost:8011/api/health`
- 前端：`http://127.0.0.1:4173`
- Dify：`http://localhost:8080`
- n8n：`http://localhost:5678`
- Langfuse：`http://localhost:3030`
- Helicone：`http://localhost:8585/healthcheck`

---

## Day 2：故障决策树（核心技能）

### 5 棵故障决策树
全部在 [ops-debug-manual-20260514.md](../ops-debug-manual-20260514.md)：

1. **检索召回不正常**：domain dict 缺词 / pg_jieba 未启用 / bm25_vector 未生成
2. **章节短 / scaffold 污染**：thin draft / scaffold-only / action_queue 三类
3. **mapping 不生效**：mapping_pack 未传 / prompt 未拼入 / world_map 命名冲突
4. **进程死掉**：LLM provider 抖动 / DB 连接池满 / OOM
5. **docker 起不来**：端口冲突 / volume 权限 / image 拉取失败

### `make smoke-external` 失败排查

| 失败项 | 常见原因 | 修复 |
|--------|----------|------|
| **Settings load** | `EMBEDDING_BACKEND=http` 但 `EMBEDDING_API_BASE` 空 | 补 EMBEDDING_API_BASE 或改 onnx |
| **PostgreSQL** | host 不通 / 用户密码错 / 库不存在 | 用 psql 验证连接串 |
| **PostgreSQL · missing extension** | DB 没装 pg_trgm / vector | `CREATE EXTENSION ...`（superuser） |
| **LLM /models 401** | LLM_API_KEY 不对 | 重新生成填 NOVEL_ANALYZER_LLM_API_KEY |
| **LLM /models 404** | provider 不暴露 /models（少数自建） | 直接试 api-dev，可用就忽略 |
| **Embedding HTTP 422** | TEI 模型名 ≠ EMBEDDING_MODEL_NAME | 改成 TEI 实际加载的模型名 |
| **Rerank 顺序错** | rerank 不是 bge-reranker-v2-m3 | 检查 TEI 启动 `--model-id` |

### 常见操作

```bash
# 重建 BM25 + Vector
.venv/bin/python -m novel_analyzer.cli.app rebuild-bm25-vector <branch_id>

# 跑领域词典刷新
.venv/bin/python -m novel_analyzer.cli.app rebuild-domain-dict <branch_id>

# 仅重跑缺失章节
.venv/bin/python -m novel_analyzer.cli.app resume-imitation <branch_id>

# 查看 Loom 状态
.venv/bin/novel-analyzer loom-status <branch_id>

# 性能剖析
.venv/bin/python -m novel_analyzer.cli.app perf-profile <branch_id>
```

### 反模式（**不要做**）
- ❌ 直接 `DELETE FROM ...`：会破坏 active branch 语义，必须走 CLI
- ❌ 改完 prompt 不重跑：参与下游的章节会停留在旧版本
- ❌ 失败章节强制 mark pass：会污染 cluster 与 audit_conclusion
- ❌ 不跑 alembic 直接改表：schema drift 会让 ORM 报错
- ❌ 多个进程同时跑同一 branch：会触发 in-flight contamination

---

## Day 3：生产长跑

### 100+ 章后台跑批 SOP
1. **资源准备**：DB 连接池 ≥ 20，LLM rate limit ≥ 1.5 req/s
2. **provider fallback 准备**：当前手动 ops（nassaapi → sealos），监控抖动
3. **进度监控**：tail logs，关键字 `imitate_chapter` `verdict=pass` `verdict=fail`
4. **失败恢复**：仅重跑缺失章节
5. **成本监控**：Helicone 看 cost，Langfuse 看 trace

### 跨题材改写实证（参考工作量）

| 项目 | 章数 | 字数 | 实测时间 | 失败率 |
|------|------|------|---------|--------|
| 卫图 → 太空科幻 | 102 | 227,037 | ~6 小时 | 0/102 |
| 诛仙 → 太空科幻 | 59 | 151,267 | ~3.5 小时 | 1/59 |
| 卫图 → 都市修真 | 10 | 21,370 | ~30 分钟 | 0/10 |

### 监控指标

| 指标 | 来源 | 阈值 |
|------|------|------|
| `verdict=pass` 比率 | Helicone trace | ≥ 95% |
| 单章 LLM 调用次数 | Helicone | ≤ 3（merged stages） |
| 单章延迟 P99 | Langfuse | ≤ 60s |
| DB 连接池使用率 | pg_stat_activity | ≤ 80% |
| LLM provider 失败率 | Helicone | ≤ 5%（触发 fallback） |
| pgvector 索引大小 | pg_relation_size | 监控趋势 |

---

## 关键运维文档索引

### 部署 & 启动
- [runbook/deployment-and-operations-manual-20260515.md](../runbook/deployment-and-operations-manual-20260515.md) — 从零部署总章
- [runbook/v3-pickup-checklist.md](../runbook/v3-pickup-checklist.md) — v3 pickup 步骤清单
- [runbook/business-loop.md](../runbook/business-loop.md) — v3 端到端 6 步 smoke

### 故障 & 调试
- [ops-debug-manual-20260514.md](../ops-debug-manual-20260514.md) — **scenario-first 故障速查（必备）**
- [runbook/postgres-ops-cheatsheet.md](../runbook/postgres-ops-cheatsheet.md) — PG 速查
- [runbook/bm25-jieba-reindex.md](../runbook/bm25-jieba-reindex.md) — BM25 + jieba 重建

### 单点能力运维
- [runbook/helicone-enable.md](../runbook/helicone-enable.md) — Helicone proxy
- [runbook/loom-ab-experiment.md](../runbook/loom-ab-experiment.md) — Loom A/B 实验
- [runbook/migration-guide.md](../runbook/migration-guide.md) — 迁移指南
- [foundation-optimization/p0-maintenance-checklist.md](../foundation-optimization/p0-maintenance-checklist.md) — P0 维护清单
- [foundation-optimization/pg-jieba-userdict-ops.md](../foundation-optimization/pg-jieba-userdict-ops.md) — pg_jieba 词典运维

### 性能
- [deconstruction-acceleration/performance-profiling-20260517.md](../deconstruction-acceleration/performance-profiling-20260517.md) — 雪中悍刀行 229 章实测

### 角色入口
- [roles/maintainer/README.md](../roles/maintainer/README.md)

---

## 必备速查表

### 后端
```bash
make api-dev                  # 启动后端 :8011 (uvicorn FastAPI)
make smoke-external            # 4 端点探针
.venv/bin/alembic upgrade head # DB 迁移
.venv/bin/python -m pytest tests/ -q  # 全量测试
```

### 前端
```bash
cd apps/web && npm install
npm run dev                    # 开发 :4173
npm run build                  # 生产构建
```

### Infra
```bash
make v2-up-all                 # Dify + n8n + Langfuse 全部启动
make v2-down-all               # 全部下线
make v2-status                 # 查看 plan 进度
make tei-up / tei-doctor       # TEI embedding 启停 + 自检
```

### CLI 高频
```bash
.venv/bin/python -m novel_analyzer.cli.app --help
.venv/bin/python -m novel_analyzer.cli.app retrieval-benchmark <branch_id>
.venv/bin/python -m novel_analyzer.cli.app writer-imitate-range <branch_id> ...
.venv/bin/novel-analyzer loom-status <branch_id>
```

---

## 进阶：v4 商业化前的 6 项 SLA gap

商业化运维最终需要补齐：定价 / 多租户隔离 / 限流 / LLM fallback / 版权合规 / 监控仪表盘。

详细：[capabilities/04-commercialization.md § 6 项 SLA gap](../capabilities/04-commercialization.md#6-项-sla-gap商用前必须补齐)

---

返回 [training/](./README.md) ｜ [文档中心](../README.md)
