# 培训路径 — 使用者 / 作家 / 创作

> **目标读者**：作家、编辑、内容创作者，要用系统做拆书 / 问答 / 仿写，**不需要懂代码**。
> **预计时长**：1-2 小时上手，半天熟练。

---

## 5 分钟先了解能不能用

### 它能给你做什么

| 你想做… | 系统怎么帮你 |
|--------|-------------|
| 把一本几百章的书整理出人物、伏笔、规则线 | 拆书 → 自动生成结构化 facts 和图谱 |
| 问 "第 12 章那个伏笔回收了吗？" | 流式 Q&A + 引用跳转，可以看到答案来源章节 |
| 担心仿写出来人物失格、规则乱、时间线不对 | 9 个 risk checker 自动扫，给你问题清单 |
| 用 A 书的风格写 B 题材（比如把仙侠改成科幻） | 跨题材 mapping_pack，已验证 99.4% 通过率 |
| 整本仿写不丢章节、不污染前后文 | per-chapter 增量保存 + auto-retry |
| 多次尝试不同设定不混乱 | Loom 项目壳：7 层 markdown，可锁定可对比 |

### 它不会做什么

- ❌ 完全自动写一本好看的小说（不能宣称 "AI 自动写书"）
- ❌ 评判你的小说好不好看
- ❌ 替代人工编辑
- ❌ 凭空帮你想出爆款

定位：**辅助工具**，不是 **替代品**。

---

## 选你的入口

### 我用 UI（推荐新手）

#### Workbench（旧工作台）
```
http://127.0.0.1:4173
```

| 页面 | 你能做什么 |
|------|----------|
| `/control` | 上传小说 → 启动分析 → 监控进度 |
| `/reader` | 查看分析后的章节，对照原文 |
| `/qa` | 流式 Q&A，问题答完会显示证据章节 |
| `/pipeline` | 看 pipeline 编排进度 |
| `/quality` | 质量仪表盘 |
| `/ops` | 导出报告、恢复中断 |

#### Writer Studio（作家端，v2/v3 新出）
```
http://127.0.0.1:4173/writer/<branch_id>
```
- 编辑器画布，**自动保存**
- Loom 信号侧栏：节奏 / 张力 / 风格 / 伏笔密度
- AI 副驾（流式聊天，引用跳转）
- 版本树（仿写分支管理）

#### Reader Studio（读者端）
```
http://127.0.0.1:4173/reader/<branch_id>
```
- 三栏布局：章节导航 / 阅读区 / Q&A
- 防剧透 Q&A：默认只用 ≤ 当前章节的数据回答
- 读者反馈：1-5 星评分 + 评论

### 我用 CLI（喜欢命令行的进阶用户）

详见 [cli-operations-manual.md](../cli-operations-manual.md)。常用 5 条：

```bash
# 1. 一键导入（注意 max-chapters=0 表示全部章节）
.venv/bin/python -m novel_analyzer.cli.app auto-run /path/to/novel.txt --max-chapters 0

# 2. 检索基准（看你的 R@5 多少）
.venv/bin/python -m novel_analyzer.cli.app retrieval-benchmark <branch_id>

# 3. 同题材 5 章 spike 仿写
.venv/bin/python -m novel_analyzer.cli.app writer-imitate-range \
  <branch_id> "2:目标A" "3:目标B" "4:目标C" "5:目标D" "6:目标E" \
  --output-dir output/spike --use-llm --max-rounds 2

# 4. 跨题材改写（仙侠 → 科幻）
.venv/bin/python -m novel_analyzer.cli.app writer-imitate-range \
  <branch_id> "2:目标A" "3:目标B" \
  --output-dir output/scifi --use-llm --max-rounds 2 \
  --world-map "郑国=星际联邦" --character-map "卫图=魏拓" \
  --power-map "养生功=星能调息术" \
  --rule-override "封建奴籍替换为合同义务工"

# 5. Loom 项目壳（一站式新故事编排）
.venv/bin/novel-analyzer imitate-project init my-new-story --source-branch-id <branch_id>
.venv/bin/novel-analyzer imitate-project run my-new-story --until prose --use-llm
```

---

## 完整使用流程（推荐顺序）

