"""ProjectCharactersService: CharacterPersona ↔ editable markdown card bridge.

Loom Phase 6 – T6. Generates character card templates and bridges to/from
CharacterPersona (Phase 4 character_agent_service). Does NOT reimplement
persona derivation — delegates to build_character_persona() unchanged.
"""

from __future__ import annotations

import logging
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from novel_analyzer.services.character_agent_service import (
    CharacterAgentService,
    CharacterPersona,
)
from novel_analyzer.services.project_shell_service import ProjectShellService

logger = logging.getLogger(__name__)

_DEFAULT_NAMES = ["protagonist", "female_lead", "antagonist", "mentor", "comic_relief"]

_CARD_TEMPLATE = """\
# {name}

## 基本信息
- 姓名: {name}
- 年龄: 待填写
- 身份: 待填写
- 一句话标签: 待填写

## 价值观 + 目标 + 恐惧
- 价值观: 待填写
- 短期目标: 待填写
- 中期目标: 待填写
- 长期目标: 待填写
- 核心恐惧: 待填写

## 说话风格指纹
- 口头禅: 待填写
- 句式偏好: 待填写
- 情绪释放阀: 待填写

## 性格弧
- 起点: 待填写
- 钩子事件: 待填写
- 转变方向: 待填写

## 关系网
- 与其他角色定位: 待填写

## 严禁动作
(违背声音的反模式,会进入 frontmatter lock_assertions)
- 待填写

## 行为标签 + 关系网络摘要
(对应 FactRecord 行为标签 / GraphNode 关系)
- 待填写
"""

_REQUIRED_H2_SECTIONS = [
    "基本信息",
    "价值观 + 目标 + 恐惧",
    "说话风格指纹",
    "性格弧",
    "关系网",
    "严禁动作",
    "行为标签 + 关系网络摘要",
]


def _parse_h2_section(text: str, heading: str) -> str:
    """Extract body text under ``## heading`` until the next ``##`` heading."""
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


def _extract_bullets(section_text: str) -> list[str]:
    """Return non-empty bullet values from a markdown section."""
    results: list[str] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            value = stripped[2:].strip()
            if value and value != "待填写":
                results.append(value)
    return results


