# Session Handoff — 2026-05-17 (Phase 6 完成)

> 接手人速读：本文档记录 Loom Phase 6 Author Project Shell 的完整交付。
> 上一棒：[`session-handoff-20260517.md`](./session-handoff-20260517.md)

---

## 0. 环境状态（接手即可用）

| 项 | 值 |
|---|---|
| 分支 | `build` |
| 最新 commit | `84bcb18 docs(loom-phase6): mark Phase 6 complete in handoff + roadmap + sota-checklist` |
| Phase 6 commits | 18 个（`e17a030` → `84bcb18`） |
| 数据库 | PostgreSQL 17.5 @ 127.0.0.1:5432 / d2 / novel_analyzer |
| LLM | `claude-haiku-4.5` @ `http://34.97.18.233:65432/v1` |
| Loom mode | `ab`（50/50 A/B split，`.env.local` 已启用） |
| Phase 6 测试 | 89 pass |
| Loom Phase 1-5 测试 | 132 pass（零回归） |
| imitation 测试 | 15 pass |

---

## 1. Phase 6 核心交付

### 1.1 新增能力：`imitate-project` CLI（14 个子命令）

```bash
.venv/bin/novel-analyzer imitate-project --help
```

| 命令 | 功能 |
|------|------|
| `init <slug> --source-branch-id <id>` | 初始化项目目录 |
| `fingerprint <slug>` | 生成风格指纹（复用 Phase 4 style/rhythm 服务） |
| `macro <slug> [--use-llm]` | 生成 L1 大观（premise + world） |
| `characters <slug> [--use-llm]` | 生成 L2 角色卡（CharacterPersona 双向桥） |
| `plot <slug> [--use-llm]` | 生成 L3 剧情（arcs + chapter_goals + continuity） |
| `conflicts <slug> [--use-llm]` | 生成 L4 冲突（axes + innovation + taboo） |
| `outline <slug> [--chapter N] [--use-llm]` | 生成 L5 章纲 |
| `storyboard <slug> [--chapter N] [--use-llm]` | 生成 L6 分镜（scene beats） |
| `prose <slug> [--chapter N\|--all] [--use-llm] [--fast]` | 生成 L7 正文（复用 harness-imitation） |
| `revise <slug> <stage> --feedback "..."` | 任意层反馈修改 |
| `lock <slug> <file_glob>` | 锁定产物（下游必须适配） |
| `diff <slug> <stage>` | 版本 diff |
| `status <slug>` | 项目状态总览 |
| `run <slug> --until <stage> [--fast]` | 一键跑到指定层 |

### 1.2 新增服务文件

| 文件 | 职责 |
|------|------|
| `novel_analyzer/domain/project_config.py` | ProjectConfig + LoomFlagsConfig Pydantic 模型 |
| `novel_analyzer/services/project_shell_service.py` | 文件系统 artifact 管理（版本归档 + lock） |
| `novel_analyzer/services/project_compiler_service.py` | 7 层 markdown → 9 steering flag + 5 Loom env var |
| `novel_analyzer/services/project_style_view_service.py` | 风格指纹 VIEW（复用 Phase 4 服务） |
| `novel_analyzer/services/project_macro_service.py` | L1 大观生成 + RAG worldview-dossiers 贡献 |
| `novel_analyzer/services/project_characters_service.py` | L2 角色卡 + CharacterPersona ↔ markdown 双向桥 |
| `novel_analyzer/services/project_plot_service.py` | L3 剧情 + L4 冲突 + RAG trope-library 贡献 |
| `novel_analyzer/services/project_outline_service.py` | L5 章纲 + L6 分镜（scene beats） |
| `novel_analyzer/services/project_prose_service.py` | L7 正文编排（Loom flag 注入 + harness 调用 + 信号回流） |
| `novel_analyzer/services/satire_anti_slop_service.py` | 6 类讽刺文反 AI slop 检测 |
| `novel_analyzer/services/lock_contract_checker_service.py` | 锁定约束检查 |

### 1.3 新增 Skill

| Skill | 状态 |
|-------|------|
| `skills_dir/satire-anti-slop-guard/` | ✅ 已注册（list-skills 可见） |

### 1.4 MVP 验证结果

```
项目: meiqian-new-story（基于《没钱修什么仙》风格，全新故事）
源 branch: 72da24e9-e65c-45a9-836d-957c4ae783ec（卫图，200 章）

产物:
  output/projects/meiqian-new-story/
  ├── style/fingerprint.md + heuristics.json
  ├── macro/premise.md + world.md（已 lock）
  ├── characters/protagonist.md + female_lead.md + antagonist.md + mentor.md
  ├── plot/arcs.md + chapter_goals.md + continuity.md
  ├── conflicts/axes.md + innovation.md + taboo.md
  ├── chapters/ch001-003.outline.md + .storyboard.md + .draft.md
  └── book.config.yaml + locked.yaml

正文质量:
  ch001: 卫图在马厩发现大器晚成命格，决心修炼养生功（~850 字）
  ch002: 卫图买礼物拜访二姑卫荭，感受阶层落差（~750 字）
  ch003: 卫图从阮武师处得到龟息养气功，开始修炼（~700 字）

Loom 验证:
  loom-reference-eval ch2: overall_fidelity=0.62（enhanced vs baseline 4.3x）
  final_verdict: pass（全部 3 章）
  anti_slop_verdict: pass（全部 3 章）
```

