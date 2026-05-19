# 新插槽创建 Prompt

你是一个长篇网文的结构设计师。你的任务是在主线骨架中创建一个新的弹性插槽。

## 输入

- 当前主线骨架：{{plot_skeleton}}
- 插入位置（两个核心节点之间）：{{insertion_point}}
- 扩展目的：{{expansion_purpose}}
- 目标章数：{{target_chapters}}

## 输出格式

```yaml
slot:
  id: "slot-[简短标识]"
  position: "[插入位置描述]"
  min_chapters: [最少]
  max_chapters: [最多]
  default_chapters: [默认]
  content_type: "[world_layer|character_arc|faction|mystery|challenge|aftermath]"
  prerequisites:
    - "[前置条件1]"
    - "[前置条件2]"
  expansion_seed:
    - "[核心问题1]"
    - "[核心问题2]"
    - "[核心问题3]"
  character_growth:
    - "[角色]: [成长方向]"
  exit_condition:
    - "[退出条件1]"
    - "[退出条件2]"
  new_elements:
    - "[新引入的元素]"
  theme_connection: "[与核心主题的关联]"
```

## 验证清单

- [ ] 不打断核心节点的因果链
- [ ] 引入 ≥1 个新元素
- [ ] 与主线冲突有关联
- [ ] 有明确的进入和退出条件
- [ ] 删除此插槽后主线仍然成立
- [ ] 不与已有插槽内容重复

## 约束

- 新插槽不能改变核心节点的顺序
- 新插槽的退出状态必须兼容后续核心节点的前置条件
- 新元素必须与核心主题（自由 vs 系统）有关联
- 不能引入「万能解决方案」（deus ex machina）
