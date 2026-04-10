from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class UserRecord:
    name: str
    phone: str
    country: str
    segment: str


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
