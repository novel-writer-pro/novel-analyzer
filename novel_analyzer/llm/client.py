"""LLM client helpers."""

from __future__ import annotations

from functools import lru_cache

from langchain_core.rate_limiters import BaseRateLimiter, InMemoryRateLimiter
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from novel_analyzer.config.settings import Settings, get_settings


# Provider-specific completion-budget caps. Some upstream gateways reject
# requests above these limits or, like deepseek-v4-*, silently spend the
# budget on reasoning_tokens before emitting any visible content.
_DEEPSEEK_MAX_OUTPUT_TOKENS = 4000


def _resolve_max_tokens(model_name: str) -> int | None:
    """Return a max_tokens cap appropriate to the model family, else None."""
    name = (model_name or "").lower()
    if "deepseek" in name:
        return _DEEPSEEK_MAX_OUTPUT_TOKENS
    return None


@lru_cache(maxsize=4)
def _build_rate_limiter(
    rps: float,
    check_every: float,
    max_bucket: float,
) -> BaseRateLimiter:
    """Token-bucket rate limiter, cached so all chat models share a single bucket."""
    return InMemoryRateLimiter(
        requests_per_second=rps,
        check_every_n_seconds=check_every,
        max_bucket_size=max_bucket,
    )


def get_rate_limiter(settings: Settings | None = None) -> BaseRateLimiter | None:
    """Return a shared rate limiter when configured, else None."""
    runtime = settings or get_settings()
    if runtime.llm_requests_per_second <= 0:
        return None
    return _build_rate_limiter(
        runtime.llm_requests_per_second,
        runtime.llm_check_every_n_seconds,
        runtime.llm_max_bucket_size,
    )


def build_chat_model(
    settings: Settings | None = None,
    *,
    model_name: str | None = None,
) -> ChatOpenAI:
    """Create the configured ChatOpenAI client.

    When ``NOVEL_ANALYZER_LLM_REQUESTS_PER_SECOND > 0`` the client wears a shared
    token-bucket rate limiter so every concurrent caller respects the upstream RPS
    cap (LangChain ``InMemoryRateLimiter``). The bucket is process-wide and cached.

    Per-provider output caps: deepseek-* models are capped at 4000 max_tokens,
    because the upstream gateway rejects > 4096 and the model otherwise burns
    the entire budget on reasoning_tokens (see deepseek-v4-flash empirical run
    2026-05-16: 273 completion tokens, 265 of them reasoning).
    """

    runtime = settings or get_settings()
    api_key_value = runtime.resolved_llm_api_key
    api_key = SecretStr(api_key_value) if api_key_value else None
    base_url = runtime.llm_base_url_override or runtime.resolved_llm_base_url
    resolved_model = model_name or runtime.llm_model_name
    kwargs: dict[str, object] = {
        "model": resolved_model,
        "base_url": base_url,
        "api_key": api_key,
        "timeout": runtime.llm_timeout_seconds,
        "max_retries": runtime.llm_max_retries,
        "rate_limiter": get_rate_limiter(runtime),
    }
    cap = _resolve_max_tokens(resolved_model)
    if cap is not None:
        kwargs["max_tokens"] = cap
    return ChatOpenAI(**kwargs)
