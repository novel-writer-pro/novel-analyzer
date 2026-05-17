from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from novel_analyzer.config.settings import Settings
from novel_analyzer.services.project_outline_service import ProjectOutlineService
from novel_analyzer.services.project_shell_service import ProjectShellService


def _make_shell(tmp_path: Path) -> ProjectShellService:
    shell = ProjectShellService(base_dir=tmp_path)
    shell.init("e2e-demo", source_branch_id="fake-branch")
    return shell


def _make_settings() -> Settings:
    return MagicMock(spec=Settings)


def _make_session() -> MagicMock:
    return MagicMock()


def test_e2e_7_layer_pipeline_no_llm(tmp_path: Path) -> None:
    from novel_analyzer.services.project_macro_service import ProjectMacroService
    from novel_analyzer.services.project_characters_service import ProjectCharactersService
    from novel_analyzer.services.project_plot_service import ProjectPlotService
    from novel_analyzer.services.project_compiler_service import ProjectCompilerService
    from novel_analyzer.services.project_prose_service import ProjectProseService

    settings = _make_settings()
    session = _make_session()
    shell = _make_shell(tmp_path)
    slug = "e2e-demo"

    macro_svc = ProjectMacroService(settings=settings, session=session, base_dir=tmp_path)
    premise_path, world_path, _ = macro_svc.generate(slug, use_llm=False)
    assert premise_path.exists()
    assert world_path.exists()

    char_svc = ProjectCharactersService(session=session, base_dir=tmp_path)
    char_paths = char_svc.generate_initial_cards(slug, count=2, use_llm=False)
    assert len(char_paths) == 2

    plot_svc = ProjectPlotService(settings=settings, session=session, base_dir=tmp_path)
    arcs, goals, cont = plot_svc.generate_plot(slug, use_llm=False)
    assert arcs.exists()
    assert goals.exists()
    assert cont.exists()

    axes, innov, taboo, _ = plot_svc.generate_conflicts(slug, use_llm=False)
    assert axes.exists()
    assert innov.exists()
    assert taboo.exists()

    outline_svc = ProjectOutlineService(settings=settings, session=session, base_dir=tmp_path)
    pairs = outline_svc.generate_all(slug, use_llm=False)
    assert len(pairs) == 3
    for outline_path, storyboard_path in pairs:
        assert outline_path.exists()
        assert storyboard_path.exists()

    compiler = ProjectCompilerService(base_dir=tmp_path, shell=shell)
    flags = compiler.compile_for_chapter(slug, 1)
    assert flags.worldview_note or flags.worldview_note == ""
    assert isinstance(flags.scene_beats, list)

    prose_svc = ProjectProseService(settings=settings, session=session, base_dir=tmp_path)
    draft_paths = prose_svc.generate_all(slug, use_llm=False)
    assert len(draft_paths) == 3
    for dp in draft_paths:
        assert dp.exists()


def test_e2e_lock_prevents_overwrite(tmp_path: Path) -> None:
    shell = _make_shell(tmp_path)
    slug = "e2e-demo"

    shell.write_artifact(slug, "macro", "premise", "original content")
    shell.lock(slug, "macro/premise.md")

    from novel_analyzer.services.project_shell_service import ProjectArtifactLockedError
    with pytest.raises(ProjectArtifactLockedError):
        shell.write_artifact(slug, "macro", "premise", "new content")


def test_e2e_revise_creates_version(tmp_path: Path) -> None:
    shell = _make_shell(tmp_path)
    slug = "e2e-demo"

    shell.write_artifact(slug, "macro", "premise", "v1 content")
    fm1, _ = shell.read_artifact_with_frontmatter(slug, "macro", "premise")
    assert fm1.get("version") == 1

    shell.write_artifact(slug, "macro", "premise", "v2 content")
    fm2, body2 = shell.read_artifact_with_frontmatter(slug, "macro", "premise")
    assert fm2.get("version") == 2
    assert "v2 content" in body2


def test_e2e_compiler_env_vars_complete(tmp_path: Path) -> None:
    from novel_analyzer.services.project_compiler_service import ProjectCompilerService
    shell = _make_shell(tmp_path)
    slug = "e2e-demo"

    compiler = ProjectCompilerService(base_dir=tmp_path, shell=shell)
    flags = compiler.compile_for_chapter(slug, 1)
    env_vars = compiler.to_env_vars(flags)

    expected_keys = {
        "NOVEL_ANALYZER_LOOM_MEMORY_MODE",
        "NOVEL_ANALYZER_LOOM_TENSION_ENABLED",
        "NOVEL_ANALYZER_LOOM_PAIRWISE_ENABLED",
        "NOVEL_ANALYZER_LOOM_STYLE_ENABLED",
        "NOVEL_ANALYZER_LOOM_CHARACTER_ENABLED",
    }
    assert expected_keys == set(env_vars.keys())


def test_e2e_prose_env_scope_isolation(tmp_path: Path) -> None:
    import os
    from novel_analyzer.services.project_prose_service import ProjectProseService

    settings = _make_settings()
    session = _make_session()
    shell = _make_shell(tmp_path)
    slug = "e2e-demo"

    sentinel_key = "NOVEL_ANALYZER_LOOM_MEMORY_MODE"
    original = os.environ.get(sentinel_key)

    prose_svc = ProjectProseService(settings=settings, session=session, base_dir=tmp_path)
    prose_svc.generate_chapter(slug, 1, use_llm=False)

    after = os.environ.get(sentinel_key)
    assert after == original, (
        f"Env var {sentinel_key!r} was not restored: before={original!r}, after={after!r}"
    )


def test_e2e_satire_anti_slop_clean_draft(tmp_path: Path) -> None:
    from novel_analyzer.services.satire_anti_slop_service import SatireAntiSlopChecker
    from novel_analyzer.services.project_prose_service import ProjectProseService

    settings = _make_settings()
    session = _make_session()
    _make_shell(tmp_path)
    slug = "e2e-demo"

    prose_svc = ProjectProseService(settings=settings, session=session, base_dir=tmp_path)
    draft_path = prose_svc.generate_chapter(slug, 1, use_llm=False)

    draft_text = draft_path.read_text(encoding="utf-8")
    body_start = draft_text.find("\n---\n", 4)
    body = draft_text[body_start + 5:] if body_start != -1 else draft_text

    checker = SatireAntiSlopChecker()
    report = checker.check_text(body)
    assert report.verdict in ("pass", "warn"), (
        f"Template draft triggered anti-slop fail: {report.findings}"
    )
