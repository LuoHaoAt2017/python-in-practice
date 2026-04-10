from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeVar

T = TypeVar("T")
Rule = Callable[[T], tuple[bool, str]]


def validate(value: T, rules: Sequence[Rule[T]]) -> list[str]:
    """Run rules in order and collect messages from failures."""

    errors: list[str] = []
    for rule in rules:
        ok, message = rule(value)
        if not ok:
            errors.append(message)
    return errors


def compose_rules(*rules: Rule[T]) -> Rule[T]:
    """Compose many rules into one rule that aggregates failure messages."""

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
    return (bool(s.strip()), "must not be empty")


def min_len(n: int) -> Rule[str]:
    def rule(s: str) -> tuple[bool, str]:
        return (len(s) >= n, f"length must be >= {n}")

    return rule


def no_space(s: str) -> tuple[bool, str]:
    return (" " not in s, "must not contain spaces")
