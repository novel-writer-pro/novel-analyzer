# Loom Phase 6 — Author Project Shell

> 让 Loom 的 Phase 1-5 能力对作家可用的 UX 层。**纯增量,不重写任何 Loom 服务**。

## TL;DR

> **核心定位**: Loom 已经把"长记忆 + 张力 + Pairwise 评估 + 风格量化 + 节奏 + 对话信号 + 角色认知 + 读者模拟 + 多线调度 + 长书健康"都做了(Phase 1-5,130+ 测试通过,卫图样例 fidelity=0.78 已验证)。但作家**没法直接编辑**这些抽象产物——所有 steering 都靠 9 个 CLI flag 在终端里背。
>
> Phase 6 = **作家面向的项目壳**:把 Loom 已有信号 + steering pack 入参,**收口成 7 层可编辑 markdown 项目目录**,作家在 macro/characters/plot/conflicts/outline/storyboard 任何一层审阅、批注、锁定、回退、重写,系统编译成现有 CLI flag + Loom feature flag 喂给 harness-imitation。
>
> **Deliverables**:
> - 11 个新 CLI 子命令: `imitate-project init / fingerprint / macro / characters / plot / conflicts / outline / storyboard / prose / revise / lock / diff / status / run`
> - 7 层 markdown 模板,落到 `output/projects/<slug>/`
> - 1 个 stage-to-flag 编译器 + Loom feature flag mapping(把项目 gates 翻译成 `loom_memory_mode/style/character/pairwise` 等开关)
> - 1 个 storyboard 层(扩展 `imitation-constraint-pack` skill input,scene_beats 字段向后兼容)
> - 1 个 `satire-anti-slop-guard` skill + checker(讽刺文专属反 AI slop)
> - 1 个 `lock_contract_checker`(项目 lock 语义,findings 通过 `session_loom_signals` 通道暴露)
> - 文档: `docs/loom/phase6/` 系列,slot 进 Loom canonical 5 份主文档结构
> - 端到端 MVP:基于《没钱修什么仙》的新故事 3 章正文,用 `loom-reference-eval` + `loom-ab-compare` 验证
>
> **Estimated Effort**: Medium (11 实施任务 + 4 终审,~5 天)
> **Parallel Execution**: YES,4 waves
> **Critical Path**: T1 → T3 → T8 → T9 → T12 → F1-F4

---

## Context

### Original Request
> "基于这个项目做仿写实操,详细的人机交互方案。从大观、角色、剧情、冲突、小章描写、分镜等等都能有反馈、有修改的这种模式。结合当前的架构,可以反馈、可以仿写实操、快速看到效果。"
>
> 范本:`/home/user/txt111/01.txt`《没钱修什么仙》(讽刺现实修仙文)

### 用户已确认决策
- Q1 风格借鉴 + 全新故事 / Q2 MVP 3 章 / Q3 markdown + CLI / Q4 用户自选 gates / Q5 锁定=只读

### Loom 当前状态(已落地能力,本计划复用)

**Phase 1-5 全部服务已实现 + 130 tests passing**(`docs/loom/handoff.md`):

| Loom 模块 | 已落地服务 | Phase 6 怎么用 |
|-----------|----------|---------------|
| **memory** | `memory_assembler_service` / `memory_consolidation_service` | T9 prose 调用 `assemble` 获得三层记忆喂 prompt;`plot/continuity.md` 是 _legacy_compat 字段的 markdown 视图 |
| **tension** | `tension_service`(plot_similarity / conflict_density / surprise_index) | T9 prose frontmatter 渲染 `_loom_tension` 信号 |
| **reward** | `pairwise_eval_service`(5 维度 LLM-as-judge) | T9 自动产 pairwise 数据;T12 调用 `loom-reference-eval` 做 MVP 验收 |
| **style** | `style_calibration_service`(向量化 + 漂移) | T4 渲染到 `style/fingerprint.md`;T9 frontmatter 显示 style_drift_score |
| **rhythm** | `rhythm_analysis_service`(hook_density / pacing_type / climax_score) | T4 渲染到 fingerprint;T9 frontmatter |
| **dialogue** | `dialogue_signal_service`(voice_consistency / efficiency / conflict_dialogue_density) | T9 frontmatter 显示 `_loom_dialogue` |
| **character** | `character_agent_service.build_character_persona / check_character_consistency` | T6 把 CharacterPersona 序列化为可编辑 markdown,作家修改后反序列化 |
| **reader_sim** | `reader_simulation_service`(4 panels: casual/veteran/satisfaction/editor) | T9 frontmatter 显示 `_loom_reader_sim` |
| **threads** | `thread_scheduler_service`(active/dormant/overdue + suggestion) | T9 prose 后回填到 `plot/continuity.md` |
| **long_book** | `long_book_health_service` | future-proof 接(MVP 不需要,3 章不触发健康监测) |

**已有 Loom CLI 8 个**: `loom-status / loom-consolidate / loom-assemble / loom-collect-pairs / loom-pairs-stats / loom-ab-compare / loom-collect-pairs-from-db / loom-collect-pairs-from-manual / loom-reference-eval`

**已有 Loom 输出字段**(operator surface 已暴露):
- `session_loom_signals`(tension / quality / style / rhythm / character / reader_sim / thread_activation)
- `session_loom_gate_summary`(质量、张力、迁移状态摘要)
- `session_primary_verdicts` 含 `chapter_quality_score / quality_verdict / average_chapter_quality_score`
- `_loom_*` 系列 skill output 字段

**已有 Loom feature flags**:
```
NOVEL_ANALYZER_LOOM_MEMORY_MODE      # disabled / shadow / ab / enabled
NOVEL_ANALYZER_LOOM_TENSION_ENABLED
NOVEL_ANALYZER_LOOM_PAIRWISE_ENABLED
NOVEL_ANALYZER_LOOM_STYLE_ENABLED
NOVEL_ANALYZER_LOOM_CHARACTER_ENABLED
```

### Loom 缺的(Phase 6 要补的)

| 缺口 | 来源 | Phase 6 解法 |
|------|------|-------------|
| 作家无法直接编辑中间产物 | 用户原始诉求 | 7 层 markdown 项目目录 + 编辑/lock/revise/diff |
| 没有"项目"实体 | `output/` 散落 writer-imitate-* | `book.config.yaml` + `output/projects/<slug>/` 标准化 |
| 9 个 steering flag 命令行难记 | `writer-imitation-workflow.md` | stage-to-flag 编译器,作家只编辑 markdown |
| Loom feature flags 是全局环境变量 | `handoff.md` | 项目级配置,每项目独立 toggle |
| 反讽/讽刺文专属 anti-slop 缺失 | 范本风格画像 | 新 skill `satire-anti-slop-guard` |
| 没有作家"lock"语义 | `gap-analysis-and-evolution.md` | `lock_contract_checker` + frontmatter `lock_assertions` |
| `scene_beats` 字段不可作家编辑 | Loom roadmap 未涉及 | 扩展 `imitation-constraint-pack` skill input,markdown 化 |
| `CharacterPersona` 不可作家编辑 | 同上 | T6 序列化/反序列化双向桥 |

### 范本风格画像(简记,详见 `.sisyphus/drafts/`)
讽刺引擎: 万物商品化 / 声音: 务实计算 + "特么的" / 冲突: 3 拍(setup → power reveal → dystopian reversal) / 节奏: 40/35/15/10。

---

## Work Objectives

### Core Objective
作为 Loom Phase 6,在 Phase 1-5 已有的 9 个服务 + 8 个 CLI 之上,新增"作家面向 markdown 项目壳"。让用户能在 7 层(style / macro / characters / plot / conflicts / outline / storyboard / prose)逐层审阅 + 编辑 + 锁定 + 回退 + 再生成,最终用 Loom 已验证的 reference-eval 跑出基于范本风格的全新原创小说前 3 章。

### 7 层产物对照表

| 层级 | 用户编辑文件 | 编译产物 | 复用 Loom 什么 |
|------|-------------|---------|---------------|
| L0 风格 | `style/fingerprint.md` | `--knowledge-ref` + Loom flags toggle | `style_calibration_service` + `rhythm_analysis_service` |
| L1 大观 | `macro/premise.md` `macro/world.md` | `--worldview-note` `--rule-override` | 直接进 `imitation-constraint-pack` |
| L2 角色 | `characters/<name>.md` | `--character-map` + author-knowledge | `character_agent_service.build_character_persona`(双向序列化) |
| L3 剧情 | `plot/arcs.md` `plot/chapter_goals.md` `plot/continuity.md` | `chapter_goals` 列表 + carry-over | `memory_assembler_service` 的 `_legacy_compat` 字段 |
| L4 冲突 | `conflicts/{axes,innovation,taboo}.md` | `--trope-axis*N` `--innovation-directive` `--taboo-innovation` | 已有 steering pack 通道 |
| L5 章纲 | `chapters/ch{NNN}.outline.md` | `target_goal` for `iterate-imitation` | 已有 `iterate-imitation` |
| L6 分镜 ⭐NEW | `chapters/ch{NNN}.storyboard.md` | 注入 `imitation-constraint-pack` 的 `scene_beats` | 扩展现有 skill(向后兼容) |
| L7 正文 | `chapters/ch{NNN}.draft.md`(多版) | LLM 生成 | `harness-imitation` + 全部 `_loom_*` 信号回流 frontmatter |

### Concrete Deliverables
- 11 个 `imitate-project` CLI 子命令
- 1 个新 service: `novel_analyzer/services/project_shell_service.py`
- 1 个新 service: `novel_analyzer/services/project_compiler_service.py`(stage-to-flag + Loom flag mapping)
- 1 个新 service: `novel_analyzer/services/satire_anti_slop_service.py`
- 1 个新 service: `novel_analyzer/services/lock_contract_checker_service.py`
- 1 个 skill 扩展(向后兼容): `skills_dir/imitation-constraint-pack/`(append `scene_beats` field)
- 1 个新 skill: `skills_dir/satire-anti-slop-guard/`
- 1 个 character 双向序列化器(在 `project_shell_service`,调 `character_agent_service`)
- 文档 4 份: 入口 + workflow + roadmap-slot + arch-alignment-update
- 测试: `tests/test_loom_phase6_*.py` 系列(新增) + 现有 130 Loom 测试零回归
- MVP: 基于范本的 3 章正文,用 `loom-reference-eval` 验证

### Definition of Done
- [x] `.venv/bin/novel-analyzer imitate-project --help` 显示 11 个子命令
- [x] 完整跑通 7 层(任意章节),每层产物落盘可读
- [x] 任意层 `imitate-project revise <stage> --feedback "..."` 生成 v2,v1 自动归档
- [x] `imitate-project diff <stage>` 输出 unified diff
- [x] `imitate-project lock <file>` 写 locked.yaml + frontmatter,下游 prose 把 `lock_assertions` 注入 prompt
- [x] 现有 Loom 测试 100% pass:`pytest tests/test_loom_phase[1-5]*.py -q` 全绿(零回归基线)
- [x] 新加 `tests/test_loom_phase6_*.py` 100% pass
- [x] 现有 imitation 服务签名零变更(`git diff main -- novel_analyzer/services/{chapter,imitation,whole_book}_imitation_service.py` 空)
- [x] 无 alembic migration 新增
- [x] 端到端 MVP 3 章正文 ≥ 12,000 中文字
- [x] `loom-reference-eval` 在 MVP 上跑出 fidelity ≥ 0.5(参考卫图基线)
- [x] `loom-ab-compare` 显示 Phase 6 项目壳产物质量 ≥ baseline writer-imitate-range 产物
- [x] 4 个终审 agent 全部 APPROVE,用户给 explicit okay

