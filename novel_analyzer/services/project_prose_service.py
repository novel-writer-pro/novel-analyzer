from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]
from sqlalchemy.orm import Session

from novel_analyzer.config.settings import Settings
from novel_analyzer.domain.project_config import ProjectConfig, load_book_config
from novel_analyzer.services.lock_contract_checker_service import LockContractChecker
from novel_analyzer.services.project_compiler_service import CompiledFlags, ProjectCompilerService
from novel_analyzer.services.project_shell_service import ProjectShellService
from novel_analyzer.services.satire_anti_slop_service import SatireAntiSlopChecker

logger = logging.getLogger(__name__)

_LOOM_ENV_MAP: dict[str, str] = {
    "loom_memory_mode": "NOVEL_ANALYZER_LOOM_MEMORY_MODE",
    "loom_tension_enabled": "NOVEL_ANALYZER_LOOM_TENSION_ENABLED",
    "loom_pairwise_enabled": "NOVEL_ANALYZER_LOOM_PAIRWISE_ENABLED",
    "loom_style_enabled": "NOVEL_ANALYZER_LOOM_STYLE_ENABLED",
    "loom_character_enabled": "NOVEL_ANALYZER_LOOM_CHARACTER_ENABLED",
}

_TEMPLATE_DRAFT = "[请填写正文]"


def _safe_float(d: dict[str, object], key: str) -> float:
    val = d.get(key, 0.0)
    try:
        return float(val)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0


def _extract_loom_signals(skill_outputs: dict[str, dict[str, object]]) -> dict[str, float]:
    tension_sig = skill_outputs.get("_loom_tension") or {}
    style_sig = skill_outputs.get("_loom_style") or {}
    reader_sig = skill_outputs.get("_loom_reader_sim") or {}
    quality_sig = skill_outputs.get("_loom_chapter_quality") or {}
    dialogue_sig = skill_outputs.get("_loom_dialogue") or {}
    return {
        "tension_score": _safe_float(tension_sig, "tension_score"),
        "chapter_quality_score": _safe_float(quality_sig, "chapter_quality_score"),
        "style_drift_score": _safe_float(style_sig, "style_drift_score"),
        "hook_density": _safe_float(style_sig, "hook_density"),
        "dialogue_voice_consistency": _safe_float(dialogue_sig, "dialogue_voice_consistency"),
        "reader_sim_overall": _safe_float(reader_sig, "overall_score"),
    }


def _merge_report_signals(
    chapter_quality_signal: dict[str, object],
    dialogue_signal: dict[str, object],
    rounds_skill_outputs: dict[str, dict[str, object]],
) -> dict[str, float]:
    base = _extract_loom_signals(rounds_skill_outputs)
    cq = _safe_float(chapter_quality_signal, "chapter_quality_score")
    if cq:
        base["chapter_quality_score"] = cq
    dv = _safe_float(dialogue_signal, "dialogue_voice_consistency")
    if dv:
        base["dialogue_voice_consistency"] = dv
    return base


