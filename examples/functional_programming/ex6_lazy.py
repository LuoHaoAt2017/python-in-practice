from __future__ import annotations

"""练习 6：用生成器实现惰性求值。

我们构建一个管道：

    lines -> parse -> 过滤非法 -> 映射为 (user, cost) -> 聚合

parse/filter/map 阶段由生成器（`iter_user_cost`）实现，按需逐行处理；
只有最终聚合阶段才会落地（例如累加到 dict）。
"""

from collections import defaultdict
from collections.abc import Iterable, Iterator


def parse_line(line: str) -> dict[str, str]:
    """把按空白分隔的 key=value 行解析成 dict。

    约定：忽略不包含 '=' 的 token。
    """
    parts = line.strip().split()
    kv: dict[str, str] = {}
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            kv[k] = v
    return kv


def iter_user_cost(lines: Iterable[str]) -> Iterator[tuple[str, float]]:
    """从日志行中惰性产出 (user, cost) 对。

    - 跳过缺少必要字段的行
    - 跳过 cost 无法解析的行
    - 惰性：一次只处理一行
    """
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
    """按总 cost 返回 Top-N 用户。

    聚合阶段必须是急切的（需要拿到总和），但输入读取/解析仍通过 `iter_user_cost`
    保持惰性。
    """
    totals: dict[str, float] = defaultdict(float)
    for user, cost in iter_user_cost(lines):
        totals[user] += cost

    return sorted(totals.items(), key=lambda x: x[1], reverse=True)[:n]
