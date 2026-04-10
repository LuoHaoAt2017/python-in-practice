# Python 函数式编程 7 道题（含解析与参考答案）

目标：通过 7 个循序渐进的练习，系统掌握 Python 函数式编程的核心能力：**纯函数**、**高阶函数**、**组合与管道**、**闭包与偏函数**、**装饰器**、**惰性迭代器**、以及用这些概念完成一次小型“可测试的重构”。

> 建议做题方式：先读题→自己实现→再对照解析与答案→最后补齐测试与边界条件。

## 配套代码与测试

- 可运行参考实现：`examples/functional_programming/`（按题号拆分为 `ex1_pure.py` … `ex7_etl.py`）
- pytest 用例（表驱动 + 不变式）：`tests/test_functional_programming_exercises.py`

在本仓库 venv 下运行测试：

```bash
d:/github/python-in-practice/venv/Scripts/python.exe -m pytest .\\tests\\test_functional_programming_exercises.py
```

---

## 题 1：把业务规则写成纯函数（Pure Function）

### 题目
实现用户信息规范化函数：

- 函数签名：`normalize_user(user: dict) -> dict`
- `user` 可能缺字段、大小写混乱、手机号带空格/符号、国家码不统一
- 返回**新 dict**（禁止原地修改入参），包含字段：
  - `name`: 去除首尾空格，按“单词首字母大写”（`"aLiCe bob" -> "Alice Bob"`）
  - `phone`: 只保留数字字符（`"+86 138-0013-8000" -> "8613800138000"`）
  - `country`: 统一为两位大写国家码；无法识别则为 `"ZZ"`

### 解析
纯函数的关键约束：

1. **无副作用**：不打印、不写文件、不读写全局状态；不修改入参对象。
2. **可重复推理**：同输入必得同输出（不依赖当前时间/随机数）。
3. **便于测试**：输入→输出的映射稳定，可以表驱动测试。

国家码统一通常来自别名映射，例如：`"CHINA"/"CN"/"CHN" -> "CN"`；对不在映射表内的值统一回落到 `"ZZ"`。

### 参考答案
```python
from __future__ import annotations

from typing import Any

COUNTRY_ALIASES: dict[str, str] = {
    "CN": "CN",
    "CHN": "CN",
    "CHINA": "CN",
    "PRC": "CN",
    "US": "US",
    "USA": "US",
    "UNITED STATES": "US",
    "UK": "GB",
    "GB": "GB",
    "UNITED KINGDOM": "GB",
}


def _title_words(value: str) -> str:
    words = [w for w in value.strip().split() if w]
    return " ".join(w[:1].upper() + w[1:].lower() for w in words)


def _digits_only(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


def _normalize_country(value: str) -> str:
    key = value.strip().upper()
    return COUNTRY_ALIASES.get(key, "ZZ")


def normalize_user(user: dict[str, Any]) -> dict[str, str]:
    name_raw = str(user.get("name", ""))
    phone_raw = str(user.get("phone", ""))
    country_raw = str(user.get("country", ""))

    return {
        "name": _title_words(name_raw),
        "phone": _digits_only(phone_raw),
        "country": _normalize_country(country_raw),
    }
```

自测要点（不变式）：
- `normalize_user(u)` 不会改变 `u`
- 结果 `phone` 仅由数字组成
- `country` 必为 `"ZZ"` 或两位大写字母

---

## 题 2：用高阶函数消灭 if/else（规则注入）

### 题目
实现通用校验器：

- `Rule = Callable[[T], tuple[bool, str]]`
- `validate(value, rules) -> list[str]`：按顺序执行规则，返回所有失败信息
- 要求：`validate` 内禁止写具体业务判断；业务必须通过 `rules` 传入

并实现一个组合器：`compose_rules(*rules)`：把多个规则合成一个规则。

### 解析
这题是“**策略模式**”的函数式版本：把变化点（校验逻辑）从框架（validate）中解耦。

- `validate` 只做“循环执行 + 收集失败”这种稳定结构
- 新增/修改校验只需要新增规则函数，不改 `validate`
- `compose_rules` 是“把一组规则当作一个规则”的能力，便于复用（例如：`is_email` 由多条规则组成）

### 参考答案
```python
from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeVar

T = TypeVar("T")
Rule = Callable[[T], tuple[bool, str]]


def validate(value: T, rules: Sequence[Rule[T]]) -> list[str]:
    errors: list[str] = []
    for rule in rules:
        ok, message = rule(value)
        if not ok:
            errors.append(message)
    return errors


def compose_rules(*rules: Rule[T]) -> Rule[T]:
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


# 示例规则
def not_empty(s: str) -> tuple[bool, str]:
    return (bool(s.strip()), "must not be empty")


def min_len(n: int) -> Rule[str]:
    def rule(s: str) -> tuple[bool, str]:
        return (len(s) >= n, f"length must be >= {n}")

    return rule


def no_space(s: str) -> tuple[bool, str]:
    return (" " not in s, "must not contain spaces")


username_rule = compose_rules(not_empty, min_len(3), no_space)
```

