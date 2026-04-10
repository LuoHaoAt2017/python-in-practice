from __future__ import annotations

"""练习 5：装饰器（横切关注点）。

装饰器本质上是高阶函数：

    decorator: (func) -> wrapped_func

它允许你在不修改业务函数本体的情况下，复用通用能力（计时、重试、缓存、鉴权等）。

本模块实现：
- `timed`：返回 (result, elapsed_ms)
- `retry`：捕获指定异常后重试
"""

import time
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def timed(func: Callable[P, R]) -> Callable[P, tuple[R, float]]:
    """装饰器：返回 (result, elapsed_ms)。

    注意：使用 `wraps` 保留原函数的元数据（如 __name__/__doc__）。
    """

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
    """装饰器工厂：当捕获到指定异常时，重试调用函数。

    返回的装饰器由 `max_attempts` 与 `exceptions` 配置。
    """

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
                    # 这里集中体现“重试策略”。
                    # 为聚焦练习要点，此处不加入 sleep/backoff 等策略。
                    last_exc = exc
            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator


class FlakyError(RuntimeError):
    """示例 flaky 函数使用的自定义异常。"""

    pass


def make_flaky(counter: dict[str, int]) -> Callable[[], str]:
    """返回一个可调用对象：前两次失败，第三次成功。

    该函数刻意引入状态（会修改 `counter`），以便用确定性的失败模式测试 `retry`。
    """

    def f() -> str:
        counter["n"] += 1
        if counter["n"] < 3:
            raise FlakyError("boom")
        return "ok"

    return f
