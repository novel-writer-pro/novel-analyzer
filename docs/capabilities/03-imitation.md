# 能力线 3 — 受控仿写（Imitation）

> **一句话定位**：章节级 / 整本 / 跨题材改写三档仿写能力，全程 harness 控制（preflight + skills pipeline + risk routing + revise lane），产物可控、可回退、可商用。

**状态**：✅ 跨题材 170/171 pass（99.4%）｜🔧 同题材 prompt 修复后 Stage A/B/C 长跑验证中｜✅ Loom Phase 1-6 完成

---

## 能解决什么问题

| 问题 | 受控仿写给的答案 |
|------|-----------------|
| 直接喂 LLM 写，风格漂移、动机断裂、爽点稀释 | harness 全程控制 + Loom 信号反馈 |
| 100+ 章长篇连续性失控 | 分层记忆 + carry_over_state + auto-retry |
| 想用一本书的风格写另一种题材 | mapping_pack：world / character / power / rule 设定替换 |
| 仿写产物被骨架占满（thin / scaffold / action_queue） | service 层 in-flight 检测 + 自动重跑 3 次 |
| 多次实验产物散落到处都是 | Phase 6 Author Project Shell：7 层 markdown 项目目录 |

---

## 当前能做到什么（实证）

### 跨题材改写（mapping_pack）— 已商用就绪

| 测试 | 章数 | 字数 | full pass | mapping accuracy |
|---|---:|---:|---|---|
| 卫图（古典仙侠）→ 太空科幻 | 102 | 227,037 | **102/102 (100%)** | 98.0% |
| 诛仙（古典仙侠）→ 太空科幻 | 59 | 151,267 | **58/59 (98.3%)** | 97.5% |
| 卫图（古典仙侠）→ 都市修真 | 10 | 21,370 | **10/10 (100%)** | 96.1% |
| **合计** | **171** | **399,674** | **170/171 (99.4%)** | **96-98%** |

✅ 2 套源题材 × 2 套目标题材 ｜ ✅ 5/30/100+ 三个量级稳定 ｜ ✅ name leak rate 2-4% 可接受 ｜ ✅ scaffold-only chapter < 5%

详细：[cross-genre-imitation-commercial-readiness-20260515.md](../cross-genre-imitation-commercial-readiness-20260515.md)

### 同题材整本仿写 — 验证中

| 测试 | 章数 | full pass |
|------|------|----------|
| 卫图（古典仙侠 baseline） | 102 | 0/102 ❌ |
| 诛仙（古典仙侠 baseline） | 102 | 0/102 ❌ |
| 雪中悍刀行（江湖武侠 baseline） | 103 | 0/103 ❌ |

**关键诊断**：mapping pass / baseline fail 时 score、severity、gate_verdict 完全相同，差异 = mapping prompt 多了一个"二次检查"。

**修复**（commit `9704127`）：baseline prompt 加入 5 项 self-check（节奏 / 对话 / 动机 / 关系 / 营销冗余）。

**当前状态**：scaffold 三层修复已上线，Stage A/B/C 长跑验证中，详见 [baseline-imitation-quality-validation-handoff-20260515.md](../handoffs/baseline-imitation-quality-validation-handoff-20260515.md)

### 章节级仿写
- `imitate-chapter` / `iterate-imitation` / `review-imitation` 全部支持映射 flag
- harness 控制：preflight + skills pipeline + risk routing + revise lane

### 整本编排
- `writer-imitate-range`：per-chapter 增量保存、进程被杀不丢章节
- auto-retry：thin / scaffold / action-queue 三类 contamination 实时拦截
- 失败恢复：仅重跑缺失章节

### Loom Phase 6 项目壳（最新交付）
- `imitate-project` CLI 14 个子命令
- 7 层 markdown：style / macro / characters / plot / conflicts / outline / storyboard / prose
- 编译成 9 steering flag + 5 Loom env var
- MVP 已跑通：基于卫图风格生成全新故事 3 章

