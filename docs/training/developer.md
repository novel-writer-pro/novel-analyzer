# 培训路径 — 开发 / 工程师

> **目标读者**：刚接手项目 / 加入团队 / 要做新需求或修 bug 的工程师。
> **预计时长**：第 1 天精读 + 第 2-3 天上手跑通。

---

## Day 1：建立心智模型（4-5 小时精读）

### 1. 系统全貌（30 分钟）
- [OVERVIEW.md](../OVERVIEW.md) — 是什么、给谁、当前状态
- [ROADMAP.md](../ROADMAP.md) — 4 条能力线进度
- [GLOSSARY.md](../GLOSSARY.md) — 术语表（先扫一遍知道有哪些词）

### 2. 项目代码结构（30 分钟）
- 根 [README.md](../../README.md) — 启动方式、技术栈、UI 入口
- 工作目录浏览：`novel_analyzer/` `apps/` `skills_dir/` `tests/` `docs/` `infra/`

### 3. 4 条能力线 landing（每条 20-30 分钟，共 2 小时）
- [capabilities/01-deconstruction.md](../capabilities/01-deconstruction.md)
- [capabilities/02-risk-audit.md](../capabilities/02-risk-audit.md)
- [capabilities/03-imitation.md](../capabilities/03-imitation.md)
- [capabilities/04-commercialization.md](../capabilities/04-commercialization.md)

### 4. 架构（30 分钟）
- [architecture/README.md](../architecture/README.md) — 架构专题入口
- [architecture/ai-novel-system-blueprint.md](../architecture/ai-novel-system-blueprint.md) — 系统蓝图
- [architecture/novel-assistant-system-architecture.md](../architecture/novel-assistant-system-architecture.md) — 系统架构详解

### 5. API 与接口（30 分钟）
- [api-current-surface.md](../api-current-surface.md) — 当前 API 端点
- [api-contract.md](../api-contract.md) — API 合同（稳定字段）
- [interface-manifest.md](../interface-manifest.md) — 稳定接口结构

### 6. 最近一棒交接（30 分钟）
- [handoffs/README.md](../handoffs/README.md) — 看最近 3 棒交接

---

## Day 2：本地跑通（4-6 小时）

