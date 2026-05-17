# Loom Phase 6 — Author Project Shell Runbook

> Quick reference for creating a new imitation project from a source novel.

## Prerequisites
- Source novel `.txt` file
- Running PostgreSQL + LLM provider configured in `.env.local`
- `NOVEL_ANALYZER_LLM_MODEL_NAME=minimaxai/minimax-m2.7` (or your preferred model)

## Step 1: Ingest source novel

```bash
.venv/bin/novel-analyzer auto-run /path/to/novel.txt --max-chapters 30
# Note the branch_id from output
```

## Step 2: Initialize project

```bash
.venv/bin/novel-analyzer imitate-project init <slug> --source-branch <branch_id>
# Creates output/projects/<slug>/
```

## Step 3: Generate layers (or run all at once)

```bash
# Option A: step by step (recommended for first run)
.venv/bin/novel-analyzer imitate-project fingerprint <slug>
.venv/bin/novel-analyzer imitate-project macro <slug> --use-llm
.venv/bin/novel-analyzer imitate-project characters <slug> --use-llm
.venv/bin/novel-analyzer imitate-project plot <slug> --use-llm
.venv/bin/novel-analyzer imitate-project conflicts <slug> --use-llm
.venv/bin/novel-analyzer imitate-project outline <slug> --use-llm
.venv/bin/novel-analyzer imitate-project storyboard <slug> --use-llm

# Option B: one-shot (fast mode, no gate stops)
.venv/bin/novel-analyzer imitate-project run <slug> --until prose --fast --use-llm
```

## Step 4: Review and edit

- Open `output/projects/<slug>/` in your editor
- Edit any markdown file directly
- Lock approved artifacts: `.venv/bin/novel-analyzer imitate-project lock <slug> macro/*.md`
- Revise with feedback: `.venv/bin/novel-analyzer imitate-project revise <slug> macro --feedback "more satirical"`

## Step 5: Generate prose

```bash
.venv/bin/novel-analyzer imitate-project prose <slug> --all --use-llm
# Output: output/projects/<slug>/chapters/ch001.draft.md etc.
```

## Validate with Loom

```bash
.venv/bin/novel-analyzer loom-status --branch-id <branch_id>
.venv/bin/novel-analyzer loom-reference-eval <branch_id> 0 output/projects/<slug>/chapters/
```
