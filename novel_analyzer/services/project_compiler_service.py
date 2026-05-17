"""Stage-to-flag compiler: parses 7-layer markdown project files into CompiledFlags.

Bridges the author-facing markdown UX to the existing 9 steering CLI flags
and 5 Loom feature env vars. Pure deterministic parsing — no LLM calls.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from novel_analyzer.domain.project_config import ProjectConfig, load_book_config
from novel_analyzer.services.project_shell_service import ProjectShellService

logger = logging.getLogger(__name__)


@dataclass
class Beat:
    """A single scene beat parsed from a storyboard markdown file."""

    index: int
    title: str
    location: str = ""
    pov: str = ""
    lens_type: str = ""  # 内心独白/对话/动作/描写/世界观揭示
    rhythm_tag: str = ""  # 平庸setup/权力揭示/讽刺反转/钩子
    info_reveal: str = ""
    summary: str = ""


@dataclass
class CompiledFlags:
    """All steering flags compiled from a project's markdown artifacts."""

    worldview_note: str = ""
    rule_overrides: list[str] = field(default_factory=list)
    trope_axes: list[str] = field(default_factory=list)
    innovation_directives: list[str] = field(default_factory=list)
    taboo_innovations: list[str] = field(default_factory=list)
    knowledge_refs: list[str] = field(default_factory=list)
    world_map: dict[str, str] = field(default_factory=dict)
    character_map: dict[str, str] = field(default_factory=dict)
    power_map: dict[str, str] = field(default_factory=dict)
    target_goal: str = ""
    scene_beats: list[Beat] = field(default_factory=list)
    lock_assertions: list[str] = field(default_factory=list)
    loom_memory_mode: str = "enabled"
    loom_tension_enabled: bool = True
    loom_pairwise_enabled: bool = True
    loom_style_enabled: bool = True
    loom_character_enabled: bool = True


