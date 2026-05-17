# 培训幻灯材料（1-page A4）

> 每份能力线一份**单页 A4 幻灯材料**，10-15 分钟讲解用。
>
> 格式：纯 Markdown，可直接渲染成 PDF（建议工具：[Marp](https://marp.app/) / pandoc / VS Code Markdown Preview Enhanced）。
>
> 渲染建议：每份独立一页 A4，横版，字号 10-12pt。

---

## 4 份能力线幻灯

| 能力线 | 文件 | 适合场合 |
|--------|------|---------|
| 拆书引擎 | [01-deconstruction.slide.md](./01-deconstruction.slide.md) | 给开发新人 / 接入方讲检索与 Q&A 能力 |
| 风险检查 | [02-risk-audit.slide.md](./02-risk-audit.slide.md) | 给编辑 / 平台讲审稿自动化 |
| 受控仿写 | [03-imitation.slide.md](./03-imitation.slide.md) | 给作家 / IP 工作室讲仿写商用 |
| 商业化运营 | [04-commercialization.slide.md](./04-commercialization.slide.md) | 给销售 / BD / 投资方讲路线图 |

---

## 渲染成 PDF（可选）

### 用 Marp（推荐）
```bash
npm install -g @marp-team/marp-cli
marp --pdf 01-deconstruction.slide.md
```

### 用 pandoc
```bash
pandoc 01-deconstruction.slide.md -o 01-deconstruction.pdf \
  --pdf-engine=weasyprint -V geometry:landscape
```

---

## 设计原则（如果你要写新的）

- **1 页 A4 横版**，字号 10-12pt
- **3-5 个核心看点**，不要超过 7 个
- **必含一个证据数据**（实测数据、benchmark 等）
- **必含一行"不要说什么"**（合规边界）
- **保留 1 个深入文档入口**

---

返回 [training/](../README.md)
