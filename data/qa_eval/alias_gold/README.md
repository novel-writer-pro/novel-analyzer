# Alias Gold

用途：承接 alias → canonical 的人工确认样本。

建议主文件：
- `aliases.jsonl`

建议字段：
- `branch_id`
- `canonical`
- `aliases`
- `confidence`
- `notes`

这个目录直接支撑：
- alias expansion 回归
- query understanding 的 entity grounding
- graph node merge / canonical 化核查
