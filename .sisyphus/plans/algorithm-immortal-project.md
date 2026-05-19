# 实施计划：《算法修仙》项目

> 方案 B：修仙 × 算法/注意力经济
> 主角：过气顶流仙人重生，看透系统荒诞后重新崛起
> 基调：爽 + 讽刺
> 规模：120 章完整卷

---

## 世界观核心设定

### 一句话

天地灵气枯竭后，修士发现「信仰之力」可替代灵气。修为高低 = 信众数量 × 虔诚度。宗门变成 MCN，天道变成算法。

### 核心映射表

| 修仙概念 | 现实映射 | 讽刺锚点 |
|----------|---------|---------|
| 灵气/法力 | 粉丝注意力（信力） | 没人看你 = 没有灵气 |
| 修为境界 | 粉丝量级（万粉筑基、百万金丹、千万元婴） | 买粉 = 服用伪灵丹 |
| 天道 | 推荐算法 | 天道不公 = 算法不透明 |
| 天劫 | 全网黑/舆论风暴 | 越红劫越猛，塌房 = 渡劫失败 |
| 宗门 | MCN / 经纪公司 | 签约 = 卖身契 |
| 散修 | 独立创作者 / 素人 | 没有流量扶持，永远练气期 |
| 闭关 | 停更/消失 | 闭关太久 = 掉粉 = 修为倒退 |
| 法宝 | 设备/道具（环形灯、滤镜法器、剪辑神通） | 装备越贵内容越空 |
| 丹药 | 热点/话题（蹭热度 = 服丹） | 药效短暂，副作用大 |
| 飞升 | 全网顶流 / 跨平台封神 | 飞升后发现上界也是打工 |
| 心魔 | 数据焦虑 / 对比心态 | 每天看数据 = 走火入魔 |
| 道心 | 创作初心 / 真实表达 | 道心不稳 = 为流量妥协 |
| 双修 | 连麦/合拍 | CP 营业 = 合欢宗 |
| 渡劫 | 全网争议/黑料曝光 | 渡过 = 黑红也是红 |
| 飞剑传书 | 私信/弹幕 | 万剑齐发 = 弹幕刷屏 |

### 主角设定

- **名字**：顾流年（谐音「故流量」）
- **前世**：曾经的「天道宠儿」——算法天道主动推荐的顶流仙人，元婴期（千万信众）
- **陨落原因**：被算法天道判定「内容同质化」，一夜之间限流归零，信力枯竭，元婴碎裂
- **重生后**：回到筑基前（零粉状态），但保留前世记忆——知道算法规则、知道流量密码、也知道这一切的荒诞
- **核心矛盾**：他知道怎么玩这个游戏，但他已经看透了游戏的虚无。是再次迎合算法，还是找到真正的「道」？
- **金手指**：能看到每个人头顶的「信力值」实时波动 + 前世对算法规则的完整认知

### 世界结构

- **昆仑云台**：修仙界的「互联网平台」，所有修士在此展示道法获取信众
- **天道算法**：决定谁被推荐、谁被限流的神秘存在，无人知道完整规则
- **信力**：信众注意力凝聚的能量，是修炼唯一资源
- **宗门 = MCN**：签约弟子，提供流量扶持，抽取信力分成（通常 70%）
- **天劫 = 舆论风暴**：境界越高，天劫越猛（因为曝光度越大，被攻击面越大）
- **散修困境**：没有宗门扶持 = 没有初始流量 = 永远筑基

---

## 实施路径

### Phase 0：环境准备（前置，不依赖分析完成）

| Task | 说明 | 依赖 |
|------|------|------|
| T0.1 | 初始化 Project Shell：`imitate-project init algorithm-immortal --source-branch-id 4d87504f-...` | 分析 ch1-32 已完成 ✅ |
| T0.2 | 风格指纹提取：`imitate-project fingerprint algorithm-immortal` | T0.1 |
| T0.3 | 创建 satirical-worldbuilding skill 骨架 | 无 |

### Phase 1：世界观 + 角色（L1-L2）

| Task | 说明 | Agent | 依赖 |
|------|------|-------|------|
| T1.1 | 生成 L1 大观（premise.md + world.md），注入上方映射表 | project_macro_service + LLM | T0.2 |
| T1.2 | 生成 L2 角色卡（主角 + 5 核心配角） | project_characters_service + LLM | T1.1 |
| T1.3 | 人工审阅 + lock macro/characters | 你 | T1.1, T1.2 |

### Phase 2：剧情 + 冲突（L3-L4）

| Task | 说明 | Agent | 依赖 |
|------|------|-------|------|
| T2.1 | 生成 L3 剧情弧线（120 章分 4 卷 × 30 章） | project_plot_service + LLM | T1.3 |
| T2.2 | 生成 L4 冲突轴（主线 + 3 条支线） | project_plot_service + LLM | T2.1 |
| T2.3 | 人工审阅 + lock plot/conflicts | 你 | T2.1, T2.2 |

