from __future__ import annotations

import time
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def timed(func: Callable[P, R]) -> Callable[P, tuple[R, float]]:
    """Decorator: return (result, elapsed_ms)."""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> tuple[R, float]:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return result, elapsed_ms

    return wrapper


def retry(
    max_attempts: int,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator factory: retry calling func when exceptions are raised."""

    if max_attempts <= 0:
        raise ValueError("max_attempts must be > 0")

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exc: BaseException | None = None
            for _ in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator


class FlakyError(RuntimeError):
    pass


def make_flaky(counter: dict[str, int]) -> Callable[[], str]:
    """Return a callable that fails twice, then succeeds."""

    def f() -> str:
        counter["n"] += 1
        if counter["n"] < 3:
            raise FlakyError("boom")
        return "ok"

    return f