### 1.5 贡献 Loom Roadmap

| Roadmap 项 | 贡献 |
|-----------|------|
| Phase 3 P3 pairwise 数据积累（当前 30/500） | prose 生成后自动 log loom-collect-pairs |
| Phase 5 P4 worldview-dossiers RAG 库 | `rag/worldview-dossiers/meiqian-new-story-worldview.md` |
| Phase 5 P4 trope-library RAG 库 | `rag/trope-library/meiqian-new-story-tropes.md` |

---

## 2. 下一步推荐（接手人）

### P0：真实 LLM 长跑验证

当前 MVP 用 `claude-haiku-4.5` 跑了 3 章，字数偏少（每章 ~700-850 字，正常网文章节应 2000-3000 字）。原因是 harness 在 `use_llm=False` 时走 template fallback，`use_llm=True` 时 harness 的 max_rounds=1 限制了迭代。

**建议**：
```bash
# 用更强模型 + 更多轮次重跑正文
NOVEL_ANALYZER_LLM_MODEL_NAME=minimaxai/minimax-m2.7 \
.venv/bin/novel-analyzer imitate-project prose meiqian-new-story \
  --all --use-llm --max-rounds 3
```

### P1：扩充 pairwise 数据池

当前 30/500 pairs（6%）。每次 prose 生成后运行：
```bash
.venv/bin/novel-analyzer loom-collect-pairs \
  --output-dir output/projects/meiqian-new-story/chapters/ \
  --pairs-file output/loom-pairs.jsonl
.venv/bin/novel-analyzer loom-pairs-stats --pairs-file output/loom-pairs.jsonl
```

### P2：多本范本叠加

当前只用了卫图（古典仙侠）作为源 branch。可以叠加《没钱修什么仙》（讽刺修仙）：
```bash
.venv/bin/novel-analyzer auto-run /home/user/txt111/01.txt --max-chapters 30
# 然后在 book.config.yaml 里配置多个 source_branch_id
```

### P3：Web UI 桥接

把 `output/projects/<slug>/` 的 markdown 文件流接到 `/writer/<branch_id>` 编辑器画布（Writer Studio）。这是 Loom Phase 6 的自然延伸，但超出当前 MVP 范围。

---

## 3. 已知限制

| 限制 | 说明 | 缓解 |
|------|------|------|
| 正文字数偏少 | harness 在 1 轮内生成，未充分迭代 | 增加 `--max-rounds 3`，换更强模型 |
| loom-collect-pairs 未真实触发 | T9 只 log，未实际调用 CLI | 手动运行 loom-collect-pairs |
| style_calibration 需要 loom_style_enabled=True | 默认 False，fingerprint 中 style_drift=0 | 在 book.config.yaml 设 `style_enabled: true` |
| 角色卡无 LLM 内容 | `use_llm=False` 时全是 `[请填写]` 占位符 | 运行 `imitate-project characters <slug> --use-llm` |

---

## 4. 标准操作手册（SOP）

### 4.1 从零开始新仿写项目

```bash
# Step 1: 导入范本小说（已有 branch 可跳过）
.venv/bin/novel-analyzer auto-run /path/to/novel.txt --max-chapters 30
# 记录输出的 branch_id

# Step 2: 初始化项目
.venv/bin/novel-analyzer imitate-project init <slug> --source-branch-id <branch_id>

# Step 3: 生成风格指纹（无需 LLM）
.venv/bin/novel-analyzer imitate-project fingerprint <slug>
# 查看: output/projects/<slug>/style/fingerprint.md

# Step 4: 生成大观（可选 LLM）
.venv/bin/novel-analyzer imitate-project macro <slug> --use-llm
# 审阅: output/projects/<slug>/macro/premise.md + world.md
# 满意后锁定: imitate-project lock <slug> "macro/*.md"

# Step 5: 生成角色
.venv/bin/novel-analyzer imitate-project characters <slug> --use-llm
# 审阅: output/projects/<slug>/characters/*.md
# 锁定主角: imitate-project lock <slug> "characters/protagonist.md"

# Step 6: 生成剧情 + 冲突
.venv/bin/novel-analyzer imitate-project plot <slug> --use-llm
.venv/bin/novel-analyzer imitate-project conflicts <slug> --use-llm

# Step 7: 生成章纲 + 分镜（3 章）
.venv/bin/novel-analyzer imitate-project outline <slug> --use-llm
.venv/bin/novel-analyzer imitate-project storyboard <slug> --use-llm

# Step 8: 生成正文
.venv/bin/novel-analyzer imitate-project prose <slug> --all --use-llm --max-rounds 2

# Step 9: 查看状态
.venv/bin/novel-analyzer imitate-project status <slug>

# Step 10: Loom 验证
.venv/bin/novel-analyzer loom-reference-eval <branch_id> 0 output/projects/<slug>/chapters/
```