### Phase 3：章纲 + 分镜（L5-L6）

| Task | 说明 | Agent | 依赖 |
|------|------|-------|------|
| T3.1 | 生成 L5 章纲（120 章标题 + 目标 + 钩子） | project_outline_service + LLM | T2.3 |
| T3.2 | 生成 L6 分镜（每章 scene beats） | project_outline_service + LLM | T3.1 |
| T3.3 | 人工审阅前 10 章分镜 | 你 | T3.2 |

### Phase 4：正文生成（L7）

| Task | 说明 | Agent | 依赖 |
|------|------|-------|------|
| T4.1 | 生成正文 ch1-10（spike 验证质量） | project_prose_service + harness | T3.3 |
| T4.2 | Reader Panel 评估 ch1-10 | reader_panel_service | T4.1 |
| T4.3 | 根据 panel 反馈调整 prompt/世界观 | 你 + LLM | T4.2 |
| T4.4 | 批量生成 ch11-120 | project_prose_service + harness | T4.3 |

### Phase 5：质量验证 + 发布

| Task | 说明 | Agent | 依赖 |
|------|------|-------|------|
| T5.1 | 全书 Reader Panel 评估 | reader_panel_service | T4.4 |
| T5.2 | 风险审查（OOC / 时间线 / 设定一致性） | risk_audit 9 checkers | T4.4 |
| T5.3 | Loom 信号验证（节奏/张力/风格一致性） | loom services | T4.4 |
| T5.4 | 人工终审 + 修订 | 你 | T5.1-T5.3 |

---

## Skill 沉淀：satirical-worldbuilding

### 目标

创建一个可复用的 skill，输入「现实痛点」，输出完整的讽刺修仙世界观设定包。

### Skill 结构

```
skills_dir/satirical-worldbuilding/
├── SKILL.md              # 主文件：流程 + 模板
├── prompts/
│   ├── pain-to-mapping.md    # 痛点 → 修仙映射 prompt
│   ├── world-structure.md    # 世界结构生成 prompt
│   ├── protagonist-archetype.md  # 主角原型选择 prompt
│   └── satire-anchor.md     # 讽刺锚点设计 prompt
└── examples/
    ├── economic-anxiety.md   # 《没钱》的映射分析
    └── algorithm-attention.md # 本项目的映射（作为范例）
```

### Skill 核心流程

1. **输入**：一个现实痛点关键词（如「教育贷」「996」「算法」「医疗」「房产」）
2. **Step 1**：痛点解构 → 提取 5-8 个核心矛盾
3. **Step 2**：矛盾 → 修仙概念映射（用映射表模板）
4. **Step 3**：生成世界结构（经济系统 / 权力结构 / 修炼机制 / 社会分层）
5. **Step 4**：设计主角原型（3 选 1）
6. **Step 5**：设计讽刺锚点（每 10 章至少 1 个「读者会心一笑」的场景）
7. **Step 6**：差异化检查（与已有作品对比，确保不是换皮）
8. **输出**：完整的 world.md + characters.md + satire-anchors.md

---

## Team 模式编排

启动时可以 4 路并行：

```
Lane A (worldbuilding):  T0.1 → T0.2 → T1.1 → T1.2
Lane B (skill):          T0.3（独立，不依赖任何其他 lane）
Lane C (analysis):       等待 resume13 完成 120 章分析（后台自动）
Lane D (infra check):    验证 LLM 余额 / 确认 provider 稳定性
```

Phase 1 完成后合流，进入 Phase 2-5 的串行流程（需要你审阅 lock）。

---

## 验收标准

| 阶段 | 验收 |
|------|------|
| Phase 1 | premise.md + world.md + 6 角色卡，你审阅 lock |
| Phase 2 | 4 卷弧线 + 冲突轴，你审阅 lock |
| Phase 3 | 120 章纲 + 前 10 章分镜，你审阅 |
| Phase 4 spike | ch1-10 comfort_score ≥ 65，anti_slop pass |
| Phase 4 full | 120 章全部 harness pass |
| Phase 5 | Reader Panel avg comfort ≥ 65，risk audit 无 critical |
| Skill | 用另一个痛点（如「996」）跑一遍，能产出完整世界观 |

---

## 风险

| 风险 | 缓解 |
|------|------|
| LLM 余额再次耗尽 | 监控 provider 状态，准备 fallback provider |
| 120 章正文生成耗时长（~60h） | 分批跑，每 30 章验证一次 |
| 讽刺尺度过大导致内容风险 | satire-anti-slop-guard skill 已就绪，每章检查 |
| 世界观设定前后矛盾 | risk_audit 9 checkers 自动检测 |
| 风格漂移（后期章节不像前期） | Loom style_drift 监控 |
