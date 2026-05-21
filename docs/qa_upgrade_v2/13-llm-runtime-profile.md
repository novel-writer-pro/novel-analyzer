# 13. LLM Runtime Profile

## 目标

本文件记录 QA Upgrade V2 当前指定的 LLM 运行配置，方便开发、演示、联调和回归验证时保持一致。

---

## 当前指定配置

用户指定：

- model: `minimaxai/minimax-m2.7`
- base_url: `http://43.155.145.78:65432/`
- api_key: **已脱敏，不入库；请仅在本地环境变量中配置**

---

## 推荐映射到本项目 Settings

根据 `novel_analyzer/config/settings.py`，建议最小配置：

```bash
export NOVEL_ANALYZER_LLM_PROVIDER_NAME=minimax-local
export NOVEL_ANALYZER_LLM_BASE_URL=http://43.155.145.78:65432/
export NOVEL_ANALYZER_LLM_API_KEY=<set-locally>
export NOVEL_ANALYZER_LLM_MODEL_NAME=minimaxai/minimax-m2.7
export NOVEL_ANALYZER_LLM_QA_MODEL_NAME=minimaxai/minimax-m2.7
```

如果后续 query understanding 也接 LLM，可保持统一模型，先不要多模型化。

---

## 推荐用途

### 适合
- ask-branch / ask-branch-stream
- query understanding parse（如果启用 LLM 解析）
- grounded answer generation
- demo / 联调 / 验证

### 暂不建议过度依赖
- 大规模离线 benchmark 全量跑（先看吞吐和稳定性）
- 多阶段重型 prompt 编排（P0/P1 阶段不需要）

---

## 推荐验证方式

### 1. 配置加载验证
建议先确认 Settings 已拿到这组值。

### 2. QA 最小链路验证
对一个已知 branch 跑：
- `/api/ask-branch`
- `/api/ask-branch-stream`

### 3. Provider 可用性验证
观察：
- provider health
- degraded rate
- answer latency

---

## 运行建议

### P0 / P1 阶段
优先保证：
- 接口稳定
- diagnostics 可见
- grounding 能跑

### P2 以后
再评估是否需要：
- query parse 和 answer generation 分开模型
- 更快的小模型做 parser
- 更强模型只负责 final answer

---

## 安全提醒

这份配置目前是“本仓库开发上下文的指定运行配置”。
`api_key` 不应进入仓库文件；如曾在本地文档或聊天中暴露，建议按已泄露处理并及时轮换。
