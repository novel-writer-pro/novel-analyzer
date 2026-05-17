# Phase 6 架构边界澄清

## Phase 6 vs 0509 控制层

**0509 控制层**是 operator 面向的运营控制面：session_state、action_queue、retirement gate、live mutation bridge。服务对象是平台运营者，关注的是批量任务调度、质量门控、legacy retirement。

**Phase 6**是作家面向的 UX 层：7 层 markdown 项目目录、逐层 lock/revise/diff、分镜生成。服务对象是写作者，关注的是"我的故事长什么样"。

两者不重叠。Phase 6 在最终调用 harness-imitation 时，产物自然流入 0509 控制层的 session_state，不需要任何特殊对接。

## Phase 6 vs Loom Phase 1-5

Phase 1-5 是**基础设施层**：记忆代谢、张力信号、pairwise 评估、风格/节奏/对话信号、读者模拟。这些服务已经实现，有稳定 API。

Phase 6 是**调用层**：把这些服务的输出收口成作家可读的 markdown，把作家的编辑意图编译成这些服务的输入参数。Phase 6 不修改任何 Phase 1-5 服务签名。

## Phase 6 vs writer-imitate-range

`writer-imitate-range` 是**单次执行命令**：给定 branch_id + 章节范围，跑完返回结果。没有"项目"概念，没有层级 lock，没有跨次实验的状态持久化。

Phase 6 是**项目壳**：持久化项目目录（`output/projects/<slug>/`），支持多次 revise/lock/run，跨 session 保留作家决策。`writer-imitate-range` 是 Phase 6 在 L7 层的底层调用之一。

## Phase 6 不做什么

- **不新增 DB schema**：所有持久化都在 `output/projects/<slug>/` 文件系统，不碰数据库
- **不新增 LLM pipeline**：复用现有 harness-imitation + plan-whole-book，不引入新的 LLM 调用链
- **不提供 Web UI**：纯 CLI，作家用编辑器打开 markdown 文件审阅
- **不替换现有命令**：`writer-imitate-range`、`iterate-imitation`、`imitate-chapter` 继续独立可用

## 关联文档

- [README.md](./README.md) — Phase 6 定位
- [workflow.md](./workflow.md) — 5 步工作流
- [../roadmap.md](../roadmap.md) — Phase 6 任务清单
