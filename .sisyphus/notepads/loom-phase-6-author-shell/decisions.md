## [2026-05-17] Decisions

### Operating Contract (per user directive 2026-05-17)

Every task **must** follow this 4-step rhythm:

1. **Roadmap reference** — At task start, cite the Loom roadmap item this task contributes to.
   - Phase 6 itself is the new roadmap item (slot it into `docs/loom/roadmap.md` in T13).
   - Cross-reference: `docs/loom/handoff.md`, `docs/loom/roadmap.md`, plus the plan at `.sisyphus/plans/loom-phase-6-author-shell.md`.
2. **Checklist** — Before coding, write the task-specific checklist (sub-steps + AC) into the notepad.
3. **Changelog** — As work progresses (especially fixes/experiments), append entries to `CHANGELOG.md` under a Phase 6 header.
4. **Commit** — At the end of each task (or each logical batch within a task), commit with **Lore protocol trailers** (Constraint / Tested / Not-tested / Directive / Confidence).
   - Pre-commit gate: `ruff check && mypy --strict && pytest tests/test_loom_phase[1-6]*.py tests/test_imitation*.py -q`

### LLM Model
- **User-specified**: `minimaxai/minimax-m2.7`
- Set via `NOVEL_ANALYZER_LLM_MODEL_NAME` env var
- Code MUST NOT hardcode this string; pass through `Settings.llm_model_name`
- T12 MVP evidence must record actual model used

### Project Shell Conventions
- All artifacts → `output/projects/<slug>/`
- frontmatter via PyYAML
- Loom feature flags via contextmanager (no global env pollution)
- Tests at `tests/test_loom_phase6_*.py`
- Per-project model override (book.config.yaml `llm_model_name`) is OUT-OF-MVP unless time permits

### Settings.py Reference (already discovered)
- `loom_memory_mode` defaults to `shadow` — Phase 6 ProjectConfig defaults to `enabled` (project shell explicit opt-in)
- 5 Loom flags already in Settings: `loom_memory_mode / loom_tension_enabled / loom_pairwise_enabled / loom_style_enabled / loom_character_enabled`
- Plus 2 tunables we'll inherit: `loom_episodic_top_k=20`, `loom_tension_lookback_n=3`
