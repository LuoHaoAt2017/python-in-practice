from __future__ import annotations

"""练习 2：用“规则注入”理解高阶函数。

我们把稳定的“框架函数”（`validate`）与易变的业务逻辑（rules）解耦。
每条规则就是一个函数，这会让校验逻辑：

- 易扩展：新增规则不需要修改 `validate`
- 易测试：规则函数确定性强（输入固定，输出可预测）
- 易组合：小规则可组合成大规则（复用能力强）
"""

from collections.abc import Callable, Sequence
from typing import TypeVar

T = TypeVar("T")
Rule = Callable[[T], tuple[bool, str]]


def validate(value: T, rules: Sequence[Rule[T]]) -> list[str]:
    """按顺序执行规则，并收集失败信息。

    这里刻意不包含任何具体业务判断：
    `validate` 只负责“协调执行 + 汇总错误”，业务约束全部通过 `rules` 传入。
    """

    errors: list[str] = []
    for rule in rules:
        ok, message = rule(value)
        if not ok:
            errors.append(message)
    return errors


def compose_rules(*rules: Rule[T]) -> Rule[T]:
    """把多条规则组合成一条规则，并聚合失败信息。

    返回约定：
    - 全部通过：返回 (True, "")
    - 存在失败：返回 (False, "msg1; msg2; ...")
    """

    def composed(value: T) -> tuple[bool, str]:
        messages: list[str] = []
        for rule in rules:
            ok, message = rule(value)
            if not ok:
                messages.append(message)
        if messages:
            return False, "; ".join(messages)
        return True, ""

    return composed


def not_empty(s: str) -> tuple[bool, str]:
    """规则：去掉首尾空白后不能为空。"""
    return (bool(s.strip()), "must not be empty")


def min_len(n: int) -> Rule[str]:
    """规则工厂：生成“最小长度为 n”的规则。"""
    def rule(s: str) -> tuple[bool, str]:
        return (len(s) >= n, f"length must be >= {n}")

    return rule


def no_space(s: str) -> tuple[bool, str]:
    """规则：不允许包含空格（适用于用户名、标识符等）。"""
    return (" " not in s, "must not contain spaces")
