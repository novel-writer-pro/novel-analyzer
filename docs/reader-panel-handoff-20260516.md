# Reader Panel — 4-persona × 7-dimension 阅读体验评估 (2026-05-16)

> **状态**：✅ 已上线（commit `5a0eb94`），Stage A 实测验证通过。
>
> **目的**：解决"harness gate 通过但内容平白无特色"的盲点。给仿写每章追加一个 0-100 的 `comfort_score` 综合可读性评分 + 段落级具体修改建议。
>
> **互补文档**：
> - [`chapter-imitation-capability-matrix.md`](./chapter-imitation-capability-matrix.md) — 全能力矩阵（reader panel 改写"读者模拟评审"行）
> - [`baseline-imitation-quality-validation-handoff-20260515.md`](./baseline-imitation-quality-validation-handoff-20260515.md) — 同题材 prompt 修复验证
> - [`ops-debug-manual-20260514.md`](./ops-debug-manual-20260514.md) — 故障速查

---

## 1. 一句话定位

不替代 harness，**叠在 harness 之后做 soft gate**：当 harness 判 pass 但 reader panel 判 `comfort_score < 60`，把 verdict 反转为 needs_revision，stop_reason = `reader_panel_comfort_below_threshold`，并在 report 里挂一份 4 persona × 7 dim 的诊断 + 段落级 targeted_revisions。

---

## 2. 4 personas（独立打分，不互相协调）

| persona | 视角 | 关注 |
|---|---|---|
| `naive_reader` | 第一次接触此题材的普通读者 | 容易跟上吗？节奏会不会闷？ |
| `genre_veteran` | 看过 100 本同类型的老书虫 | 套路 vs 新意？爽点密度？ |
| `editor` | 商业出版编辑 | 节奏 / 悬念 / 章末付费点？ |
| `prose_critic` | 文笔老饕 | 比喻新鲜 / 对话生动 / 感官层次？ |

每 persona 独立 0-100 分 + `feel`（一句话真实感受）+ `strengths` / `weaknesses`（具体到段落）。

---

## 3. 7 个量化维度

| 维度 | 量化 | 失分点 |
|---|---|---|
| 对话生动度 | 对话占比 + 立场反映率 | 工具人台词 |
| 环境描写 | 感官词密度 + 场景切换 | 光秃白描 |
| 阅读舒适度 | 句长方差 + 段落节奏 + 信息密度 | 又长又密 / 又短又散 |
| 文笔质感 | 比喻 / 通感 / 意象密度 | 直白叙述 |
| 悬念强度 | 钩子 + 信息差 + 章末悬置 | 一切交代清楚 |
| 支线管理 | 主线推进 + 支线埋点 + 未回收线索 | 只有主线 |
| 特色（抗平白） | 反"目标→阻力→回应→钩子"模板 | 模板化严重 |

---

## 4. 验证结果（2026-05-16 真实数据）

### 4.1 离线评估（5 章 spike outputs）

跑 `ReaderPanelService.evaluate_draft()` over `output/baseline-spike-after-fix/`：

| ch | harness verdict | comfort | panel verdict | 解读 |
|---:|---|---:|---|---|
| 2 | pass | 63 | needs_polish | 通过但需润色 |
| 3 | needs_revision (scaffold) | 60 | needs_polish | 短文本 fallback |
| 4 | needs_revision (scaffold) | **18** | **needs_rewrite** | 强力识别 scaffold |
| 5 | **pass** | 60 | **needs_rewrite** | **抓 false-positive** |
| 6 | pass | 62 | needs_polish | 通过但需润色 |

### 4.2 端到端集成（`writer-imitate-range --reader-panel`）

跑 ch 2/5/6 with harness + reader panel 联动：

| ch | harness verdict | stop_reason | comfort | panel verdict |
|---:|---|---|---:|---|
| 2 | **needs_revision** | `reader_panel_comfort_below_threshold` | 58 | needs_rewrite |
| 5 | pass | `harness_soft_pass` | 64 | needs_polish |
| 6 | pass | `harness_soft_pass` | 68 | needs_polish |

**ch2 的 verdict 翻转就是 soft gate 的工作证据**：之前在 [Stage A spike](./baseline-imitation-quality-validation-handoff-20260515.md) 里 ch2=pass / score=84，现在因为 comfort=58 < 60 自动降级为 needs_revision。

### 4.3 实际给出的修改建议（节选 ch2 P1 actions）

