import pytest
from collections.abc import Callable, Sequence
from typing import TypeVar

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


def _only_digital(value: str) -> str:
    """_summary_
        将手机号中的非数字剔除掉
    Args:
        value (str): _description_

    Returns:
        str: _description_
    """

    return "".join(ch for ch in value if ch.isdigit())


def _capital_name(value: str) -> str:
    """_summary_
        将姓名中的首字母大写
    Args:
        value (str): _description_

    Returns:
        str: _description_
    """
    return " ".join(word[:1].upper() + word[1:].lower() for word in value if word)


def _normalize_country(value: str) -> str:
    key = value.strip().upper()
    return COUNTRY_ALIASES.get(key, "ZZ")


def normalize_user(user: dict[str, any]) -> dict[str, str]:
    user["name"] = _capital_name(user["name"])
    user["phone"] = _only_digital(user["phone"])
    user["country"] = _normalize_country(user["country"])
    return user


@pytest.mark.parametrize(
    "origin_country,expect_country",
    [
        ("CN", "CN"),
        ("chn", "CN"),
        ("United States", "US"),
        ("uk", "GB"),
        ("", "ZZ"),
        ("unknown", "ZZ"),
    ],
)
def test_normalize_country(origin_country: str, expect_country: str):
    result = normalize_user({"name": "x", "phone": "1", "country": origin_country})
    assert result["country"] == expect_country


T = TypeVar("T")
Rule = Callable[[T], tuple[bool, str]]


def no_space(value: str) -> tuple[bool, str]:
    return [" " not in value, "must not contain spaces"]


def not_empty(value: str) -> tuple[bool, str]:
    return [bool(value.strip()), "must not be empty"]


def min_len(count: int) -> tuple[bool, str]:
    """_summary_

    Args:
        count (int): _description_

    Returns:
        tuple[bool, str]: _description_
    """

    def rule(value: str) -> tuple[bool, str]:
        return [len(value) >= count, f"length must be >= {count}"]

    return rule


def max_len(count: int) -> Rule[str]:
    """_summary_
    「函数工厂 / 闭包（Closure）」
    Args:
        count (int): _description_

    Returns:
        Rule[str]: _description_
    """

    def rule(value: str) -> tuple[bool, str]:
        return [len(value) <= count, f"length must be <= {count}"]

    return rule


def validate(value: str, rules: list[Rule]) -> list[str]:
    messages: list[str] = []

    for rule in rules:
        [ok, mesg] = rule(value)
        if not ok:
            messages.append(mesg)

    return messages


def test_validate_rules():
    rules = [not_empty, min_len(3), no_space]
    assert validate("", rules) == ["must not be empty", "length must be >= 3"]
    assert validate("ab", rules) == ["length must be >= 3"]
    assert validate("abc def", rules) == ["must not contain spaces"]
    assert validate("abcd", rules) == []
