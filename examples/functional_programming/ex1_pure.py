from __future__ import annotations

"""练习 1：用纯函数做数据规范化。

本模块演示 Python 中非常重要的函数式习惯：
把数据清洗/规范化逻辑提炼为**纯函数**。

我们期望的关键性质：
- 无副作用：不打印、不做 I/O、不修改全局状态。
- 不修改入参映射（不做原地修改）。
- 同输入必得同输出（可推理/可复现）。
"""

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
    """把姓名按“单词首字母大写”规范化。

    说明：这是一个纯函数辅助方法，只依赖入参 `value`。
    """
    words = [w for w in value.strip().split() if w]
    return " ".join(w[:1].upper() + w[1:].lower() for w in words)


def _digits_only(value: str) -> str:
    """仅保留数字字符。

    常用于手机号规范化：去掉空格、加号、短横线、括号等格式字符。
    """
    return "".join(ch for ch in value if ch.isdigit())


def _normalize_country(value: str) -> str:
    """把国家输入映射为标准的两位大写国家码。

    未识别的值统一回落为 "ZZ"。
    """
    key = value.strip().upper()
    return COUNTRY_ALIASES.get(key, "ZZ")


def normalize_user(user: dict[str, Any]) -> dict[str, str]:
    """规范化用户字段，且不修改入参。

    这是本练习对外的“纯函数”。它会构造并返回一个新 dict，
    而不是在原 `user` 上原地修改。

    返回字段固定为：name / phone / country。
    """

    name_raw = str(user.get("name", ""))
    phone_raw = str(user.get("phone", ""))
    country_raw = str(user.get("country", ""))

    # 关键点：构造新对象，确保调用方可以安全复用原始 `user`。
    return {
        "name": _title_words(name_raw),
        "phone": _digits_only(phone_raw),
        "country": _normalize_country(country_raw),
    }
