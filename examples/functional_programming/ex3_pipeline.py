from __future__ import annotations

"""练习 3：变换管道（map/filter/reduce）。

同一个数据处理问题可以表达为：
- filter -> map -> reduce（更“显式”的函数式管道）
- 推导式 + `sum` 等内置函数（通常更 Pythonic、可读性更强）

本练习的重点不是“总要用 reduce”，而是掌握拆解方法：
filter（筛选）/ map（变换）/ reduce（归约聚合）。
"""

from collections.abc import Iterable
from functools import reduce


def order_total(order: dict) -> float:
    """计算单个订单的总金额。"""
    return sum(item["qty"] * item["price"] for item in order.get("items", []))


def is_not_empty_order(order: dict) -> bool:
    """filter 的谓词：保留至少有一个商品项的订单。"""
    return bool(order.get("items"))


def to_pair(order: dict) -> tuple[str, float]:
    """把订单映射为 (order_id, total_amount)。"""
    return order["id"], order_total(order)


def gmv(pairs: Iterable[tuple[str, float]]) -> float:
    """把 (id, total) 对归约为 GMV（总成交额）。"""
    return reduce(lambda acc, p: acc + p[1], pairs, 0.0)


def pairs_map_filter_reduce(orders: list[dict]) -> Iterable[tuple[str, float]]:
    """用 filter+map 返回一个 *迭代器*（惰性：被消费时才执行）。"""
    non_empty = filter(is_not_empty_order, orders)
    return map(to_pair, non_empty)


def pairs_pythonic(orders: list[dict]) -> list[tuple[str, float]]:
    """用推导式返回 pairs 列表（急切：立即计算，通常更直观）。"""
    return [(o["id"], order_total(o)) for o in orders if o.get("items")]
