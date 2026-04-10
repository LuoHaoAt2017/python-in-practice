from __future__ import annotations

from collections.abc import Iterable
from functools import reduce


def order_total(order: dict) -> float:
    return sum(item["qty"] * item["price"] for item in order.get("items", []))


def is_not_empty_order(order: dict) -> bool:
    return bool(order.get("items"))


def to_pair(order: dict) -> tuple[str, float]:
    return order["id"], order_total(order)


def gmv(pairs: Iterable[tuple[str, float]]) -> float:
    return reduce(lambda acc, p: acc + p[1], pairs, 0.0)


def pairs_map_filter_reduce(orders: list[dict]) -> Iterable[tuple[str, float]]:
    non_empty = filter(is_not_empty_order, orders)
    return map(to_pair, non_empty)


def pairs_pythonic(orders: list[dict]) -> list[tuple[str, float]]:
    return [(o["id"], order_total(o)) for o in orders if o.get("items")]