---

## 怎么用

### 章节级仿写
```bash
.venv/bin/python -m novel_analyzer.cli.app imitate-chapter \
  <branch_id> <chapter_index> --use-llm
```

### 5 章 spike（同题材）
```bash
.venv/bin/python -m novel_analyzer.cli.app writer-imitate-range \
  <branch_id> "2:目标A" "3:目标B" "4:目标C" "5:目标D" "6:目标E" \
  --output-dir output/spike --use-llm --max-rounds 2
```

### 跨题材改写（mapping_pack，已验证 99.4% pass）
```bash
.venv/bin/python -m novel_analyzer.cli.app writer-imitate-range \
  <branch_id> "2:目标A" "3:目标B" \
  --output-dir output/scifi --use-llm --max-rounds 2 \
  --world-map "郑国=星际联邦" \
  --character-map "卫图=魏拓" \
  --power-map "养生功=星能调息术" \
  --rule-override "封建奴籍替换为合同义务工"
```

### Loom 项目壳工作流
```bash
# Step 1: 初始化项目
.venv/bin/novel-analyzer imitate-project init meiqian-new --source-branch-id <branch_id>

# Step 2: 风格指纹（无需 LLM）
.venv/bin/novel-analyzer imitate-project fingerprint meiqian-new

# Step 3-7: 大观 → 角色 → 剧情 → 章纲 → 分镜
.venv/bin/novel-analyzer imitate-project macro meiqian-new --use-llm
.venv/bin/novel-analyzer imitate-project characters meiqian-new --use-llm
.venv/bin/novel-analyzer imitate-project plot meiqian-new --use-llm
.venv/bin/novel-analyzer imitate-project outline meiqian-new --use-llm
.venv/bin/novel-analyzer imitate-project storyboard meiqian-new --use-llm

# Step 8: 生成正文
.venv/bin/novel-analyzer imitate-project prose meiqian-new --all --use-llm --max-rounds 2

# 一键到指定层
.venv/bin/novel-analyzer imitate-project run meiqian-new --until prose --use-llm
```

---

## 架构概览

```
chapter_artifact + carry_over_state + mapping_pack
    ↓
imitation harness
    ├─ preflight              # 风险预检
    ├─ skills pipeline        # chapter-intake / draft-writer / draft-reviser
    ├─ risk audit routing     # 路由到对应 checker
    ├─ revise lane            # 修复通道
    ├─ auto-retry             # thin/scaffold/action_queue 三类拦截
    └─ in-flight contamination check
    ↓
draft chapter
    ↓
0509 控制层
    ├─ session_state
    ├─ operator_surface
    ├─ action_queue
    └─ execution_state
    ↓
Loom 上层（feature flag 渐进启用）
    ├─ memory      working / episodic / semantic
    ├─ tension     plot_similarity / conflict_density / surprise
    ├─ reward      pairwise eval (LLM-as-judge)
    ├─ style       fingerprint / drift detection
    ├─ character   CharacterPersona
    └─ project shell (Phase 6)  7 层 markdown
    ↓
output/<branch_or_project>/chapters/<idx>.md
```

---

## 全能力矩阵（仿写需要的所有能力）

| 能力类 | 当前覆盖度 | 状态 |
|--------|-----------|------|
| 风控审查 | 高 | ✅ risk audit + preflight + harness routing |
| 知识提炼 | 高 | ✅ facts / state / graph / unresolved threads |
| 章节规划 | 高 | ✅ next chapter planner + imitation plan |
| whole-book 编排 | 中高 | ✅ sandbox orchestration |
| 跨题材改写 | 高 | ✅ 170/171 pass |
| 同题材整本 | 中 | 🔧 prompt 已修复，长跑验证中 |
| 在飞 contamination 拦截 | 高 | ✅ auto-retry |
| 模拟读者评审 | 中高 | ✅ LLM 4-persona × 7-dim panel + comfort_score |
| 节奏分析 | 中低 | 🔄 Phase 4 已实现，待消费 |
| 对话设计 | 低 | 🔄 Phase 4 已实现，待消费 |
| 文风修辞 | 低 | 🔄 Phase 4 已实现，待消费 |
| 多线叙事 | 中低 | 🔲 Phase 5 待实现 |
| 资料研究 | 低 | 🔲 RAG library 填充中 |

