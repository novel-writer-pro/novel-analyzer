# Loom Phase 6 — Author Project Shell

> UX layer on top of Loom Phase 1-5. Lets authors edit 7 layers of markdown, then compiles to existing CLI flags + Loom feature env vars.

## 定位

Phase 6 不是新 pipeline，而是 Phase 1-5 的**作家面向 UX 层**：

- 把 9 个 steering flag 收口成可编辑 markdown 文件
- 把 5 个 Loom feature flag 收口成项目级配置
- 唯一新增生成层：分镜/scene_beats（扩展 imitation-constraint-pack skill input）

## 7 层产物

| 层 | 文件 | 编译产物 |
|---|---|---|
| L0 风格 | style/fingerprint.md | --knowledge-ref |
| L1 大观 | macro/premise.md + world.md | --worldview-note + --rule-override |
| L2 角色 | characters/<name>.md | --character-map |
| L3 剧情 | plot/arcs.md + chapter_goals.md | chapter_goals for plan-whole-book |
| L4 冲突 | conflicts/axes.md + innovation.md + taboo.md | --trope-axis + --innovation-directive + --taboo-innovation |
| L5 章纲 | chapters/ch001.outline.md | target_goal for iterate-imitation |
| L6 分镜 ⭐NEW | chapters/ch001.storyboard.md | scene_beats → imitation-constraint-pack |
| L7 正文 | chapters/ch001.draft.md | harness-imitation + Loom signals |

## 快速开始

```bash
# 1. 导入范本小说
.venv/bin/novel-analyzer auto-run /path/to/novel.txt --max-chapters 30

# 2. 初始化项目
.venv/bin/novel-analyzer imitate-project init <slug> --source-branch <branch_id>

# 3. 一键跑到正文（快速模式）
.venv/bin/novel-analyzer imitate-project run <slug> --until prose --fast --use-llm

# 4. 或逐层审阅（推荐）
.venv/bin/novel-analyzer imitate-project fingerprint <slug>
.venv/bin/novel-analyzer imitate-project macro <slug> --use-llm
# ... 审阅 output/projects/<slug>/macro/ ...
.venv/bin/novel-analyzer imitate-project lock <slug> "macro/*.md"
.venv/bin/novel-analyzer imitate-project characters <slug> --use-llm
# ... 继续 ...
```

## 与 Phase 1-5 的关系

Phase 6 复用所有 Phase 1-5 服务（不修改任何签名）：
- T4 调用 style_calibration_service + rhythm_analysis_service
- T6 调用 character_agent_service.build_character_persona
- T9 调用 memory_assembler_service.assemble + imitation_harness_service.harness_imitation
- T9 自动调用 loom-collect-pairs（贡献 Phase 3 P3 数据池）

详见 [workflow.md](./workflow.md) | [arch-alignment.md](./arch-alignment.md)
