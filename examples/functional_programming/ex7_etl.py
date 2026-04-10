from __future__ import annotations

"""练习 7：用可组合、可测试的函数实现一个迷你 ETL。

目标：把脏数据 records 转成不可变、可推理的 enriched 结果，并产出摘要统计。

函数式编程强调点：
- 每一步都是小函数，输入/输出契约清晰。
- 各步骤尽量避免修改入参。
- 最终数据输出不可变（`tuple` + 冻结 dataclass）。
"""

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class UserRecord:
    """ETL 产出的不可变记录（已校验/已增强）。"""

    name: str
    phone: str
    country: str
    segment: str


COUNTRY_ALIASES: dict[str, str] = {"CN": "CN", "CHINA": "CN", "US": "US", "USA": "US"}


def clean(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    """规范化原始 records。

    该步骤是纯的：返回一个新 list，且每个元素都是新 dict。
    """
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
    """校验 clean 后的记录，并拆分为 (valid, errors)。

    把错误显式地作为返回值（而不是直接 raise）是一种常见的函数式风格：
    能让管道更容易测试、也更容易推理与组合。
    """
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
    """派生字段并返回不可变的 `UserRecord`。"""
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
    """从 enriched 记录计算一个摘要统计。"""
    total = 0
    by_segment: dict[str, int] = {"domestic": 0, "overseas": 0}
    for u in enriched:
        total += 1
        by_segment[u.segment] = by_segment.get(u.segment, 0) + 1

    return {"total": total, "by_segment": by_segment}


def run_etl(records: list[dict[str, Any]]) -> dict[str, Any]:
    """执行完整 ETL，返回 data + errors + summary。

    出于教学目的，这里保持为一个很小的编排函数；在更大的工程里，
    你可以引入 `pipe(...)` 工具函数或更正式的组合方式。
    """
    valid, errors = validate_records(clean(records))
    enriched = enrich(valid)
    summary = summarize(enriched)
    return {"errors": tuple(errors), "data": enriched, "summary": summary}