详细：[chapter-imitation-capability-matrix.md](../chapter-imitation-capability-matrix.md)

---

## 路线图

### 已完成
- 章级 + 整本 + 跨题材三档
- Loom Phase 1-2（memory + tension + pairwise）
- Loom Phase 3（reward + character）
- Loom Phase 4（style + rhythm + dialogue）
- Loom Phase 5（reader sim + 多线 + 自适应）
- Loom Phase 6（Author Project Shell）

### 进行中
- 🔧 同题材 Stage A/B/C 长跑验证
- 🔄 真实 LLM 长跑（更强模型 + max-rounds 3）
- 🔄 pairwise 数据池扩充（30 / 500）

### 计划
- 🔲 Phase 7 Web UI 桥接到 Writer Studio
- 🔲 多本范本叠加
- 🔲 reader_sim_score 真实读者校准
- 🔲 RAG worldview/trope library 填充

详细：[loom/roadmap.md](../loom/roadmap.md) ｜ [ROADMAP.md](../ROADMAP.md)

---

## 深入文档

### 工作流
- [writer-imitation-workflow.md](../writer-imitation-workflow.md) — 完整仿写工作流
- [chapter-imitation-capability-matrix.md](../chapter-imitation-capability-matrix.md) — 全能力矩阵
- [imitation-control-plane-glossary.md](../imitation-control-plane-glossary.md) — 控制层术语表

### Loom 架构
- [loom/README.md](../loom/README.md) — 总入口（5 份 canonical 阅读顺序）
- [loom/overview.md](../loom/overview.md) — 完整架构图 + SOTA 对比表
- [loom/handoff.md](../loom/handoff.md) — 当前状态、已完成 / 未完成闭环
- [loom/roadmap.md](../loom/roadmap.md) — Phase 1-6 路线图
- [loom/sota-imitation-progression-checklist.md](../loom/sota-imitation-progression-checklist.md) — SOTA 推进 checklist

### Loom 子模块
- [loom/memory/](../loom/memory/README.md) — 分层记忆 + 冲突代谢
- [loom/tension/](../loom/tension/README.md) — 张力指标
- [loom/reward/](../loom/reward/README.md) — Pairwise 评估 + reward model
- [loom/style/](../loom/style/README.md) — 风格 / 节奏 / 对话
- [loom/character/](../loom/character/README.md) — CharacterPersona
- [loom/phase6/](../loom/phase6/README.md) — Author Project Shell

### 商用与质量
- [cross-genre-imitation-commercial-readiness-20260515.md](../cross-genre-imitation-commercial-readiness-20260515.md) — 跨题材商用决策表
- [handoffs/baseline-imitation-quality-validation-handoff-20260515.md](../handoffs/baseline-imitation-quality-validation-handoff-20260515.md) — 同题材修复长跑
- [handoffs/reader-panel-handoff-20260516.md](../handoffs/reader-panel-handoff-20260516.md) — Reader Panel
- [handoffs/session-handoff-20260517-phase6.md](../handoffs/session-handoff-20260517-phase6.md) — Loom Phase 6 完成

### 控制层（0509）
- [architecture/README.md § 仿写控制层](../architecture/README.md) — 6 份控制层文档导引
- [tracks/imitation/README.md](../tracks/imitation/README.md) — 仿写能力线 track

---

返回 [capabilities/](./README.md) ｜ [文档中心](../README.md)
