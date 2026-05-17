"""Loom Phase 6 T4: Style fingerprint VIEW service.

Aggregates StyleCalibrationService + RhythmAnalysisService outputs into:
  - style/fingerprint.md  — human-readable markdown report
  - style/heuristics.json — machine-readable metrics dict

No heuristics are re-implemented here; this is a pure VIEW layer over
existing Loom Phase 4 services.
"""

from __future__ import annotations

import json
import logging
import statistics
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from novel_analyzer.domain.project_config import load_book_config
from novel_analyzer.services.project_shell_service import ProjectShellService
from novel_analyzer.services.rhythm_analysis_service import RhythmAnalysisService
from novel_analyzer.services.style_calibration_service import StyleCalibrationService

logger = logging.getLogger(__name__)


class ProjectStyleViewService:
    """Render style/rhythm signals to markdown + JSON for a project."""

    def __init__(
        self,
        session: Session,
        base_dir: Path = Path("output/projects"),
        shell: ProjectShellService | None = None,
    ) -> None:
        self._session = session
        self._base_dir = base_dir
        self._shell = shell or ProjectShellService(base_dir=base_dir)
        self._style_svc = StyleCalibrationService(session=session)
        self._rhythm_svc = RhythmAnalysisService(session=session)

    def generate_fingerprint(
        self,
        slug: str,
        sample_chapters: list[int] | None = None,
    ) -> dict[str, Any]:
        cfg = load_book_config(slug, self._base_dir)
        branch_id = cfg.source_branch_id
        chapters = sample_chapters if sample_chapters is not None else cfg.source_chapters_for_style

        style_drifts: list[float] = []
        hook_densities: list[float] = []
        climax_scores: list[float] = []

        for chapter_idx in chapters:
            try:
                metrics = self._compute_chapter_metrics(branch_id, chapter_idx)
                style_drifts.append(metrics["style_drift_score"])
                hook_densities.append(metrics["hook_density"])
                climax_scores.append(metrics["climax_score"])
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Skipping chapter %d for slug %r: %s",
                    chapter_idx,
                    slug,
                    exc,
                )

        n = len(style_drifts)
        heuristics: dict[str, Any] = {
            "slug": slug,
            "branch_id": branch_id,
            "chapters_analyzed": n,
            "median_style_drift": round(statistics.median(style_drifts), 4) if n else 0.0,
            "median_hook_density": round(statistics.median(hook_densities), 4) if n else 0.0,
            "median_climax_score": round(statistics.median(climax_scores), 4) if n else 0.0,
        }

        markdown_body = self._render_fingerprint_md(heuristics)
        self._shell.write_artifact(slug, "style", "fingerprint", markdown_body, parents=[])

        json_path = self._base_dir / slug / "style" / "heuristics.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(self._build_heuristics_json(heuristics), encoding="utf-8")

        return heuristics

    def _compute_chapter_metrics(
        self, branch_id: str, chapter_idx: int
    ) -> dict[str, float]:
        """Call Phase 4 services and return raw metrics for one chapter.

        Raises on any service failure so the caller can skip gracefully.
        """
        drift_result = self._style_svc.compute_style_drift(branch_id, chapter_idx)
        rhythm_result = self._rhythm_svc.compute(branch_id, chapter_idx)
        return {
            "style_drift_score": drift_result.style_drift_score,
            "hook_density": rhythm_result.hook_density,
            "climax_score": rhythm_result.climax_score,
        }

    def _render_fingerprint_md(self, heuristics: dict[str, Any]) -> str:
        n = heuristics.get("chapters_analyzed", 0)
        drift = heuristics.get("median_style_drift", 0.0)
        hook = heuristics.get("median_hook_density", 0.0)
        climax = heuristics.get("median_climax_score", 0.0)

        drift_lo = round(float(drift) * 0.8, 4)
        drift_hi = round(float(drift) * 1.2, 4)
        hook_lo = round(float(hook) * 0.8, 4)
        hook_hi = round(float(hook) * 1.2, 4)
        climax_lo = round(float(climax) * 0.8, 4)
        climax_hi = round(float(climax) * 1.2, 4)

        return f"""\
## 风格向量 + 节奏指纹

| 指标 | 值 | 说明 |
|---|---|---|
| chapters_analyzed | {n} | 采样章节数 |
| median_style_drift | {drift} | 风格漂移中位数(越低越稳定) |
| median_hook_density | {hook} | 钩子密度(每千字事件数) |
| median_climax_score | {climax} | 高潮密度评分 |

## 范本基线 ±20% 阈值

| 指标 | 下限 | 基线 | 上限 |
|---|---|---|---|
| median_style_drift | {drift_lo} | {drift} | {drift_hi} |
| median_hook_density | {hook_lo} | {hook} | {hook_hi} |
| median_climax_score | {climax_lo} | {climax} | {climax_hi} |

## 调性提示(讽刺文专属)

- 内心独白比例目标: 35-45%
- 反讽词节制使用,每章 1-3 次
- 3 拍冲突结构(平庸 setup → 权力揭示 → 讽刺反转)
- 章末钩子三选一(悬念问句/模棱两可/新威胁)
"""

    def _build_heuristics_json(self, heuristics: dict[str, Any]) -> str:
        return json.dumps(heuristics, indent=2, ensure_ascii=False)
