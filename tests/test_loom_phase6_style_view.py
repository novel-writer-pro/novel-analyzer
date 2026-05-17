from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from novel_analyzer.services.project_shell_service import ProjectShellService
from novel_analyzer.services.project_style_view_service import ProjectStyleViewService


def _setup_project(tmp_path: Path, slug: str = "demo") -> ProjectShellService:
    shell = ProjectShellService(base_dir=tmp_path)
    shell.init(slug, source_branch_id="fake-branch", source_chapters_for_style=[1, 2, 3])
    return shell


def test_generate_fingerprint_empty_chapters(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    session = MagicMock()
    svc = ProjectStyleViewService(session=session, base_dir=tmp_path)
    with patch.object(svc, "_compute_chapter_metrics", side_effect=Exception("no data")):
        result = svc.generate_fingerprint("demo")
    assert result["chapters_analyzed"] == 0


def test_generate_fingerprint_writes_markdown(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    session = MagicMock()
    svc = ProjectStyleViewService(session=session, base_dir=tmp_path)
    metrics = {"style_drift_score": 0.1, "hook_density": 2.0, "climax_score": 0.5}
    with patch.object(svc, "_compute_chapter_metrics", return_value=metrics):
        svc.generate_fingerprint("demo")
    md_path = tmp_path / "demo" / "style" / "fingerprint.md"
    assert md_path.exists()
    assert "## 风格向量" in md_path.read_text(encoding="utf-8")


def test_generate_fingerprint_writes_heuristics_json(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    session = MagicMock()
    svc = ProjectStyleViewService(session=session, base_dir=tmp_path)
    metrics = {"style_drift_score": 0.1, "hook_density": 2.0, "climax_score": 0.5}
    with patch.object(svc, "_compute_chapter_metrics", return_value=metrics):
        svc.generate_fingerprint("demo")
    json_path = tmp_path / "demo" / "style" / "heuristics.json"
    assert json_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert "chapters_analyzed" in data
    assert "median_style_drift" in data


def test_generate_fingerprint_aggregates_median(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    session = MagicMock()
    svc = ProjectStyleViewService(session=session, base_dir=tmp_path)
    side_effects = [
        {"style_drift_score": 0.1, "hook_density": 1.0, "climax_score": 0.4},
        {"style_drift_score": 0.2, "hook_density": 2.0, "climax_score": 0.5},
        {"style_drift_score": 0.3, "hook_density": 3.0, "climax_score": 0.6},
    ]
    with patch.object(svc, "_compute_chapter_metrics", side_effect=side_effects):
        result = svc.generate_fingerprint("demo")
    assert result["chapters_analyzed"] == 3
    assert result["median_style_drift"] == pytest.approx(0.2, abs=1e-4)


def test_render_fingerprint_md_has_required_sections(tmp_path: Path) -> None:
    _setup_project(tmp_path)
    session = MagicMock()
    svc = ProjectStyleViewService(session=session, base_dir=tmp_path)
    heuristics = {
        "slug": "demo",
        "branch_id": "fake-branch",
        "chapters_analyzed": 2,
        "median_style_drift": 0.1,
        "median_hook_density": 1.5,
        "median_climax_score": 0.4,
    }
    md = svc._render_fingerprint_md(heuristics)
    h2_sections = [line for line in md.splitlines() if line.startswith("## ")]
    assert len(h2_sections) == 3