class ProjectCompilerService:
    """Compile a project's markdown artifacts into CompiledFlags for a given chapter."""

    def __init__(
        self,
        base_dir: Path = Path("output/projects"),
        shell: ProjectShellService | None = None,
    ) -> None:
        self._base_dir = base_dir
        self._shell = shell or ProjectShellService(base_dir=base_dir)

    def compile_for_chapter(self, slug: str, chapter_idx: int) -> CompiledFlags:
        """Parse all markdown layers for *slug* and return CompiledFlags for *chapter_idx*."""
        cfg: ProjectConfig = load_book_config(slug, self._base_dir)
        flags = CompiledFlags(
            loom_memory_mode=cfg.loom_flags.memory_mode,
            loom_tension_enabled=cfg.loom_flags.tension_enabled,
            loom_pairwise_enabled=cfg.loom_flags.pairwise_enabled,
            loom_style_enabled=cfg.loom_flags.style_enabled,
            loom_character_enabled=cfg.loom_flags.character_enabled,
        )

        _, world_body = self._safe_read_artifact(slug, "macro", "world")
        if world_body:
            flags.worldview_note = world_body[:2000]
            flags.rule_overrides = self._parse_list_items(
                self._parse_h2_section(world_body, "规则")
            )
            flags.world_map = self._parse_table_rows(
                self._parse_h2_section(world_body, "名词映射")
            )
            flags.power_map = self._parse_kv_lines(
                self._parse_h2_section(world_body, "力量")
            )

        _, premise_body = self._safe_read_artifact(slug, "macro", "premise")
        if premise_body:
            flags.knowledge_refs.append(premise_body[:500])

        _, axes_body = self._safe_read_artifact(slug, "conflicts", "axes")
        if axes_body:
            flags.trope_axes = self._parse_list_items(axes_body)

        _, innovation_body = self._safe_read_artifact(slug, "conflicts", "innovation")
        if innovation_body:
            flags.innovation_directives = self._parse_h2_titles(innovation_body)

        _, taboo_body = self._safe_read_artifact(slug, "conflicts", "taboo")
        if taboo_body:
            flags.taboo_innovations = self._parse_list_items(taboo_body)

        _, fp_body = self._safe_read_artifact(slug, "style", "fingerprint")
        if fp_body:
            flags.knowledge_refs.append(fp_body[:500])

        chars_dir = self._base_dir / slug / "characters"
        if chars_dir.is_dir():
            for char_file in sorted(chars_dir.glob("*.md")):
                fm, _ = self._shell._parse_frontmatter(  # noqa: SLF001
                    char_file.read_text(encoding="utf-8")
                )
                key = str(fm.get("character_map_key", "")) or char_file.stem
                name = str(fm.get("name", "")) or char_file.stem
                if key:
                    flags.character_map[key] = name

        stem = self._chapter_stem(chapter_idx)
        _, outline_body = self._safe_read_artifact(slug, "chapters", f"{stem}.outline")
        if outline_body:
            flags.target_goal = self._extract_target_goal(outline_body)

        _, storyboard_body = self._safe_read_artifact(slug, "chapters", f"{stem}.storyboard")
        if storyboard_body:
            flags.scene_beats = self._parse_beats(storyboard_body)

        flags.lock_assertions = self._shell.list_locked_assertions(slug)

        return flags

    def to_cli_args(self, flags: CompiledFlags) -> list[str]:
        args: list[str] = []
        if flags.worldview_note:
            args += ["--worldview-note", flags.worldview_note]
        for axis in flags.trope_axes:
            args += ["--trope-axis", axis]
        for directive in flags.innovation_directives:
            args += ["--innovation-directive", directive]
        for taboo in flags.taboo_innovations:
            args += ["--taboo-innovation", taboo]
        for ref in flags.knowledge_refs:
            args += ["--knowledge-ref", ref]
        for k, v in flags.world_map.items():
            args += ["--world-map", f"{k}={v}"]
        for k, v in flags.character_map.items():
            args += ["--character-map", f"{k}={v}"]
        for k, v in flags.power_map.items():
            args += ["--power-map", f"{k}={v}"]
        for override in flags.rule_overrides:
            args += ["--rule-override", override]
        return args

    def to_env_vars(self, flags: CompiledFlags) -> dict[str, str]:
        return {
            "NOVEL_ANALYZER_LOOM_MEMORY_MODE": flags.loom_memory_mode,
            "NOVEL_ANALYZER_LOOM_TENSION_ENABLED": str(flags.loom_tension_enabled).lower(),
            "NOVEL_ANALYZER_LOOM_PAIRWISE_ENABLED": str(flags.loom_pairwise_enabled).lower(),
            "NOVEL_ANALYZER_LOOM_STYLE_ENABLED": str(flags.loom_style_enabled).lower(),
            "NOVEL_ANALYZER_LOOM_CHARACTER_ENABLED": str(flags.loom_character_enabled).lower(),
        }

    def to_constraint_pack_input(self, flags: CompiledFlags) -> dict[str, Any]:
        """Return a dict suitable for the imitation-constraint-pack skill input."""
        return {
            "worldview_note": flags.worldview_note,
            "rule_overrides": flags.rule_overrides,
            "world_map": flags.world_map,
            "character_map": flags.character_map,
            "power_map": flags.power_map,
            "target_goal": flags.target_goal,
            "scene_beats": [vars(b) for b in flags.scene_beats],
            "lock_assertions": flags.lock_assertions,
            "trope_axes": flags.trope_axes,
            "innovation_directives": flags.innovation_directives,
            "taboo_innovations": flags.taboo_innovations,
            "knowledge_refs": flags.knowledge_refs,
        }

    def _safe_read_artifact(
        self, slug: str, stage: str, name: str
    ) -> tuple[dict[str, object], str]:
        """Read artifact; return ({}, "") on missing file instead of raising."""
        try:
            return self._shell.read_artifact_with_frontmatter(slug, stage, name)
        except FileNotFoundError:
            logger.warning(
                "project_compiler: artifact not found — slug=%r stage=%r name=%r (skipping)",
                slug,
                stage,
                name,
            )
            return {}, ""

    @staticmethod
    def _parse_list_items(text: str) -> list[str]:
        items: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                items.append(stripped[2:].strip())
        return items

    @staticmethod
    def _parse_h2_titles(text: str) -> list[str]:
        titles: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("## "):
                titles.append(stripped[3:].strip())
        return titles

    @staticmethod
    def _parse_table_rows(text: str) -> dict[str, str]:
        """Parse `| key | value |` markdown table rows, skipping separator rows."""
        result: dict[str, str] = {}
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            if re.match(r"^\|[\s\-|:]+\|$", stripped):  # separator row e.g. |---|---|
                continue
            parts = [p.strip() for p in stripped.strip("|").split("|")]
            if len(parts) >= 2 and parts[0] and parts[1]:
                result[parts[0]] = parts[1]
        return result

    @staticmethod
    def _parse_kv_lines(text: str) -> dict[str, str]:
        result: dict[str, str] = {}
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                stripped = stripped[2:].strip()
            if "=" in stripped:
                key, _, val = stripped.partition("=")
                key = key.strip()
                val = val.strip()
                if key:
                    result[key] = val
        return result

    @staticmethod
    def _parse_h2_section(text: str, heading: str) -> str:
        """Extract body text under `## heading` until the next `##` heading."""
        pattern = re.compile(
            r"^##\s+" + re.escape(heading) + r"\s*$",
            re.MULTILINE,
        )
        match = pattern.search(text)
        if not match:
            return ""
        start = match.end()
        next_h2 = re.search(r"^##\s+", text[start:], re.MULTILINE)
        if next_h2:
            return text[start : start + next_h2.start()]
        return text[start:]

    @staticmethod
    def _parse_beats(text: str) -> list[Beat]:
        """Parse `## Beat #N: <title>` blocks from a storyboard markdown."""
        beats: list[Beat] = []
        beat_pattern = re.compile(r"^##\s+Beat\s+#(\d+):\s*(.+)$", re.MULTILINE)
        matches = list(beat_pattern.finditer(text))
        for i, m in enumerate(matches):
            idx = int(m.group(1))
            title = m.group(2).strip()
            block_start = m.end()
            block_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            block = text[block_start:block_end]

            beat = Beat(index=idx, title=title)
            for line in block.splitlines():
                line = line.strip()
                ll = line.lower()
                if ll.startswith("location:") or line.startswith("场所:"):
                    beat.location = line.split(":", 1)[1].strip()
                elif ll.startswith("pov:"):
                    beat.pov = line.split(":", 1)[1].strip()
                elif (
                    ll.startswith("lens:")
                    or ll.startswith("lens_type:")
                    or line.startswith("镜头类型:")
                ):
                    beat.lens_type = line.split(":", 1)[1].strip()
                elif (
                    ll.startswith("rhythm:")
                    or ll.startswith("rhythm_tag:")
                    or line.startswith("节奏标签:")
                ):
                    beat.rhythm_tag = line.split(":", 1)[1].strip()
                elif (
                    ll.startswith("info_reveal:")
                    or ll.startswith("info reveal:")
                    or line.startswith("信息释放:")
                ):
                    beat.info_reveal = line.split(":", 1)[1].strip()
                elif ll.startswith("summary:") or line.startswith("内容草要:"):
                    beat.summary = line.split(":", 1)[1].strip()
            beats.append(beat)
        return beats

    @staticmethod
    def _extract_target_goal(outline_body: str) -> str:
        h1_match = re.search(r"^#\s+(.+)$", outline_body, re.MULTILINE)
        h1 = h1_match.group(1).strip() if h1_match else ""

        goal_section = ProjectCompilerService._parse_h2_section(outline_body, "本章目标")
        first_goal_line = ""
        for line in goal_section.splitlines():
            stripped = line.strip()
            if stripped:
                first_goal_line = stripped
                break

        if h1 and first_goal_line:
            return f"{h1} — {first_goal_line}"
        return h1 or first_goal_line

    @staticmethod
    def _chapter_stem(chapter_idx: int) -> str:
        return f"ch{chapter_idx:03d}"
