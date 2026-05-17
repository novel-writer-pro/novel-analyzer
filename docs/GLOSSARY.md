# novel-analyzer 全局术语表

> 跨能力线、跨阶段共享的核心术语。读文档遇到陌生词先来这里查。
> 仿写控制层细粒度术语见 [imitation-control-plane-glossary.md](./imitation-control-plane-glossary.md)。

---

## A. 系统层级

| 术语 | 含义 | 出现在 |
|------|------|--------|
| **branch** | 一本书的分析分支。一个原始小说可衍生多个分支（baseline / 仿写 / 跨题材改写）。`branch_id` 是大部分 API 的入参 | 全系统 |
| **run** | 一次完整的处理任务（导入 / 分析 / 仿写） | pipeline / API |
| **chapter** | 章节，是最小提交单元。当前章成功后才能继续下一章 | 全系统 |
| **active branch** | 当前可读分支。回退采用逻辑隐藏，默认只读 active | 拆书 / API |
| **artifact** | 章节级结构化产物（facts / state / graph / windows / risk card） | 拆书 / 风控 |
| **manifest** | 章节切分后的 segment 元信息 | ingest |

---

## B. 拆书引擎（Deconstruction）

| 术语 | 含义 |
|------|------|
| **canonical chapter artifact** | 章节默认读路径产物（quick + deep 都从它派生） |
| **enrichment** | 在 canonical 之上叠加的增强信号（伏笔状态机、因果图等） |
| **facts** | LLM 从章节抽取的结构化事实（event / state / claim） |
| **graph (GraphNode/GraphEdge)** | 实体与关系图谱，承载人物/事件/伏笔/因果 |
| **window** | 章节滚动摘要，用于 context 注入 |
| **state summary** | 跨章累积的状态机（角色 / 关系 / 规则） |
| **adaptive context** | 实体驱动三策略检索（relevance + recency + foreshadowing） |
| **stage merging** | 把 5 次 LLM 调用合并成 3 次（intake+facts、evidence+analysis、guard） |
| **chapter complexity router** | 简单章节走小模型，复杂章节走大模型 |
| **arc memory** | 三层渐进压缩记忆（recent / midrange / distant） |
| **entity resolution** | 字符级 Jaccard 聚类做别名归一 |
| **claim grounding** | 每条分析声称必须有原文锚定 |
| **auto-repair** | 检测到问题后自动修复（4 类：overclaim 降级 / 去重 / thin 回填 / 空摘要兜底） |
| **R@5** | 检索 top-5 召回率，当前 simple = 0.81 / jieba = 0.84（5 本书 587 docs 锁基线） |

---

## C. 风险检查（Risk Audit）

| 术语 | 含义 |
|------|------|
| **checker** | 单一风险维度的判定器，目前 9 个：character_ooc / world_rule / relationship / foreshadow / setting_scope / thread_closure / plot_logic / timeline / power_scaling |
| **GateRiskItem / CheckerResult** | checker 输出的统一契约 |
| **ChapterRiskCard** | 章节级风险卡，含 supporting / counter evidence |
| **review candidate** | 待复核的风险条目 |
| **review candidate cluster** | 跨章节问题簇（cluster_title / chapters / max_confidence / suggested_review_action / cluster_status） |
| **audit conclusion** | 分支级审查结论 |
| **advisory-only** | 默认语义：风险审查不阻断主提交，只标记可疑章节 |
| **preflight** | 仿写写入前的风险预检 |
| **harness routing** | 根据风险类型路由到对应 skill |
| **risk semantic signal** | 上游 artifact 提供的细粒度信号（world_rule_signals / timeline_signals / power_signals 等） |

---

## D. 仿写（Imitation）

| 术语 | 含义 |
|------|------|
| **imitate-chapter** | 章节级仿写 CLI |
| **iterate-imitation** | 章节级仿写迭代 |
| **review-imitation** | 仿写后的审阅 |
| **writer-imitate-range** | 整本/区间仿写编排 CLI（per-chapter 增量保存） |
| **imitate-project** | Loom Phase 6 项目壳 14 个子命令（init / fingerprint / macro / characters / plot / conflicts / outline / storyboard / prose / revise / lock / diff / status / run） |
| **mapping_pack** | 跨题材改写映射包（world_map / character_map / power_map / rule_override） |
| **scaffold contamination** | 仿写产物被骨架占满（thin / scaffold / action_queue 三类） |
| **auto-retry** | service 层在 in-flight 检测到 contamination 自动重跑 3 次 |
| **carry_over_state** | 跨章节传递的状态（Loom Phase 1 增强为分层结构） |
| **harness** | 仿写控制器（preflight + skills pipeline + risk routing + revise lane） |
| **skill** | harness 调用的原子能力（chapter-intake / fact-extractor / draft-writer / draft-reviser …） |
| **session_state** | 0509 控制层运行时状态 |
| **operator_surface** | 0509 控制台暴露的操作面 |
| **action_queue** | 0509 控制层动作队列（revise / commit / discard） |
| **execution_state** | 0509 动作执行状态 |
| **primary / legacy** | 0509 双层治理：primary 是新字段，legacy 是兼容字段 |
| **retirement** | legacy 字段的退场路线（readiness → plan → pilot → preview → patch） |
| **live mutation bridge** | 从 preview/governance 到第一次真实 live mutation 的通路 |

