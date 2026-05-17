# Session Handoff — 2026-05-17

> 接手人速读：本文档是 2026-05-16/17 跨夜会话的完整交接。
> 上一棒：[`session-handoff-20260516.md`](./session-handoff-20260516.md)

---

## 0. 环境状态（接手即可用）

| 项 | 值 |
|---|---|
| 分支 | `build` |
| 最新 commit | `fbccd69 fix(imitation): also strip marketing tags from source_text first line` |
| 本会话 commits | 31 个（`7e1a15c` → `fbccd69`） |
| 数据库 | PostgreSQL 17.5 @ 127.0.0.1:5432 / d2 / novel_analyzer（43 novels / 40 branches / 363k graph_edges） |
| LLM | `claude-haiku-4.5` @ `http://34.97.18.233:65432/v1`，rps=1.5 / bucket=3 |
| Embedding | ONNX bge-m3 INT8 @ `/home/user/migrate/bge-m3-onnx-int8/` |
| Rerank | ONNX bge-reranker-v2-m3 @ `.cache/rerank-models/` |
| Loom mode | `ab`（50/50 A/B split，已在 `.env.local` 启用） |
| 测试 | 715/718 pass（3 个 pre-existing 环境依赖失败） |

---

## 1. 本会话核心交付

### 1.1 Scaffold 污染三层修复（最重要）

原始问题：同题材 baseline 0/307 pass → prompt 修复后 Stage A 3/5 (60%)，但仍有大量 scaffold 污染。

| 层 | 根因 | 修复 commit | 验证 |
|---|---|---|---|
| **L1 JSON 解析** | `chapter_imitation_service._extract_json_payload` 裸 `json.loads`，LLM 返回含 trailing comma / unicode 引号时 3 次全失败 | `984c9c9` | Stage B: 20→25/30 pass (66%→83%) |
| **L2 标题污染** | `source_title` 含 `（求收藏，求追读）` 嵌入 JSON 模板，LLM 返回纯文本 | `f130eb3` | Stage B2 scaffold 5/30 → 预期 ≤2/30 |
| **L3 正文标题污染** | `source_text` 第一行含同样标签，LLM 仍返回纯文本 | `fbccd69` | Stage C 部分验证（34 章，修复前基线） |

**Stage C 修复前基线**（34/100 章，已停止）：pass=24/34 (70%)，scaffold=10/34 (29%)。
**预期修复后**：scaffold 率降至 <5%，pass rate ≥85%。

### 1.2 其他交付

| 功能 | commit | 状态 |
|---|---|---|
| Reader Panel（4 persona × 7 dim + comfort_score soft gate + revise_with_panel_feedback） | `62e2db2` `5a0eb94` `3d78cc6` | ✅ 完成，13 个测试 |
| T7 FActScore-lite shadow mode（qa_service） | `f067d90` | ✅ 完成 |
| B5 Elo（DB table + ORM + loom-elo CLI） | `76a3bae` `ea8761b` | ✅ 完成 |
| B2 relationship route（retrieval pipeline） | `1ff9a11` | ✅ 完成，21 个测试 |
| Loom Phase 3 P1（ab mode + pairwise enabled） | `.env.local` | ✅ 完成 |
| WSGI fallback 退役 | `e5975d0` | ✅ 完成 |
| PG 运维速查手册 | `96966a5` | ✅ 完成 |
| source_path relink | `2045992` | ✅ 完成 |

---

## 2. 待办（下一棒）

| 优先级 | 项 | 备注 |
|---|---|---|
| **P0** | **Stage C 重跑（含三层修复）** | 用新代码跑 100 章，验证 scaffold <5%，pass ≥85%。命令见下方 |
| P1 | T2.5 Helicone 启动 | GitHub 网络不通，clone 超时。需网络恢复后手动执行 |
| P2 | Stage B re-run（含三层修复） | 30 章，验证 scaffold 率降至 <5% |
| P3 | T5 Loom A/B | 20h LLM 预算，runbook 已就绪 |
| P3 | T8 Persona correlation | reader_feedback 需 ≥30 行（当前 6 行） |

### Stage C 重跑命令

