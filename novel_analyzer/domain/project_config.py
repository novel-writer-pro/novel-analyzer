from __future__ import annotations

import re
from pathlib import Path
from typing import Literal, cast

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, Field, field_validator

Stage = Literal[
    "style",
    "macro",
    "characters",
    "plot",
    "conflicts",
    "outline",
    "storyboard",
    "prose",
]

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


class LoomFlagsConfig(BaseModel):
    """Per-project Loom feature flags.

    Defaults to ALL ENABLED — project shell is explicit opt-in,
    unlike the global shadow default in Settings.
    """

    memory_mode: str = "enabled"
    tension_enabled: bool = True
    pairwise_enabled: bool = True
    style_enabled: bool = True
    character_enabled: bool = True


class ProjectConfig(BaseModel):
    name: str
    slug: str = Field(..., description="URL-safe project identifier")
    source_branch_id: str
    source_chapters_for_style: list[int] = Field(
        default_factory=lambda: list(range(1, 31))
    )
    target_chapters: int = 3
    gates: list[Stage] = Field(
        default_factory=lambda: cast(
            list[Stage], ["macro", "characters", "plot", "outline", "prose"]
        )
    )
    auto_pass: list[Stage] = Field(
        default_factory=lambda: cast(list[Stage], ["conflicts", "storyboard"])
    )
    locked_files: list[str] = Field(default_factory=list)
    loom_flags: LoomFlagsConfig = Field(default_factory=LoomFlagsConfig)

    @field_validator("slug")
    @classmethod
    def _validate_slug(cls, v: str) -> str:
        if not _SLUG_RE.match(v):
            raise ValueError(
                f"slug must match ^[a-z0-9][a-z0-9_-]*$ — got {v!r}"
            )
        return v


def load_book_config(
    slug: str,
    base_dir: Path = Path("output/projects"),
) -> ProjectConfig:
    config_path = base_dir / slug / "book.config.yaml"
    with config_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return ProjectConfig.model_validate(data)


def save_book_config(
    cfg: ProjectConfig,
    base_dir: Path = Path("output/projects"),
) -> Path:
    project_dir = base_dir / cfg.slug
    project_dir.mkdir(parents=True, exist_ok=True)
    config_path = project_dir / "book.config.yaml"
    with config_path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(cfg.model_dump(), fh, allow_unicode=True, sort_keys=False)
    return config_path


def default_config(slug: str, source_branch_id: str) -> ProjectConfig:
    return ProjectConfig(
        name=slug,
        slug=slug,
        source_branch_id=source_branch_id,
    )