---

## E. Loom（仿写上层）

| 术语 | 含义 |
|------|------|
| **Loom** | 织机，下一代架构层。不重写现有系统，叠加在已有 GraphRAG + 0509 控制层之上 |
| **Working Memory** | 当前章节工作记忆（≤ 2000 tokens） |
| **Episodic Memory** | 章节级长期记忆（importance_score / decay_factor 加权） |
| **Semantic Memory** | 跨章稳定语义记忆（人物 / 规则 / 关系 snapshot） |
| **conflict metabolism** | 冲突代谢机制：contradiction / evolution / ambiguity 三类 |
| **tension signal** | 张力信号三件套：plot_similarity_score / conflict_density / surprise_index |
| **pairwise eval** | LLM-as-judge 双盘对比评估，输出 chapter_quality_score |
| **CharacterPersona** | 角色认知基（价值观 / 目标 / 恐惧 / 说话风格向量） |
| **style fingerprint** | 风格指纹（风格向量 + 节奏类型 + 钩子密度） |
| **reader simulation** | 4-persona × 7-dim 读者模拟评审 |
| **comfort_score** | 读者舒适度评分，soft gate 阈值 |
| **Author Project Shell** | Phase 6 项目壳，7 层 markdown：style / macro / characters / plot / conflicts / outline / storyboard / prose |
| **anti-slop** | 反 AI slop 6 类讽刺文检测器 |
| **lock contract** | 锁定的产物，下游必须适配 |

---

## F. 接入层与运营

| 术语 | 含义 |
|------|------|
| **Writer Studio** | 作家端 UI，`/writer/<branch_id>`，含编辑器 + Loom 信号侧栏 + AI 副驾 + 版本树 |
| **Reader Studio** | 读者端 UI，`/reader/<branch_id>`，含三栏布局 + 防剧透 Q&A |
| **Workbench** | 旧工作台，根路径下的 `/control` `/reader` `/qa` `/pipeline` `/quality` `/ops` |
| **owner_user_id** | DB 多租户隔离字段（v2 加列，v3 service 层 WHERE） |
| **IdentityMiddleware** | v3 引入的请求头 `X-User-Id` 透传中间件 |
| **Dify** | 自托管 LLM 编排平台（Chatbot / Workflow / Prompt Studio），:8080 |
| **n8n** | 自托管自动化（pipeline-complete webhook / 通知 / 日报），:5678 |
| **Langfuse** | LLM trace（Dify 内置集成），:3030 |
| **Helicone** | LLM proxy trace（imitation 主流量），:8585 |
| **TEI** | HuggingFace Text Embeddings Inference 服务（embed + rerank） |
| **smoke-external** | `make smoke-external` 一键探针 4 个外部端点（DB + LLM + TEI embed + TEI rerank） |

---

## G. 商业化

| 术语 | 含义 |
|------|------|
| **B2B API** | 跨题材改写定向商用上线路径 |
| **跨题材改写商用就绪报告** | 6 项 SLA gap + 3 条上线路径，决策表见 [cross-genre-imitation-commercial-readiness-20260515.md](./cross-genre-imitation-commercial-readiness-20260515.md) |
| **tenant_id** | 多租户隔离字段（待 v4 引入，目前用 owner_user_id 临时承担） |
| **per-chapter 计费** | 一次成功 pass 算一个章节，失败章节不计费 |
| **mapping accuracy** | 跨题材改写映射准确率（目前 96-98%） |
| **full pass** | 整本仿写所有章节 verdict=pass 的比率（目前跨题材 99.4%） |

---

## H. 检索与基础设施

| 术语 | 含义 |
|------|------|
| **pg_trgm** | PostgreSQL trigram 扩展，模糊匹配 |
| **pgvector** | PostgreSQL 向量扩展，向量召回 |
| **pg_jieba** | PostgreSQL 中文分词扩展，BM25 召回（中文检索 R@5 +0.03） |
| **bm25_vector** | BM25 文档向量列（attgenerated 自动生成） |
| **domain dict** | 领域词典（自动从 GraphNode 收集，写入 .cache/novel-analyzer/domain-dict.txt） |
| **RRF** | Reciprocal Rank Fusion，多路召回融合 |
| **stage model** | 分阶段 LLM model（NOVEL_ANALYZER_LLM_STAGE_MODEL_NAME 单独配置） |

---

## I. 缩写

| 缩写 | 全称 |
|------|------|
| OOC | Out-Of-Character，人物失格 |
| RAG | Retrieval-Augmented Generation |
| RLS | Row-Level Security |
| SLA | Service Level Agreement |
| SOTA | State-Of-The-Art |
| TEI | Text Embeddings Inference |
| TTL | Time To Live |
| FTS | Full Text Search |
| LLM | Large Language Model |
| QA | Question & Answering |
| MVP | Minimum Viable Product |

---

返回 [文档中心](./README.md)
