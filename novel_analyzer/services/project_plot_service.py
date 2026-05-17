"""Loom Phase 6 T7: Plot + Conflicts stages.

Outputs:
  plot/arcs.md            — main arc + 2 sub-arcs, each with 4 H2 sections
  plot/chapter_goals.md   — one line per chapter: {idx}:{goal} (≤50 chars)
  plot/continuity.md      — Loom _legacy_compat fields
  conflicts/axes.md       — list of trope axes (≥3, each ≤20 chars)
  conflicts/innovation.md — innovation directives
  conflicts/taboo.md      — taboo list with 3 default anti-slop items
  rag/trope-library/<slug>-tropes.md — RAG trope library entry
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from novel_analyzer.config.settings import Settings
from novel_analyzer.domain.project_config import load_book_config
from novel_analyzer.services.project_shell_service import ProjectShellService

logger = logging.getLogger(__name__)

_ARCS_TEMPLATE = """\
## 主弧
### 类型
[请填写]

### 目标
[请填写]

### 节奏曲线
[请填写]

### 关键节点
[请填写]

## 支线弧一
### 类型
[请填写]

### 目标
[请填写]

### 节奏曲线
[请填写]

### 关键节点
[请填写]

## 支线弧二
### 类型
[请填写]

### 目标
[请填写]

### 节奏曲线
[请填写]

### 关键节点
[请填写]
"""

_CONTINUITY_TEMPLATE = """\
## characters
- [请填写]

## rules
- [请填写]

## unresolved_threads
- [请填写]

## previous_chapter_summary
"""

_AXES_TEMPLATE = """\
- 强弱逆转
- 忠诚与背叛
- 权力与代价
"""

_INNOVATION_TEMPLATE = """\
## 创新指令
[请填写]

## 反套路策略
[请填写]

## 差异化定位
[请填写]
"""

_TABOO_DEFAULTS = [
    "禁止无代价系统外挂",
    "禁止突兀大团圆收尾",
    "禁止角色情绪化爆发",
]

_TROPES_TEMPLATE = """\
## 冲突轴
{axes}

