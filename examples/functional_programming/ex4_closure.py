from __future__ import annotations

from collections.abc import Callable, Sequence

Item = dict[str, float]


def make_price_calculator(tax_rate: float, discount: float) -> Callable[[Sequence[Item]], float]:
    """Return a calculator function configured by tax_rate and discount."""

    tax_rate = float(tax_rate)
    discount = float(discount)

    def calc(items: Sequence[Item]) -> float:
        subtotal = sum(it["price"] * it["qty"] for it in items)
        discounted = subtotal * (1.0 - discount)
        total = discounted * (1.0 + tax_rate)
        return total

    return calc