```
P1 [文笔质感] 在灶房场景加入 2-3 处感官细节：灶火的烟味呛鼻、汤碗的热气烫手、
            杏衣服上的油烟味。在黄宅场景加入 1-2 处意象：如'厢房的光线透过纸窗洒下来，像...'
P1 [特色（抗平白）] 在卫荭出场时加入一个小反转：比如卫荭先冷淡，但在看到胭脂后
              态度有细微变化，或者她问的问题不是'你知道这意味着什么'而是更意外的内容
              （如'你为什么突然想到给我送胭脂？'）
```

每条 revision 都是**段落级可执行**的，不是"提升文笔"这种空话。

### 4.4 维度分布（ch2/5/6）

```
ch | 对话 | 环境 | 舒适 | 文笔 | 悬念 | 支线 | 特色
 2 |  54 |  48 |  66 |  44 |  59 |  53 |  40   ← 文笔/特色双低
 5 |  52 |  68 |  70 |  59 |  48 |  64 |  50   ← 对话/悬念低
 6 |  66 |  58 |  70 |  61 |  76 |  68 |  59   ← 整体最稳
```

→ 修改方向自动指向最弱维度，不需要人工挑。

---

## 5. 怎么用

### 5.1 CLI flag

```bash
.venv/bin/python -m novel_analyzer.cli.app writer-imitate-range \
  <branch_id> "2:目标A" "3:目标B" "4:目标C" \
  --output-dir output/with-panel \
  --use-llm --max-rounds 2 \
  --reader-panel
```

### 5.2 输出位置

每章 `output/<dir>/writer-imitate-ch{N}.json` 多一个 `reader_panel_report` 字段：

```json
{
  "source_chapter_index": 2,
  "final_verdict": "needs_revision",
  "stop_reason": "reader_panel_comfort_below_threshold",
  "policy_summary": {
    "reader_panel_comfort_score": 58,
    "reader_panel_verdict": "needs_rewrite",
    "reader_panel_priority1_count": 3,
    ...
  },
  "reader_panel_report": {
    "comfort_score": 58,
    "personas": [...],
    "dimension_scores": [...],
    "targeted_revisions": [
      {"dimension": "文笔质感", "action": "...", "priority": 1}
    ],
    "overall_verdict": "needs_rewrite"
  }
}
```

CLI 实时输出含 comfort：
```
[1/3] ch2 done in 154.6s chars=1354 verdict=needs_revision comfort=58/needs_rewrite -> output/...
```

### 5.3 阈值（可调）

定义在 `novel_analyzer/services/reader_panel_service.py`：

```python
COMFORT_PASS_THRESHOLD = 70           # >=70 = polished
COMFORT_NEEDS_REWRITE_THRESHOLD = 60  # <60  = needs_rewrite
```

**Soft gate 触发**：harness=pass + comfort < 60 → 反转为 needs_revision。

调整建议：先在 30+ 章混合数据上跑一遍，对比 comfort_score 与人工评分相关性，再调阈值。

---

## 6. 成本

| 项 | 数值 |
|---|---:|
| LLM 调用次数 | 1 / 章（在 harness 之后） |
| 输出 token | ~2000 / 章（4 persona × 7 dim 完整 JSON） |
| 时间 | ~30s / 章 (claude-haiku-4.5) |
| `--reader-panel` 单章总耗时 | 154-217s（含 harness） vs 88-105s（不含） |

**不开 panel 时零成本**（默认 off）。

---

## 7. 已知限制 + 下一步

### 限制

1. **单 LLM judge**：4 persona 在一次 LLM 调用里产出，不是 4 次独立调用。优势：成本低；劣势：persona 之间会互相校准。
2. **scaffold-only 章节直接跳过**：harness 已判定 needs_revision 且 is_scaffold_only=True 时不调 panel（节省成本，因为答案已经明确）。
3. **无 retry 反馈循环**：当前 panel 只在最后一轮 harness 后跑一次，**不会用 targeted_revisions 触发新一轮 harness 重试**。这是 Phase B 的工作。

### Phase B（建议下一步，3-5 天）

把 `targeted_revisions` 接到 harness 的 `_apply_actions_to_draft`：
- comfort < 60 时不只是改 verdict，还把 panel 的 P1 修改建议作为 `revise_payload` feed 给 LLM 重写
- 重写后再跑一次 panel，直到 comfort >= 60 或达到 max_rounds
- 这才是真正的"读者反馈闭环"

