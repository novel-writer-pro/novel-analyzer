from __future__ import annotations

import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from novel_analyzer.domain.project_config import (
    ProjectConfig,
    LoomFlagsConfig,
    default_config,
    load_book_config,
    save_book_config,
)
from novel_analyzer.services.project_shell_service import (
    ProjectArtifactLockedError,
    ProjectShellService,
)


@pytest.fixture()
def tmp_base(tmp_path: Path) -> Path:
    return tmp_path / "projects"


@pytest.fixture()
def svc(tmp_base: Path) -> ProjectShellService:
    return ProjectShellService(base_dir=tmp_base)


def test_project_config_round_trip(tmp_base: Path) -> None:
    cfg = ProjectConfig(
        name="My Novel",
        slug="my-novel",
        source_branch_id="branch-abc-123",
        target_chapters=5,
    )
    save_book_config(cfg, tmp_base)
    loaded = load_book_config("my-novel", tmp_base)
    assert loaded.name == cfg.name
    assert loaded.slug == cfg.slug
    assert loaded.source_branch_id == cfg.source_branch_id
    assert loaded.target_chapters == cfg.target_chapters
    assert loaded.loom_flags.memory_mode == "enabled"
    assert loaded.gates == cfg.gates
    assert loaded.auto_pass == cfg.auto_pass


def test_project_config_slug_invalid() -> None:
    with pytest.raises(ValidationError):
        ProjectConfig(name="x", slug="Bad Slug!", source_branch_id="b")


def test_project_config_slug_invalid_uppercase() -> None:
    with pytest.raises(ValidationError):
        ProjectConfig(name="x", slug="MyProject", source_branch_id="b")


def test_project_config_source_branch_id_required() -> None:
    with pytest.raises(ValidationError):
        ProjectConfig(name="x", slug="valid-slug")


def test_shell_service_init_creates_dirs_and_files(svc: ProjectShellService, tmp_base: Path) -> None:
    cfg = svc.init("my-proj", "branch-001")
    assert cfg.slug == "my-proj"
    project_dir = tmp_base / "my-proj"
    for subdir in ("style", "macro", "characters", "plot", "conflicts", "chapters", "runs"):
        assert (project_dir / subdir).is_dir(), f"missing subdir: {subdir}"
    assert (project_dir / "book.config.yaml").exists()
    assert (project_dir / "locked.yaml").exists()


def test_write_and_read_artifact(svc: ProjectShellService) -> None:
    svc.init("proj1", "branch-x")
    svc.write_artifact("proj1", "macro", "world", "Hello world content")
    body = svc.read_artifact("proj1", "macro", "world")
    assert body == "Hello world content"


def test_version_archiving(svc: ProjectShellService, tmp_base: Path) -> None:
    svc.init("proj2", "branch-y")
    svc.write_artifact("proj2", "macro", "world", "v1 content")
    svc.write_artifact("proj2", "macro", "world", "v2 content")

    body = svc.read_artifact("proj2", "macro", "world")
    assert body == "v2 content"

    versions = svc.list_versions("proj2", "macro", "world")
    assert len(versions) == 1
    assert versions[0].version == 1
    archived_body = versions[0].path.read_text(encoding="utf-8")
    assert "v1 content" in archived_body


def test_lock_and_is_locked(svc: ProjectShellService) -> None:
    svc.init("proj3", "branch-z")
    svc.write_artifact("proj3", "plot", "outline", "some plot")
    svc.lock("proj3", "plot/outline.md")
    assert svc.is_locked("proj3", "plot/outline.md") is True


def test_write_locked_artifact_raises(svc: ProjectShellService) -> None:
    svc.init("proj4", "branch-w")
    svc.write_artifact("proj4", "plot", "outline", "initial")
    svc.lock("proj4", "plot/outline.md")
    with pytest.raises(ProjectArtifactLockedError):
        svc.write_artifact("proj4", "plot", "outline", "overwrite attempt")


def test_list_locked_assertions(svc: ProjectShellService) -> None:
    svc.init("proj5", "branch-v")
    svc.write_artifact(
        "proj5", "macro", "world", "content",
        lock_assertions=["no dragons", "medieval setting"],
    )
    svc.lock("proj5", "macro/world.md")
    assertions = svc.list_locked_assertions("proj5")
    assert "no dragons" in assertions
    assert "medieval setting" in assertions


def test_apply_loom_flags_sets_and_restores_env(svc: ProjectShellService, tmp_base: Path) -> None:
    svc.init("proj6", "branch-u")

    original_memory = os.environ.get("NOVEL_ANALYZER_LOOM_MEMORY_MODE")
    original_tension = os.environ.get("NOVEL_ANALYZER_LOOM_TENSION_ENABLED")

    with svc.apply_loom_flags("proj6"):
        assert os.environ["NOVEL_ANALYZER_LOOM_MEMORY_MODE"] == "enabled"
        assert os.environ["NOVEL_ANALYZER_LOOM_TENSION_ENABLED"] == "true"
        assert os.environ["NOVEL_ANALYZER_LOOM_PAIRWISE_ENABLED"] == "true"
        assert os.environ["NOVEL_ANALYZER_LOOM_STYLE_ENABLED"] == "true"
        assert os.environ["NOVEL_ANALYZER_LOOM_CHARACTER_ENABLED"] == "true"

    assert os.environ.get("NOVEL_ANALYZER_LOOM_MEMORY_MODE") == original_memory
    assert os.environ.get("NOVEL_ANALYZER_LOOM_TENSION_ENABLED") == original_tension


def test_apply_loom_flags_restores_on_exception(svc: ProjectShellService) -> None:
    svc.init("proj7", "branch-t")
    os.environ["NOVEL_ANALYZER_LOOM_MEMORY_MODE"] = "shadow"
    try:
        with pytest.raises(RuntimeError):
            with svc.apply_loom_flags("proj7"):
                raise RuntimeError("boom")
        assert os.environ.get("NOVEL_ANALYZER_LOOM_MEMORY_MODE") == "shadow"
    finally:
        os.environ.pop("NOVEL_ANALYZER_LOOM_MEMORY_MODE", None)
