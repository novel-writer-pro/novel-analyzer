#!/usr/bin/env python3
"""End-to-end smoke check for external dependencies.

Verifies that the four external services declared in .env / .env.local are
actually reachable and behave as expected:

  1. PostgreSQL        - connect, run SELECT 1, check pg_trgm / pgvector / pg_jieba
  2. LLM provider      - GET {base}/models with the configured API key
  3. Embedding (TEI)   - POST /embed and check returned dim
  4. Rerank (TEI)      - POST /rerank and check ordering

Exit code 0 if every required check passes, 1 otherwise.
Optional checks (rerank when backend != http/tei) are reported as SKIP.

Usage:
    .venv/bin/python scripts/dev/smoke-external.py
    .venv/bin/python scripts/dev/smoke-external.py --skip llm
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class C:
    G = "\033[92m"
    R = "\033[91m"
    Y = "\033[93m"
    B = "\033[94m"
    DIM = "\033[2m"
    RST = "\033[0m"
    BOLD = "\033[1m"


def _print_header(text: str) -> None:
    bar = "=" * 64
    print(f"\n{C.BOLD}{C.B}{bar}\n{text}\n{bar}{C.RST}\n")


def _print_check(name: str, status: str, detail: str = "", fix: str = "") -> None:
    icon = {"PASS": f"{C.G}✓{C.RST}", "FAIL": f"{C.R}✗{C.RST}", "SKIP": f"{C.Y}–{C.RST}"}[status]
    print(f"{icon} {name}")
    if detail:
        print(f"  {C.DIM}{detail}{C.RST}")
    if status == "FAIL" and fix:
        print(f"  {C.Y}→ {fix}{C.RST}")


def check_settings() -> tuple[str, str, Any]:
    try:
        from novel_analyzer.config.settings import get_settings
        settings = get_settings()
        masked = settings.masked_database_url
        return "PASS", f"db={masked}  llm={settings.resolved_llm_base_url}", settings
    except Exception as exc:
        return "FAIL", f"{type(exc).__name__}: {exc}", None


def check_database(settings: Any) -> tuple[str, str, str]:
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(settings.resolved_database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            ext_rows = conn.execute(
                text("SELECT extname FROM pg_extension")
            ).fetchall()
        ext_names = {row[0] for row in ext_rows}
        required = {"pg_trgm", "vector"}
        optional = {"pg_jieba"}
        missing = required - ext_names
        missing_opt = optional - ext_names
        detail = f"connected, ext={sorted(ext_names & (required | optional))}"
        if missing:
            return ("FAIL", f"{detail}, missing={sorted(missing)}",
                    f"CREATE EXTENSION {', '.join(sorted(missing))};")
        if missing_opt:
            return "PASS", f"{detail}  {C.Y}(optional missing: {sorted(missing_opt)}){C.RST}", ""
        return "PASS", detail, ""
    except Exception as exc:
        return ("FAIL", f"{type(exc).__name__}: {exc}",
                "Check DB host/port/user/password and that the database exists")


def check_llm(settings: Any) -> tuple[str, str, str]:
    base = (settings.llm_base_url_override or settings.resolved_llm_base_url or "").rstrip("/")
    if not base:
        return "FAIL", "no llm_base_url configured", "Set NOVEL_ANALYZER_LLM_BASE_URL"
    api_key = settings.resolved_llm_api_key or ""
    if not api_key:
        return "FAIL", "no llm_api_key configured", "Set NOVEL_ANALYZER_LLM_API_KEY"

    url = f"{base}/models"
    try:
        req = urllib.request.Request(url, method="GET")
        req.add_header("Authorization", f"Bearer {api_key}")
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            if resp.status != 200:
                return "FAIL", f"HTTP {resp.status} from {url}", "Check API key and base URL"
        try:
            data = json.loads(body)
            count = len(data.get("data", [])) if isinstance(data, dict) else 0
            return "PASS", f"{url} -> 200, models={count}", ""
        except json.JSONDecodeError:
            return "PASS", f"{url} -> 200 (non-json body)", ""
    except urllib.error.HTTPError as exc:
        return ("FAIL", f"HTTP {exc.code} from {url}: {exc.reason}",
                "Verify API key and that the provider exposes /models")
    except Exception as exc:
        return "FAIL", f"{type(exc).__name__}: {exc}", f"Cannot reach {url}"


def check_embedding(settings: Any) -> tuple[str, str, str]:
    backend = settings.embedding_backend
    if backend not in ("http", "openai"):
        return "SKIP", f"backend={backend} (no external embedding endpoint to probe)", ""
    base = settings.embedding_api_base.rstrip("/")
    if not base:
        return "FAIL", "embedding_api_base empty", "Set NOVEL_ANALYZER_EMBEDDING_API_BASE"

    fmt = settings.embedding_api_format
    if fmt == "tei":
        url = f"{base}/embed"
        body = {"inputs": ["smoke test"]}
    else:
        url = f"{base}/v1/embeddings"
        body = {"model": settings.embedding_model_name, "input": ["smoke test"]}

    try:
        req = urllib.request.Request(
            url, data=json.dumps(body).encode("utf-8"), method="POST",
            headers={"Content-Type": "application/json"},
        )
        if settings.embedding_api_key:
            req.add_header("Authorization", f"Bearer {settings.embedding_api_key}")
        with urllib.request.urlopen(req, timeout=settings.embedding_http_timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if fmt == "tei":
            vec = data[0] if isinstance(data, list) else None
        else:
            vec = data["data"][0]["embedding"]
        if not vec or not isinstance(vec, list):
            return "FAIL", f"unexpected response shape from {url}", "Check api_format setting"
        return "PASS", f"{fmt} {url} -> dim={len(vec)}", ""
    except urllib.error.HTTPError as exc:
        return ("FAIL", f"HTTP {exc.code} from {url}: {exc.reason}",
                f"Verify {fmt} server is up and accepts the request shape")
    except Exception as exc:
        return "FAIL", f"{type(exc).__name__}: {exc}", f"Cannot reach {url}"


def check_rerank(settings: Any) -> tuple[str, str, str]:
    backend = settings.rerank_backend
    if backend not in ("http", "tei"):
        return "SKIP", f"backend={backend} (no external rerank endpoint to probe)", ""
    base = settings.rerank_api_base.rstrip("/")
    if not base:
        return "FAIL", "rerank_api_base empty", "Set NOVEL_ANALYZER_RERANK_API_BASE"

    url = f"{base}/rerank"
    body = {
        "query": "machine learning algorithms",
        "texts": ["AI and ML are related fields", "today I cooked pasta for dinner"],
        "raw_scores": False,
        "return_text": False,
        "truncate": True,
    }
    try:
        req = urllib.request.Request(
            url, data=json.dumps(body).encode("utf-8"), method="POST",
            headers={"Content-Type": "application/json"},
        )
        if settings.rerank_api_key:
            req.add_header("Authorization", f"Bearer {settings.rerank_api_key}")
        with urllib.request.urlopen(req, timeout=settings.rerank_http_timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        scores = {item["index"]: item["score"] for item in data}
        ml_score = scores.get(0, 0.0)
        food_score = scores.get(1, 0.0)
        ok = ml_score > food_score
        detail = f"{url} -> ml={ml_score:.3f}, food={food_score:.3f}"
        if not ok:
            return "FAIL", detail, "Rerank ordering wrong - check model is bge-reranker-v2-m3"
        return "PASS", detail, ""
    except urllib.error.HTTPError as exc:
        return ("FAIL", f"HTTP {exc.code} from {url}: {exc.reason}",
                "Verify TEI rerank server is up")
    except Exception as exc:
        return "FAIL", f"{type(exc).__name__}: {exc}", f"Cannot reach {url}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--skip", action="append", default=[],
        choices=["db", "llm", "embedding", "rerank"],
        help="Skip a specific check (repeatable)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skip = set(args.skip)

    _print_header("Smoke Test - External Dependencies")
    overall_start = time.time()

    print(f"{C.BOLD}[0/5] Loading settings{C.RST}")
    status, detail, settings = check_settings()
    _print_check("Settings load (.env / .env.local)", status, detail,
                 "Check pydantic validation errors above")
    if status != "PASS" or settings is None:
        print(f"\n{C.R}Cannot continue without valid settings.{C.RST}\n")
        return 1

    failures: list[str] = []

    def run(idx: int, name: str, key: str, fn) -> None:
        print(f"\n{C.BOLD}[{idx}/5] {name}{C.RST}")
        if key in skip:
            _print_check(name, "SKIP", "explicitly skipped via --skip")
            return
        t0 = time.time()
        s, d, fix = fn(settings)
        elapsed = (time.time() - t0) * 1000
        d_full = f"{d}  {C.DIM}({elapsed:.0f}ms){C.RST}" if d else f"({elapsed:.0f}ms)"
        _print_check(name, s, d_full, fix)
        if s == "FAIL":
            failures.append(name)

    run(1, "PostgreSQL connectivity + extensions", "db", check_database)
    run(2, "LLM provider /models", "llm", check_llm)
    run(3, "Embedding HTTP backend", "embedding", check_embedding)
    run(4, "Rerank HTTP backend", "rerank", check_rerank)

    elapsed_total = time.time() - overall_start
    print(f"\n{C.BOLD}{'=' * 64}{C.RST}")
    if not failures:
        print(f"{C.G}{C.BOLD}✓ All external checks passed{C.RST}  ({elapsed_total:.1f}s)")
        print(f"{C.BOLD}{'=' * 64}{C.RST}\n")
        return 0
    print(f"{C.R}{C.BOLD}✗ {len(failures)} check(s) failed: {failures}{C.RST}  ({elapsed_total:.1f}s)")
    print(f"{C.Y}See README.md '环境变量' section and .env.example for configuration.{C.RST}")
    print(f"{C.BOLD}{'=' * 64}{C.RST}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