### 第一步：准备好你的小说文本
- 格式参考：[novel-ingest-input-spec.md](../novel-ingest-input-spec.md)
- 章节切分标准：[novel-ingest-chapter-standard.md](../novel-ingest-chapter-standard.md)

### 第二步：导入并拆书
```bash
.venv/bin/python -m novel_analyzer.cli.app auto-run /path/to/novel.txt --max-chapters 0
# 记录返回的 branch_id
```

### 第三步：验证质量
- 在 `/quality` 看仪表盘
- 在 `/qa` 问几个问题，看能不能引用到正确章节

### 第四步（可选）：仿写
**同题材**（保持原 setting）：
- 用 `writer-imitate-range` 不带 mapping flag

**跨题材改写**（换设定）：
- 用 `writer-imitate-range` 加上 `--world-map / --character-map / --power-map / --rule-override`
- 已经在 3 题材 170/171 章上跑通

**整本新故事**（基于参考小说风格）：
- 用 Loom 项目壳 `imitate-project`
- 7 层 markdown 一步步生成 + 锁定

### 第五步：审阅产物
- 风险审查：跑 `risk-audit <branch_id>`，看 risk card + cluster
- 读者评估：跑 4-persona × 7-dim panel（Reader Panel）

---

## 常见任务速查

| 我想… | 命令 / 入口 |
|------|-----------|
| 看系统能做什么 | [OVERVIEW.md](../OVERVIEW.md) |
| 一键探针环境 | `make smoke-external` |
| 看所有 CLI 命令 | [cli-operations-manual.md](../cli-operations-manual.md) |
| 看跨题材改写实证 | [cross-genre-imitation-commercial-readiness-20260515.md](../cross-genre-imitation-commercial-readiness-20260515.md) |
| 看仿写架构 | [loom/overview.md](../loom/overview.md) |
| 看 Loom 项目壳 SOP | [loom/phase6/runbook-template.md](../loom/phase6/runbook-template.md) |
| 看读者体验评估 | [handoffs/reader-panel-handoff-20260516.md](../handoffs/reader-panel-handoff-20260516.md) |
| 出问题不知道怎么办 | [ops-debug-manual-20260514.md](../ops-debug-manual-20260514.md) |

---

## 重要约定（避免踩坑）

- **章节是最小提交单元**：当前章失败时不会前进到下一章
- **拆书失败自动重试 5 次**：超过后进入人工恢复，不会继续浪费 token
- **回退采用逻辑隐藏**：你"撤销"后旧分支还在，只是被标记为 inactive
- **手工结果默认不参与下游**：你手动改的章节默认不会被检索 / 仿写消费，需要显式开启
- **风险审查不会阻断你**：advisory-only，给你提示但不强制停下来
- **跨题材必须显式给 mapping_pack**：不然系统按同题材处理，会保留原 setting

---

## 进阶：调优你的产出

### 模型选择
推荐配置（已经验证过的）：
```bash
NOVEL_ANALYZER_LLM_BASE_URL=http://34.97.18.233:65432/v1
NOVEL_ANALYZER_LLM_MODEL_NAME=claude-haiku-4.5
NOVEL_ANALYZER_LLM_STAGE_MODEL_NAME=claude-haiku-4.5
NOVEL_ANALYZER_LLM_REQUESTS_PER_SECOND=1.5
NOVEL_ANALYZER_USE_MERGED_STAGES=true
NOVEL_ANALYZER_LOOM_MEMORY_MODE=ab           # 启用 Loom 分层记忆
NOVEL_ANALYZER_LOOM_PAIRWISE_ENABLED=true     # 启用 pairwise 评估
```

### 提升仿写字数 / 质量
```bash
# 用更强模型 + 更多轮次
NOVEL_ANALYZER_LLM_MODEL_NAME=minimaxai/minimax-m2.7 \
.venv/bin/novel-analyzer imitate-project prose <slug> \
  --all --use-llm --max-rounds 3
```

### 检索召回上不去
- 检查领域词典：`.cache/novel-analyzer/domain-dict.txt` 是否为最新
- 检查 pg_jieba 是否启用：`CREATE EXTENSION IF NOT EXISTS pg_jieba;`
- 跑 `make tei-doctor` 看 embedding 服务

---

返回 [training/](./README.md) ｜ [文档中心](../README.md)
