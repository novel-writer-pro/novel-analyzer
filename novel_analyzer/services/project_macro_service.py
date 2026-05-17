"""Loom Phase 6 T5: Macro stage — premise + world + RAG library entry.

Outputs:
  macro/premise.md  — 5 H2 sections
  macro/world.md    — 6 H2 sections (keys match T3 compiler: 规则/名词映射/力量体系)
  rag/worldview-dossiers/<slug>-worldview.md  — RAG library copy of world body

Source-novel proper nouns are replaced with [请填写] in all LLM output.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from novel_analyzer.config.settings import Settings
from novel_analyzer.domain.project_config import load_book_config
from novel_analyzer.services.project_shell_service import ProjectShellService

logger = logging.getLogger(__name__)

_SOURCE_NOVEL_BANNED = (
    "箓书",
    "万民部",
    "昆墟",
    "张羽",
    "白真真",
    "张翩翩",
    "玉星寒",
    "宋海龙",
    "周澈尘",
    "赵天行",
)

_PREMISE_TEMPLATE = """\
## 题材
[请填写]

## 主旨
[请填写]

## 调性
[请填写]

## 核心讽刺引擎
[请填写]

## 与范本的相似/差异轴
[请填写]
"""

_WORLD_TEMPLATE = """\
## 世界观底座
[请填写]

## 力量体系
key=[请填写]

## 经济与权力结构
[请填写]

## 现代映射
[请填写]

## 规则
- [请填写]

