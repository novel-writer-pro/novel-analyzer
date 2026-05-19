---
name: ai-detection-validator
description: 多维度 AI 味检测验证器。对生成文本进行 5 维度评分，定位具体问题段落，输出修改建议。作为发布前的最终门控。
---

# ai-detection-validator

## 定位

生成后的最终验证层。模拟主流 AI 检测工具的检测逻辑，在本地完成评分，避免将文本上传到第三方检测平台（泄露内容风险）。

## 检测维度（5 维度 + 综合分）

### D1: 困惑度估算 (Perplexity Proxy)

不需要真正计算 perplexity（需要模型），用代理指标：

```python
def perplexity_proxy(text: str) -> float:
    """
    代理指标：词汇惊喜度
    - 统计每个词在常用词表中的频率排名
    - 高频词占比越高 → 困惑度越低 → 越像 AI
    - 目标：高频词占比 < 70%（人类通常 55-65%）
    """
    # 用 jieba 分词，对比词频表
    # 返回 0-1，越高越像 AI
```

### D2: 突发性 (Burstiness)

```python
def burstiness_score(text: str) -> float:
    """
    句长变异系数 (CV = stdev / mean)
    - AI 典型 CV: 0.3-0.5（均匀）
    - 人类典型 CV: 0.6-1.2（波动大）
    - 目标：CV ≥ 0.6
    """
    sentences = split_sentences(text)
    lengths = [len(s) for s in sentences]
    cv = stdev(lengths) / mean(lengths)
    # 返回 0-1，越高越像 AI（CV 越低越像 AI）
```

### D3: 句式重复度 (Structural Repetition)

```python
def structural_repetition(text: str) -> float:
    """
    检测连续句子的开头模式重复
    - 提取每句前 2-3 个词的词性模式
    - 连续 3+ 句相同模式 → 高重复度
    - 目标：最长连续相同模式 ≤ 2
    """
```

### D4: 连接词密度 (Connector Density)

```python
def connector_density(text: str) -> float:
    """
    连接词/虚词出现频率
    - AI 典型：每 100 字 3-5 个连接词
    - 人类典型：每 100 字 0-2 个
    - 目标：≤ 2/100字
    """
    connectors = count_connectors(text)
    return connectors / (len(text) / 100)
```

### D5: 情感直述率 (Telling Rate)

```python
def telling_rate(text: str) -> float:
    """
    直接情绪词 vs 展示性描写的比率
    - 统计「他感到X」「她很X」等直述模式
    - 目标：直述率 < 5%（每 20 句最多 1 句直述）
    """
```

---

## 综合评分

```python
def ai_detection_score(text: str) -> dict:
    """
    返回:
    {
        "overall": 0.0-1.0,  # 越高越像 AI，≥0.6 判定为高风险
        "dimensions": {
            "perplexity_proxy": 0.0-1.0,
            "burstiness": 0.0-1.0,
            "structural_repetition": 0.0-1.0,
            "connector_density": 0.0-1.0,
            "telling_rate": 0.0-1.0,
        },
        "verdict": "pass" | "warn" | "fail",
        "problem_paragraphs": [
            {"index": 3, "issue": "连续4句句长相近", "suggestion": "插入极短句打破节奏"},
            ...
        ]
    }
    """
    # 权重：burstiness 30% + connector 25% + perplexity 20% + structure 15% + telling 10%
    # 阈值：<0.4 pass, 0.4-0.6 warn, >0.6 fail
```

---

## 段落级问题定位

不只给总分，还要定位具体哪些段落有问题：

```
问题段落报告:
  ¶3 (第45-78字): 连续4句句长在18-22字之间 → 建议插入极短句
  ¶7 (第201-250字): 出现「渐渐」「似乎」「仿佛」3个禁用词 → 删除或替换
  ¶12 (第380-420字): 「他感到一阵愤怒」直接告知情绪 → 改为身体反应描写
  ¶15 (第490-530字): 连续3句「他……他……他……」开头 → 变换句式
```

---

## 阈值校准

需要用真实人类写作样本校准阈值。数据来源：

1. **源小说（《没钱修什么仙？》）**：已分析 48+ 章，可提取各维度基线
2. **其他人类网文**：从 DB 中已有的 43 本小说提取
3. **AI 生成样本**：从当前 golden-ch1 和 prose-30ch 提取

校准脚本：
```bash
.venv/bin/python scripts/dev/calibrate-ai-detection.py \
  --human-branch 4d87504f-9b13-4efa-abe1-279266ee181c \
  --ai-dir output/projects/algorithm-immortal/prose-30ch/ \
  --output knowledge/ai-detection-thresholds.json
```

---

## 与 pipeline 的集成点

```
writer-imitate-range (生成)
    ↓
satire-anti-slop-guard (讽刺 slop)
    ↓
reader-panel (可读性)
    ↓
ai-detection-validator ← 本 skill
    ↓ 如果 fail
humanize-prose (重写问题段落)
    ↓
ai-detection-validator (二次验证)
    ↓ 如果 pass
发布
```

---

## 使用方式

```python
from novel_analyzer.services.ai_detection_validator_service import validate_ai_detection

result = validate_ai_detection(chapter_text)
if result["verdict"] == "fail":
    # 取出 problem_paragraphs，喂给 humanize-prose 重写
    for p in result["problem_paragraphs"]:
        print(f"¶{p['index']}: {p['issue']} → {p['suggestion']}")
```

---

## 重要说明

**本地检测 ≠ 平台检测**。本地检测是近似模拟，不能保证 100% 通过平台检测。但可以：
1. 过滤掉最明显的 AI 特征（禁用词、均匀句长、直述情绪）
2. 大幅降低被检测概率（从 90% → 30% 以下）
3. 配合 humanize-prose 重写后进一步降低

最终建议：重要章节（前 3 章/高潮章节）手动过一遍第三方检测工具确认。
