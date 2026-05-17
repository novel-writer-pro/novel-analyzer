from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import yaml

from novel_analyzer.services.project_prose_service import ProjectProseService
from novel_analyzer.services.project_shell_service import ProjectShellService


def _setup_project(tmp_path: Path) -> ProjectShellService:
    shell = ProjectShellService(base_dir=tmp_path)
    shell.init("demo", source_branch_id="fake-branch")
    return shell


def _make_svc(tmp_path: Path) -> ProjectProseService:
    settings = MagicMock()
    session = MagicMock()
    return ProjectProseService(settings=settings, session=session, base_dir=tmp_path)


def test_generate_chapter_no_llm_creates_file(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    path = svc.generate_chapter("demo", 1, use_llm=False)
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "---" in content


def test_generate_chapter_frontmatter_has_loom_signals(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    path = svc.generate_chapter("demo", 1, use_llm=False)
    raw = path.read_text(encoding="utf-8")
    assert raw.startswith("---\n")
    end = raw.find("\n---\n", 4)
    fm = yaml.safe_load(raw[4:end]) or {}
    assert "loom_signals" in fm
    signals = fm["loom_signals"]
    assert isinstance(signals, dict)
    for key in ("tension_score", "chapter_quality_score", "style_drift_score",
                "hook_density", "dialogue_voice_consistency", "reader_sim_overall"):
        assert key in signals


def test_generate_chapter_frontmatter_has_verdict(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    path = svc.generate_chapter("demo", 1, use_llm=False)
    raw = path.read_text(encoding="utf-8")
    end = raw.find("\n---\n", 4)
    fm = yaml.safe_load(raw[4:end]) or {}
    assert "final_verdict" in fm
    assert "stop_reason" in fm
    assert "anti_slop_verdict" in fm
    assert "lock_contract_verdict" in fm


def test_generate_all_creates_3_drafts(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    paths = svc.generate_all("demo", use_llm=False)
    assert len(paths) == 3
    for p in paths:
        assert p.exists()
        assert p.suffix == ".md"


def test_env_scope_restored_after_generate(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    env_key = "NOVEL_ANALYZER_LOOM_MEMORY_MODE"
    original = "sentinel_value_xyz"
    import os
    os.environ[env_key] = original
    try:
        svc.generate_chapter("demo", 1, use_llm=False)
        assert os.environ.get(env_key) == original
    finally:
        os.environ.pop(env_key, None)


def test_fast_mode_still_creates_file(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    svc = _make_svc(tmp_path)
    path = svc.generate_chapter("demo", 1, use_llm=False, fast_mode=True)
    assert path.exists()
    raw = path.read_text(encoding="utf-8")
    assert "---" in raw
