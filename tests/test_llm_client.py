"""LLM client wiring tests."""

from __future__ import annotations

from langchain_core.rate_limiters import InMemoryRateLimiter

from novel_analyzer.config.settings import Settings
from novel_analyzer.llm.client import (
    _build_rate_limiter,
    build_chat_model,
    get_rate_limiter,
)


def _settings(**overrides) -> Settings:
    base = {
        "llm_provider_name": "deepseek",
        "llm_base_url": "http://example.test/v1",
        "llm_api_key": "sk-test",
        "llm_model_name": "claude-haiku-4.5",
    }
    base.update(overrides)
    return Settings(**base)


def test_rate_limiter_disabled_when_rps_zero() -> None:
    settings = _settings(llm_requests_per_second=0.0)
    assert get_rate_limiter(settings) is None
    assert build_chat_model(settings).rate_limiter is None


def test_rate_limiter_enabled_when_rps_positive() -> None:
    settings = _settings(
        llm_requests_per_second=1.5,
        llm_max_bucket_size=3,
        llm_check_every_n_seconds=0.1,
    )
    limiter = get_rate_limiter(settings)
    assert isinstance(limiter, InMemoryRateLimiter)
    assert limiter.requests_per_second == 1.5

    chat = build_chat_model(settings)
    assert isinstance(chat.rate_limiter, InMemoryRateLimiter)


def test_rate_limiter_singleton_per_config() -> None:
    """Same RPS settings must yield the SAME bucket so concurrent callers share it."""
    _build_rate_limiter.cache_clear()
    a = _build_rate_limiter(2.0, 0.1, 5.0)
    b = _build_rate_limiter(2.0, 0.1, 5.0)
    c = _build_rate_limiter(3.0, 0.1, 5.0)
    assert a is b
    assert a is not c


def test_build_chat_model_passes_model_override() -> None:
    settings = _settings(llm_model_name="claude-haiku-4.5")
    chat = build_chat_model(settings, model_name="deepseek-v4-flash")
    assert chat.model_name == "deepseek-v4-flash"


def test_deepseek_models_capped_at_4000_tokens() -> None:
    """Deepseek burns budget on reasoning_tokens; gateway also rejects > 4096."""
    settings = _settings(llm_model_name="deepseek-v4-flash")
    chat = build_chat_model(settings)
    assert chat.max_tokens == 4000

    settings_pro = _settings(llm_model_name="deepseek-v4-pro")
    chat_pro = build_chat_model(settings_pro)
    assert chat_pro.max_tokens == 4000


def test_claude_models_have_no_token_cap() -> None:
    settings = _settings(llm_model_name="claude-haiku-4.5")
    chat = build_chat_model(settings)
    assert chat.max_tokens is None


def test_model_override_drives_cap_not_settings() -> None:
    """Cap is decided by the actually-used model name, not by settings.llm_model_name."""
    settings = _settings(llm_model_name="claude-haiku-4.5")
    chat = build_chat_model(settings, model_name="deepseek-v4-flash")
    assert chat.max_tokens == 4000

    chat_back = build_chat_model(_settings(llm_model_name="deepseek-v4-flash"), model_name="claude-haiku-4.5")
    assert chat_back.max_tokens is None
