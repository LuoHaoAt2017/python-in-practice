from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Iterator


def parse_line(line: str) -> dict[str, str]:
    parts = line.strip().split()
    kv: dict[str, str] = {}
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            kv[k] = v
    return kv


def iter_user_cost(lines: Iterable[str]) -> Iterator[tuple[str, float]]:
    for line in lines:
        kv = parse_line(line)
        if kv.get("user") is None or kv.get("cost") is None:
            continue
        try:
            cost = float(kv["cost"])
        except ValueError:
            continue
        yield kv["user"], cost


def top_users_by_cost(lines: Iterable[str], n: int) -> list[tuple[str, float]]:
    totals: dict[str, float] = defaultdict(float)
    for user, cost in iter_user_cost(lines):
        totals[user] += cost

    return sorted(totals.items(), key=lambda x: x[1], reverse=True)[:n]
