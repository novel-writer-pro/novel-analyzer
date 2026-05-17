from __future__ import annotations

import contextlib
import logging
import os
from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from novel_analyzer.database.models import ChapterArtifact, RunBranch
from novel_analyzer.domain.project_config import (
    ProjectConfig,
    default_config,
    load_book_config,
    save_book_config,
)

logger = logging.getLogger(__name__)

_LOOM_ENV_MAP = {
    "memory_mode": "NOVEL_ANALYZER_LOOM_MEMORY_MODE",
    "tension_enabled": "NOVEL_ANALYZER_LOOM_TENSION_ENABLED",
    "pairwise_enabled": "NOVEL_ANALYZER_LOOM_PAIRWISE_ENABLED",
    "style_enabled": "NOVEL_ANALYZER_LOOM_STYLE_ENABLED",
    "character_enabled": "NOVEL_ANALYZER_LOOM_CHARACTER_ENABLED",
}

_SUBDIRS = ("style", "macro", "characters", "plot", "conflicts", "chapters", "runs")


class ProjectArtifactLockedError(Exception):
    pass


class SourceBranchNotReadyError(Exception):
    pass


class ArtifactVersion(BaseModel):
    version: int
    path: Path
    created_at: datetime


class ProjectShellService:
    def __init__(
        self,
        base_dir: Path = Path("output/projects"),
        session: Session | None = None,
    ) -> None:
        self._base_dir = base_dir
        self._session = session

    def _project_dir(self, slug: str) -> Path:
        return self._base_dir / slug

    def _locked_yaml_path(self, slug: str) -> Path:
        return self._project_dir(slug) / "locked.yaml"

    def _artifact_path(self, slug: str, stage: str, name: str) -> Path:
        return self._project_dir(slug) / stage / f"{name}.md"

    def init(self, slug: str, source_branch_id: str, **opts: object) -> ProjectConfig:
        project_dir = self._project_dir(slug)
        project_dir.mkdir(parents=True, exist_ok=True)
        for subdir in _SUBDIRS:
            (project_dir / subdir).mkdir(exist_ok=True)

        locked_path = self._locked_yaml_path(slug)
        if not locked_path.exists():
            with locked_path.open("w", encoding="utf-8") as fh:
                yaml.safe_dump({"locked": []}, fh)

        cfg = default_config(slug, source_branch_id)
        for key, val in opts.items():
            if hasattr(cfg, key):
                object.__setattr__(cfg, key, val)
        save_book_config(cfg, self._base_dir)
        return cfg

    def read_artifact(self, slug: str, stage: str, name: str) -> str:
        _, body = self.read_artifact_with_frontmatter(slug, stage, name)
        return body

    def read_artifact_with_frontmatter(
        self, slug: str, stage: str, name: str
    ) -> tuple[dict[str, object], str]:
        path = self._artifact_path(slug, stage, name)
        raw = path.read_text(encoding="utf-8")
        if raw.startswith("---\n"):
            end = raw.find("\n---\n", 4)
            if end != -1:
                fm_text = raw[4:end]
                body = raw[end + 5:]
                fm = yaml.safe_load(fm_text) or {}
                return fm, body
        return {}, raw

    def write_artifact(
        self,
        slug: str,
        stage: str,
        name: str,
        content: str,
        parents: list[str] | None = None,
        lock_assertions: list[str] | None = None,
    ) -> Path:
        rel = f"{stage}/{name}.md"
        if self.is_locked(slug, rel):
            raise ProjectArtifactLockedError(f"{rel} is locked in project {slug!r}")

        path = self._artifact_path(slug, stage, name)
        version = 1

        if path.exists():
            existing_fm, _ = self.read_artifact_with_frontmatter(slug, stage, name)
            version = int(existing_fm.get("version", 1) or 1)  # type: ignore[call-overload]
            version += 1
            ts = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
            archive_dir = self._project_dir(slug) / "runs" / ts / stage
            archive_dir.mkdir(parents=True, exist_ok=True)
            archive_path = archive_dir / f"{name}.md"
            archive_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

        fm: dict[str, object] = {
            "stage": stage,
            "version": version,
            "parents": parents or [],
            "locked": False,
            "lock_assertions": lock_assertions or [],
            "generated_at": datetime.now(tz=UTC).isoformat(),
        }
        fm_text = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False)
        full = f"---\n{fm_text}---\n{content}"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(full, encoding="utf-8")
        return path

    def list_versions(self, slug: str, stage: str, name: str) -> list[ArtifactVersion]:
        runs_dir = self._project_dir(slug) / "runs"
        versions: list[ArtifactVersion] = []
        if not runs_dir.exists():
            return versions
        for ts_dir in sorted(runs_dir.iterdir()):
            candidate = ts_dir / stage / f"{name}.md"
            if candidate.exists():
                fm, _ = self._parse_frontmatter(candidate.read_text(encoding="utf-8"))
                ver = int(fm.get("version", 0) or 0)  # type: ignore[call-overload]
                created_raw = fm.get("generated_at", "")
                try:
                    created_at = datetime.fromisoformat(str(created_raw))
                except (ValueError, TypeError):
                    created_at = datetime.fromtimestamp(candidate.stat().st_mtime, tz=UTC)
                versions.append(ArtifactVersion(version=ver, path=candidate, created_at=created_at))
        return versions

    def lock(self, slug: str, file_glob: str) -> list[str]:
        return self._set_locked(slug, file_glob, locked=True)

    def unlock(self, slug: str, file_glob: str) -> list[str]:
        return self._set_locked(slug, file_glob, locked=False)

    def is_locked(self, slug: str, relpath: str) -> bool:
        locked_path = self._locked_yaml_path(slug)
        if not locked_path.exists():
            return False
        with locked_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        return relpath in (data.get("locked") or [])

    def list_locked_assertions(self, slug: str) -> list[str]:
        project_dir = self._project_dir(slug)
        assertions: list[str] = []
        for md_file in project_dir.rglob("*.md"):
            if "runs" in md_file.parts:
                continue
            fm, _ = self._parse_frontmatter(md_file.read_text(encoding="utf-8"))
            if fm.get("locked") and fm.get("lock_assertions"):
                assertions.extend(fm["lock_assertions"])  # type: ignore[arg-type]
        return assertions

    @contextlib.contextmanager
    def apply_loom_flags(self, slug: str) -> Generator[None, None, None]:
        cfg = load_book_config(slug, self._base_dir)
        flags = cfg.loom_flags
        saved: dict[str, str | None] = {}
        try:
            for field, env_key in _LOOM_ENV_MAP.items():
                saved[env_key] = os.environ.get(env_key)
                val = getattr(flags, field)
                os.environ[env_key] = str(val).lower() if isinstance(val, bool) else str(val)
            yield
        finally:
            for env_key, original in saved.items():
                if original is None:
                    os.environ.pop(env_key, None)
                else:
                    os.environ[env_key] = original

    def ensure_source_branch(self, slug: str) -> str:
        if self._session is None:
            raise RuntimeError("ProjectShellService requires a session for DB operations")
        cfg = load_book_config(slug, self._base_dir)
        branch_id = cfg.source_branch_id
        required = max(cfg.source_chapters_for_style) if cfg.source_chapters_for_style else 1

        branch = self._session.scalar(select(RunBranch).where(RunBranch.id == branch_id))
        count: int = (
            self._session.scalar(
                select(func.count(ChapterArtifact.id)).where(  # type: ignore[arg-type, unused-ignore]
                    ChapterArtifact.branch_id == branch_id
                )
            )
            or 0
        )

        if branch is None or count < required:
            raise SourceBranchNotReadyError(
                f"Source branch '{branch_id}' not ready"
                f" (found {count} chapters, need {required}).\n"
                "Please run: .venv/bin/novel-analyzer auto-run <txt_path> --max-chapters 30"
            )
        return branch_id

    def sample_source_chapters(self, slug: str, indices: list[int]) -> list[ChapterArtifact]:
        if self._session is None:
            raise RuntimeError("ProjectShellService requires a session for DB operations")
        branch_id = self.ensure_source_branch(slug)
        results: list[ChapterArtifact] = []
        for idx in indices:
            artifact = self._session.scalar(
                select(ChapterArtifact)
                .where(ChapterArtifact.branch_id == branch_id)
                .where(ChapterArtifact.chapter_index == idx)
            )
            if artifact is None:
                logger.warning(
                    "sample_source_chapters: chapter index %d not found in branch %s, skipping",
                    idx,
                    branch_id,
                )
            else:
                results.append(artifact)
        return results

    def _set_locked(self, slug: str, file_glob: str, *, locked: bool) -> list[str]:
        import fnmatch
        project_dir = self._project_dir(slug)
        locked_path = self._locked_yaml_path(slug)

        with locked_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        locked_set: set[str] = set(data.get("locked") or [])

        matched: list[str] = []
        for md_file in project_dir.rglob("*.md"):
            if "runs" in md_file.parts:
                continue
            rel = str(md_file.relative_to(project_dir))
            if fnmatch.fnmatch(rel, file_glob):
                matched.append(rel)
                if locked:
                    locked_set.add(rel)
                else:
                    locked_set.discard(rel)
                self._patch_frontmatter_locked(md_file, locked)

        data["locked"] = sorted(locked_set)
        with locked_path.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(data, fh, allow_unicode=True)
        return matched

    def _patch_frontmatter_locked(self, path: Path, locked: bool) -> None:
        raw = path.read_text(encoding="utf-8")
        fm, body = self._parse_frontmatter(raw)
        fm["locked"] = locked
        fm_text = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False)
        path.write_text(f"---\n{fm_text}---\n{body}", encoding="utf-8")

    @staticmethod
    def _parse_frontmatter(raw: str) -> tuple[dict[str, object], str]:
        if raw.startswith("---\n"):
            end = raw.find("\n---\n", 4)
            if end != -1:
                fm = yaml.safe_load(raw[4:end]) or {}
                return fm, raw[end + 5:]
        return {}, raw