## 禁忌
{taboos}
"""


class ProjectPlotService:
    def __init__(
        self,
        settings: Settings,
        session: Session,
        base_dir: Path = Path("output/projects"),
        shell: ProjectShellService | None = None,
        rag_dir: Path = Path("rag"),
    ) -> None:
        self._settings = settings
        self._session = session
        self._base_dir = base_dir
        self._shell = shell or ProjectShellService(base_dir=base_dir)
        self._rag_dir = rag_dir

    def generate_plot(
        self, slug: str, use_llm: bool = False
    ) -> tuple[Path, Path, Path]:
        cfg = load_book_config(slug, self._base_dir)

        premise_body = self._read_context(slug, "macro", "premise")
        world_body = self._read_context(slug, "macro", "world")
        context = f"{premise_body}\n\n{world_body}".strip()

        if use_llm:
            arcs_body, goals_body, continuity_body = self._generate_plot_with_llm(
                context, cfg.target_chapters
            )
        else:
            arcs_body = _ARCS_TEMPLATE
            goals_body = self._default_chapter_goals(cfg.target_chapters)
            continuity_body = _CONTINUITY_TEMPLATE

        arcs_path = self._shell.write_artifact(
            slug,
            "plot",
            "arcs",
            arcs_body,
            parents=["macro/premise.md", "macro/world.md"],
        )
        goals_path = self._shell.write_artifact(
            slug,
            "plot",
            "chapter_goals",
            goals_body,
            parents=["macro/premise.md"],
        )
        continuity_path = self._shell.write_artifact(
            slug,
            "plot",
            "continuity",
            continuity_body,
            parents=["plot/arcs.md"],
        )
        return arcs_path, goals_path, continuity_path

    def generate_conflicts(
        self, slug: str, use_llm: bool = False
    ) -> tuple[Path, Path, Path, Path | None]:
        load_book_config(slug, self._base_dir)

        if use_llm:
            axes_body, innovation_body, taboo_body = self._generate_conflicts_with_llm(
                slug
            )
        else:
            axes_body = _AXES_TEMPLATE
            innovation_body = _INNOVATION_TEMPLATE
            taboo_body = self._default_taboo_body()

        axes_path = self._shell.write_artifact(
            slug,
            "conflicts",
            "axes",
            axes_body,
            parents=["plot/arcs.md"],
        )
        innovation_path = self._shell.write_artifact(
            slug,
            "conflicts",
            "innovation",
            innovation_body,
            parents=["plot/arcs.md"],
        )
        taboo_path = self._shell.write_artifact(
            slug,
            "conflicts",
            "taboo",
            taboo_body,
            parents=["conflicts/axes.md"],
        )

        rag_path = self._write_rag_tropes(slug, axes_body, taboo_body)
        return axes_path, innovation_path, taboo_path, rag_path

    def _read_context(self, slug: str, stage: str, name: str) -> str:
        try:
            _, body = self._shell.read_artifact_with_frontmatter(slug, stage, name)
            return body
        except FileNotFoundError:
            logger.warning(
                "Context artifact %s/%s.md not found for %r — using empty string",
                stage,
                name,
                slug,
            )
            return ""

    @staticmethod
    def _default_chapter_goals(target_chapters: int) -> str:
        lines = [f"{i}:[请填写章节目标]" for i in range(1, target_chapters + 1)]
        return "\n".join(lines) + "\n"

    @staticmethod
    def _default_taboo_body() -> str:
        items = "\n".join(f"- {t}" for t in _TABOO_DEFAULTS)
        return items + "\n"

    def _write_rag_tropes(
        self, slug: str, axes_body: str, taboo_body: str
    ) -> Path | None:
        if not self._rag_dir.exists():
            logger.warning(
                "rag/ directory not found — skipping RAG trope entry for %r", slug
            )
            return None
        trope_dir = self._rag_dir / "trope-library"
        trope_dir.mkdir(parents=True, exist_ok=True)
        rag_path = trope_dir / f"{slug}-tropes.md"
        content = _TROPES_TEMPLATE.format(
            axes=axes_body.strip(), taboos=taboo_body.strip()
        )
        rag_path.write_text(content, encoding="utf-8")
        logger.debug("Wrote RAG trope entry: %s", rag_path)
        return rag_path

    def _generate_plot_with_llm(
        self, context: str, target_chapters: int
    ) -> tuple[str, str, str]:
        import json

        from langchain_core.messages import HumanMessage

        from novel_analyzer.llm.client import build_chat_model

        model = build_chat_model(self._settings)
        prompt = (
            "你是中文小说策划助手。基于以下宏观设定，生成情节规划。"
            "返回 JSON: {"
            '"arcs": [{"type": "", "goal": "", "rhythm": "", "nodes": ""},'
            '{"type": "", "goal": "", "rhythm": "", "nodes": ""},'
            '{"type": "", "goal": "", "rhythm": "", "nodes": ""}],'
            f'"chapter_goals": ["{{}}",...] (共{target_chapters}条,每条≤50字),'
            '"continuity": {"characters": [""], "rules": [""], '
            '"unresolved_threads": [""], "previous_chapter_summary": ""}'
            "}\n\n宏观设定:\n" + context
        )
        raw = str(model.invoke([HumanMessage(content=prompt)]).content)
        try:
            data: dict[str, Any] = json.loads(raw)
            arcs_body = self._render_arcs(data.get("arcs") or [])
            goals_list: list[str] = data.get("chapter_goals") or []
            goals_body = self._render_chapter_goals(goals_list, target_chapters)
            cont_data: dict[str, Any] = data.get("continuity") or {}
            continuity_body = self._render_continuity(cont_data)
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            logger.warning("LLM plot JSON parse failed (%s) — using templates", exc)
            arcs_body = _ARCS_TEMPLATE
            goals_body = self._default_chapter_goals(target_chapters)
            continuity_body = _CONTINUITY_TEMPLATE
        return arcs_body, goals_body, continuity_body

    def _generate_conflicts_with_llm(
        self, slug: str
    ) -> tuple[str, str, str]:
        import json

        from langchain_core.messages import HumanMessage

        from novel_analyzer.llm.client import build_chat_model

        model = build_chat_model(self._settings)
        prompt = (
            "你是中文小说策划助手。为项目生成冲突设计。"
            "返回 JSON: {"
            '"axes": ["冲突轴1(≤20字)", "冲突轴2(≤20字)", "冲突轴3(≤20字)"],'
            '"innovation": {"创新指令": "", "反套路策略": "", "差异化定位": ""},'
            '"taboo": ["禁止无代价系统外挂", "禁止突兀大团圆收尾", "禁止角色情绪化爆发"]'
            "}"
        )
        raw = str(model.invoke([HumanMessage(content=prompt)]).content)
        try:
            data: dict[str, Any] = json.loads(raw)
            axes_list: list[str] = data.get("axes") or []
            axes_body = (
                "\n".join(f"- {a}" for a in axes_list) + "\n"
                if axes_list
                else _AXES_TEMPLATE
            )
            innov_data: dict[str, Any] = data.get("innovation") or {}
            innovation_body = self._render_innovation(innov_data)
            taboo_list: list[str] = data.get("taboo") or []
            # Always ensure defaults are present
            for default in _TABOO_DEFAULTS:
                if default not in taboo_list:
                    taboo_list.append(default)
            taboo_body = "\n".join(f"- {t}" for t in taboo_list) + "\n"
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            logger.warning("LLM conflicts JSON parse failed (%s) — using templates", exc)
            axes_body = _AXES_TEMPLATE
            innovation_body = _INNOVATION_TEMPLATE
            taboo_body = self._default_taboo_body()
        return axes_body, innovation_body, taboo_body

    @staticmethod
    def _render_arcs(arcs: list[Any]) -> str:
        arc_names = ["主弧", "支线弧一", "支线弧二"]
        parts: list[str] = []
        for i, name in enumerate(arc_names):
            arc: dict[str, Any] = arcs[i] if i < len(arcs) else {}
            parts.append(
                f"## {name}\n"
                f"### 类型\n{arc.get('type') or '[请填写]'}\n\n"
                f"### 目标\n{arc.get('goal') or '[请填写]'}\n\n"
                f"### 节奏曲线\n{arc.get('rhythm') or '[请填写]'}\n\n"
                f"### 关键节点\n{arc.get('nodes') or '[请填写]'}\n"
            )
        return "\n".join(parts)

    @staticmethod
    def _render_chapter_goals(goals: list[str], target_chapters: int) -> str:
        lines: list[str] = []
        for i in range(1, target_chapters + 1):
            raw_goal = goals[i - 1] if i - 1 < len(goals) else "[请填写章节目标]"
            goal = str(raw_goal)[:50]
            lines.append(f"{i}:{goal}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _render_continuity(data: dict[str, Any]) -> str:
        def _list_items(key: str) -> str:
            items = data.get(key) or []
            if isinstance(items, list) and items:
                return "\n".join(f"- {item}" for item in items)
            return "- [请填写]"

        return (
            f"## characters\n{_list_items('characters')}\n\n"
            f"## rules\n{_list_items('rules')}\n\n"
            f"## unresolved_threads\n{_list_items('unresolved_threads')}\n\n"
            f"## previous_chapter_summary\n{data.get('previous_chapter_summary') or ''}\n"
        )

    @staticmethod
    def _render_innovation(data: dict[str, Any]) -> str:
        def v(key: str) -> str:
            return str(data.get(key) or "[请填写]").strip() or "[请填写]"

        return (
            f"## 创新指令\n{v('创新指令')}\n\n"
            f"## 反套路策略\n{v('反套路策略')}\n\n"
            f"## 差异化定位\n{v('差异化定位')}\n"
        )