### 4.2 反馈修改循环

```bash
# 修改某层后重新生成
.venv/bin/novel-analyzer imitate-project revise <slug> macro --feedback "调性更冷峻" --use-llm

# 查看版本差异
.venv/bin/novel-analyzer imitate-project diff <slug> macro

# 锁定满意的版本
.venv/bin/novel-analyzer imitate-project lock <slug> "macro/*.md"

# 重新生成下游（outline 会读取新的 macro）
.venv/bin/novel-analyzer imitate-project outline <slug> --use-llm
.venv/bin/novel-analyzer imitate-project prose <slug> --all --use-llm
```

### 4.3 快速原型（跳过所有 gate）

```bash
.venv/bin/novel-analyzer imitate-project run <slug> --until prose --fast --use-llm
```

### 4.4 验证 Loom 信号

```bash
# 查看 Loom 状态
.venv/bin/novel-analyzer loom-status <branch_id>

# 评估仿写还原度
.venv/bin/novel-analyzer loom-reference-eval <branch_id> 1 output/projects/<slug>/chapters/

# A/B 对比
.venv/bin/novel-analyzer loom-ab-compare output/baseline/ output/projects/<slug>/chapters/

# 查看 pairwise 数据进度
.venv/bin/novel-analyzer loom-pairs-stats --pairs-file output/loom-pairs.jsonl
```

---

## 5. 文档索引

| 文档 | 说明 |
|------|------|
| [docs/loom/phase6/README.md](./loom/phase6/README.md) | Phase 6 定位 + 7 层表 + 快速开始 |
| [docs/loom/phase6/workflow.md](./loom/phase6/workflow.md) | 5 步工作流 + mermaid 图 + 反馈循环 |
| [docs/loom/phase6/arch-alignment.md](./loom/phase6/arch-alignment.md) | 边界澄清（vs 0509 / vs Phase 1-5 / vs writer-imitate-range） |
| [docs/loom/phase6/runbook-template.md](./loom/phase6/runbook-template.md) | 端到端命令清单 |
| [docs/loom/handoff.md](./loom/handoff.md) | Loom 整体交接（含 Phase 6 完成记录） |
| [docs/loom/roadmap.md](./loom/roadmap.md) | Phase 1-6 路线图（Phase 6 已 ✅） |
| [docs/loom/sota-imitation-progression-checklist.md](./loom/sota-imitation-progression-checklist.md) | SOTA 推进 checklist（Section I 全 ✅） |

---

## 6. 本会话 commit 列表（Phase 6，18 commits）

```
84bcb18 docs(loom-phase6): mark Phase 6 complete in handoff + roadmap + sota-checklist
4c06c18 fix(loom-phase6): add YAML frontmatter + prompts/ to satire-anti-slop-guard + style-calibrator skills
fc9e6c6 feat(loom-phase6): T12 MVP run + T14 plan complete — all 14 tasks done
43a9fb5 test(loom-phase6): zero-regression + e2e integration test + compare script (T14)
e568d14 chore(loom-phase6): mark T14 done in plan
c2c86d8 test(loom-phase6): e2e 7-layer pipeline + compare_loom_metrics script (T14)
699e61d feat(loom-phase6): prose orchestrator with Loom flag injection + signal frontmatter (T9)
92029d0 docs(changelog): record T8 outline + storyboard + scene_beats skill extension
e829977 feat(loom-phase6): outline + storyboard stages + scene_beats skill extension (T8)
6185fa0 docs(loom-phase6): slot Phase 6 into Loom canonical docs structure (T13)
7e63cab docs(changelog): record T11 satire-anti-slop-guard + lock_contract_checker
a781b13 feat(loom-phase6): plot + conflicts stages aligned to _legacy_compat (T7)
0622cf1 feat(loom-phase6): satire-anti-slop-guard skill + lock_contract_checker (T11)
457e1ee feat(loom-phase6): revise/lock/diff/status/run ops subcommands (T10)
745469f feat(loom-phase6): macro stage — premise + world + RAG library entry (T5)
817d99d feat(loom-phase6): characters stage with CharacterPersona ↔ markdown bridge (T6)
f3e1735 feat(loom-phase6): style fingerprint VIEW reusing Phase 4 services (T4)
e17a030 feat(loom-phase6): stage-to-flag compiler + Loom env var mapping (T3)
91ca858 feat(loom-phase6): foundation — ProjectConfig + shell service + CLI stubs (T1+T2)
```