---

## 题 3：用 map/filter/reduce（或等价写法）写变换管道

### 题目
给定订单列表：

```python
orders = [
    {"id": "A", "items": [{"sku": "x", "qty": 2, "price": 10.0}]},
    {"id": "B", "items": []},
    {"id": "C", "items": [{"sku": "y", "qty": 1, "price": 7.5}]},
]
```

完成：
1) 过滤掉空订单（`items` 为空）
2) 映射为 `(order_id, total_amount)`
3) 聚合得到 GMV（总成交额）

要求：
- 写 A 版：使用 `map/filter/reduce`
- 写 B 版：使用更常见的 Python 写法（推导式 + `sum`）

### 解析
`reduce` 在 Python 里并不总是最可读，尤其当聚合逻辑稍复杂时。很多场景：

- `sum(...)` 是最自然的 reduce
- 推导式通常比 `map/filter` 更直观

但理解 `map/filter/reduce` 的模型很重要：它能帮助你把问题拆成“过滤/变换/归约”三段。

### 参考答案
```python
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


# A 版：map/filter/reduce
non_empty = filter(is_not_empty_order, orders)
pairs_a = map(to_pair, non_empty)
gmv_a = gmv(pairs_a)

# B 版：推导式 + sum（更常见/更可读）
pairs_b = [(o["id"], order_total(o)) for o in orders if o.get("items")]
gmv_b = sum(total for _, total in pairs_b)
```

---

## 题 4：闭包（Closure）实现“带配置的函数”

### 题目
实现：`make_price_calculator(tax_rate: float, discount: float)`，返回函数 `calc(items) -> float`。

- `items` 为 `[{"price": 10.0, "qty": 2}, ...]`
- 计算顺序固定：
  1) 小计 subtotal
  2) 打折：`subtotal * (1 - discount)`
  3) 加税：`discounted * (1 + tax_rate)`

### 解析
闭包的价值：

- 把配置（税率、折扣）“封进”返回的函数，使调用方只需传入 items
- 避免全局变量，便于测试

注意：闭包本身不等于不可变；要做到“外部改变量不会影响”，关键是**不要引用会被外部继续修改的可变对象**。

### 参考答案
```python
from __future__ import annotations

from collections.abc import Callable, Sequence

Item = dict[str, float]


def make_price_calculator(tax_rate: float, discount: float) -> Callable[[Sequence[Item]], float]:
    tax_rate = float(tax_rate)
    discount = float(discount)

    def calc(items: Sequence[Item]) -> float:
        subtotal = sum(it["price"] * it["qty"] for it in items)
        discounted = subtotal * (1.0 - discount)
        total = discounted * (1.0 + tax_rate)
        return total

    return calc
```

---

## 题 5：装饰器（Decorator）实现横切复用：计时 + 重试

### 题目
实现两个可叠加装饰器：

1) `@timed`：返回 `(result, elapsed_ms)`
2) `@retry(max_attempts, exceptions)`：捕获指定异常重试

要求：
- 使用 `functools.wraps`
- 不改变被装饰函数的可调用方式（支持 `*args, **kwargs`）
- 重试次数达到上限后，抛出最后一次异常

### 解析
装饰器本质是：**接收函数 → 返回增强后的函数**（高阶函数 + 闭包）。

叠加顺序会影响行为：

- `@timed` 在外：计时包含重试的总耗时
- `@retry` 在外：只计时每次尝试（取决于你 timed 怎么写）

### 参考答案
```python
from __future__ import annotations

import time
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def timed(func: Callable[P, R]) -> Callable[P, tuple[R, float]]:
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
    if max_attempts <= 0:
        raise ValueError("max_attempts must be > 0")

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exc: BaseException | None = None
            for _ in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:  # noqa: PERF203 (retry 需要)
                    last_exc = exc
            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator


# 示例：偶发失败函数
class FlakyError(RuntimeError):
    pass


def make_flaky(counter: dict[str, int]) -> Callable[[], str]:
    def f() -> str:
        counter["n"] += 1
        if counter["n"] < 3:
            raise FlakyError("boom")
        return "ok"

    return f


# 用法示例
# counter = {"n": 0}
# flaky = make_flaky(counter)
# safe = retry(5, (FlakyError,))(flaky)
# value = safe()  # -> "ok"
```

---

## 题 6：惰性求值与迭代器管道（generator / itertools）

### 题目
实现日志分析（禁止一次性把所有行读入内存）：