### 1. 环境就绪
按根 [README.md § 快速启动](../../README.md#快速启动) 选路径 A 或 B：
- 路径 A（推荐）：外部 PostgreSQL + 外部 LLM + 外部 TEI
- 路径 B：本地 PostgreSQL + 外部 LLM + 本地 ONNX embedding

### 2. 探针验证
```bash
make smoke-external                    # 4 个外部端点全部 ✓
.venv/bin/alembic upgrade head        # DB schema 就位
.venv/bin/python -m pytest tests/ -q  # 全量测试
```

### 3. 跑通核心流程
```bash
# 导入一本短篇
.venv/bin/python -m novel_analyzer.cli.app auto-run /path/to/novel.txt --max-chapters 5

# 检索基准
.venv/bin/python -m novel_analyzer.cli.app retrieval-benchmark <branch_id>

# 5 章 spike 仿写
.venv/bin/python -m novel_analyzer.cli.app writer-imitate-range \
  <branch_id> "2:目标A" "3:目标B" "4:目标C" \
  --output-dir output/spike --use-llm --max-rounds 2
```

### 4. UI 验证
```bash
make api-dev                                         # :8011
cd apps/web && npm install && npm run dev            # :4173
```
打开 `http://127.0.0.1:4173/control` 导入；`/qa` 问问题。

---

## Day 3：动手做需求（按方向选）

### 我要做拆书相关
- [deconstruction-acceleration/development-guide.md](../deconstruction-acceleration/development-guide.md) — 开发顺序 + 代码触点 + 测试矩阵 + 易踩的坑
- [foundation-optimization/README.md](../foundation-optimization/README.md) — 底座优化六层
- 关注代码：`novel_analyzer/services/context_service.py` `analysis_service.py` `retrieval_service.py`

### 我要做风险检查相关
- [risk-audit-runtime-architecture.md](../risk-audit-runtime-architecture.md)
- [risk-audit-checker-roadmap.md](../risk-audit-checker-roadmap.md)
- 关注代码：`novel_analyzer/services/risk_audit_service.py`、`risk_checkers/*`

### 我要做仿写相关
- [writer-imitation-workflow.md](../writer-imitation-workflow.md)
- [loom/handoff.md](../loom/handoff.md)
- [loom/roadmap.md](../loom/roadmap.md)
- [chapter-imitation-capability-matrix.md](../chapter-imitation-capability-matrix.md)
- 关注代码：`novel_analyzer/services/imitation_harness_service.py`、`skills_dir/`

### 我要做商业化 / API 相关
- [strategy/writer-studio-roadmap.md](../strategy/writer-studio-roadmap.md)
- [runbook/business-loop.md](../runbook/business-loop.md)
- [cross-genre-imitation-commercial-readiness-20260515.md](../cross-genre-imitation-commercial-readiness-20260515.md)
- 关注代码：`novel_analyzer/api/*`、`apps/web/`、`infra/`

### 我要做 Loom 上层（仿写增强）
- [loom/README.md](../loom/README.md) — 5 份 canonical 阅读顺序
- [loom/overview.md](../loom/overview.md) — 完整架构图
- 子模块按需深入：[memory/](../loom/memory/README.md) [tension/](../loom/tension/README.md) [reward/](../loom/reward/README.md) [style/](../loom/style/README.md) [character/](../loom/character/README.md) [phase6/](../loom/phase6/README.md)

---

## 开发约定（每个工程师都必须遵守）

### 重要语义
- 章节是最小提交单元，当前章成功后才能继续下一章
- 回退采用**逻辑隐藏**，默认只读 active branch
- 手工结果允许保留，但默认 `participates_in_downstream = false`
- 拆书失败自动重试上限 **5 次**，超过进入人工恢复
- 风险审查 **advisory-only**，不阻断主提交
- Loom 增量演进，feature flag 渐进启用、可随时回滚

### 开发流程
```bash
# 测试
.venv/bin/python -m pytest tests/ -q                  # 全量
.venv/bin/python -m pytest tests/test_imitation*.py   # 仿写
make v3-smoke                                          # e2e 烟雾

# 类型检查
.venv/bin/python -m mypy novel_analyzer/

# Lint
.venv/bin/ruff check novel_analyzer/
```

### 代码风格
- 后端 Python 3.11，使用 type hints；不准 `cast`、`type: ignore` 绕过类型错误
- 前端 TypeScript strict，不准 `any`
- DB 改动必须通过 Alembic migration，不直接改表
- 任何新功能加 feature flag，默认 OFF

---

## 进阶阅读（按需）

### 系统全景
- [whitepaper/ai-novel-system-whitepaper-v2.md](../whitepaper/ai-novel-system-whitepaper-v2.md) — 白皮书 v2
- [research/competing-novel-ai-projects-20260515.md](../research/competing-novel-ai-projects-20260515.md) — 竞品研究

### 跨能力线协作
- [tracks/README.md](../tracks/README.md) — 按能力线查文档
- [roles/backend/README.md](../roles/backend/README.md) — 后端角色入口

### 常见操作手册
- [cli-operations-manual.md](../cli-operations-manual.md) — CLI 命令真相源
- [ops-debug-manual-20260514.md](../ops-debug-manual-20260514.md) — 故障速查

---

## 检验清单（结束前自测）

读完这份路径后，应该能回答：

- [ ] 系统服务的两类用户和核心价值是什么？
- [ ] 4 条能力线分别叫什么、当前各自的状态？
- [ ] 章节为什么是最小提交单元？回退是怎么做的？
- [ ] adaptive context、stage merging、arc memory 大致是干什么的？
- [ ] 9 个 risk checker 是哪些？advisory-only 是什么意思？
- [ ] 跨题材改写为什么需要 mapping_pack？
- [ ] Loom 跟现有系统是叠加还是替换？
- [ ] v2 / v3 各做了什么？v4 还有几个 gap？
- [ ] 接到一个 bug，应该先看哪些文档？
- [ ] 接到一个新需求，应该先做什么验证？

如果上面有 3 个以上答不出来，回到对应章节再读一遍。

---

返回 [training/](./README.md) ｜ [文档中心](../README.md)
