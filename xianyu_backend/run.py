from __future__ import annotations

import argparse
import asyncio
import os
import socket
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import uvicorn
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT)

from app.shared.config import settings  # noqa: E402


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str
    blocking: bool = True


def mask_url(raw_url: str) -> str:
    parsed = urlparse(raw_url)

    if not parsed.password:
        return raw_url

    username = parsed.username or ""
    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    auth = f"{username}:***@" if username else ""
    return parsed._replace(netloc=f"{auth}{hostname}{port}").geturl()


async def check_postgres(timeout: float) -> CheckResult:
    engine = create_async_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        connect_args={"timeout": timeout},
    )

    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return CheckResult(
            name="PostgreSQL",
            ok=True,
            detail=f"connected: {mask_url(settings.DATABASE_URL)}",
        )
    except Exception as exc:
        return CheckResult(
            name="PostgreSQL",
            ok=False,
            detail=f"{type(exc).__name__}: {exc}",
        )
    finally:
        await engine.dispose()


def check_tcp_service(name: str, host: str, port: int, timeout: float) -> CheckResult:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            pass
        return CheckResult(
            name=name,
            ok=True,
            detail=f"tcp reachable: {host}:{port}",
        )
    except OSError as exc:
        return CheckResult(
            name=name,
            ok=False,
            detail=f"{type(exc).__name__}: {exc}",
        )


def check_postgres_tcp(timeout: float) -> CheckResult:
    parsed = urlparse(settings.DATABASE_URL)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 5432
    return check_tcp_service("PostgreSQL TCP", host, port, timeout)


def check_redis(redis_url: str, timeout: float) -> CheckResult:
    parsed = urlparse(redis_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 6379

    return check_tcp_service("Redis TCP", host, port, timeout)


def print_result(result: CheckResult) -> None:
    if result.ok:
        marker = "OK"
    elif result.blocking:
        marker = "FAIL"
    else:
        marker = "WARN"
    print(f"[{marker}] {result.name}: {result.detail}")


async def run_preflight(args: argparse.Namespace) -> int:
    results: list[CheckResult] = []

    if not args.skip_db_check:
        postgres_tcp = check_postgres_tcp(args.timeout)
        results.append(postgres_tcp)
        if postgres_tcp.ok:
            results.append(await check_postgres(args.timeout))
    else:
        print("[SKIP] PostgreSQL: disabled by --skip-db-check")

    redis_url = args.redis_url or os.getenv("REDIS_URL")
    if redis_url:
        results.append(check_redis(redis_url, args.timeout))
    else:
        print("[SKIP] Redis: no REDIS_URL configured")

    for result in results:
        print_result(result)

    return 0 if all(result.ok or not result.blocking for result in results) else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Development runner for Xianyu backend.")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "7000")))
    parser.add_argument("--reload", action="store_true", help="Enable uvicorn reload mode.")
    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "info"))
    parser.add_argument("--check-only", action="store_true", help="Run service checks without starting API.")
    parser.add_argument("--skip-db-check", action="store_true", help="Start API without checking PostgreSQL.")
    parser.add_argument("--redis-url", default=None, help="Optional Redis URL for TCP reachability check.")
    parser.add_argument("--timeout", type=float, default=3.0, help="Service check timeout in seconds.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    check_code = asyncio.run(run_preflight(args))

    if check_code != 0:
        print("Preflight checks failed. Fix the service above or use --skip-db-check when appropriate.")
        return check_code

    if args.check_only:
        return 0

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