- 输入：`Iterable[str]` 日志行，例如：
  - `"ts=2026-01-01 level=INFO user=alice cost=12"`
- 输出：Top N 用户的总 `cost`（按 cost 降序）

要求：
- parse/filter/map 步骤用生成器惰性处理
- 只有最终聚合（按用户汇总）才落地为 dict/Counter

### 解析
惰性管道的好处：

- 逐行处理，内存占用更稳定
- 步骤可组合（像积木一样拼）

常见坑：迭代器只能消费一次。比如 `pairs = map(...)` 消费后再次 `list(pairs)` 会得到空结果。

### 参考答案
```python
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
```

---

## 题 7：综合题——用函数组合 + 不可变结果完成一次 ETL

### 题目
给定脏数据 `records: list[dict]`，实现一个可组合 ETL：

- `clean(records) -> cleaned_records`
- `validate_records(cleaned_records) -> (valid_records, errors)`
- `enrich(valid_records) -> enriched_records`
- `summarize(enriched_records) -> summary`

要求：
- 每一步都是纯函数（不修改入参）
- 用 `compose` 把流程串起来
- 最终产物尽量不可变（例如 `tuple`、或 `@dataclass(frozen=True)`）

### 解析
综合题的目标是把“可变、混乱、难测试”的脚本式代码，重构成：

- **每一步小而纯**：输入/输出清晰，可单测
- **组合式主流程**：像搭积木一样替换/新增步骤
- **不可变结果**：减少后续步骤意外修改数据的风险（更可推理、更适合缓存/并发）

### 参考答案
```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def compose(f: Callable[[U], V], g: Callable[[T], U]) -> Callable[[T], V]:
    def h(x: T) -> V:
        return f(g(x))

    return h


def pipe(x: Any, *funcs: Callable[[Any], Any]) -> Any:
    for f in funcs:
        x = f(x)
    return x


@dataclass(frozen=True)
class UserRecord:
    name: str
    phone: str
    country: str
    segment: str


# 复用题1的规范化思想（简化版）
COUNTRY_ALIASES: dict[str, str] = {"CN": "CN", "CHINA": "CN", "US": "US", "USA": "US"}


def clean(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    def digits_only(s: str) -> str:
        return "".join(ch for ch in s if ch.isdigit())

    cleaned: list[dict[str, str]] = []
    for r in records:
        name = str(r.get("name", "")).strip()
        phone = digits_only(str(r.get("phone", "")))
        country_key = str(r.get("country", "")).strip().upper()
        country = COUNTRY_ALIASES.get(country_key, "ZZ")
        cleaned.append({"name": name, "phone": phone, "country": country})
    return cleaned


def validate_records(records: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[str]]:
    valid: list[dict[str, str]] = []
    errors: list[str] = []

    for i, r in enumerate(records):
        if not r["name"]:
            errors.append(f"record[{i}]: name is empty")
            continue
        if not r["phone"].isdigit():
            errors.append(f"record[{i}]: phone must be digits")
            continue
        valid.append(dict(r))

    return valid, errors


def enrich(valid_records: list[dict[str, str]]) -> tuple[UserRecord, ...]:
    def segment_by_country(country: str) -> str:
        return "domestic" if country == "CN" else "overseas"

    out: list[UserRecord] = []
    for r in valid_records:
        out.append(
            UserRecord(
                name=r["name"],
                phone=r["phone"],
                country=r["country"],
                segment=segment_by_country(r["country"]),
            )
        )
    return tuple(out)


def summarize(enriched: Iterable[UserRecord]) -> dict[str, Any]:
    total = 0
    by_segment: dict[str, int] = {"domestic": 0, "overseas": 0}
    for u in enriched:
        total += 1
        by_segment[u.segment] = by_segment.get(u.segment, 0) + 1

    return {"total": total, "by_segment": by_segment}


def run_etl(records: list[dict[str, Any]]) -> dict[str, Any]:
    valid, errors = validate_records(clean(records))
    enriched = enrich(valid)
    summary = summarize(enriched)
    return {"errors": tuple(errors), "data": enriched, "summary": summary}


# 或者用 pipe 组合（更直观）
# result = pipe(records, clean, validate_records, ...)  # 注意 validate_records 返回结构不同，需要适配
```

---

## 结语：你真正“掌握了”的标志

当你能在真实项目里做到这些，就算把函数式编程基础夯实了：

- 把复杂逻辑拆成 5~20 个小纯函数，每个都容易测试
- 用规则注入/组合器避免 if/else 爆炸
- 用惰性迭代器处理大数据流，最终聚合才落地
- 用装饰器把计时、重试、缓存、鉴权等横切关注点模块化

如果你希望进一步提升：可以在每题后补充 `pytest` 用例（表驱动 + 不变式），效果会非常明显。