### Must Have
- 所有 7 层产物带 YAML frontmatter(stage / version / parents / locked / lock_assertions / generated_at)
- `book.config.yaml` 包含 `gates / locked / loom_flags`(项目级 Loom toggle)
- T3 编译器同时输出 9 个现有 steering flag + 5 个 Loom feature flag
- L6 storyboard 是唯一新生成层,通过追加 `scene_beats` 到 `imitation-constraint-pack` 实现(向后兼容)
- T6 角色双向桥: CharacterPersona ↔ markdown,作家编辑后反序列化喂回 character_agent_service
- T9 prose frontmatter 渲染所有 `_loom_*` 信号(tension / style / rhythm / character / reader_sim / chapter_quality_score)
- T9 prose 后调用 `loom-collect-pairs` 自动累积 pairwise 数据(贡献 Loom Phase 3 P3 数据积累目标 500 pairs)
- 反 AI slop 6 类反讽文专属反模式(详见 T11)
- 项目层不写数据库,只用 `output/projects/`
- MVP 验收用 `loom-reference-eval` + `loom-ab-compare`

### Must NOT Have(Guardrails)
- ❌ 修改任何 Loom 服务的方法签名(`memory_assembler / memory_consolidation / tension / pairwise_eval / style_calibration / rhythm_analysis / dialogue_signal / character_agent / reader_simulation / thread_scheduler / long_book_health`)
- ❌ 修改 `chapter_imitation_service` / `imitation_harness_service` / `whole_book_imitation_service` 现有签名
- ❌ 添加 alembic migration / 修改 PostgreSQL schema(Loom Phase 1 已有 migration,Phase 6 不需要)
- ❌ 触碰现有 9 个 risk checker 实现
- ❌ 修改任何 `tests/test_loom_phase[1-5]*.py` 测试(零回归硬门)
- ❌ Web UI / `apps/web/` 改动(项目壳是 CLI-only)
- ❌ 引入新 pip 依赖
- ❌ 反讽小说 6 类 AI slop 反模式(详见 T11)
- ❌ 项目壳直接调 LLM 写正文(必须经 `harness-imitation` + Loom 增强后)
- ❌ Fast 模式跳 gate 但不留版本(必须留可回退)
- ❌ 用 Loom shadow 模式当 enabled 用(必须 explicit 设 loom_memory_mode=enabled 才走完整 Loom 链路)

---

## Verification Strategy

### Test Decision
- **Infrastructure**: ✅ pytest(已配)+ Loom 已有 130 tests
- **Strategy**: tests-after,每个 service 写完即补单元 + 集成
- **回归基线(硬门)**: `pytest tests/test_imitation*.py tests/test_loom_phase[1-5]*.py -q` 必须 100% pass

### Loom-Aligned MVP Validation
- 用 `loom-reference-eval` 跑 fidelity(已被卫图样例验证过的方法)
- 用 `loom-ab-compare` 比较 Phase 6 项目壳 vs 直接 `writer-imitate-range`
- 用 `loom-collect-pairs` 累积 pairwise 数据,贡献 Loom Phase 3 数据池

### Anti-Slop 验证(范本不误报)
范本前 5 章作 negative test set,`satire-anti-slop-guard` 必须全部 pass(否则误报)

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation, 3 parallel):
├── T1: ProjectConfig + ProjectShellService skeleton + CLI subgroup stubs [quick]
├── T2: Source branch validator + chapter sampler + runbook [quick]
└── T3: Stage-to-flag compiler + Loom flag mapping [unspecified-high]

Wave 2 (Editable layers, 4 parallel):
├── T4: Style fingerprint VIEW (call style_calibration + rhythm_analysis) [unspecified-high]
├── T5: Macro stage (premise + world; emit RAG library entry) [deep]
├── T6: Characters stage (CharacterPersona ↔ markdown bridge) [deep]
└── T7: Plot + Conflicts stages (combined) [deep]

Wave 3 (Bottom-up to prose, 3):
├── T8: Outline + Storyboard ⭐NEW (extend imitation-constraint-pack) [artistry]
├── T9: Prose orchestrator (Loom flag injection + _loom_* frontmatter + auto loom-collect-pairs) [unspecified-high]
└── T10: revise/lock/diff/status/run ops commands [unspecified-high]

Wave 4 (Validation + UX checkers + docs, 4 parallel):
├── T11: satire-anti-slop-guard skill + checker + lock_contract_checker [artistry]
├── T12: MVP run + loom-reference-eval + loom-ab-compare validation [unspecified-high]
├── T13: Loom-aligned docs (slot into docs/loom/phase6/) [writing]
└── T14: Tests + zero-regression + style fingerprint + Loom flag verification [unspecified-high]

Wave FINAL:
├── F1: Plan compliance audit (oracle)
├── F2: Code quality + Loom-zero-regression review (unspecified-high)
├── F3: Real manual QA on 3-chapter MVP with loom-reference-eval (unspecified-high)
└── F4: Scope fidelity + Loom integration audit (deep)