class ProjectProseService:
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

    def generate_chapter(
        self,
        slug: str,
        chapter_idx: int,
        max_rounds: int = 2,
        use_llm: bool = False,
        fast_mode: bool = False,
    ) -> Path:
        cfg = load_book_config(slug, self._base_dir)
        compiler = ProjectCompilerService(base_dir=self._base_dir, shell=self._shell)
        flags = compiler.compile_for_chapter(slug, chapter_idx)
        env_vars = compiler.to_env_vars(flags)

        saved: dict[str, str | None] = {}
        for env_key, val in env_vars.items():
            saved[env_key] = os.environ.get(env_key)
            os.environ[env_key] = val
        try:
            return self._do_generate(
                cfg=cfg,
                slug=slug,
                chapter_idx=chapter_idx,
                flags=flags,
                max_rounds=max_rounds,
                use_llm=use_llm,
                fast_mode=fast_mode,
            )
        finally:
            for env_key, original in saved.items():
                if original is None:
                    os.environ.pop(env_key, None)
                else:
                    os.environ[env_key] = original

    def generate_all(
        self,
        slug: str,
        max_rounds: int = 2,
        use_llm: bool = False,
        fast_mode: bool = False,
    ) -> list[Path]:
        cfg = load_book_config(slug, self._base_dir)
        paths: list[Path] = []
        for idx in range(1, cfg.target_chapters + 1):
            path = self.generate_chapter(
                slug, idx, max_rounds=max_rounds, use_llm=use_llm, fast_mode=fast_mode
            )
            paths.append(path)
        return paths

    def _do_generate(
        self,
        cfg: ProjectConfig,
        slug: str,
        chapter_idx: int,
        flags: CompiledFlags,
        max_rounds: int,
        use_llm: bool,
        fast_mode: bool,
    ) -> Path:
        draft_text, final_verdict, stop_reason, rounds_used, loom_signals = (
            self._run_harness_or_template(
                cfg=cfg,
                chapter_idx=chapter_idx,
                flags=flags,
                max_rounds=max_rounds,
                use_llm=use_llm,
            )
        )

        anti_slop_report = SatireAntiSlopChecker().check_text(draft_text, fast_mode=fast_mode)
        lock_report = LockContractChecker(base_dir=self._base_dir, shell=self._shell).check(
            slug, draft_text
        )

        path = self._write_draft(
            slug=slug,
            chapter_idx=chapter_idx,
            draft_text=draft_text,
            final_verdict=final_verdict,
            stop_reason=stop_reason,
            rounds_used=rounds_used,
            loom_signals=loom_signals,
            anti_slop_verdict=anti_slop_report.verdict,
            lock_contract_verdict=lock_report.verdict,
        )

        self._update_continuity(slug, chapter_idx, draft_text)

        try:
            output_dir = self._base_dir / slug / "chapters"
            pairs_file = Path("output") / "loom-pairs.jsonl"
            logger.info("loom-collect-pairs: would collect from %s to %s", output_dir, pairs_file)
        except Exception as exc:  # noqa: BLE001
            logger.warning("loom-collect-pairs failed (non-fatal): %s", exc)

        return path

    def _run_harness_or_template(
        self,
        cfg: ProjectConfig,
        chapter_idx: int,
        flags: CompiledFlags,
        max_rounds: int,
        use_llm: bool,
    ) -> tuple[str, str, str, int, dict[str, float]]:
        if not use_llm:
            return (_TEMPLATE_DRAFT, "template", "use_llm=False", 0, _extract_loom_signals({}))

        try:
            return self._call_harness(cfg, chapter_idx, flags, max_rounds)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "harness-imitation failed for ch%03d, falling back to template: %s",
                chapter_idx,
                exc,
            )
            return (
                _TEMPLATE_DRAFT,
                "template",
                f"harness_error: {exc}",
                0,
                _extract_loom_signals({}),
            )

    def _call_harness(
        self,
        cfg: ProjectConfig,
        chapter_idx: int,
        flags: CompiledFlags,
        max_rounds: int,
    ) -> tuple[str, str, str, int, dict[str, float]]:
        from novel_analyzer.services.imitation_harness_service import HarnessControllerService

        steering_pack: dict[str, Any] = {
            "worldview_capsule": flags.worldview_note,
            "trope_axes": flags.trope_axes,
            "innovation_directives": flags.innovation_directives,
            "taboo_innovations": flags.taboo_innovations,
            "knowledge_refs": flags.knowledge_refs,
        }

        svc = HarnessControllerService(self._session, self._settings)
        report = svc.run_harness(
            cfg.source_branch_id,
            source_chapter_index=chapter_idx,
            target_goal=flags.target_goal,
            max_rounds=max_rounds,
            use_llm=True,
            steering_pack=steering_pack,
        )

        last_skill_outputs: dict[str, dict[str, object]] = {}
        if report.rounds:
            last_skill_outputs = report.rounds[-1].skill_outputs

        loom_signals = _merge_report_signals(
            chapter_quality_signal=report.chapter_quality_signal,
            dialogue_signal=report.dialogue_signal,
            rounds_skill_outputs=last_skill_outputs,
        )

        return (
            report.final_draft.draft_text or _TEMPLATE_DRAFT,
            report.final_verdict,
            report.stop_reason,
            len(report.rounds),
            loom_signals,
        )

    def _write_draft(
        self,
        slug: str,
        chapter_idx: int,
        draft_text: str,
        final_verdict: str,
        stop_reason: str,
        rounds_used: int,
        loom_signals: dict[str, float],
        anti_slop_verdict: str,
        lock_contract_verdict: str,
    ) -> Path:
        stem = f"ch{chapter_idx:03d}.draft"
        parents = [
            f"chapters/ch{chapter_idx:03d}.outline.md",
            f"chapters/ch{chapter_idx:03d}.storyboard.md",
        ]

        path = self._shell.write_artifact(slug, "chapters", stem, draft_text, parents=parents)

        raw = path.read_text(encoding="utf-8")
        if raw.startswith("---\n"):
            end = raw.find("\n---\n", 4)
            if end != -1:
                fm: dict[str, object] = yaml.safe_load(raw[4:end]) or {}
                body = raw[end + 5:]
            else:
                fm = {}
                body = raw
        else:
            fm = {}
            body = raw

        fm["final_verdict"] = final_verdict
        fm["stop_reason"] = stop_reason
        fm["max_rounds_used"] = rounds_used
        fm["loom_signals"] = loom_signals
        fm["anti_slop_verdict"] = anti_slop_verdict
        fm["lock_contract_verdict"] = lock_contract_verdict

        fm_text = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False)
        path.write_text(f"---\n{fm_text}---\n{body}", encoding="utf-8")
        logger.info("draft written: %s", path)
        return path

    def _update_continuity(self, slug: str, chapter_idx: int, draft_text: str) -> None:
        try:
            continuity_path = self._base_dir / slug / "plot" / "continuity.md"
            continuity_path.parent.mkdir(parents=True, exist_ok=True)
            ts = datetime.now(tz=UTC).isoformat()
            entry = (
                f"\n## ch{chapter_idx:03d} carry-over ({ts})\n\n"
                f"Draft length: {len(draft_text)} chars\n"
            )
            with continuity_path.open("a", encoding="utf-8") as fh:
                fh.write(entry)
        except Exception as exc:  # noqa: BLE001
            logger.warning("continuity update failed (non-fatal): %s", exc)
