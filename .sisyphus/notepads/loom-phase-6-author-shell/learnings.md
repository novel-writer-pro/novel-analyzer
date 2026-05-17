## [2026-05-17] Session ses_1ccc68bacffevjKAzMF8AN7ZTb — Start

### Architecture Conventions
- Loom feature flags are env vars: NOVEL_ANALYZER_LOOM_MEMORY_MODE / LOOM_TENSION_ENABLED / LOOM_PAIRWISE_ENABLED / LOOM_STYLE_ENABLED / LOOM_CHARACTER_ENABLED
- ProjectConfig.loom_flags must use contextmanager to scope env vars (no global pollution)
- All project artifacts go to output/projects/<slug>/ — never to DB
- markdown frontmatter uses PyYAML (already in deps)
- Typer subgroup pattern: see existing @app.command() in cli/app.py
- node_type in graph is "entity" not "character", "world_rule" not "rule" (see loom/handoff.md §3)
- chunk_order starts at 1 not 0 (fixed bug in loom, don't repeat)

### Loom Service Interfaces (do not modify)
- memory_assembler_service.assemble(branch_id, chapter_idx) → carry_over_state with _legacy_compat
- style_calibration_service.compute_style_drift(branch_id, chapter_index) → StyleDriftResult
- rhythm_analysis_service.compute(branch_id, chapter_index) → RhythmSignal
- character_agent_service.build_character_persona(branch_id, character_name) → CharacterPersona
- character_agent_service.check_character_consistency(persona, draft_text, chapter_index) → CharacterConsistencySignal
- imitation_harness_service.harness_imitation(...) — main prose generation entry

### RAG Library Paths
- rag/worldview-dossiers/ — T5 macro outputs here
- rag/trope-library/ — T7 conflicts outputs here
- rag/audience-expectation-notes/ — T4 style snippets output here

## T6 — ProjectCharactersService (CharacterPersona ↔ markdown bridge)

- CharacterPersona fields: character_id, branch_id, built_at_chapter, behavior_labels, episodic_anchors, relationship_network, speech_style_vector, chapter_appearances. No values/goals/fears fields — those are placeholder-only in cards.
- speech_style_vector is numeric (list[float]), not text; rendered as dimension count in markdown.
- _parse_h2_section() copied locally (same pattern as project_compiler_service.py) to avoid cross-service import.
- write_artifact() auto-adds stage/version/locked/generated_at frontmatter; name/character_map_key must be added separately if needed — current impl relies on shell defaults.
- inherit_from_source() requires as_of_chapter param for build_character_persona(); used 0 as safe default.
- markdown_to_persona() returns None when both behavior_labels and relationship_network are empty (insufficient data guard).
- 166 Loom phase tests pass (zero regression).
