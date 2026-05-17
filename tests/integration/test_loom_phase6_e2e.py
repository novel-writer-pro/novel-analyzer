from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from novel_analyzer.services.project_characters_service import ProjectCharactersService
from novel_analyzer.services.project_compiler_service import ProjectCompilerService
from novel_analyzer.services.project_macro_service import ProjectMacroService
from novel_analyzer.services.project_outline_service import ProjectOutlineService
from novel_analyzer.services.project_plot_service import ProjectPlotService
from novel_analyzer.services.project_prose_service import ProjectProseService
from novel_analyzer.services.project_shell_service import ProjectShellService
from novel_analyzer.services.project_style_view_service import ProjectStyleViewService


def test_full_7_layer_pipeline_no_llm(tmp_path: Path) -> None:
    slug = "test-novel"
    settings = MagicMock()
    session = MagicMock()

    shell = ProjectShellService(base_dir=tmp_path)
    shell.init(slug, source_branch_id="fake-branch")

    style_svc = ProjectStyleViewService(session=session, base_dir=tmp_path, shell=shell)
    with patch.object(style_svc, "_compute_chapter_metrics", side_effect=Exception("no data")):
        style_svc.generate_fingerprint(slug)

    macro_svc = ProjectMacroService(
        settings=settings, session=session, base_dir=tmp_path, shell=shell
    )
    macro_svc._rag_dir = tmp_path / "rag"
    macro_svc.generate(slug, use_llm=False)

    char_svc = ProjectCharactersService(session=session, base_dir=tmp_path, shell=shell)
    char_svc.generate_initial_cards(slug, count=2, use_llm=False)

    plot_svc = ProjectPlotService(
        settings=settings, session=session, base_dir=tmp_path, shell=shell,
        rag_dir=tmp_path / "rag",
    )
    plot_svc.generate_plot(slug, use_llm=False)
    plot_svc.generate_conflicts(slug, use_llm=False)

    outline_svc = ProjectOutlineService(
        settings=settings, session=session, base_dir=tmp_path, shell=shell
    )
    for ch in range(1, 4):
        outline_svc.generate_outline(slug, ch, use_llm=False)
        outline_svc.generate_storyboard(slug, ch, use_llm=False)

    prose_svc = ProjectProseService(
        settings=settings, session=session, base_dir=tmp_path, shell=shell
    )
    for ch in range(1, 4):
        prose_svc.generate_chapter(slug, ch, use_llm=False)

    project_dir = tmp_path / slug
    assert (project_dir / "style" / "fingerprint.md").exists()
    assert (project_dir / "macro" / "premise.md").exists()
    assert (project_dir / "macro" / "world.md").exists()
    assert (project_dir / "plot" / "arcs.md").exists()
    assert (project_dir / "plot" / "chapter_goals.md").exists()
    assert (project_dir / "plot" / "continuity.md").exists()
    assert (project_dir / "conflicts" / "axes.md").exists()
    for ch in range(1, 4):
        stem = f"ch{ch:03d}"
        assert (project_dir / "chapters" / f"{stem}.outline.md").exists()
        assert (project_dir / "chapters" / f"{stem}.storyboard.md").exists()
        assert (project_dir / "chapters" / f"{stem}.draft.md").exists()

    draft = (project_dir / "chapters" / "ch001.draft.md").read_text(encoding="utf-8")
    assert "loom_signals" in draft
    assert "final_verdict" in draft


def test_compiler_reads_all_layers(tmp_path: Path) -> None:
    slug = "test-novel-2"

    shell = ProjectShellService(base_dir=tmp_path)
    shell.init(slug, source_branch_id="fake-branch")

    shell.write_artifact(slug, "conflicts", "axes", "- 底层逆袭\n- 账本修仙\n")
    shell.write_artifact(slug, "macro", "world", "## 世界观底座\n测试世界\n## 规则\n- 规则1\n")
    shell.write_artifact(
        slug, "chapters", "ch001.outline", "# 第一章 测试\n## 本章目标\n主角出场\n"
    )
    shell.write_artifact(
        slug,
        "chapters",
        "ch001.storyboard",
        (
            "## Beat #1: 开场\n"
            "场所: 茶馆\n"
            "POV: 主角\n"
            "镜头类型: 内心独白\n"
            "节奏标签: 平庸setup\n"
            "信息释放: 世界观\n"
            "内容草要: 主角进入茶馆\n"
        ),
    )

    compiler = ProjectCompilerService(base_dir=tmp_path, shell=shell)
    flags = compiler.compile_for_chapter(slug, 1)

    assert flags.trope_axes == ["底层逆袭", "账本修仙"]
    assert flags.rule_overrides == ["规则1"]
    assert "第一章" in flags.target_goal
    assert len(flags.scene_beats) == 1
    assert flags.scene_beats[0].location == "茶馆"
