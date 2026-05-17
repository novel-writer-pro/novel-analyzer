# 培训幻灯材料

> 4 份单页幻灯，每份对应一条能力线，10-15 分钟讲解用。
> 源文件 Markdown + Marp，可一键渲染成 PDF。

---

## 4 份能力线幻灯

| 能力线 | 源文件 | 渲染产物 | 适合场合 |
|--------|--------|---------|---------|
| 拆书引擎 | [01-deconstruction.slide.md](./01-deconstruction.slide.md) | `01-deconstruction.slide.pdf` | 给开发新人 / 接入方讲检索与 Q&A |
| 风险检查 | [02-risk-audit.slide.md](./02-risk-audit.slide.md) | `02-risk-audit.slide.pdf` | 给编辑 / 平台讲审稿自动化 |
| 受控仿写 | [03-imitation.slide.md](./03-imitation.slide.md) | `03-imitation.slide.pdf` | 给作家 / IP 工作室讲仿写商用 |
| 商业化运营 | [04-commercialization.slide.md](./04-commercialization.slide.md) | `04-commercialization.slide.pdf` | 给销售 / BD / 投资方讲路线图 |

---

## 渲染 PDF

### 一键脚本（推荐）

```bash
cd docs/training/slides
./render.sh
```

脚本会自动：
1. 检查全局 `marp` 命令；没有则在本目录 `npm install` 一次本地安装
2. 渲染 4 份 PDF，输出到当前目录

### 手动渲染

```bash
npm install -g @marp-team/marp-cli
cd docs/training/slides
marp --pdf 01-deconstruction.slide.md
marp --pdf 02-risk-audit.slide.md
marp --pdf 03-imitation.slide.md
marp --pdf 04-commercialization.slide.md
```

---

## 渲染规格

- 单页 16:9（960×540 pt），用 A4 横向打印 fit-to-page 即可
- 字号：标题 34-38px ｜ 正文 16-19px ｜ 表格 14-17px
- 主色：深蓝 `#1e3a8a`（标题）/ 蓝 `#2563eb`（强调线）/ 红 `#be123c`（关键数据）/ 黄 `#fbbf24`（引言）
- 字体栈：Noto Sans CJK SC → Noto Sans → PingFang SC → Microsoft YaHei
- 渲染引擎：Marp + Firefox（Linux 默认）/ Chrome（Mac/Windows）

---

## 设计原则（如果你要写新的）

- **1 页装下**，10-15 分钟能讲完
- **3-5 个核心看点**，不超过 7 个
- **必含一个证据数据**（实测、benchmark、A/B 对比）
- **必含一行"不要说什么"**（合规边界）
- **保留 1 个深入文档入口**
- 所有 style 写在 frontmatter 的 `style:` 内联块里，不依赖外部 theme（保证一键渲染）

---

返回 [training/](../README.md) ｜ [文档中心](../../README.md)