class ProjectCharactersService:
    """Generate and parse character card markdown files for a project."""

    def __init__(
        self,
        session: Session,
        base_dir: Path = Path("output/projects"),
        shell: ProjectShellService | None = None,
    ) -> None:
        self._session = session
        self._base_dir = base_dir
        self._shell = shell or ProjectShellService(base_dir=base_dir, session=session)

    def generate_initial_cards(
        self,
        slug: str,
        count: int = 4,
        use_llm: bool = False,
    ) -> list[Path]:
        """Create N empty character card templates.

        If *use_llm* is True, logs a deferral notice — LLM enrichment is
        wired in T9 prose orchestrator, not here.
        """
        if use_llm:
            logger.info(
                "use_llm=True character generation deferred to T9 prose orchestrator"
            )

        names = _DEFAULT_NAMES[:count]
        paths: list[Path] = []

        parents: list[str] = []
        for candidate in ("macro/premise.md", "macro/world.md"):
            candidate_path = self._base_dir / slug / candidate
            if candidate_path.exists():
                parents.append(candidate)

        for name in names:
            body = _CARD_TEMPLATE.format(name=name)
            path = self._shell.write_artifact(
                slug,
                "characters",
                name,
                body,
                parents=parents,
            )
            paths.append(path)
            logger.debug("Wrote character card: %s", path)

        return paths

    def inherit_from_source(
        self,
        slug: str,
        character_names: list[str],
    ) -> list[Path]:
        """Build personas from source branch and write as markdown cards.

        Calls ``CharacterAgentService.build_character_persona()`` for each
        name. On failure, falls back to an empty card and logs a warning.
        """
        from novel_analyzer.domain.project_config import load_book_config

        try:
            cfg = load_book_config(slug, self._base_dir)
            source_branch_id = cfg.source_branch_id
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not load project config for %r: %s", slug, exc)
            source_branch_id = ""

        agent = CharacterAgentService(self._session)
        paths: list[Path] = []

        for name in character_names:
            try:
                persona = agent.build_character_persona(
                    branch_id=source_branch_id,
                    character_name=name,
                    as_of_chapter=0,
                )
                body = self._persona_to_markdown(persona, name)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "build_character_persona failed for %r: %s — using empty card",
                    name,
                    exc,
                )
                body = _CARD_TEMPLATE.format(name=name)

            path = self._shell.write_artifact(
                slug,
                "characters",
                name,
                body,
            )
            paths.append(path)

        return paths

    def markdown_to_persona(
        self,
        slug: str,
        name: str,
    ) -> CharacterPersona | None:
        """Parse a character card back into a CharacterPersona.

        Returns None if the card is missing or has insufficient data.
        """
        try:
            fm, body = self._shell.read_artifact_with_frontmatter(
                slug, "characters", name
            )
        except FileNotFoundError:
            logger.warning("Character card not found: %s / characters / %s", slug, name)
            return None

        behavior_section = _parse_h2_section(body, "行为标签 + 关系网络摘要")
        behavior_labels = _extract_bullets(behavior_section)

        relationship_section = _parse_h2_section(body, "关系网")
        rel_bullets = _extract_bullets(relationship_section)
        relationship_network: dict[str, str] = {}
        for bullet in rel_bullets:
            if ":" in bullet:
                k, _, v = bullet.partition(":")
                relationship_network[k.strip()] = v.strip()
            else:
                relationship_network[bullet] = ""

        branch_id = str(fm.get("character_map_key", ""))

        if not behavior_labels and not relationship_network:
            logger.warning(
                "Insufficient data in character card %r/%r to build persona", slug, name
            )
            return None

        return CharacterPersona(
            character_id=name,
            branch_id=branch_id,
            built_at_chapter=0,
            behavior_labels=behavior_labels,
            episodic_anchors=[],
            relationship_network=relationship_network,
            speech_style_vector=[],
            chapter_appearances=[],
        )

    def _persona_to_markdown(self, persona: CharacterPersona, name: str) -> str:
        """Render a CharacterPersona into the 7-H2 card markdown format."""
        d: dict[str, Any] = asdict(persona)

        behavior_labels: list[str] = d.get("behavior_labels") or []
        relationship_network: dict[str, str] = d.get("relationship_network") or {}
        speech_style_vector: list[float] = d.get("speech_style_vector") or []
        episodic_anchors: list[dict[str, object]] = d.get("episodic_anchors") or []
        chapter_appearances: list[int] = d.get("chapter_appearances") or []

        rel_lines = (
            "\n".join(f"- {k}: {v}" for k, v in relationship_network.items())
            if relationship_network
            else "- 待填写"
        )
        behavior_lines = (
            "\n".join(f"- {lbl}" for lbl in behavior_labels)
            if behavior_labels
            else "- 待填写"
        )
        speech_note = (
            f"- 向量维度: {len(speech_style_vector)}" if speech_style_vector else "- 待填写"
        )
        anchor_note = (
            f"- 锚点数量: {len(episodic_anchors)}" if episodic_anchors else "- 待填写"
        )
        chapters_note = (
            f"- 出场章节: {', '.join(str(c) for c in chapter_appearances)}"
            if chapter_appearances
            else "- 待填写"
        )

        return f"""\
# {name}

## 基本信息
- 姓名: {name}
- 年龄: 待填写
- 身份: 待填写
- 一句话标签: 待填写

## 价值观 + 目标 + 恐惧
- 价值观: 待填写
- 短期目标: 待填写
- 中期目标: 待填写
- 长期目标: 待填写
- 核心恐惧: 待填写

## 说话风格指纹
{speech_note}
- 句式偏好: 待填写
- 情绪释放阀: 待填写

## 性格弧
{anchor_note}
{chapters_note}
- 转变方向: 待填写

## 关系网
{rel_lines}

## 严禁动作
(违背声音的反模式,会进入 frontmatter lock_assertions)
- 待填写

## 行为标签 + 关系网络摘要
(对应 FactRecord 行为标签 / GraphNode 关系)
{behavior_lines}
"""
