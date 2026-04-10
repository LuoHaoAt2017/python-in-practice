from __future__ import annotations

import random
import re

import pytest

from examples.functional_programming.ex1_pure import normalize_user
from examples.functional_programming.ex2_rules import compose_rules, min_len, no_space, not_empty, validate
from examples.functional_programming.ex3_pipeline import gmv, pairs_map_filter_reduce, pairs_pythonic
from examples.functional_programming.ex4_closure import make_price_calculator
from examples.functional_programming.ex5_decorators import FlakyError, make_flaky, retry, timed
from examples.functional_programming.ex6_lazy import iter_user_cost, top_users_by_cost
from examples.functional_programming.ex7_etl import UserRecord, run_etl


def test_ex1_normalize_user_table() -> None:
    user = {"name": "  aLiCe  bob ", "phone": "+86 138-0013-8000", "country": "china"}
    user_before = dict(user)

    out = normalize_user(user)

    assert user == user_before  # input not mutated
    assert out == {"name": "Alice Bob", "phone": "8613800138000", "country": "CN"}


@pytest.mark.parametrize(
    "country_input, expected",
    [
        ("CN", "CN"),
        ("chn", "CN"),
        ("United States", "US"),
        ("uk", "GB"),
        ("", "ZZ"),
        ("unknown", "ZZ"),
    ],
)
def test_ex1_country_aliases(country_input: str, expected: str) -> None:
    out = normalize_user({"name": "x", "phone": "1", "country": country_input})
    assert out["country"] == expected


def test_ex1_invariants_randomized() -> None:
    rng = random.Random(0)
    for _ in range(200):
        raw_phone = "".join(rng.choice("+ -()0123456789abc") for _ in range(30))
        raw_country = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz ") for _ in range(10))
        out = normalize_user({"name": "  a  ", "phone": raw_phone, "country": raw_country})

        assert out["phone"].isdigit() or out["phone"] == ""
        assert re.fullmatch(r"[A-Z]{2}", out["country"]) or out["country"] == "ZZ"


def test_ex2_validate_collects_messages() -> None:
    rules = [not_empty, min_len(3), no_space]
    assert validate("", rules) == ["must not be empty", "length must be >= 3"]
    assert validate("ab", rules) == ["length must be >= 3"]
    assert validate("abc def", rules) == ["must not contain spaces"]
    assert validate("abcd", rules) == []


def test_ex2_compose_rules_aggregates() -> None:
    username_rule = compose_rules(not_empty, min_len(3), no_space)
    ok, msg = username_rule("")
    assert ok is False
    assert "must not be empty" in msg

    ok, msg = username_rule("abcd")
    assert ok is True
    assert msg == ""


def test_ex3_pipeline_results_equal() -> None:
    orders = [
        {"id": "A", "items": [{"sku": "x", "qty": 2, "price": 10.0}]},
        {"id": "B", "items": []},
        {"id": "C", "items": [{"sku": "y", "qty": 1, "price": 7.5}]},
    ]

    pairs_a = list(pairs_map_filter_reduce(orders))
    pairs_b = pairs_pythonic(orders)

    assert pairs_a == pairs_b
    assert gmv(iter(pairs_a)) == pytest.approx(27.5)


def test_ex4_closure_calculator() -> None:
    calc = make_price_calculator(tax_rate=0.1, discount=0.2)
    total = calc([{"price": 100.0, "qty": 1}, {"price": 10.0, "qty": 3}])

    # subtotal = 130; discounted = 104; taxed = 114.4
    assert total == pytest.approx(114.4)


def test_ex5_timed_wraps_and_returns_elapsed() -> None:
    @timed
    def f(x: int) -> int:
        return x + 1

    value, elapsed_ms = f(1)
    assert value == 2
    assert elapsed_ms >= 0
    assert f.__name__ == "f"


