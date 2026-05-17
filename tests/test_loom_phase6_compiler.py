"""Tests for ProjectCompilerService (Loom Phase 6 T3)."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from novel_analyzer.services.project_compiler_service import (
    Beat,
    CompiledFlags,
    ProjectCompilerService,
)
from novel_analyzer.services.project_shell_service import ProjectShellService


def _setup_project(
    tmp_path: Path, slug: str = "demo"
) -> tuple[ProjectShellService, ProjectCompilerService]:
    shell = ProjectShellService(base_dir=tmp_path)
    shell.init(slug, source_branch_id="fake-branch")
    compiler = ProjectCompilerService(base_dir=tmp_path, shell=shell)
    return shell, compiler


def _write_md(
    tmp_path: Path,
    slug: str,
    stage: str,
    name: str,
    body: str,
    frontmatter: dict | None = None,
) -> None:
    fm = frontmatter or {
        "stage": stage,
        "version": 1,
        "parents": [],
        "locked": False,
        "lock_assertions": [],
        "generated_at": "2026-05-17T00:00:00Z",
    }
    fm_text = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False)
    path = tmp_path / slug / stage / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{fm_text}---\n{body}", encoding="utf-8")


def test_compile_empty_project(tmp_path: Path) -> None:
    _, compiler = _setup_project(tmp_path)
    flags = compiler.compile_for_chapter("demo", 1)
    assert flags.trope_axes == []
    assert flags.worldview_note == ""
    assert flags.loom_memory_mode == "enabled"
    assert flags.loom_tension_enabled is True


def test_compile_trope_axes(tmp_path: Path) -> None:
    _, compiler = _setup_project(tmp_path)
    _write_md(
        tmp_path,
        "demo",
        "conflicts",
        "axes",
        "- 底层逆袭\n- 账本修仙\n- 阶层跃迁\n",
    )
    flags = compiler.compile_for_chapter("demo", 1)
    assert flags.trope_axes == ["底层逆袭", "账本修仙", "阶层跃迁"]


def test_compile_worldview_note(tmp_path: Path) -> None:
    _, compiler = _setup_project(tmp_path)
    _write_md(
        tmp_path,
        "demo",
        "macro",
        "world",
        "## 世界观底座\n这是一个商品化讽刺世界。\n",
    )
    flags = compiler.compile_for_chapter("demo", 1)
    assert "商品化" in flags.worldview_note


def test_compile_rule_overrides(tmp_path: Path) -> None:
    _, compiler = _setup_project(tmp_path)
    body = "## 规则\n- rule1\n- rule2\n## 力量\n- 内力=精神力\n"
    _write_md(tmp_path, "demo", "macro", "world", body)
    flags = compiler.compile_for_chapter("demo", 1)
    assert flags.rule_overrides == ["rule1", "rule2"]


def test_compile_world_map(tmp_path: Path) -> None:
    _, compiler = _setup_project(tmp_path)
    body = "## 名词映射\n| 原 | 新 |\n|---|---|\n| 郑国 | 星际联邦 |\n"
    _write_md(tmp_path, "demo", "macro", "world", body)
    flags = compiler.compile_for_chapter("demo", 1)
    assert flags.world_map.get("郑国") == "星际联邦"


def test_compile_target_goal(tmp_path: Path) -> None:
    _, compiler = _setup_project(tmp_path)
    body = "# 第一章 测试\n## 本章目标\n主角出场\n## 主冲突\nx\n"
    _write_md(tmp_path, "demo", "chapters", "ch001.outline", body)
    flags = compiler.compile_for_chapter("demo", 1)
    assert "第一章" in flags.target_goal
    assert "主角出场" in flags.target_goal


def test_compile_scene_beats(tmp_path: Path) -> None:
    _, compiler = _setup_project(tmp_path)
    body = """## Beat #1: 开场
location: 茶馆
pov: 张羽
lens: 内心独白
rhythm: 平庸setup

## Beat #2: 转折
location: 街角
pov: 张羽
lens: 对话
rhythm: 讽刺反转
"""
    _write_md(tmp_path, "demo", "chapters", "ch001.storyboard", body)
    flags = compiler.compile_for_chapter("demo", 1)
    assert len(flags.scene_beats) == 2
    assert flags.scene_beats[0].title == "开场"
    assert flags.scene_beats[0].location == "茶馆"
    assert flags.scene_beats[1].rhythm_tag == "讽刺反转"


def test_to_cli_args_trope_axes(tmp_path: Path) -> None:
    _, compiler = _setup_project(tmp_path)
    flags = CompiledFlags(trope_axes=["a", "b", "c"])
    args = compiler.to_cli_args(flags)
    assert args.count("--trope-axis") == 3


def test_to_env_vars(tmp_path: Path) -> None:
    _, compiler = _setup_project(tmp_path)
    flags = CompiledFlags(loom_memory_mode="ab", loom_tension_enabled=False)
    env = compiler.to_env_vars(flags)
    assert env["NOVEL_ANALYZER_LOOM_MEMORY_MODE"] == "ab"
    assert env["NOVEL_ANALYZER_LOOM_TENSION_ENABLED"] == "false"


def test_compile_lock_assertions(tmp_path: Path) -> None:
    shell, compiler = _setup_project(tmp_path)
    fm = {
        "stage": "characters",
        "version": 1,
        "parents": [],
        "locked": True,
        "lock_assertions": ["主角不暴怒"],
        "generated_at": "2026-05-17T00:00:00Z",
    }
    _write_md(tmp_path, "demo", "characters", "zhang_yu", "test", frontmatter=fm)
    locked_path = tmp_path / "demo" / "locked.yaml"
    locked_path.write_text(
        yaml.safe_dump({"locked": ["characters/zhang_yu.md"]}, allow_unicode=True),
        encoding="utf-8",
    )
    flags = compiler.compile_for_chapter("demo", 1)
    assert "主角不暴怒" in flags.lock_assertions


def test_missing_file_graceful(tmp_path: Path) -> None:
    _, compiler = _setup_project(tmp_path)
    flags = compiler.compile_for_chapter("demo", 99)
    assert flags.trope_axes == []
    assert flags.target_goal == ""
