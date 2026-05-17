from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy.orm import Session

from novel_analyzer.config.settings import Settings
from novel_analyzer.domain.project_config import load_book_config
from novel_analyzer.services.project_shell_service import ProjectShellService

logger = logging.getLogger(__name__)

_HOOK_TYPES = ["悬念问句", "模棱两可话", "新威胁"]

_DEFAULT_BEATS = [
    ("setup", "开场铺垫", "平庸setup"),
    ("conflict", "核心冲突", "权力揭示"),
    ("reversal", "讽刺反转", "讽刺反转"),
    ("hook", "章末钩子", "钩子"),
]

_LENS_TYPES = ["内心独白", "对话", "动作", "描写", "世界观揭示"]


class ProjectOutlineService:
    def __init__(
        self,
        settings: Settings,
        session: Session,
        base_dir: Path = Path("output/projects"),
        shell: ProjectShellService | None = None,
    ) -> None:
        self._settings = settings
        self._session = session
        self._base_dir = base_dir
        self._shell = shell or ProjectShellService(base_dir=base_dir, session=session)

    def generate_outline(self, slug: str, chapter_idx: int, use_llm: bool = False) -> Path:
        axes = self._safe_read(slug, "conflicts", "axes")
        chapter_goal = self._extract_chapter_goal(slug, chapter_idx)
        prev_outline = (
            self._safe_read(slug, "chapters", f"ch{(chapter_idx - 1):03d}.outline")
            if chapter_idx > 1
            else ""
        )
        char_names = self._list_character_names(slug)
        hook_type = _HOOK_TYPES[(chapter_idx - 1) % len(_HOOK_TYPES)]

        body = self._build_outline_body(
            chapter_idx=chapter_idx,
            chapter_goal=chapter_goal,
            axes=axes,
            prev_outline=prev_outline,
            char_names=char_names,
            hook_type=hook_type,
        )
        path = self._shell.write_artifact(
            slug,
            "chapters",
            f"ch{chapter_idx:03d}.outline",
            body,
            parents=["plot/chapter_goals.md", "macro/premise.md"],
        )
        logger.info("outline written: %s", path)
        return path

    def generate_storyboard(self, slug: str, chapter_idx: int, use_llm: bool = False) -> Path:
        outline_body = self._safe_read(slug, "chapters", f"ch{chapter_idx:03d}.outline")
        body = self._build_storyboard_body(chapter_idx=chapter_idx, outline_body=outline_body)
        path = self._shell.write_artifact(
            slug,
            "chapters",
            f"ch{chapter_idx:03d}.storyboard",
            body,
            parents=[f"chapters/ch{chapter_idx:03d}.outline.md"],
        )
        logger.info("storyboard written: %s", path)
        return path

    def generate_all(self, slug: str, use_llm: bool = False) -> list[tuple[Path, Path]]:
        cfg = load_book_config(slug, self._base_dir)
        results: list[tuple[Path, Path]] = []
        for idx in range(1, cfg.target_chapters + 1):
            outline_path = self.generate_outline(slug, idx, use_llm=use_llm)
            storyboard_path = self.generate_storyboard(slug, idx, use_llm=use_llm)
            results.append((outline_path, storyboard_path))
        return results

    def _build_outline_body(
        self,
        chapter_idx: int,
        chapter_goal: str,
        axes: str,
        prev_outline: str,
        char_names: list[str],
        hook_type: str,
    ) -> str:
        goal_text = chapter_goal if chapter_goal else "[请填写本章核心目标]"
        conflict_text = self._extract_first_axis(axes) or "[请填写主冲突]"
        chars_hint = "、".join(char_names[:3]) if char_names else "[请填写角色]"
        prev_hint = (
            self._extract_prev_hook(prev_outline) if prev_outline else "[请填写与上一章衔接]"
        )
        lines = [
            f"# 第{chapter_idx}章 [请填写标题]",
            "",
            "## 本章目标",
            goal_text,
            "",
            "## 主冲突",
            conflict_text,
            "",
            "## 关键转折",
            f"1. [请填写转折一 — 涉及 {chars_hint}]",
            "2. [请填写转折二]",
            "3. [请填写转折三（可选）]",
            "",
            "## 信息释放顺序",
            "1. [请填写第一个信息释放节点]",
            "2. [请填写第二个信息释放节点]",
            "3. [请填写第三个信息释放节点]",
            "",
            f"## 章末钩子类型: {hook_type}",
            "[请填写具体钩子内容]",
            "",
            "## 与上一章衔接",
            prev_hint,
            "",
        ]
        return "\n".join(lines)

    def _build_storyboard_body(self, chapter_idx: int, outline_body: str) -> str:
        blocks: list[str] = []
        for beat_num, (_key, beat_title, rhythm) in enumerate(_DEFAULT_BEATS, start=1):
            lens = _LENS_TYPES[beat_num % len(_LENS_TYPES)]
            blocks.append(
                self._beat_block(
                    index=beat_num,
                    title=beat_title,
                    location="[请填写场所]",
                    pov="[请填写POV角色]",
                    lens_type=lens,
                    rhythm_tag=rhythm,
                    info_reveal=f"[请填写Beat #{beat_num}揭示内容]",
                    summary=f"[请填写Beat #{beat_num}内容草要，约200字]",
                )
            )
        return "\n".join(blocks)

    @staticmethod
    def _beat_block(
        index: int,
        title: str,
        location: str,
        pov: str,
        lens_type: str,
        rhythm_tag: str,
        info_reveal: str,
        summary: str,
    ) -> str:
        return (
            f"## Beat #{index}: {title}\n"
            f"场所: {location}\n"
            f"POV: {pov}\n"
            f"镜头类型: {lens_type}\n"
            f"节奏标签: {rhythm_tag}\n"
            f"信息释放: {info_reveal}\n"
            f"内容草要: {summary}\n"
        )

    def _safe_read(self, slug: str, stage: str, name: str) -> str:
        try:
            return self._shell.read_artifact(slug, stage, name)
        except FileNotFoundError:
            logger.debug("outline_service: artifact not found — %s/%s (skipping)", stage, name)
            return ""

    def _extract_chapter_goal(self, slug: str, chapter_idx: int) -> str:
        body = self._safe_read(slug, "plot", "chapter_goals")
        if not body:
            return ""
        lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
        for line in lines:
            if line.startswith(f"{chapter_idx}:"):
                return line.split(":", 1)[1].strip()
            if line.startswith(f"{chapter_idx}.") or line.startswith(f"{chapter_idx}、"):
                return line.split(".", 1)[-1].split("、", 1)[-1].strip()
        if 0 < chapter_idx <= len(lines):
            return lines[chapter_idx - 1]
        return ""

    def _list_character_names(self, slug: str) -> list[str]:
        chars_dir = self._base_dir / slug / "characters"
        if not chars_dir.is_dir():
            return []
        names: list[str] = []
        for md_file in sorted(chars_dir.glob("*.md")):
            fm, _ = self._shell._parse_frontmatter(  # noqa: SLF001
                md_file.read_text(encoding="utf-8")
            )
            names.append(str(fm.get("name", "")) or md_file.stem)
        return names

    def _extract_first_axis(self, axes_body: str) -> str:
        for line in axes_body.splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                return stripped[2:].strip()
        return ""

    def _extract_prev_hook(self, prev_outline: str) -> str:
        for line in prev_outline.splitlines():
            if "章末钩子类型" in line:
                return f"承接上章钩子: {line.strip()}"
        return "[请填写与上一章衔接]"