def test_ex5_retry_eventually_succeeds() -> None:
    counter = {"n": 0}
    flaky = make_flaky(counter)

    safe = retry(5, (FlakyError,))(flaky)
    assert safe() == "ok"
    assert counter["n"] == 3


def test_ex5_retry_raises_after_max_attempts() -> None:
    counter = {"n": 0}

    def always_fail() -> str:
        counter["n"] += 1
        raise FlakyError("boom")

    safe = retry(2, (FlakyError,))(always_fail)
    with pytest.raises(FlakyError):
        safe()
    assert counter["n"] == 2


def test_ex5_retry_rejects_non_positive_attempts() -> None:
    with pytest.raises(ValueError):
        retry(0)


def test_ex6_iter_user_cost_is_lazy_and_filters_invalid() -> None:
    lines = [
        "ts=1 level=INFO user=alice cost=1.5",
        "ts=2 level=INFO user=bob cost=bad",
        "ts=3 level=INFO cost=10",  # missing user
        "ts=4 level=INFO user=alice cost=2",
    ]

    pairs = list(iter_user_cost(lines))
    assert pairs == [("alice", 1.5), ("alice", 2.0)]


def test_ex6_top_users_by_cost_sorted_and_bounded() -> None:
    lines = [
        "ts=1 level=INFO user=alice cost=1",
        "ts=2 level=INFO user=bob cost=3",
        "ts=3 level=INFO user=alice cost=2",
        "ts=4 level=INFO user=carol cost=2.5",
    ]

    top2 = top_users_by_cost(lines, 2)
    assert len(top2) == 2
    assert top2[0][1] >= top2[1][1]
    assert top2[0][0] == "alice" and top2[0][1] == pytest.approx(3.0)


def test_ex7_run_etl_returns_immutable_data_and_summary() -> None:
    records = [
        {"name": " Alice ", "phone": "138-0013", "country": "CN"},
        {"name": "", "phone": "123", "country": "US"},
        {"name": "Bob", "phone": "abc", "country": "USA"},
    ]

    result = run_etl(records)

    assert isinstance(result["errors"], tuple)
    assert len(result["errors"]) == 2

    data = result["data"]
    assert isinstance(data, tuple)
    assert len(data) == 1
    assert isinstance(data[0], UserRecord)

    summary = result["summary"]
    assert summary["total"] == 1
    assert summary["by_segment"]["domestic"] == 1


def test_ex7_invariant_segment_matches_country() -> None:
    records = [
        {"name": "A", "phone": "1", "country": "CN"},
        {"name": "B", "phone": "2", "country": "US"},
        {"name": "C", "phone": "3", "country": "ZZ"},
    ]
    result = run_etl(records)
    for u in result["data"]:
        assert (u.country == "CN" and u.segment == "domestic") or (
            u.country != "CN" and u.segment == "overseas"
        )

def test_list_comprehension_map() -> None:
    input = [1, 2, 3, 4, 5]
    # 列表推导式【表达式 + for + 可选 if】
    assert [x * x for x in input] == [1, 4, 9, 16, 25]

def test_list_comprehension_filter() -> None:
    input = [1, 2, 3, 4, 5]
    # 列表推导式【表达式 + for + 可选 if】
    assert [x for x in input if x % 2 == 0] == [2, 4]
    
def test_list_comprehension_filter_map() -> None:
    input = [1, 2, 3, 4, 5]
    # 列表推导式【表达式 + for + 可选 if】
    assert [x * 2 for x in input if x % 2 == 0] == [4, 8]
   
def test_list_comprehension_nested() -> None:
    input = [[1, 2], [3, 4], [5]]
    # 列表推导式【表达式 + for + 可选 if】
    assert [y for x in input for y in x] == [1, 2, 3, 4, 5]
    
def test_list_comprehension_with_tuple_unpacking() -> None:
    input = [(1, 'a'), (2, 'b'), (3, 'c')]
    # 列表推导式【表达式 + for + 可选 if】
    assert [f"{num}:{char}" for num, char in input] == ["1:a", "2:b", "3:c"]