Critical Path: T1 → T3 → T8 → T9 → T12 → F1-F4
Max Concurrent: 4
```

### Dependency Matrix
- **T1**: blocks T2, T3, T4-T14 — 项目骨架
- **T2**: blocks T4-T7 — 需要 source branch
- **T3**: blocks T5-T10 — 各 stage 依赖编译器
- **T4-T7**: parallel,都依赖 T1+T2+T3
- **T8**: depends T5/T6/T7(需要全部上游)
- **T9**: depends T3, T4, T8(需要 flag 编译器 + storyboard + 风格信号)
- **T10**: depends T1
- **T11**: depends T1, T6(主角名要从 characters)
- **T12**: depends T9, T11
- **T13**: depends T9, T10, T11
- **T14**: depends T1-T13
- **F1-F4**: 全部完成后并行

### Agent Dispatch
- W1: T1, T2 → `quick` | T3 → `unspecified-high`
- W2: T4 → `unspecified-high` | T5, T6, T7 → `deep`
- W3: T8 → `artistry` | T9, T10 → `unspecified-high`
- W4: T11 → `artistry` | T12, T14 → `unspecified-high` | T13 → `writing`
- Final: F1 → `oracle` | F2, F3 → `unspecified-high` | F4 → `deep`

---

## TODOs

- [x] 1. **ProjectConfig + ProjectShellService skeleton + CLI subgroup**

  **What to do**:
  - 在 `novel_analyzer/domain/project_config.py` 创建 Pydantic v2 `ProjectConfig`,字段:
    - `name: str`, `slug: str`, `source_branch_id: str`(必填), `source_chapters_for_style: list[int] = list(range(1,31))`
    - `target_chapters: int = 3`
    - `gates: list[Stage]`, `auto_pass: list[Stage]`, `locked_files: list[str]`
    - **`loom_flags`**:`LoomFlagsConfig`(项目级 Loom toggle)
      - `memory_mode: Literal["disabled","shadow","ab","enabled"] = "enabled"`
      - `tension_enabled: bool = True`
      - `pairwise_enabled: bool = True`
      - `style_enabled: bool = True`
      - `character_enabled: bool = True`
    - 7 个 stage enum: `Stage = Literal["style","macro","characters","plot","conflicts","outline","storyboard","prose"]`
    - default gates: `["macro","characters","plot","outline","prose"]`,auto_pass: `["conflicts","storyboard"]`
  - 在 `novel_analyzer/services/project_shell_service.py` 创建 `ProjectShellService`,核心方法:
    - `init(slug, source_branch_id, **opts) -> ProjectConfig`(创建目录树 + book.config.yaml)
    - `read_artifact / write_artifact`(带 frontmatter,版本归档到 `runs/<ISO_ts>/`)
    - `lock / unlock / is_locked / list_locked_assertions`
    - `apply_loom_flags(slug)`(把 ProjectConfig.loom_flags 设到环境变量,临时生效)
  - 注册 Typer subgroup `imitate-project`,11 个子命令 stub(stub 仅打印 "TODO",T2-T10 填充)
  - 目录树:`output/projects/<slug>/{book.config.yaml, locked.yaml, style/, macro/, characters/, plot/, conflicts/, chapters/, runs/}`
  - markdown frontmatter: `stage / version / parents / locked / lock_assertions / generated_at`

  **Must NOT do**:
  - 不要写数据库
  - 不要把 ProjectConfig 持有 LLM client
  - 11 个子命令在 T1 阶段全是 stub
  - 不要修改任何 Loom 服务

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES — Wave 1
  - **Blocks**: T2-T14
  - **Blocked By**: None

  **References**:
  - `novel_analyzer/config/settings.py` — Pydantic Settings 模式 + Loom flags 现有 5 个环境变量
  - `novel_analyzer/cli/app.py:1-80` — Typer subgroup 注册模式
  - `novel_analyzer/runtime/storage.py` — runtime 路径解析
  - `docs/loom/handoff.md` §6 变量速查 — 现有 Loom feature flags 名称

  **WHY**:
  - Loom flags 是环境变量,ProjectConfig 通过 `apply_loom_flags` 临时设置 = 项目级隔离不破坏 Loom shadow/ab 模式

  **Acceptance Criteria**:
  - [x] `from novel_analyzer.domain.project_config import ProjectConfig, LoomFlagsConfig` 可 import
  - [x] `imitate-project --help` 显示 11 个子命令
  - [x] `pytest tests/test_loom_phase6_shell.py -q` 通过
  - [x] `git diff main -- novel_analyzer/services/{memory_assembler,memory_consolidation,tension,pairwise_eval,style_calibration,rhythm_analysis,dialogue_signal,character_agent,reader_simulation,thread_scheduler}_service.py` 空
  - [x] `pytest tests/test_loom_phase[1-5]*.py -q` 100% pass

  **QA Scenarios**:

  ```
  Scenario: init + Loom flags
    Tool: Bash
    Steps:
      1. .venv/bin/novel-analyzer imitate-project init demo --source-branch FAKE
      2. cat output/projects/demo/book.config.yaml | grep -E 'loom_flags|memory_mode|tension_enabled'
      3. python -c "from novel_analyzer.services.project_shell_service import ProjectShellService; svc=ProjectShellService(...); svc.apply_loom_flags('demo'); import os; print(os.environ.get('NOVEL_ANALYZER_LOOM_MEMORY_MODE'))"
    Expected: yaml 含 loom_flags 段;apply 后环境变量被设
    Evidence: .sisyphus/evidence/task-1-init.txt

  Scenario: 零 Loom 回归
    Tool: Bash
    Steps:
      1. .venv/bin/pytest tests/test_loom_phase[1-5]*.py -q
    Expected: 130 passed
    Evidence: .sisyphus/evidence/task-1-loom-regression.txt
  ```

  **Commit**: YES
  - Message: `feat(loom-phase6): foundation — ProjectConfig + shell service + CLI stubs`
  - Constraint: must not modify Phase 1-5 Loom services

- [x] 2. **Source branch validator + chapter sampler + runbook**

  **What to do**:
  - 在 `project_shell_service.py` 添加:
    - `ensure_source_branch(slug) -> str`: 验证 branch 存在 + chapter count ≥ source_chapters_for_style 最大值;失败抛 `SourceBranchNotReadyError` 含修复命令 `请先执行: auto-run <txt> --max-chapters 30`
    - `sample_source_chapters(slug, indices) -> list[ChapterArtifact]`: 通过 `ChapterIndexService` 拿 raw text
  - 写 runbook 模板 `docs/loom/phase6/runbook-template.md`,5 步:`auto-run` → `imitate-project init` → `run --until prose` → 审阅 markdown → revise/lock/diff
  - 不实际跑 auto-run(T12 MVP 才跑)

  **Must NOT do**:
  - 不要 subprocess.run("auto-run")(必须接 service)
  - 不要重新解析 txt(必须从 ChapterArtifact 表读)
  - 不要假设 source branch 一定存在

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES — Wave 1
  - **Blocks**: T4-T7
  - **Blocked By**: T1

  **References**:
  - `novel_analyzer/services/chapter_index_service.py` — 章节查询接口
  - `novel_analyzer/services/run_service.py` — branch 元数据
  - `novel_analyzer/database/models.py:ChapterArtifact` — ORM 模型
  - `docs/whole-book-quickstart-20260514.md` — auto-run 现有流程

  **WHY**:
  - 必须用 ChapterIndexService 而非直 SQL,保持分层

  **Acceptance Criteria**:
  - [x] 缺 branch 时抛 `SourceBranchNotReadyError` 含 `auto-run` 命令
  - [x] `sample_source_chapters` 返回带 raw_text 的 ChapterArtifact
  - [x] `docs/loom/phase6/runbook-template.md` 存在
  - [x] pytest 单测通过

  **QA Scenarios**:

  ```
  Scenario: 缺 branch 友好失败
    Tool: Bash
    Steps:
      1. svc.ensure_source_branch("nonexistent") 2>&1 | grep "auto-run"
    Expected: 抛错且消息含 auto-run 修复命令
    Evidence: .sisyphus/evidence/task-2-missing.txt

  Scenario: 抽样可用
    Tool: Bash (有真实 branch 时)
    Steps:
      1. svc.sample_source_chapters("real_demo", [1,2,3]) → 3 个 artifact 都有 raw_text > 1000
    Evidence: .sisyphus/evidence/task-2-sample.txt
  ```

  **Commit**: YES
  - Message: `feat(loom-phase6): source branch validator + chapter sampler + runbook`

- [x] 3. **Stage-to-flag compiler + Loom flag mapping**

  **What to do**:
  - 创建 `novel_analyzer/services/project_compiler_service.py:ProjectCompilerService`
  - 核心方法 `compile_for_chapter(slug, chapter_idx) -> CompiledFlags`:
    ```python
    @dataclass
    class CompiledFlags:
        # 现有 9 个 steering flag
        worldview_note: str           # 来自 macro/world.md
        rule_overrides: list[str]     # 来自 macro/world.md "规则" 段
        trope_axes: list[str]         # 来自 conflicts/axes.md
        innovation_directives: list[str]  # 来自 conflicts/innovation.md
        taboo_innovations: list[str]  # 来自 conflicts/taboo.md
        knowledge_refs: list[str]     # 来自 style/fingerprint.md + 命中 snippets
        world_map: dict[str, str]     # 来自 macro/premise.md "映射" 段
        character_map: dict[str, str] # 来自 characters/*.md frontmatter
        power_map: dict[str, str]     # 来自 macro/world.md "力量" 段
        target_goal: str              # 来自 chapters/ch{NNN}.outline.md H1
        scene_beats: list[Beat]       # 来自 chapters/ch{NNN}.storyboard.md
        lock_assertions: list[str]    # 来自所有 locked 文件
        # Loom feature flags(从 ProjectConfig.loom_flags)
        loom_memory_mode: str
        loom_tension_enabled: bool
        loom_pairwise_enabled: bool
        loom_style_enabled: bool
        loom_character_enabled: bool
    ```
  - `to_cli_args(flags) -> list[str]`:steering flag 转 CLI argv
  - `to_env_vars(flags) -> dict[str,str]`:**Loom flag 转环境变量**(`NOVEL_ANALYZER_LOOM_*`)
  - `to_constraint_pack_input(flags) -> dict`:scene_beats 注入(为 T8 准备)
  - 所有解析 deterministic,不调 LLM

  **Must NOT do**:
  - 不要在编译器做创作
  - 不要假设 markdown 一定有某段(missing 返回空 + warning)
  - 不要修改 imitation 服务 contract(只产出可消费 input)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES — Wave 1
  - **Blocks**: T5-T10
  - **Blocked By**: T1

  **References**:
  - `novel_analyzer/services/whole_book_imitation_service.py` — `WholeBookImitationContract` 字段类型对齐
  - `novel_analyzer/services/imitation_harness_helpers.py` — argv 拼装 helper
  - `docs/writer-imitation-workflow.md` §3 — 9 个 steering flag 语义
  - `docs/loom/handoff.md` §6 变量速查 — Loom flag 环境变量名

  **WHY**:
  - 类型对齐 → T9 prose 喂入零类型转换
  - 复用 helper → 防引号转义 bug

  **Acceptance Criteria**:
  - [x] `compile_for_chapter("demo", 1)` 返回 CompiledFlags 全字段类型对
  - [x] 缺失文件返回空 + warning,不抛错
  - [x] `to_cli_args(flags)` 可被 `typer.testing.CliRunner` 解析
  - [x] `to_env_vars(flags)` 含 5 个 `NOVEL_ANALYZER_LOOM_*`
  - [x] lock_assertions 出现在 flags

  **QA Scenarios**:

  ```
  Scenario: 完整编译 + Loom flag mapping
    Tool: Bash
    Steps:
      1. flags = svc.compile_for_chapter("demo", 1)
      2. assert flags.loom_memory_mode == "enabled"
      3. envs = svc.to_env_vars(flags)
      4. assert "NOVEL_ANALYZER_LOOM_MEMORY_MODE" in envs
      5. argv = svc.to_cli_args(flags); assert "--worldview-note" in argv
    Evidence: .sisyphus/evidence/task-3-compile.txt

  Scenario: 缺失字段优雅降级
    Tool: Bash
    Steps:
      1. 删 demo/macro/world.md
      2. compile_for_chapter("demo", 1) → worldview_note=""
      3. stderr 含 "warning: missing"
    Evidence: .sisyphus/evidence/task-3-missing.txt
  ```

  **Commit**: YES
  - Message: `feat(loom-phase6): stage-to-flag compiler + Loom env var mapping`

- [x] 4. **Style fingerprint VIEW (call style_calibration + rhythm_analysis)**

  **What to do**:
  - 创建 `novel_analyzer/services/project_style_view_service.py:ProjectStyleViewService`
  - **不重写 heuristic** — 直接调 Loom Phase 4 已落地服务:
    - `style_calibration_service.compute_style_drift` 拿风格向量
    - `rhythm_analysis_service.compute` 拿 hook_density / pacing_type / climax_score
    - `dialogue_signal_service.compute`(可选)拿对话指纹
  - 把 3 个服务输出聚合渲染为 `output/projects/<slug>/style/fingerprint.md`(human-readable):
    - H2 风格向量 + cosine baseline
    - H2 节奏指纹(hook_density / pacing_type / climax_score)
    - H2 对话指纹
    - H2 范本基线 ±20% 阈值表
    - H2 给作家的"调性提示"(文本 30-50 字,讽刺文专属)
  - 同时输出 `style/heuristics.json`(结构化,T9 prose 注入用)
  - **Snippet 抽取**(讽刺文 RAG 库扩库,贡献 Loom Phase 5 P4):
    - 从 source_chapters 抽 200-500 字片段,标 tag
    - 输出 `style/snippets.jsonl` + 复制一份到 `rag/audience-expectation-notes/<slug>-source-style.md`(贡献 Loom RAG 库)
  - 提供 `query_snippets(slug, tags, top_k=5)` 给 T9 prose 做 few-shot

  **Must NOT do**:
  - 不要重写 style/rhythm/dialogue 计算逻辑(必须调 Loom 服务)
  - 不要修改 Loom 服务签名
  - 不要硬编码《没钱修什么仙》主角名
  - 不要把 single snippet > 500 字
  - 不要调 embedding API(MVP tag-based)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES — Wave 2
  - **Blocks**: T9
  - **Blocked By**: T1, T2, T3

  **References**:
  - **Loom Pattern**: `novel_analyzer/services/style_calibration_service.py` — Phase 4 P1,看 `compute_style_drift` 输出 schema
  - **Loom Pattern**: `novel_analyzer/services/rhythm_analysis_service.py` — Phase 4 P2,看 RhythmSignal 字段
  - **Loom Pattern**: `novel_analyzer/services/dialogue_signal_service.py` — Phase 4 P3
  - **Loom Doc**: `docs/loom/style/README.md` — Phase 4 设计文档
  - **External**: 范本《没钱修什么仙》前 30 章 baseline
  - **RAG library**: `docs/deprecated/trope-worldview-rag-library-format.md` + `rag/` 目录结构

  **WHY**:
  - Loom 已经有完整 style/rhythm/dialogue 服务且测试通过,Phase 6 只做 markdown 视图层
  - snippet 同时贡献 Loom Phase 5 P4 RAG 库扩库目标

  **Acceptance Criteria**:
  - [x] `style/fingerprint.md` 含 4 个 H2 段
  - [x] `style/heuristics.json` 字段类型与 Loom 服务输出一致
  - [x] 在范本前 30 章上跑出 hook_density 与 Loom 已验证基线一致(`loom-status` 输出对照)
  - [x] `style/snippets.jsonl` ≥ 200 条
  - [x] tag 分布 ≥ 5 类,每类 ≥ 10 条
  - [x] `rag/audience-expectation-notes/<slug>-source-style.md` 落盘(贡献 RAG 库)
  - [x] 调 Loom 服务时,服务文件 git diff 空

  **QA Scenarios**:

  ```
  Scenario: 复用 Loom 服务
    Tool: Bash
    Steps:
      1. grep -n "from novel_analyzer.services.style_calibration_service import" novel_analyzer/services/project_style_view_service.py
      2. grep -n "from novel_analyzer.services.rhythm_analysis_service import" novel_analyzer/services/project_style_view_service.py
    Expected: 两个 import 都在
    Evidence: .sisyphus/evidence/task-4-reuse.txt

  Scenario: fingerprint 与 loom-status 一致
    Tool: Bash
    Steps:
      1. .venv/bin/novel-analyzer loom-status --branch-id $BRANCH_ID > loom-status.txt
      2. .venv/bin/novel-analyzer imitate-project fingerprint demo
      3. python compare_metrics.py style/heuristics.json loom-status.txt
    Expected: hook_density / climax_score / style_drift_score 数值一致(±0.01)
    Evidence: .sisyphus/evidence/task-4-consistency.txt

  Scenario: snippet 抽取 + RAG 贡献
    Tool: Bash
    Steps:
      1. wc -l output/projects/demo/style/snippets.jsonl → ≥ 200
      2. test -f rag/audience-expectation-notes/demo-source-style.md
    Evidence: .sisyphus/evidence/task-4-snippets.txt
  ```

  **Commit**: YES
  - Message: `feat(loom-phase6): style fingerprint VIEW (reuse Phase 4 services)`
  - Constraint: must reuse style_calibration / rhythm_analysis / dialogue_signal services unchanged

- [x] 5. **Macro stage — premise + world (RAG library entry)**

  **What to do**:
  - 实现 `imitate-project macro <slug>` 子命令
  - LLM prompt 读 fingerprint + 调用 LLM 生成 2 个文件:
    - `macro/premise.md`(5 H2 段): 题材 / 主旨 / 调性 / 核心讽刺引擎 / 与范本的相似差异轴
    - `macro/world.md`(6 H2 段): 世界观底座 / 力量体系 / 经济与权力结构 / 现代映射 / 规则(rule_overrides 列表)/ 名词映射(world_map 表格)
  - **同时**输出 RAG 库 entry(贡献 Loom Phase 5 P4):
    - `rag/worldview-dossiers/<slug>-worldview.md`(world.md 的 RAG 副本)
  - revise: `imitate-project revise macro --feedback "再讽刺点" --use-llm` 生成 v2
  - 强约束: 不能照抄范本专有名词(箓书 / 万民部 / 昆墟塔)

  **Must NOT do**:
  - 不要照抄范本世界观元素
  - 不要让 LLM 跳过 fingerprint
  - 不要在 macro 写主角名(在 T6)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: `["satire-anti-slop-guard"](T11 完成后启用)`

  **Parallelization**:
  - **Can Run In Parallel**: YES — Wave 2
  - **Blocks**: T8
  - **Blocked By**: T1, T2, T3, T4

  **References**:
  - `skills_dir/imitation-constraint-pack/` + prompts/ — constraint-pack input slot
  - `skills_dir/research-pack/SKILL.md` — worldview/trope/audience prompt 设计
  - `docs/deprecated/trope-worldview-rag-library-format.md` — `rag/worldview-dossiers/` 标准格式
  - `rag/worldview-dossiers/` 现有目录(若存在)

  **WHY**:
  - macro.md 输出符合 RAG 库格式 → 同时完成 Loom Phase 5 P4 第一份样例

  **Acceptance Criteria**:
  - [x] premise.md 5 个 H2 + world.md 6 个 H2
  - [x] frontmatter 完整
  - [x] T3 编译器 dry-run worldview_note ≥ 200 字
  - [x] revise 生成 v2,parents 含 v1
  - [x] `rag/worldview-dossiers/<slug>-worldview.md` 落盘
  - [x] grep 范本专有名词为空

  **QA Scenarios**:

  ```
  Scenario: macro + RAG 贡献
    Tool: Bash
    Steps:
      1. imitate-project macro demo --use-llm
      2. test -f rag/worldview-dossiers/demo-worldview.md
      3. grep -E "箓书|万民部|昆墟" output/projects/demo/macro/world.md && exit 1 || echo OK
    Evidence: .sisyphus/evidence/task-5-macro.txt

  Scenario: revise
    Tool: Bash
    Steps:
      1. imitate-project revise macro --feedback "x" --use-llm
      2. grep "version: 2" macro/premise.md
    Evidence: .sisyphus/evidence/task-5-revise.txt
  ```

  **Commit**: YES
  - Message: `feat(loom-phase6): macro stage + RAG worldview dossier contribution`

- [x] 6. **Characters stage — CharacterPersona ↔ markdown bridge**

  **What to do**:
  - 实现 `imitate-project characters <slug>` 子命令
  - **关键设计**: CharacterPersona ↔ markdown 双向序列化
    - 创建初始角色: 调 LLM 基于 macro 生成 4-6 个角色卡 markdown
    - 角色卡 schema(对齐 Loom `CharacterPersona` 字段):
      - `H2 基本信息`(name / age / identity / 一句话标签)
      - `H2 价值观 + 目标 + 恐惧`(对应 Loom CharacterPersona)
      - `H2 说话风格指纹`(口头禅 / 句式偏好 / 情绪释放阀)
      - `H2 性格弧`(起点 → 钩子 → 转变方向)
      - `H2 关系网`(与其他角色定位)
      - `H2 严禁动作`(违背声音的反模式 → frontmatter `lock_assertions` 候选)
      - `H2 行为标签 + 关系网络` 摘要(对应 FactRecord 行为标签 / GraphNode 关系)
  - **反序列化**: 读 markdown → 构造 `CharacterPersona` → 喂回 `character_agent_service.check_character_consistency`
  - **从 source branch 复用**: 当 `--inherit-from-source` 时调 `character_agent_service.build_character_persona` 拿现有 persona 模板,作家二次编辑(避免空白生成)
  - revise 单角色: `imitate-project revise characters/<name> --feedback "..."`
  - 编译: `--character-map` from frontmatter

  **Must NOT do**:
  - 不要重写 CharacterPersona 字段定义(对齐现有 Loom)
  - 不要使用范本主角名"张羽"
  - 不要让所有角色同一种声音
  - 不要在角色卡写剧情
  - 不要修改 `character_agent_service.py`

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES — Wave 2
  - **Blocks**: T8, T11
  - **Blocked By**: T1, T2, T3

  **References**:
  - **Loom Pattern**: `novel_analyzer/services/character_agent_service.py` — Phase 4 P4,`CharacterPersona` 字段定义和 `build_character_persona` 接口
  - **Loom Pattern**: `novel_analyzer/services/author_knowledge_service.py` — `--character-map` 注入路径
  - **Loom Doc**: `docs/loom/character/character-persona-design.md` — Phase 4 角色认知基设计
  - **Style profile**: 范本 6 个主要角色画像

  **WHY**:
  - 字段对齐 Loom CharacterPersona → markdown 反序列化后零损 plug 进 `check_character_consistency`
  - `--inherit-from-source` 复用 Loom build_character_persona = 作家不必从空白开始

  **Acceptance Criteria**:
  - [x] ≥ 4 个角色卡
  - [x] 每角色 7 个 H2 段
  - [x] 主角名 ≠ "张羽"
  - [x] frontmatter `lock_assertions`(可空 list)
  - [x] 双向序列化 round-trip 保真(persona → markdown → persona,字段相等)
  - [x] `character_agent_service.py` git diff 空

  **QA Scenarios**:

  ```
  Scenario: 角色生成 + 双向序列化
    Tool: Bash
    Steps:
      1. imitate-project characters demo --use-llm --count 5
      2. ls output/projects/demo/characters/*.md | wc -l → ≥ 5
      3. python -c "from novel_analyzer.services.project_shell_service import ProjectShellService; svc=ProjectShellService(); p1 = svc.read_character_as_persona('demo','protagonist'); md = svc.persona_to_markdown(p1); p2 = svc.markdown_to_persona(md); assert p1 == p2"
    Expected: round-trip 完整保真
    Evidence: .sisyphus/evidence/task-6-roundtrip.txt

  Scenario: --inherit-from-source
    Tool: Bash
    Steps:
      1. imitate-project characters demo --inherit-from-source --use-llm
      2. grep "build_character_persona" -r .sisyphus/evidence/task-6-inherit.log
    Evidence: .sisyphus/evidence/task-6-inherit.txt
  ```

  **Commit**: YES
  - Message: `feat(loom-phase6): characters stage with CharacterPersona ↔ markdown bridge`
  - Directive: persona derivation MUST use existing build_character_persona; do not reimplement

- [x] 7. **Plot + Conflicts stages (combined)**

  **What to do**:
  - **Plot 部分**: 实现 `imitate-project plot <slug>`,输出 3 个文件:
    - `plot/arcs.md`: 主线 1 + 副线 2-3,每条 arc 含 4 H2(类型 / 目标 / 节奏曲线 / 关键节点)
    - `plot/chapter_goals.md`: 每行 `<idx>:<goal>`(≤ 50 字),格式与 `plan-whole-book-imitation` 入参对齐
    - `plot/continuity.md`: **初始连续性快照,字段对齐 Loom `_legacy_compat`**(characters / rules / unresolved_threads / previous_chapter_summary)
  - **Conflicts 部分**: 实现 `imitate-project conflicts <slug>`,输出 3 个文件:
    - `conflicts/axes.md`: 列表 `- <trope_axis>` ≥ 3 条
    - `conflicts/innovation.md`: H2 段为 innovation_directive
    - `conflicts/taboo.md`: 列表 ≥ 3 项,默认含禁止系统外挂 / 突兀大团圆 / 角色情绪化爆发
  - **同时**: conflicts 输出贡献 Loom RAG 库 — `rag/trope-library/<slug>-tropes.md`(贡献 Phase 5 P4)
  - 编译: T3 直接读
  - revise 同 T5

  **Must NOT do**:
  - 不要让 plot 章节数超过 `target_chapters`
  - 不要在 plot 写场景细节(在 T8 storyboard)
  - 不要让 chapter_goals 单条 > 50 字
  - 不要让 axes 写成段落(每条 ≤ 20 字)
  - 不要让 innovation 和 taboo 矛盾
  - 不要让 continuity.md 字段偏离 Loom `_legacy_compat` 结构

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES — Wave 2
  - **Blocks**: T8
  - **Blocked By**: T1, T2, T3, T5

  **References**:
  - **Loom Pattern**: `novel_analyzer/services/memory_assembler_service.py` — `_legacy_compat` 字段定义,continuity.md 必须对齐
  - **Loom Pattern**: `novel_analyzer/services/whole_book_imitation_service.py:plan_whole_book_imitation` — chapter_goals 格式
  - **Loom Pattern**: `novel_analyzer/services/next_chapter_planner_service.py` — chapter plan schema
  - **RAG library**: `docs/deprecated/imitation-innovation-and-steering.md` + `docs/deprecated/batch-innovation-experiment-workflow.md` — trope_axes / innovation_directives 格式
  - **RAG library**: `rag/trope-library/` 目录结构

  **WHY**:
  - continuity.md 对齐 Loom `_legacy_compat` → T9 prose 反序列化喂 memory_assembler 零转换
  - 输出符合 RAG 库格式 → 贡献 Loom Phase 5 P4 trope 库扩库目标

  **Acceptance Criteria**:
  - [x] plot 3 个文件存在
  - [x] `chapter_goals.md` ≥ 3 行,每行 `<idx>:<goal>` ≤ 50 字
  - [x] `arcs.md` ≥ 1 主线 + 1 副线
  - [x] `continuity.md` 字段含 characters / rules / unresolved_threads / previous_chapter_summary 4 个 key
  - [x] conflicts 3 个文件存在
  - [x] `axes.md` ≥ 3 条 ≤ 20 字
  - [x] `taboo.md` 含 3 个默认项
  - [x] `rag/trope-library/<slug>-tropes.md` 落盘
  - [x] T3 编译器输出 chapter_goals / trope_axes / innovation_directives / taboo_innovations 都是 list

  **QA Scenarios**:

  ```
  Scenario: plot + continuity 字段对齐 Loom
    Tool: Bash
    Steps:
      1. imitate-project plot demo --use-llm
      2. python -c "import yaml; d=yaml.safe_load(open('output/projects/demo/plot/continuity.md').read().split('---')[1]); assert all(k in d for k in ['characters','rules','unresolved_threads','previous_chapter_summary'])"
    Evidence: .sisyphus/evidence/task-7-continuity.txt

  Scenario: conflicts + RAG 贡献
    Tool: Bash
    Steps:
      1. imitate-project conflicts demo --use-llm
      2. test -f rag/trope-library/demo-tropes.md
      3. grep -c "^- " output/projects/demo/conflicts/axes.md → ≥ 3
    Evidence: .sisyphus/evidence/task-7-conflicts.txt

  Scenario: 编译多值 flag
    Tool: Bash
    Steps:
      1. flags = compile_for_chapter("demo", 1)
      2. assert len(flags.trope_axes) >= 3
      3. argv = to_cli_args(flags); test $(echo "$argv" | grep -c -- "--trope-axis") -ge 3
    Evidence: .sisyphus/evidence/task-7-compile.txt
  ```

  **Commit**: YES
  - Message: `feat(loom-phase6): plot + conflicts stages (continuity aligned to _legacy_compat, RAG contributions)`

- [x] 8. **Outline + Storyboard ⭐NEW (extend imitation-constraint-pack)**

  **What to do**:
  - **Outline 部分**: 实现 `imitate-project outline <slug> [--chapter N]`,为每章产 `chapters/ch{NNN}.outline.md`:
    - frontmatter: stage / version / parents=[macro,characters,plot,conflicts] / locked / lock_assertions
    - `H1 章节标题`(功能性,可带反讽)
    - `H2 本章目标`(plot/chapter_goals.md 第 N 行 + 扩展)
    - `H2 主冲突`(只一个)
    - `H2 关键转折`(2-3 个)
    - `H2 信息释放顺序`
    - `H2 章末钩子类型`(从 fingerprint 三选一: 悬念问句 / 模棱两可话 / 新威胁)
    - `H2 与上一章衔接`(carry-over 显式)
  - LLM prompt 必须读 macro/characters/plot/conflicts 全部 + 前 N-1 章 outline
  - 编译: target_goal = `H1` + `H2 本章目标`
  - **Storyboard 部分** ⭐NEW: 实现 `imitate-project storyboard <slug> [--chapter N]`,为每章产 `chapters/ch{NNN}.storyboard.md`,内容是 3-7 个 scene beat,每个 H2:
    - `H2 Beat #N: <场景标题>`
    - `字数预估: ≈ N 字`
    - `场所: <地点>`
    - `POV: <主视角>`
    - `镜头类型: 内心独白 / 对话 / 动作 / 描写 / 世界观揭示`(对应 fingerprint 4 种比例)
    - `节奏标签: 平庸setup / 权力揭示 / 讽刺反转 / 钩子`(对应 3-拍冲突结构)
    - `信息释放: <本 beat 揭示什么>`
    - `内容草要: 200 字简述`
  - **关键集成**: 修改 `skills_dir/imitation-constraint-pack/SKILL.md` + `prompts/` + `schemas/` — **追加(非破坏)** `scene_beats` 字段到 input schema,缺失时退回原 source-skeleton 路径(向后兼容)
  - 编译: T3 `compile_for_chapter` 的 `scene_beats` 直接从 storyboard.md 解析

  **Must NOT do**:
  - 不要在 outline 写场景细节(那是 storyboard)
  - 不要让 outline 章末钩子是大团圆词汇
  - 不要在 outline 指定具体台词(那是 prose)
  - 不要让单章 storyboard beats > 7 个
  - 不要在 beat 写完整对白
  - 不要修改 imitation-constraint-pack 现有 input 字段(只追加,不改名/删字段)
  - 不要删除原 scene_beats fallback 逻辑(向后兼容)
  - 不要在 storyboard 强制每个 beat 都用 3 拍结构(只对核心冲突场景要求)

  **Recommended Agent Profile**:
  - **Category**: `artistry`
    - Reason: 创作 + 对范本节奏的精细对照
  - **Skills**: `["imitation-constraint-pack"](因为要扩展它)`

  **Parallelization**:
  - **Can Run In Parallel**: NO(章内 outline → storyboard 串行,但跨章可并行)
  - **Parallel Group**: Wave 3
  - **Blocks**: T9
  - **Blocked By**: T5, T6, T7

  **References**:
  - `novel_analyzer/services/next_chapter_planner_service.py` — `scene_beats` 现有字段定义
  - `novel_analyzer/services/chapter_imitation_service.py:build_imitation_plan` — imitation plan schema
  - `skills_dir/imitation-constraint-pack/{SKILL.md,prompts/,schemas/}` — skill 完整 schema,扩展时严格遵守目录约定
  - `docs/chapter-imitation-method.md` §2 Step 1 — outline schema 6 条必含
  - **Industry**: Sudowrite Beats(每章 3-7 beat,行业最佳实践)
  - **Style profile**: 范本 Chapter 36 / 84 节奏样例

  **WHY**:
  - chapter-imitation-method §2 是项目"章节仿写方法论"的官方源,outline schema 1:1 对齐 = 零成本接入现有 chapter_imitation_service
  - imitation-constraint-pack 已是 prose 阶段 input 层,扩展它而不是新建 = storyboard 立即可用
  - scene_beats 字段名是 ground truth(next_chapter_planner 已用),storyboard 解析后类型 1:1

  **Acceptance Criteria**:
  - [x] 3 章 outline 文件全部生成
  - [x] 每章 outline ≥ 5 个 H2 段
  - [x] outline frontmatter parents 含 4 个上游
  - [x] outline 章末钩子类型显式标识(三选一)
  - [x] T3 编译器输出 target_goal 非空
  - [x] 3 章 storyboard 文件全部生成
  - [x] 每章 storyboard 3-7 个 H2 Beat
  - [x] 每个 Beat 含 6 个必备字段
  - [x] `imitation-constraint-pack/SKILL.md` 输入 schema 含新增 `scene_beats` 字段
  - [x] 缺 storyboard 时,prose 走原 source-skeleton fallback(向后兼容)
  - [x] `tests/test_imitation_constraint_pack*.py`(若有)100% pass(向后兼容)
  - [x] T3 编译器输出 `scene_beats: list[Beat]` 长度匹配文件

  **QA Scenarios**:

  ```
  Scenario: outline 3 章
    Tool: Bash
    Steps:
      1. imitate-project outline demo --use-llm
      2. ls output/projects/demo/chapters/ch00*.outline.md | wc -l → 3
      3. for i in 1 2 3; do grep -c "^## " ch00${i}.outline.md; done → 全 ≥ 5
      4. grep -E "钩子类型: (悬念问句|模棱两可|新威胁)" ch001.outline.md
    Evidence: .sisyphus/evidence/task-8-outline.txt

  Scenario: storyboard 字段
    Tool: Bash
    Steps:
      1. imitate-project storyboard demo --use-llm
      2. ls ch00*.storyboard.md | wc -l → 3
      3. for i in 1 2 3; do n=$(grep -c "^## Beat #" ch00${i}.storyboard.md); test $n -ge 3 && test $n -le 7; done
      4. for fld in 场所 POV 镜头类型 节奏标签 信息释放 内容草要; do grep -c "^${fld}" ch001.storyboard.md; done
    Evidence: .sisyphus/evidence/task-8-storyboard.txt

  Scenario: skill 向后兼容
    Tool: Bash
    Steps:
      1. show-imitation-skill-contracts | grep imitation-constraint-pack
      2. python -c "...verify scene_beats in input_schema..."
      3. .venv/bin/pytest tests/test_imitation_constraint_pack* -q(若存在)
    Expected: schema 含 scene_beats,现有测试 pass
    Evidence: .sisyphus/evidence/task-8-skill-compat.txt

  Scenario: storyboard 缺失时 fallback
    Tool: Bash
    Steps:
      1. 删 ch001.storyboard.md
      2. compile_for_chapter("demo", 1) → flags.scene_beats == []
      3. (T9 prose 仍能跑,走 source-skeleton fallback,在 T9 验证)
    Evidence: .sisyphus/evidence/task-8-fallback.txt
  ```

  **Commit**: YES
  - Message: `feat(loom-phase6): outline + storyboard stages with scene_beats input extension`
  - Lore Directive: scene_beats injection lives in imitation-constraint-pack input; do not split into a new skill

- [x] 9. **Prose orchestrator (Loom flag injection + _loom_* frontmatter + auto loom-collect-pairs)**

  **What to do**:
  - 实现 `imitate-project prose <slug> [--chapter N|--all] [--max-rounds 2] [--use-llm] [--fast]`
  - 命令逻辑:
    1. 调 T3 编译器拿 `CompiledFlags`(steering + Loom flags)
    2. **设环境变量**: 调 `to_env_vars(flags)` 返回的 dict 设到 `os.environ`(临时 scope,只在本命令期间生效)— 这样 Loom 服务自动按项目配置开关
    3. 调 `memory_assembler_service.assemble(branch_id, chapter_idx)` 拿三层记忆(若 loom_memory_mode != disabled)
    4. 把 `assemble` 输出的 `_legacy_compat` 字段与 `plot/continuity.md` 内容合并,作为 carry-over 注入 prompt
    5. 通过 `imitation_harness_service.harness_imitation` 跑(programmatic call,不走 subprocess)
    6. 取得 `final_draft` → 写到 `chapters/ch{NNN}.draft.md`(带 frontmatter)
    7. **frontmatter 渲染所有 `_loom_*` 信号**:
       ```yaml
       ---
       stage: prose
       version: 1
       parents: [outline, storyboard, characters, ...]
       final_verdict: pass
       stop_reason: completed
       max_rounds_used: 2
       loom_signals:
         tension_score: 0.71
         chapter_quality_score: 0.78
         style_drift_score: 0.18
         hook_density: 5.36
         dialogue_voice_consistency: 0.96
         reader_sim_overall: 0.65
       ---
       ```
    8. **调用 `satire_anti_slop_service.check_text(draft)`** + **`lock_contract_checker.check(slug, draft)`**(若 T11 完成)
    9. 把 `_loom_*` 信号同时写到 `output/projects/<slug>/runs/<ts>/loom-signals.json`
    10. 把 carry-over state 更新写回 `plot/continuity.md`(_legacy_compat 字段)
    11. **自动调** `loom-collect-pairs --output-dir output/projects/<slug>/chapters/`(贡献 Loom Phase 3 P3)
    12. 支持 `--all` 跑 1..target_chapters
    13. `--fast` 跳过 anti-slop 阻塞,只 warn(必须仍留版本)
  - **必须复用** `imitation_harness_service`,**不直接调 LLM**

  **Must NOT do**:
  - 不要在 orchestrator 直接调 LLM client(必须经 harness)
  - 不要修改 `imitation_harness_service` / `memory_assembler_service` / `satire_anti_slop_service` 现有签名
  - 不要静默吞 stop_reason / final_verdict(必须落 frontmatter)
  - 不要让 `--fast` 跳 gate 但不留版本
  - 不要污染全局环境变量(必须 scope 到命令期间,用 contextmanager)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO(critical path)
  - **Parallel Group**: Wave 3
  - **Blocks**: T12, T14
  - **Blocked By**: T3, T4, T8

  **References**:
  - **Loom**: `novel_analyzer/services/memory_assembler_service.py:assemble` — Phase 1,carry-over 三层记忆
  - **Loom**: `novel_analyzer/services/imitation_harness_service.py:harness_imitation` — 主入口,zero modification
  - `novel_analyzer/cli/app.py` — 现有 harness-imitation 命令实现,看参数怎么喂 service
  - `docs/architecture/chapter-imitation-harness-architecture.md` §3.3 — harness 4 类 routing
  - **Loom signals**: `docs/loom/handoff.md` 4.0 系列 — `_loom_*` 字段定义
  - **Loom CLI**: `docs/loom/handoff.md` §4.2 步骤 8 — `loom-collect-pairs` 自动累积入参

  **WHY**:
  - 复用 harness = 自动得到 4 类 routing 能力
  - memory_assembler.assemble 是 Loom Phase 1 主接入点,prose 必须走它
  - frontmatter 渲染所有 `_loom_*` 信号 = 作家审阅时一目了然章节质量
  - auto loom-collect-pairs = 每次 prose 贡献 Loom Phase 3 数据池(当前 30/500)

  **Acceptance Criteria**:
  - [x] `imitate-project prose demo --chapter 1 --use-llm` 生成 ch001.draft.md
  - [x] frontmatter 含 `final_verdict / stop_reason / max_rounds_used / loom_signals`
  - [x] `loom_signals` 含至少 6 个 `_loom_*` 字段
  - [x] `--all` 生成 ch001/ch002/ch003 全部
  - [x] 总字数 ≥ 12,000 中文字
  - [x] `plot/continuity.md` 在 prose 后被更新(_legacy_compat 字段有 diff)
  - [x] `imitation_harness_service.py` / `memory_assembler_service.py` / `chapter_imitation_service.py` git diff 空
  - [x] `--fast` 即使 anti-slop fail 仍出文(只 warn)
  - [x] `loom-collect-pairs` 自动调用,新 pairs 落到 `output/loom-pairs.jsonl`
  - [x] 项目环境变量在命令结束后**不污染**全局(scope 到 contextmanager)

  **QA Scenarios**:

  ```
  Scenario: 单章 prose + Loom 信号
    Tool: Bash
    Steps:
      1. imitate-project prose demo --chapter 1 --use-llm --max-rounds 2
      2. wc -m ch001.draft.md → ≥ 4000
      3. python -c "import yaml; fm=yaml.safe_load(open('ch001.draft.md').read().split('---')[1]); ls=fm['loom_signals']; assert all(k in ls for k in ['tension_score','chapter_quality_score','style_drift_score','hook_density','dialogue_voice_consistency','reader_sim_overall'])"
    Evidence: .sisyphus/evidence/task-9-prose-1.txt

  Scenario: 全 3 章 + 字数
    Tool: Bash
    Steps:
      1. imitate-project prose demo --all --use-llm
      2. wc -m output/projects/demo/chapters/ch00*.draft.md | tail -1 → ≥ 12000
    Evidence: .sisyphus/evidence/task-9-all.txt

  Scenario: Loom 服务零修改
    Tool: Bash
    Steps:
      1. git diff main -- novel_analyzer/services/{memory_assembler,memory_consolidation,imitation_harness,chapter_imitation,whole_book_imitation}_service.py | head -1
    Expected: 空
    Evidence: .sisyphus/evidence/task-9-no-drift.txt

  Scenario: 自动 loom-collect-pairs
    Tool: Bash
    Steps:
      1. wc -l output/loom-pairs.jsonl > before.txt
      2. imitate-project prose demo --chapter 1 --use-llm
      3. wc -l output/loom-pairs.jsonl > after.txt
      4. diff before.txt after.txt
    Expected: 行数增加
    Evidence: .sisyphus/evidence/task-9-pairs.txt

  Scenario: continuity 更新
    Tool: Bash
    Steps:
      1. cp continuity.md continuity.before.md
      2. imitate-project prose demo --chapter 1 --use-llm
      3. diff continuity.before.md continuity.md | head -1
    Expected: 有 diff
    Evidence: .sisyphus/evidence/task-9-continuity.txt

  Scenario: 环境变量不污染全局
    Tool: Bash
    Steps:
      1. python -c "import os; os.environ.pop('NOVEL_ANALYZER_LOOM_MEMORY_MODE',None); from novel_analyzer.cli.app import imitate_project_prose; imitate_project_prose('demo',1); assert 'NOVEL_ANALYZER_LOOM_MEMORY_MODE' not in os.environ"
    Expected: 命令结束后环境变量被恢复
    Evidence: .sisyphus/evidence/task-9-env-isolation.txt
  ```

  **Commit**: YES
  - Message: `feat(loom-phase6): prose orchestrator with Loom flag injection + signal frontmatter + auto pair collection`
  - Constraint: prose generation must go through existing harness; this command does not call LLM directly
  - Constraint: must not modify any Loom Phase 1-5 service signatures

- [x] 10. **revise / lock / diff / status / run subcommands**

  **What to do**:
  - 实现 5 个 ops 子命令(替换 T1 stub):
    1. `imitate-project revise <slug> <stage> [--chapter N] --feedback "..." [--use-llm]` — 任意 stage 重生 v2
    2. `imitate-project lock <slug> <file_glob>` — 写 locked.yaml + frontmatter `locked: true`
    3. `imitate-project diff <slug> <stage> [--from vN --to vM]` — `difflib.unified_diff` 输出
    4. `imitate-project status <slug>` — 输出表格,每个 stage 一行: `stage / version / locked / 上次更新 / final_verdict(prose) / loom_signal_summary`
    5. `imitate-project run <slug> --until <stage> [--fast]` — 一键跑到指定 stage,按 gates 自动停或继续
       - 默认 `--until prose`,gates 列表里的 stage 停下提示用户审核
       - `--fast` 全程不停留版本

  **Must NOT do**:
  - 不要在 diff 调 LLM(纯文本 diff)
  - 不要让 lock 修改文件正文(只改 locked.yaml + frontmatter)
  - 不要让 run 在 gate stop 时退出码非零(应是 0)
  - 不要让 status 漏 Loom signal 摘要

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES — Wave 3
  - **Blocks**: T12
  - **Blocked By**: T1

  **References**:
  - `novel_analyzer/cli/app.py` — Typer 命令风格
  - `novel_analyzer/services/project_shell_service.py:list_versions`(T1 已实现)
  - `stdlib`: `difflib.unified_diff`
  - **Loom**: `novel_analyzer/services/imitation_harness_service.py` — final_verdict / stop_reason 字段(供 status 显示)

  **Acceptance Criteria**:
  - [x] 5 个命令 `--help` 都可用
  - [x] revise 任意 stage 生成 v2 + 旧版归档
  - [x] diff 输出 unified diff 格式
  - [x] lock 写 locked.yaml + frontmatter
  - [x] status 输出表格,prose 行含 `loom_signal_summary`(quality_score / tension_score 等摘要)
  - [x] `run --until storyboard` 在 gates 中的 stage 停下并提示

  **QA Scenarios**:

  ```
  Scenario: revise 通用化
    Tool: Bash
    Steps:
      1. imitate-project revise demo macro --feedback "x" --use-llm
      2. imitate-project revise demo characters --chapter zhang_yu --feedback "y" --use-llm
      3. imitate-project revise demo outline --chapter 2 --feedback "z" --use-llm
    Expected: 全部产生 v2 + 归档
    Evidence: .sisyphus/evidence/task-10-revise.txt

  Scenario: status + Loom 摘要
    Tool: Bash
    Steps:
      1. imitate-project status demo
    Expected: stdout 含 prose 行 + loom_signal_summary 列(quality=0.78 / tension=0.71)
    Evidence: .sisyphus/evidence/task-10-status.txt

  Scenario: run --fast 全程不停
    Tool: Bash
    Steps:
      1. imitate-project run demo --until prose --fast --use-llm
    Expected: 一路跑到 prose,无停顿
    Evidence: .sisyphus/evidence/task-10-fast.txt
  ```

  **Commit**: YES
  - Message: `feat(loom-phase6): revise/lock/diff/status/run ops commands`

- [x] 11. **satire-anti-slop-guard skill + checker + lock_contract_checker**

  **What to do**:
  - **新建 skill**: `skills_dir/satire-anti-slop-guard/{SKILL.md, prompts/check.md, schemas/{check_input.json, check_output.json}}`
  - **新建 service**: `novel_analyzer/services/satire_anti_slop_service.py:SatireAntiSlopChecker`,实现 6 类反模式:
    1. **解释笑话(blocker)**: 含 `这其实是在|说白了就是|讽刺的是|暗示着|寓意是|象征着|表达了`
    2. **大团圆收尾(blocker)**: 章节末 200 字含 `圆满|终于幸福|一切都好|从此无忧|皆大欢喜|阖家欢乐|破镜重圆`
    3. **反讽词滥用(fail)**: 单段 `特么的|他么的|妈的` ≥ 3 OR 单章 ≥ 6
    4. **提前 deflate(warn)**: 字数总长 × 30% 处之前出现反转标志词(`原来是假的|结果竟然|没想到只是`)
    5. **现代梗滥用(warn)**: 单段 ≥ 2 个 `yyds|内卷|躺平|摆烂|破防|绝绝子|栓Q|emo`
    6. **角色情绪化爆发(warn)**: 主角名 + `怒吼|暴怒|拍桌|吼道|咆哮`,且角色卡含"克制"约束
  - **关键集成**:
    - 输出 `Finding(severity, type, evidence)` 接口与现有 `risk_audit_checkers.py:CheckerBase` 对齐
    - **暴露到 `session_loom_signals`** — 通过现有 Loom signal 通道进入 operator surface(让作家在 status 命令里直接看到)
    - 同时新建 `lock_contract_checker_service.py:LockContractChecker`:
      - 读 locked 文件 frontmatter `lock_assertions`
      - heuristic 关键词扫 + LLM 兜底(可选)
      - 输出 `LockContractReport(violations: list[Violation])`,字段对齐 `Finding`
  - 两个 checker 都集成到 T9 prose orchestrator 的 post-generation hook
  - 不修改任何现有 risk_audit_checkers.py / Loom 服务

  **Must NOT do**:
  - 不要 hardcode 范本主角名"张羽"(必须从 characters/*.md 读)
  - 不要让 fast 模式被 anti-slop 阻断(只 warn)
  - 不要重写现有 9 个 risk checker 或 Loom 服务
  - 不要把 LLM 兜底默认开
  - 不要让 satire-anti-slop 对范本本身误报(范本前 5 章作 negative test)

  **Recommended Agent Profile**:
  - **Category**: `artistry`
    - Reason: 反 AI-slop 模式判断需要"创作品味"
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES — Wave 4
  - **Blocks**: T12
  - **Blocked By**: T1, T6

  **References**:
  - `skills_dir/draft-self-check/SKILL.md` + `prompts/` + `schemas/` — skill 目录硬约定
  - `skills_dir/anti-fabrication-guard/SKILL.md` — anti-slop checker 现成模式
  - `novel_analyzer/services/risk_audit_checkers.py:CheckerBase` — Finding 接口
  - `novel_analyzer/services/claim_grounding_service.py` — LLM 兜底"声明 vs 证据"模式
  - **Loom**: `docs/loom/handoff.md` 4.0 系列 — `session_loom_signals` 字段命名
  - **Source baseline**: 范本前 5 章作 negative test
  - **Style profile**: draft "G7 反讽小说 AI slop 风险"6 类清单

  **WHY**:
  - skill 目录硬约定:不遵守 `list-skills` CLI 不能识别
  - Finding 接口对齐 = 复用现有 risk gate 渲染管线
  - 暴露到 session_loom_signals = 自动出现在 operator surface 的 Loom 信号汇总
  - 范本 negative test:防止反讽误检测(范本本身就是 ground truth)

  **Acceptance Criteria**:
  - [x] `list-skills` 可见 satire-anti-slop-guard
  - [x] 6 类反模式各 ≥ 1 unit test 命中
  - [x] 6 类反模式各 ≥ 1 对抗输入命中,命中率 ≥ 90%
  - [x] 范本前 5 章 negative test 全部 pass(无误报)
  - [x] LockContractChecker 在锁定 + 违约文本上 ≥ 1 violation
  - [x] 空锁定时 LockContractChecker 返回空 violations
  - [x] 现有 9 个 risk checker 实现 + 11 个 Loom 服务 git diff 空
  - [x] checker 输出出现在 `session_loom_signals.satire_anti_slop` 字段(operator surface)

  **QA Scenarios**:

  ```
  Scenario: 解释笑话被捕获
    Tool: Bash
    Steps:
      1. echo "张羽走进商店。这其实是在讽刺消费主义。" | python -c "...check_text..."
    Expected: verdict=fail, type=meta_commentary
    Evidence: .sisyphus/evidence/task-11-meta.txt

  Scenario: 大团圆被捕获
    Tool: Bash
    Steps:
      1. echo "...终于,他过上了幸福快乐的生活,一切都好了。" | check_text
    Expected: type=happy_ending
    Evidence: .sisyphus/evidence/task-11-happy.txt

  Scenario: 范本不误报(critical)
    Tool: Bash
    Steps:
      1. for i in 1 2 3 4 5; do python -c "sample chapter $i and check"; done
    Expected: 5 个 verdict 全 pass
    Evidence: .sisyphus/evidence/task-11-source-clean.txt

  Scenario: 暴露到 Loom signal
    Tool: Bash
    Steps:
      1. imitate-project prose demo --chapter 1 --use-llm
      2. python -c "...read operator surface..." | grep "satire_anti_slop"
    Expected: session_loom_signals 含 satire_anti_slop 字段
    Evidence: .sisyphus/evidence/task-11-loom-signal.txt

  Scenario: lock 检查
    Tool: Bash
    Steps:
      1. lock 文件含 lock_assertions: ["主角不能怒吼"]
      2. text = "张羽怒吼着拍桌而起"
      3. LockContractChecker().check(slug, text) → ≥ 1 violation
    Evidence: .sisyphus/evidence/task-11-lock.txt

  Scenario: 现有 checker + Loom 服务零回归
    Tool: Bash
    Steps:
      1. git diff main -- novel_analyzer/services/risk_audit_checkers.py | head -1
      2. for svc in memory_assembler memory_consolidation tension pairwise_eval style_calibration rhythm_analysis dialogue_signal character_agent reader_simulation thread_scheduler long_book_health; do git diff main -- novel_analyzer/services/${svc}_service.py | head -1; done
    Expected: 全部空
    Evidence: .sisyphus/evidence/task-11-no-drift.txt
  ```

  **Commit**: YES
  - Message: `feat(loom-phase6): satire-anti-slop-guard + lock_contract_checker (Loom signal channel integration)`

- [x] 12. **MVP run + loom-reference-eval + loom-ab-compare validation**

  **What to do**:
  - 这是真实跑通任务,不是单元测试
  - 步骤:
    1. `auto-run /home/user/txt111/01.txt --max-chapters 30`,记录 BRANCH_ID 到 `.sisyphus/evidence/task-12-mvp/branch.txt`
    2. `imitate-project init meiqian-new-story --source-branch $BRANCH_ID`(默认 loom_flags 全开)
    3. 顺序执行: fingerprint → macro → characters → plot → conflicts → outline → storyboard → prose(--all)
    4. 中途测试:
       - macro 后人工审阅 + lock characters/<主角>.md
       - revise plot 用反馈生成 v2
       - 重生 outline 验证 lock 不被改
    5. 全部产物存盘到 `output/projects/meiqian-new-story/`
    6. **Loom MVP 验收**:
       - 跑 `loom-status --branch-id $BRANCH_ID` 查项目对应分支的 Loom 信号
       - 跑 `loom-reference-eval $BRANCH_ID 0 output/projects/meiqian-new-story/chapters/`(批量)→ fidelity ≥ 0.5
       - 跑 baseline 对比: 用 `writer-imitate-range` 跑 3 章到 `output/baseline-meiqian/`,然后 `loom-ab-compare output/baseline-meiqian/ output/projects/meiqian-new-story/chapters/`
       - 跑 `loom-pairs-stats` 看 pairwise 数据池是否有新增
    7. anti-slop 全部 pass / lock contract 全部 pass / 现有 risk gate 全部 pass
    8. README.md 末尾追加一节 "Loom Phase 6 实证: 基于范本的新故事"(metric 摘要 + 1-2 段示例)
  - 全过程命令 + evidence 存到 `.sisyphus/evidence/task-12-mvp/`

  **Must NOT do**:
  - 不要在 MVP 跑完前断言"成功"(必须看 Loom reference fidelity / anti-slop / 字数)
  - 不要用 mock LLM 跑 MVP
  - 不要把 MVP 产物提交进 git(`output/` 在 .gitignore)
  - 不要在 MVP 中静默跳过任何 stage
  - 不要忽略 baseline 对比(必须跑 baseline 才能用 loom-ab-compare)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO(critical path 终点)
  - **Parallel Group**: Wave 4
  - **Blocks**: F1, F3
  - **Blocked By**: T9, T10, T11

  **References**:
  - `docs/whole-book-quickstart-20260514.md` — auto-run 流程
  - `docs/loom/weitu-real-effect-validation.md` — Loom 卫图样例验证标准流程(模仿其 evidence 收集模式)
  - `docs/loom/weitu-validation-log-20260511.md` — 已执行的 Loom 验证证据格式
  - 本计划全文

  **WHY**:
  - Loom 卫图样例验证已经把"如何验证仿写真实效果"标准化,Phase 6 MVP 必须按同样模式 = 可对照 Loom 已有基线

  **Acceptance Criteria**:
  - [x] BRANCH_ID 记录在 evidence
  - [x] 7 层 markdown 全部存在,每层 ≥ 1 个产物
  - [x] 3 章正文 ≥ 12,000 中文字
  - [x] `loom-reference-eval` fidelity ≥ 0.5 (参考卫图基线 enhanced=0.78)
  - [x] `loom-ab-compare` 显示 Phase 6 项目壳产物 quality 不低于 baseline writer-imitate-range
  - [x] `loom-pairs-stats` 显示 ≥ 6 个新 pairs(贡献 Loom Phase 3 P3)
  - [x] anti-slop verdict=pass
  - [x] lock contract violations 为空
  - [x] 现有 risk gate verdict ≠ block
  - [x] revise + lock 操作记录在 evidence

  **QA Scenarios**:

  ```
  Scenario: 全链路实操
    Tool: Bash
    Steps:
      1. .venv/bin/novel-analyzer auto-run /home/user/txt111/01.txt --max-chapters 30 2>&1 | tee evidence/task-12-mvp/auto-run.log
      2. BRANCH_ID=$(grep -oP 'branch_id: \K[a-f0-9-]+' evidence/task-12-mvp/auto-run.log)
      3. echo "BRANCH_ID=$BRANCH_ID" > evidence/task-12-mvp/branch.txt
      4. .venv/bin/novel-analyzer imitate-project init meiqian-new-story --source-branch $BRANCH_ID
      5. .venv/bin/novel-analyzer imitate-project run meiqian-new-story --until prose --use-llm 2>&1 | tee evidence/task-12-mvp/run.log
      6. test $(wc -m output/projects/meiqian-new-story/chapters/ch00*.draft.md | tail -1 | awk '{print $1}') -gt 12000
    Evidence: .sisyphus/evidence/task-12-mvp/

  Scenario: Loom reference eval(对照卫图基线)
    Tool: Bash
    Steps:
      1. .venv/bin/novel-analyzer loom-reference-eval $BRANCH_ID 0 output/projects/meiqian-new-story/chapters/ 2>&1 | tee evidence/task-12-mvp/reference-eval.txt
      2. python -c "...parse fidelity..." | grep -E "fidelity=0\.[5-9]"
    Expected: average fidelity ≥ 0.5
    Evidence: .sisyphus/evidence/task-12-mvp/reference-eval.txt

  Scenario: AB 对比 baseline
    Tool: Bash
    Steps:
      1. .venv/bin/novel-analyzer writer-imitate-range $BRANCH_ID '2:目标A' '3:目标B' '4:目标C' --output-dir output/baseline-meiqian --use-llm
      2. .venv/bin/novel-analyzer loom-ab-compare output/baseline-meiqian/ output/projects/meiqian-new-story/chapters/ --output-file evidence/task-12-mvp/ab-report.json
      3. python -c "import json; r=json.load(open('evidence/task-12-mvp/ab-report.json')); assert r['phase6_better_or_equal']"
    Evidence: .sisyphus/evidence/task-12-mvp/ab-report.json

  Scenario: pairwise 数据贡献
    Tool: Bash
    Steps:
      1. wc -l output/loom-pairs.jsonl > evidence/task-12-mvp/pairs-before.txt
      2. (already ran prose in previous scenario)
      3. wc -l output/loom-pairs.jsonl > evidence/task-12-mvp/pairs-after.txt
      4. .venv/bin/novel-analyzer loom-pairs-stats --pairs-file output/loom-pairs.jsonl 2>&1 | tee evidence/task-12-mvp/pairs-stats.txt
    Expected: pairs 增加 ≥ 6
    Evidence: .sisyphus/evidence/task-12-mvp/pairs-*.txt

  Scenario: lock 保护
    Tool: Bash
    Steps:
      1. (after characters generated) lock 主角文件
      2. revise plot 触发 outline 重生
      3. diff outline 前后,验证 lock 角色名/约束没变
    Evidence: .sisyphus/evidence/task-12-mvp/lock-protection.txt
  ```

  **Commit**: YES (产出可能是 README 段 + helper script)
  - Message: `feat(loom-phase6 mvp): 3-chapter end-to-end run + Loom reference fidelity + AB comparison`
  - Tested: end-to-end MVP run + loom-reference-eval + loom-ab-compare + pairwise pool contribution

- [x] 13. **Loom-aligned docs (slot into docs/loom/phase6/)**

  **What to do**:
  - **创建 4 份文档**(全部 slot 进 Loom canonical 5 份主文档结构):
    1. `docs/loom/phase6/README.md` — Phase 6 入口,定位 + 7 层概念 + 11 命令一行说明 + 与 Phase 1-5 的复用关系
    2. `docs/loom/phase6/workflow.md` — 5 步快速开始 + mermaid 7 层概念图 + 4 种典型反馈循环 + Loom MVP 验证步骤
    3. `docs/loom/phase6/runbook-template.md`(T2 已创,这里完善)— 端到端命令清单
    4. `docs/loom/phase6/arch-alignment.md` — 与 0509 控制层 + Loom Phase 1-5 + 现有 imitation pipeline 的边界澄清
  - **更新 Loom canonical 入口**:
    - `docs/loom/README.md` 新增 "Phase 6 ⏳" 段
    - `docs/loom/handoff.md` 新增 "Phase 6 进行中"小节,链接 phase6/README.md
    - `docs/loom/roadmap.md` 新增 "Phase 6: Author Project Shell" 块,验收标准对齐其他 phase 风格
    - `docs/loom/sota-imitation-progression-checklist.md` 追加 Phase 6 主链路目标
  - **更新角色入口**: `docs/roles/imitation/README.md` 表格追加 "新故事原创仿写 → docs/loom/phase6/workflow.md"
  - **更新文档中心**: `docs/README.md` Level 2 仿写小节追加链接

  **Must NOT do**:
  - 不要单文档超过 800 字
  - 不要把 Phase 6 吹成"取代 Phase 1-5"(它是 UX 层,不是替代)
  - 不要复制 chapter-imitation-method.md 内容(链接即可)
  - 不要在 README 大改架构图
  - 不要漏 update Loom canonical 5 份(否则 Phase 6 不是 Loom roadmap 一部分)

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES — Wave 4
  - **Blocks**: F1
  - **Blocked By**: T9, T10, T11

  **References**:
  - `docs/loom/README.md` — Loom 入口风格
  - `docs/loom/handoff.md` — handoff 文档结构
  - `docs/loom/roadmap.md` — Phase 1-5 验收标准格式
  - `docs/writer-imitation-workflow.md` — workflow 文档风格(短 + mermaid + 命令示例)

  **Acceptance Criteria**:
  - [x] 4 份 phase6/ 文档全部存在
  - [x] 每份 ≤ 800 字
  - [x] mermaid 图 1 张
  - [x] Loom canonical 5 份(README/handoff/roadmap/checklist + arch-diff)4 份有 Phase 6 段
  - [x] roles/imitation/README.md 含 phase6 入口
  - [x] docs/README.md 含 phase6 入口
  - [x] 所有内部链接可解析(`grep -oP '\]\(\K[^)]+'` 后 `test -e` 全 OK)

  **QA Scenarios**:

  ```
  Scenario: phase6 文档完整
    Tool: Bash
    Steps:
      1. for f in docs/loom/phase6/{README.md,workflow.md,runbook-template.md,arch-alignment.md}; do test -f $f && wc -w $f; done
    Expected: 4 个文件存在,每个 ≤ 800 词
    Evidence: .sisyphus/evidence/task-13-docs.txt

  Scenario: Loom canonical 5 份更新
    Tool: Bash
    Steps:
      1. grep -l "Phase 6" docs/loom/{README.md,handoff.md,roadmap.md,sota-imitation-progression-checklist.md}
    Expected: 4 份都命中
    Evidence: .sisyphus/evidence/task-13-canonical.txt

  Scenario: 链接全可达
    Tool: Bash
    Steps:
      1. for f in docs/loom/phase6/*.md docs/roles/imitation/README.md; do for link in $(grep -oP '\]\(\K[^)#]+' $f | grep -v '^http'); do test -e $(dirname $f)/$link || echo BROKEN: $f -> $link; done; done
    Expected: 无 BROKEN
    Evidence: .sisyphus/evidence/task-13-links.txt
  ```

  **Commit**: YES
  - Message: `docs(loom-phase6): workflow + arch alignment + canonical entry slots`

- [x] 14. **Tests + zero-regression + Loom flag verification**

  **What to do**:
  - 整合所有单元测试到 `tests/test_loom_phase6_*.py`:
    - `test_loom_phase6_shell.py` — ProjectConfig + ProjectShellService(version, lock, init, env scope)
    - `test_loom_phase6_compiler.py` — stage-to-flag 编译 + Loom flag mapping(env vars)
    - `test_loom_phase6_style_view.py` — 复用 Loom Phase 4 服务的视图层
    - `test_loom_phase6_characters_bridge.py` — CharacterPersona ↔ markdown round-trip
    - `test_loom_phase6_storyboard.py` — scene_beats input extension + 向后兼容
    - `test_loom_phase6_prose.py` — Loom flag injection + frontmatter 渲染
    - `test_loom_phase6_satire_anti_slop.py` — 6 类反模式 + 范本 negative test
    - `test_loom_phase6_lock_contract.py` — 锁定违约
    - `test_loom_phase6_cli.py` — Typer CliRunner 跑 11 子命令(mock LLM)
  - `tests/integration/test_loom_phase6_e2e.py`:mock LLM 跑完整 7 层
  - 编写 `scripts/compare_loom_metrics.py`(T12 用):接收 source branch + project slug,跑 loom-status + loom-reference-eval,输出对比表
  - **跑全量回归 + 静态检查**(必须全过):
    - `pytest tests/ -q` 100% pass
    - `pytest tests/test_loom_phase[1-5]*.py -q` 100% pass(Loom 回归基线)
    - `pytest tests/test_imitation*.py -q` 100% pass(imitation 回归基线)
    - `make v3-smoke` pass
    - `ruff check novel_analyzer/` 0 errors
    - `mypy --strict novel_analyzer/` 0 errors

  **Must NOT do**:
  - 不要在 mock LLM 中返回真实 LLM 才能产生的复杂 markdown(只验证 schema)
  - 不要新增 pip 依赖(仅 pytest fixture / monkeypatch / unittest.mock)
  - 不要在测试调真实 OpenAI/DeepSeek API(预算保护)
  - 不要 `# type: ignore` 跳过类型问题
  - 不要忘记 Loom flag 环境变量隔离测试(必须验证不污染全局)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES — Wave 4
  - **Blocks**: F2
  - **Blocked By**: T1-T13

  **References**:
  - `tests/test_loom_phase[1-5]*.py` — Loom 测试风格(尤其字段命名 / fixture 用法)
  - `tests/test_imitation*.py` — imitation 测试风格
  - `tests/conftest.py` — 现有 fixture
  - `typer.testing.CliRunner` — CLI 测试

  **WHY**:
  - 现有 fixture 已对齐 Loom session,Phase 6 复用 = 测试隔离 + DB session 正确

  **Acceptance Criteria**:
  - [x] 9 个新 test 文件 + 1 个 integration test 存在
  - [x] `pytest tests/test_loom_phase6_*.py -q` 100% pass
  - [x] `pytest tests/ -q` 全过
  - [x] `pytest tests/test_loom_phase[1-5]*.py -q` 100% pass(零回归)
  - [x] `pytest tests/test_imitation*.py -q` 100% pass(零回归)
  - [x] `make v3-smoke` pass
  - [x] `ruff check` 0 errors
  - [x] `mypy --strict` 0 errors
  - [x] `scripts/compare_loom_metrics.py --help` 可执行
  - [x] env scope 测试: prose 命令前后全局 `os.environ` 不变(只在命令期间临时设)

  **QA Scenarios**:

  ```
  Scenario: 全量测试
    Tool: Bash
    Steps:
      1. .venv/bin/pytest tests/ -q 2>&1 | tee evidence/task-14-full.txt
    Expected: passed=N, failed=0
    Evidence: .sisyphus/evidence/task-14-full.txt

  Scenario: Loom Phase 1-5 回归
    Tool: Bash
    Steps:
      1. .venv/bin/pytest tests/test_loom_phase1.py tests/test_loom_phase2.py tests/test_loom_phase3.py tests/test_loom_phase4.py tests/test_loom_phase5.py -q 2>&1 | tee evidence/task-14-loom-regression.txt
    Expected: 130 passed
    Evidence: .sisyphus/evidence/task-14-loom-regression.txt

  Scenario: imitation 回归
    Tool: Bash
    Steps:
      1. .venv/bin/pytest tests/test_imitation*.py -q 2>&1 | tee evidence/task-14-imitation-regression.txt
    Expected: failed=0
    Evidence: .sisyphus/evidence/task-14-imitation-regression.txt

  Scenario: 静态检查
    Tool: Bash
    Steps:
      1. .venv/bin/ruff check novel_analyzer/ 2>&1 | tee evidence/task-14-ruff.txt
      2. .venv/bin/mypy --strict novel_analyzer/ 2>&1 | tee evidence/task-14-mypy.txt
    Expected: 0 errors in both
    Evidence: .sisyphus/evidence/task-14-{ruff,mypy}.txt

  Scenario: Loom flag env scope
    Tool: Bash
    Steps:
      1. .venv/bin/pytest tests/test_loom_phase6_prose.py::test_env_scope -q
    Expected: pass
    Evidence: .sisyphus/evidence/task-14-env-scope.txt

  Scenario: smoke
    Tool: Bash
    Steps:
      1. make v3-smoke 2>&1 | tee evidence/task-14-smoke.txt
    Expected: 全部 ✓
    Evidence: .sisyphus/evidence/task-14-smoke.txt
  ```

  **Commit**: YES
  - Message: `test(loom-phase6): unit + integration + zero-regression + Loom flag scope verification`
  - Tested: pytest tests/ (full); make v3-smoke; ruff; mypy --strict; Loom Phase 1-5 regression; imitation regression
  - Not-tested: production-grade 50k+ word imitation runs; concurrent project workflows

---

## Final Verification Wave

> 4 个评审并行,全部 APPROVE 后呈现给用户,获得明确"okay"才能完结。

- [x] F1. **Plan Compliance + Loom Integration Audit** — `oracle`
  Read this plan + Loom canonical 5 docs. For each Must Have: verify it exists. For each Must NOT Have: grep + git diff verify. **Loom 专属**: verify all calls to Loom services use existing methods unchanged(`git diff main -- novel_analyzer/services/{memory_assembler,memory_consolidation,tension,pairwise_eval,style_calibration,rhythm_analysis,dialogue_signal,character_agent,reader_simulation,thread_scheduler,long_book_health}_service.py` 必须空); verify `tests/test_loom_phase[1-5]*.py` files unchanged; verify alembic/versions no new migration; check 8 existing Loom CLI commands still work.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Loom Service Drift [CLEAN/N] | Loom Test Drift [CLEAN/N] | VERDICT`

- [x] F2. **Code Quality + Zero-Regression Review** — `unspecified-high`
  Run `.venv/bin/ruff check novel_analyzer/`, `.venv/bin/mypy --strict novel_analyzer/`, `.venv/bin/pytest tests/ -q`(全量 must pass), `.venv/bin/pytest tests/test_loom_phase[1-5]*.py -q`(Loom 回归基线), `.venv/bin/pytest tests/test_imitation*.py -q`(imitation 回归基线), `make v3-smoke`. Review all new files: 类型/异常/命名/重复/注释/层次。
  Output: `Build [P/F] | Lint [P/F] | Type [P/F] | Tests [N/N] | Loom Regression [P/F] | Imitation Regression [P/F] | Smoke [P/F] | VERDICT`

- [x] F3. **Real Manual QA + Loom MVP Validation** — `unspecified-high`(+ tmux)
  Clean state.先 `auto-run /home/user/txt111/01.txt --max-chapters 30`。然后端到端跑 `imitate-project run meiqian-new-story --until prose --use-llm`。中途测试: lock characters/<主角> + revise plot 重生 outline 验证 lock 不被改; revise + diff; --fast 模式。**Loom 验证**: 跑 `loom-reference-eval` 验证 fidelity ≥ 0.5; 跑 `loom-ab-compare output/baseline/ output/projects/meiqian-new-story/chapters/`; 跑 `loom-status` 验证项目产物对应 branch 的 Loom 信号正常; 跑 `loom-collect-pairs` 看是否自动产 pairs。对抗输入测试 anti-slop: 喂解释笑话 / 大团圆 / 5 个"特么的"。所有证据存 `.sisyphus/evidence/final-qa/`。
  Output: `Scenarios [N/N] | Edge Cases [N] | Anti-Slop [N/N] | Loom Reference Fidelity [N.NN] | Loom AB Comparison [P/F] | VERDICT`

- [x] F4. **Scope Fidelity + Loom Architecture Audit** — `deep`
  对每个 task 读"What to do"和实际 diff。验证 1:1。检查 Must NOT 每条。**Loom 架构对齐**: 验证 T4/T6/T9 确实复用 Loom 服务而非重写(grep `style_calibration_service` / `character_agent_service.build_character_persona` / `memory_assembler_service.assemble` / `pairwise_eval_service` 调用); 验证 T9 prose frontmatter 含所有 6 个 `_loom_*` 字段; 验证项目 config 的 `loom_flags` 段确实通过环境变量影响 Loom 服务。检测 cross-task 污染。
  Output: `Tasks [N/N] | Contamination [CLEAN/N] | Loom Service Reuse [N/N] | Loom Frontmatter Coverage [N/6] | Loom Flag Mapping [P/F] | VERDICT`

---

## Commit Strategy

Lore-protocol commits, Loom-aligned messages:
- W1: `feat(loom-phase6): foundation — ProjectConfig + shell service + Loom flag mapping (T1-T3)`
  Constraint: must not modify Phase 1-5 Loom services
- W2: `feat(loom-phase6): editable layers — style/macro/characters/plot/conflicts (T4-T7)`
  Tested: pytest tests/test_loom_phase6_layers.py
  Directive: T6 character bridge MUST use existing build_character_persona; do not reimplement persona derivation
- W3: `feat(loom-phase6): storyboard + prose orchestrator + ops (T8-T10)`
  Constraint: storyboard injects via imitation-constraint-pack scene_beats append; prose reuses harness-imitation
- W4: `feat(loom-phase6): satire-anti-slop + lock checker + MVP + docs (T11-T14)`
  Tested: end-to-end MVP run + loom-reference-eval + adversarial anti-slop
  Not-tested: 100k+ word run, multi-novel concurrent project

Pre-commit each wave: `ruff check && mypy --strict && pytest tests/test_loom_phase[1-6]*.py tests/test_imitation*.py -q`

---

## Success Criteria

```bash
# Loom 回归(硬门)
.venv/bin/pytest tests/test_loom_phase1.py tests/test_loom_phase2.py tests/test_loom_phase3.py tests/test_loom_phase4.py tests/test_loom_phase5.py -q
.venv/bin/pytest tests/test_imitation*.py -q
make v3-smoke

# 新增 Phase 6
.venv/bin/pytest tests/test_loom_phase6_*.py -q

# 端到端 MVP
.venv/bin/novel-analyzer auto-run /home/user/txt111/01.txt --max-chapters 30
BRANCH_ID=...
.venv/bin/novel-analyzer imitate-project init meiqian-new-story --source-branch $BRANCH_ID
.venv/bin/novel-analyzer imitate-project run meiqian-new-story --until prose --use-llm

# Loom MVP 验收
.venv/bin/novel-analyzer loom-status --branch-id $BRANCH_ID
.venv/bin/novel-analyzer loom-reference-eval $BRANCH_ID 0 output/projects/meiqian-new-story/chapters/
.venv/bin/novel-analyzer loom-ab-compare output/baseline/ output/projects/meiqian-new-story/chapters/

# 期望产物
test -f output/projects/meiqian-new-story/style/fingerprint.md
test -f output/projects/meiqian-new-story/macro/premise.md
test -f output/projects/meiqian-new-story/characters/<protagonist>.md
test -f output/projects/meiqian-new-story/chapters/ch001.outline.md
test -f output/projects/meiqian-new-story/chapters/ch001.storyboard.md
test -f output/projects/meiqian-new-story/chapters/ch001.draft.md
```

### Final Checklist
- [x] 7 层全部跑通且产物存在
- [x] revise/lock/diff 在任意层可用
- [x] 3 章正文 ≥ 12,000 中文字
- [x] `loom-reference-eval` fidelity ≥ 0.5
- [x] `loom-ab-compare` 显示 Phase 6 ≥ baseline
- [x] satire-anti-slop 对抗输入命中率 ≥ 90%
- [x] 范本前 5 章 negative test 全 pass(无误报)
- [x] Loom Phase 1-5 services 签名 100% 不变
- [x] Loom Phase 1-5 tests 100% pass
- [x] alembic/versions 无新增
- [x] T9 prose frontmatter 含 6 个 `_loom_*` 字段
- [x] 项目 loom_flags config 通过环境变量正确影响 Loom 服务
- [x] T6 character ↔ markdown 双向序列化保真
- [x] 4 个终审 APPROVE
- [x] 用户给 explicit okay

---

## 与 Loom Roadmap 的衔接

本 Phase 6 直接贡献 `docs/loom/handoff.md` 和 `roadmap.md` 中的:
- **Phase 3 P3 Pairwise 数据积累(当前 30/500 = 6%)**: T9 每次 prose 自动产 pairs,MVP 跑 3 章 ≥ 6 pairs
- **Phase 5 P4 外部知识 RAG**: T5 macro/world 输出符合 `rag/worldview-dossiers/` 格式
- **Phase 5 P4 题材 trope 库**: T7 conflicts 输出符合 `rag/trope-library/` 格式
- **0509 控制层 🔴 Full Control Console**: 项目壳可以视为 control console 的 CLI 第一版

未来 Phase 7+ 可演进:
- Web UI 桥接(把 markdown 文件流接到 `/writer/<branch_id>` 编辑器画布)
- 多本范本叠加学习
- Project Shell ↔ Loom reader_simulation gate 直连(reader_satisfaction_score < 0.6 时自动 hold MVP)
