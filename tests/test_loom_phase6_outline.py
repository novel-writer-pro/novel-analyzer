from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from novel_analyzer.services.project_compiler_service import ProjectCompilerService
from novel_analyzer.services.project_outline_service import ProjectOutlineService
from novel_analyzer.services.project_shell_service import ProjectShellService


def _make_svc(tmp_path: Path) -> tuple[ProjectShellService, ProjectOutlineService]:
    from unittest.mock import MagicMock
    from novel_analyzer.config.settings import Settings

    shell = ProjectShellService(base_dir=tmp_path)
    settings = MagicMock(spec=Settings)
    session = MagicMock()
    svc = ProjectOutlineService(
        settings=settings,
        session=session,
        base_dir=tmp_path,
        shell=shell,
    )
    return shell, svc


def _init_project(shell: ProjectShellService, slug: str, target_chapters: int = 3) -> None:
    shell.init(slug, source_branch_id="fake-branch", target_chapters=target_chapters)


def test_generate_outline_creates_file(tmp_path: Path) -> None:
    shell, svc = _make_svc(tmp_path)
    _init_project(shell, "demo")
    path = svc.generate_outline("demo", 1)
    assert path.exists()
    assert path.name == "ch001.outline.md"


def test_outline_has_6_sections(tmp_path: Path) -> None:
    shell, svc = _make_svc(tmp_path)
    _init_project(shell, "demo")
    path = svc.generate_outline("demo", 1)
    body = path.read_text(encoding="utf-8")
    h2_sections = re.findall(r"^## .+", body, re.MULTILINE)
    assert len(h2_sections) == 6, f"Expected 6 H2 sections, got {len(h2_sections)}: {h2_sections}"


def test_outline_has_h1_title(tmp_path: Path) -> None:
    shell, svc = _make_svc(tmp_path)
    _init_project(shell, "demo")
    path = svc.generate_outline("demo", 2)
    body = path.read_text(encoding="utf-8")
    h1_lines = [ln for ln in body.splitlines() if ln.startswith("# 第")]
    assert len(h1_lines) == 1
    assert "第2章" in h1_lines[0]


def test_outline_hook_type_explicit(tmp_path: Path) -> None:
    shell, svc = _make_svc(tmp_path)
    _init_project(shell, "demo")
    path = svc.generate_outline("demo", 1)
    body = path.read_text(encoding="utf-8")
    hook_lines = [ln for ln in body.splitlines() if "章末钩子类型:" in ln]
    assert len(hook_lines) == 1
    assert any(ht in hook_lines[0] for ht in ["悬念问句", "模棱两可话", "新威胁"])


def test_generate_storyboard_creates_file(tmp_path: Path) -> None:
    shell, svc = _make_svc(tmp_path)
    _init_project(shell, "demo")
    path = svc.generate_storyboard("demo", 1)
    assert path.exists()
    assert path.name == "ch001.storyboard.md"


def test_storyboard_has_beats(tmp_path: Path) -> None:
    shell, svc = _make_svc(tmp_path)
    _init_project(shell, "demo")
    path = svc.generate_storyboard("demo", 1)
    body = path.read_text(encoding="utf-8")
    beat_headers = re.findall(r"^## Beat #\d+:", body, re.MULTILINE)
    assert 3 <= len(beat_headers) <= 7, f"Expected 3-7 beats, got {len(beat_headers)}"


def test_storyboard_beat_has_required_fields(tmp_path: Path) -> None:
    shell, svc = _make_svc(tmp_path)
    _init_project(shell, "demo")
    path = svc.generate_storyboard("demo", 1)
    body = path.read_text(encoding="utf-8")
    required_fields = ["场所:", "POV:", "镜头类型:", "节奏标签:", "信息释放:", "内容草要:"]
    beat_pattern = re.compile(r"^## Beat #\d+:.*$", re.MULTILINE)
    beat_starts = [m.start() for m in beat_pattern.finditer(body)]
    assert beat_starts, "No beats found"
    for i, start in enumerate(beat_starts):
        end = beat_starts[i + 1] if i + 1 < len(beat_starts) else len(body)
        block = body[start:end]
        for field in required_fields:
            assert field in block, f"Beat #{i + 1} missing field '{field}'"


def test_generate_all_creates_both(tmp_path: Path) -> None:
    shell, svc = _make_svc(tmp_path)
    _init_project(shell, "demo", target_chapters=3)
    results = svc.generate_all("demo")
    assert len(results) == 3
    for outline_path, storyboard_path in results:
        assert outline_path.exists(), f"Missing outline: {outline_path}"
        assert storyboard_path.exists(), f"Missing storyboard: {storyboard_path}"
    outline_names = {r[0].name for r in results}
    storyboard_names = {r[1].name for r in results}
    assert outline_names == {"ch001.outline.md", "ch002.outline.md", "ch003.outline.md"}
    assert storyboard_names == {
        "ch001.storyboard.md",
        "ch002.storyboard.md",
        "ch003.storyboard.md",
    }


def test_compiler_reads_storyboard_beats(tmp_path: Path) -> None:
    shell, svc = _make_svc(tmp_path)
    _init_project(shell, "demo")
    svc.generate_storyboard("demo", 1)

    compiler = ProjectCompilerService(base_dir=tmp_path, shell=shell)
    flags = compiler.compile_for_chapter("demo", 1)
    assert len(flags.scene_beats) >= 3
    first = flags.scene_beats[0]
    assert first.index == 1
    assert first.title
    assert first.location
    assert first.pov
    assert first.lens_type
    assert first.rhythm_tag
    assert first.info_reveal
    assert first.summary