## 名词映射
| 原 | 新 |
|---|---|
| [请填写] | [请填写] |
"""


def _filter_banned(text: str) -> str:
    for noun in _SOURCE_NOVEL_BANNED:
        text = text.replace(noun, "[请填写]")
    return text


class ProjectMacroService:
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
        self._shell = shell or ProjectShellService(base_dir=base_dir)
        self._rag_dir: Path = Path("rag")

    def generate(
        self, slug: str, use_llm: bool = False
    ) -> tuple[Path, Path, Path | None]:
        load_book_config(slug, self._base_dir)

        fingerprint_body = self._read_fingerprint(slug)

        if use_llm:
            premise_body, world_body = self._generate_with_llm(fingerprint_body)
        else:
            premise_body = _PREMISE_TEMPLATE
            world_body = _WORLD_TEMPLATE

        premise_path = self._shell.write_artifact(
            slug,
            "macro",
            "premise",
            premise_body,
            parents=["style/fingerprint.md"],
        )
        world_path = self._shell.write_artifact(
            slug,
            "macro",
            "world",
            world_body,
            parents=["style/fingerprint.md"],
        )

        rag_path = self._write_rag_entry(slug, world_body)
        return premise_path, world_path, rag_path

    def revise(
        self, slug: str, feedback: str, use_llm: bool = False
    ) -> tuple[Path, Path]:
        current_premise = self._read_macro(slug, "premise", _PREMISE_TEMPLATE)
        current_world = self._read_macro(slug, "world", _WORLD_TEMPLATE)

        if use_llm:
            new_premise, new_world = self._revise_with_llm(
                feedback, current_premise, current_world
            )
        else:
            comment = f"<!-- 修改意见: {feedback} -->\n"
            new_premise = comment + current_premise
            new_world = comment + current_world

        premise_path = self._shell.write_artifact(
            slug,
            "macro",
            "premise",
            new_premise,
            parents=["style/fingerprint.md"],
        )
        world_path = self._shell.write_artifact(
            slug,
            "macro",
            "world",
            new_world,
            parents=["style/fingerprint.md"],
        )
        return premise_path, world_path

    def _read_fingerprint(self, slug: str) -> str:
        try:
            _, body = self._shell.read_artifact_with_frontmatter(
                slug, "style", "fingerprint"
            )
            return body
        except FileNotFoundError:
            logger.warning(
                "No style/fingerprint.md found for %r — using empty context", slug
            )
            return ""

    def _read_macro(self, slug: str, name: str, fallback: str) -> str:
        try:
            _, body = self._shell.read_artifact_with_frontmatter(slug, "macro", name)
            return body
        except FileNotFoundError:
            return fallback

    def _write_rag_entry(self, slug: str, world_body: str) -> Path | None:
        if not self._rag_dir.exists():
            logger.warning(
                "rag/ directory not found — skipping RAG library entry for %r", slug
            )
            return None
        dossiers_dir = self._rag_dir / "worldview-dossiers"
        dossiers_dir.mkdir(parents=True, exist_ok=True)
        rag_path = dossiers_dir / f"{slug}-worldview.md"
        rag_path.write_text(world_body, encoding="utf-8")
        logger.debug("Wrote RAG worldview entry: %s", rag_path)
        return rag_path

    def _generate_with_llm(self, fingerprint_body: str) -> tuple[str, str]:
        from langchain_core.messages import HumanMessage

        from novel_analyzer.llm.client import build_chat_model

        model = build_chat_model(self._settings)
        prompt = (
            "你是讽刺现实风格中文小说的策划助手。"
            "基于以下风格指纹,为新故事生成 premise.md 和 world.md。"
            '返回 JSON: {"premise": {"题材": "", "主旨": "", "调性": "", '
            '"核心讽刺引擎": "", "与范本的相似/差异轴": ""}, '
            '"world": {"世界观底座": "", "力量体系": "", "经济与权力结构": "", '
            '"现代映射": "", "规则": ["str"], "名词映射": [{"原": "", "新": ""}]}}'
            f"\n\n风格指纹:\n{fingerprint_body}"
        )
        raw = str(model.invoke([HumanMessage(content=prompt)]).content)
        raw = _filter_banned(raw)

        try:
            data: dict[str, Any] = json.loads(raw)
            premise_body = self._render_premise(data.get("premise") or {})
            world_body = self._render_world(data.get("world") or {})
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            logger.warning(
                "LLM JSON parse failed (%s) — falling back to template", exc
            )
            premise_body = _PREMISE_TEMPLATE
            world_body = _WORLD_TEMPLATE

        return premise_body, world_body

    def _revise_with_llm(
        self, feedback: str, current_premise: str, current_world: str
    ) -> tuple[str, str]:
        from langchain_core.messages import HumanMessage

        from novel_analyzer.llm.client import build_chat_model

        model = build_chat_model(self._settings)
        prompt = (
            "你是讽刺现实风格中文小说的策划助手。根据以下修改意见,修订 premise.md 和 world.md。"
            '返回 JSON: {"premise": "<修订后的 premise 全文>", '
            '"world": "<修订后的 world 全文>"}\n\n'
            f"修改意见:\n{feedback}\n\n"
            f"当前 premise.md:\n{current_premise}\n\n"
            f"当前 world.md:\n{current_world}"
        )
        raw = str(model.invoke([HumanMessage(content=prompt)]).content)
        raw = _filter_banned(raw)

        try:
            data = json.loads(raw)
            new_premise = str(data.get("premise") or current_premise)
            new_world = str(data.get("world") or current_world)
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            logger.warning(
                "LLM revise JSON parse failed (%s) — appending feedback as comment", exc
            )
            comment = f"<!-- 修改意见: {feedback} -->\n"
            new_premise = comment + current_premise
            new_world = comment + current_world

        return new_premise, new_world

    def _render_premise(self, data: dict[str, Any]) -> str:
        def v(key: str) -> str:
            val = str(data.get(key) or "[请填写]").strip() or "[请填写]"
            return _filter_banned(val)

        return (
            f"## 题材\n{v('题材')}\n\n"
            f"## 主旨\n{v('主旨')}\n\n"
            f"## 调性\n{v('调性')}\n\n"
            f"## 核心讽刺引擎\n{v('核心讽刺引擎')}\n\n"
            f"## 与范本的相似/差异轴\n{v('与范本的相似/差异轴')}\n"
        )

    def _render_world(self, data: dict[str, Any]) -> str:
        def v(key: str) -> str:
            val = str(data.get(key) or "[请填写]").strip() or "[请填写]"
            return _filter_banned(val)

        rules_raw = data.get("规则", [])
        if isinstance(rules_raw, list) and rules_raw:
            rules_lines = "\n".join(
                f"- {_filter_banned(str(r))}" for r in rules_raw
            )
        else:
            rules_lines = "- [请填写]"

        nouns_raw = data.get("名词映射", [])
        if isinstance(nouns_raw, list) and nouns_raw:
            rows = "\n".join(
                "| {} | {} |".format(
                    _filter_banned(str(item.get("原", "[请填写]"))),
                    _filter_banned(str(item.get("新", "[请填写]"))),
                )
                for item in nouns_raw
                if isinstance(item, dict)
            )
            noun_table = f"| 原 | 新 |\n|---|---|\n{rows}"
        else:
            noun_table = "| 原 | 新 |\n|---|---|\n| [请填写] | [请填写] |"

        return (
            f"## 世界观底座\n{v('世界观底座')}\n\n"
            f"## 力量体系\n{v('力量体系')}\n\n"
            f"## 经济与权力结构\n{v('经济与权力结构')}\n\n"
            f"## 现代映射\n{v('现代映射')}\n\n"
            f"## 规则\n{rules_lines}\n\n"
            f"## 名词映射\n{noun_table}\n"
        )
