from __future__ import annotations

"""练习 4：闭包（捕获配置的函数）。

`make_price_calculator` 会返回一个新函数，它的行为由税率、折扣等配置参数决定。

这种写法的好处：
- 避免使用全局变量
- 函数更易测试
- 依赖更显式：配置在创建时传入一次即可
"""

from collections.abc import Callable, Sequence

Item = dict[str, float]


def make_price_calculator(tax_rate: float, discount: float) -> Callable[[Sequence[Item]], float]:
    """返回一个由 tax_rate/discount 配置好的计算函数。

    当配置固定后，返回的 `calc(items)` 对 `items` 来说仍然是纯函数。
    """

    # 把数值配置捕获到闭包里，确保行为稳定、易推理。
    tax_rate = float(tax_rate)
    discount = float(discount)

    def calc(items: Sequence[Item]) -> float:
        """计算总价：total = (subtotal * (1 - discount)) * (1 + tax_rate)。"""
        subtotal = sum(it["price"] * it["qty"] for it in items)
        discounted = subtotal * (1.0 - discount)
        total = discounted * (1.0 + tax_rate)
        return total

    return calc
