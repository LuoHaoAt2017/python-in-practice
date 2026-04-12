import pytest

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