```bash
cd /home/user/novel-analyzer
nohup bash -c 'set -a && source .env.local && set +a && timeout 28800 .venv/bin/python -m novel_analyzer.cli.app writer-imitate-range 72da24e9-e65c-45a9-836d-957c4ae783ec \
  "2:二姑卫荭" "3:养生功法" "4:珍惜眼下" "5:婚事敲定" "6:郑国官兵" "7:不入祠堂" "8:私房钱" "9:逼上绝境" "10:抬起头来" "11:脱去奴籍" \
  "12:老爷改性了" "13:改籍单武举" "14:养生功大成" "15:单武举的教导" "16:武学奇才" "17:无根浮萍" "18:四粒银豆子" "19:虎鹤双形拳" "20:命格妙用" "21:单家子女" \
  "22:卫图的拒绝" "23:参加武举" "24:县试第七" "25:近乡情怯" "26:武举考试" "27:富在深山有远亲" "28:贪财好利" "29:我师举人" "30:料峭春风" "31:贿赂县令" \
  "32:较试猫腻" "33:县试魁首" "34:府衙来人" "35:武道大派" "36:四人结盟" "37:卫某不过一介马倌" "38:榜单名次" "39:重回青山县" "40:不同境遇" "41:彩霞的决定" \
  "42:忘恩之人" "43:改换武籍" "44:武官任命" "45:薛都长老" "46:子嗣问题" "47:两年时间" "48:隔空拳劲" "49:练劲入髓" "50:庸碌之人" "51:铁锤巨汉" \
  "52:战场发财" "53:仙道功法" "54:心存异志" "55:四人重聚" "56:拿出功法" "57:三大盟约" "58:抵足而眠" "59:刻意放水" "60:西门守备" "61:修仙进度" \
  "62:单家联姻" "63:师父将死" "64:单芳算盘" "65:临终安排" "66:厚土真气" "67:仙缘在身" "68:小蚀日功" "69:丹丘仙家" "70:先天境界" "71:放弃寇良" \
  "72:广元贼寇" "73:情分有终" "74:叛军围城" "75:仙家中人" "76:上架感言" "77:仙师大战趁乱跑路" "78:生死之交莫名仇恨" "79:四个收获进入丹丘山坊市" "80:四个收获进入丹丘山坊市" "81:冰玄锁神符" \
  "82:新三大盟约丹丘山小市集" "83:新三大盟约丹丘山小市集" "84:奴家习惯了" "85:奴家习惯了" "86:傅志舟的离去" "87:积善之家必有余庆" "88:积善之家必有余庆" "89:吞服地元丹符师争执" "90:一阶符师前往世俗" "91:路遇劫修" \
  "92:练气四层寇红缨的请求" "93:练气四层寇红缨的请求" "94:小春秋功傅志舟的斩俗缘" "95:小春秋功傅志舟的斩俗缘" "96:灵武合一符屋摊主的威胁" "97:灵武合一符屋摊主的威胁" "98:租赁洞府再见巫仙师" "99:地磁灵体韦飞的仙缘" "100:今日合该庆贺" "101:青萝郡主" \
  --output-dir /tmp/stage-c-fixed --use-llm --max-rounds 2 > /tmp/stage-c-fixed.log 2>&1' > /tmp/stage-c-fixed-launch.log 2>&1 &
disown
```

---

## 3. 不做（理由记录）

- **Graph-aware rerank**：章节级 retrieval rerank 已在线，graph_signals 候选量小，没有 measurable 噪音报告。上 Helicone trace 拿数据再决策。
- **Embedding INT8 → fp32**：INT8 已验证 1024 维，基线 R@5=0.81/0.84 未掉点。
- **T2.5 Helicone**：GitHub 网络不通，clone 超时。

---

## 4. 本会话 commit 列表（31 commits）

```
fbccd69 fix(imitation): also strip marketing tags from source_text first line
f130eb3 fix(imitation): strip marketing tags from chapter title before building LLM prompt
8a31780 docs(changelog): add Stage B2 results + title fix + Loom ab mode + B2 route entries
31fd98f docs: final session handoff v0.3 + CHANGELOG with B2/Stage-B/JSON-fix entries
1ff9a11 feat(retrieval): B2 — add relationship_route to retrieval pipeline
0ffa176 fix(imitation): fix NameError in _extract_json_payload
c0880b1 docs(changelog): consolidate all 2026-05-16 session changelists
984c9c9 fix(imitation): replace bare json.loads with robust JSON parser
ea8761b feat(cli): B5 Elo — add loom-elo command
76a3bae feat(db): B5 Elo — add loom_pairwise_evaluations table + ORM model
aa9daca docs(capability-matrix): update reader-panel row
f067d90 feat(qa): T7 FActScore-lite shadow mode in answer_question
4fb3c97 feat(reader-panel): reader-panel-stats CLI for batch evaluation
b85192c feat(reader-panel): render comfort_score + dimensions + targeted_revisions in MD
7728877 docs(reader-panel): update handoff with Phase B end-to-end evidence
fdb2489 test(reader-panel): add tests for revise_with_panel_feedback
3d78cc6 feat(reader-panel): wire revise_with_panel_feedback into harness loop
d32f19a feat(reader-panel): add build_panel_driven_revision_prompt
7884cc8 docs(reader-panel): handoff doc + cross-links
92c74fb docs(reader-panel): add reader panel handoff doc with Stage A evidence
d94608d docs(handoff): update 2026-05-16 session handoff with final state
dbc808d fix(tests): fix enable_reader_panel kwarg + update CHANGELOG
5a0eb94 feat(imitation): add 4-persona reader panel with comfort_score soft gate
62e2db2 feat(reader-panel): 4-persona × 7-dimension LLM reader evaluation service
bb5ca75 docs(changelog): consolidate 2026-05-16 session changelist entries
6ca0750 fix(tests): fix 6 pre-existing test failures + retire dead WSGI contract tests
484118a feat(llm): enforce 4000 max_tokens cap on deepseek-* models
e5975d0 refactor(api): retire WSGI dispatch
96966a5 docs(ops): postgres ops cheatsheet + 2026-05-16 session handoff
2045992 chore(data): relink novel_sources.source_path via SHA256 dedup
7e1a15c feat(llm): claude-haiku-4.5 + shared token-bucket rate limiter
```

---

## 5. 修订记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0 | 2026-05-17 | 初版，跨夜会话完整收尾 |
