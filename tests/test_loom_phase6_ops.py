from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from novel_analyzer.cli.app import app
from novel_analyzer.services.project_shell_service import ProjectShellService

runner = CliRunner()


@pytest.fixture()
def tmp_base(tmp_path: Path) -> Path:
    return tmp_path / "projects"


@pytest.fixture()
def svc(tmp_base: Path) -> ProjectShellService:
    return ProjectShellService(base_dir=tmp_base)


@pytest.fixture()
def project(svc: ProjectShellService) -> ProjectShellService:
    svc.init("demo", source_branch_id="branch-001")
    return svc


def test_lock_command_writes_locked_yaml(project: ProjectShellService, tmp_base: Path) -> None:
    project.write_artifact("demo", "macro", "premise", "Some premise content")

    with patch(
        "novel_analyzer.services.project_shell_service.ProjectShellService.__init__",
        lambda self: setattr(self, "_base_dir", tmp_base) or None,
    ):
        result = runner.invoke(app, ["imitate-project", "lock", "demo", "macro/*.md"])

    assert result.exit_code == 0, result.output
    assert "Locked" in result.output

    locked_path = tmp_base / "demo" / "locked.yaml"
    assert locked_path.exists()
    content = locked_path.read_text(encoding="utf-8")
    assert "macro/premise.md" in content


def test_revise_creates_v2(project: ProjectShellService, tmp_base: Path) -> None:
    project.write_artifact("demo", "macro", "premise", "Original premise")

    with patch(
        "novel_analyzer.services.project_shell_service.ProjectShellService.__init__",
        lambda self: setattr(self, "_base_dir", tmp_base) or None,
    ):
        result = runner.invoke(
            app,
            ["imitate-project", "revise", "demo", "macro", "--feedback", "Make it darker"],
        )

    assert result.exit_code == 0, result.output
    assert "v2" in result.output

    fm, body = project.read_artifact_with_frontmatter("demo", "macro", "premise")
    assert fm.get("version") == 2
    assert "Make it darker" in body

    versions = project.list_versions("demo", "macro", "premise")
    assert len(versions) == 1
    assert versions[0].version == 1


def test_diff_no_previous_versions(project: ProjectShellService, tmp_base: Path) -> None:
    project.write_artifact("demo", "macro", "premise", "Only version")

    with patch(
        "novel_analyzer.services.project_shell_service.ProjectShellService.__init__",
        lambda self: setattr(self, "_base_dir", tmp_base) or None,
    ):
        result = runner.invoke(app, ["imitate-project", "diff", "demo", "macro"])

    assert result.exit_code == 0, result.output
    assert "No previous versions found" in result.output


def test_diff_with_previous_version(project: ProjectShellService, tmp_base: Path) -> None:
    project.write_artifact("demo", "macro", "premise", "Version one content")
    project.write_artifact("demo", "macro", "premise", "Version two content")

    with patch(
        "novel_analyzer.services.project_shell_service.ProjectShellService.__init__",
        lambda self: setattr(self, "_base_dir", tmp_base) or None,
    ):
        result = runner.invoke(app, ["imitate-project", "diff", "demo", "macro"])

    assert result.exit_code == 0, result.output
    assert "---" in result.output


def test_status_shows_stages(project: ProjectShellService, tmp_base: Path) -> None:
    import novel_analyzer.domain.project_config as _pc

    project.write_artifact("demo", "style", "fingerprint", "Style fingerprint data")
    _real_load = _pc.load_book_config

    with patch(
        "novel_analyzer.services.project_shell_service.ProjectShellService.__init__",
        lambda self: setattr(self, "_base_dir", tmp_base) or None,
    ):
        with patch.object(_pc, "load_book_config", lambda slug, base_dir=None: _real_load(slug, tmp_base)):
            result = runner.invoke(app, ["imitate-project", "status", "demo"])

    assert result.exit_code == 0, result.output
    assert "style/fingerprint" in result.output
    assert "demo" in result.output


def test_run_fast_mode_no_gate_stop(project: ProjectShellService, tmp_base: Path) -> None:
    import novel_analyzer.domain.project_config as _pc

    _real_load = _pc.load_book_config

    with patch.object(_pc, "load_book_config", lambda slug, base_dir=None: _real_load(slug, tmp_base)):
        with patch("builtins.input") as mock_input:
            result = runner.invoke(
                app, ["imitate-project", "run", "demo", "--until", "macro", "--fast"]
            )

    assert result.exit_code == 0, result.output
    mock_input.assert_not_called()
    assert "Completed up to: macro" in result.output
