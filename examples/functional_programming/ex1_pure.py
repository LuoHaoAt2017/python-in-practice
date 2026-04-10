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
    """Normalize user fields without mutating the input.

    Returns a new dict with keys: name, phone, country.
    """

    name_raw = str(user.get("name", ""))
    phone_raw = str(user.get("phone", ""))
    country_raw = str(user.get("country", ""))

    return {
        "name": _title_words(name_raw),
        "phone": _digits_only(phone_raw),
        "country": _normalize_country(country_raw),
    }