### Phase C（建议下下步，1-2 周）

- **多 LLM judge 聚合**：4 persona 各自独立调用，避免互相校准（成本×4，可只在 release 章节启用）
- **维度蒸馏到 prompt**：把高频出现的 weakness（如"对话工具化"）反向蒸馏进生成 prompt 的 §8 self-check
- **Pairwise 比较**：用旧版本 draft + 新版本 draft 同时给 panel 看，输出"哪一版更好"，用作 A/B 数据

---

## 8. 长跑验证步骤（手工执行）

### Stage A：3 章实证（已完成）

✅ commit `5a0eb94` 跑过 ch 2/5/6，端到端可用。

### Stage B：30 章对比（建议下一步）

```bash
# 对比 baseline (no panel) vs panel
mkdir -p output/baseline-30ch-no-panel output/baseline-30ch-with-panel

# Run 1: 无 panel
nohup bash -c '
cd /home/user/novel-analyzer
set -a && source .env.local && set +a
.venv/bin/python -m novel_analyzer.cli.app writer-imitate-range \
  72da24e9-e65c-45a9-836d-957c4ae783ec \
  "31:章节A" "32:章节B" ... "60:章节AD" \
  --output-dir output/baseline-30ch-no-panel \
  --use-llm --max-rounds 2 \
  > /tmp/no-panel.log 2>&1
' &
disown

# Run 2: 有 panel（同样章节）
nohup bash -c '
cd /home/user/novel-analyzer
set -a && source .env.local && set +a
.venv/bin/python -m novel_analyzer.cli.app writer-imitate-range \
  72da24e9-e65c-45a9-836d-957c4ae783ec \
  "31:章节A" ... "60:章节AD" \
  --output-dir output/baseline-30ch-with-panel \
  --use-llm --max-rounds 2 --reader-panel \
  > /tmp/with-panel.log 2>&1
' &
disown
```

### 对比验证脚本

```bash
python3 <<'PY'
import json, glob
def stats(d, has_panel=False):
    files = sorted(glob.glob(f'{d}/writer-imitate-ch*.json'))
    items = [json.load(open(f)) for f in files]
    passes = sum(1 for c in items if c['final_verdict'] == 'pass')
    if has_panel:
        comforts = [c.get('reader_panel_report',{}).get('comfort_score',-1) for c in items]
        comforts = [s for s in comforts if s >= 0]
        avg_comfort = sum(comforts)/len(comforts) if comforts else 0
        return {'n': len(items), 'pass': passes, 'avg_comfort': avg_comfort}
    return {'n': len(items), 'pass': passes}

a = stats('output/baseline-30ch-no-panel')
b = stats('output/baseline-30ch-with-panel', has_panel=True)
print(f"No-panel:    {a['pass']}/{a['n']} pass")
print(f"With-panel:  {b['pass']}/{b['n']} pass, avg_comfort={b['avg_comfort']:.1f}")
PY
```

### 判定标准

| 现象 | 判定 |
|---|---|
| 有 panel pass-rate > 无 panel +30% | ❌ panel 太松，提高阈值 |
| 有 panel pass-rate < 无 panel −20% | ✅ panel 在抓质量问题 |
| 平均 comfort > 75 | ✅ baseline 自检效果好 |
| 平均 comfort 60-70 | ✅ panel 给出有效改进方向 |
| 平均 comfort < 50 | ⚠️ 模型 / prompt 还需优化 |

---

## 9. 互补：与现有信号的关系

| 已有信号 | 解决什么 | 不解决什么 |
|---|---|---|
| `harness gate` | 结构 / 风险 / 规则违反 | 内容平白无聊 |
| `reader_simulation_service` (启发式) | 节奏 / 张力的近似数值 | 真实读者主观感受 |
| `pairwise_eval` (Loom) | 两个 draft 哪个好 | 单 draft 是否值得发布 |
| **`reader_panel_service`** (新) | **单 draft 的读者主观可读性 + 维度级修改建议** | **不替代任何上述** |

---

## 10. 一句话总结

> Reader Panel 给"看起来过了 gate 但读起来没意思"的章节装上了一面镜子。镜子说不过去就让 harness 把章节打回重写，并明确告诉 LLM 哪段对话像念目标、哪段环境光秃秃。

下一棒人接手时：
- 跑 §8 Stage B 30 章对比，决定阈值是否要调
- 决定是否做 Phase B（panel → harness 重试循环），把 targeted_revisions 真正喂回去
