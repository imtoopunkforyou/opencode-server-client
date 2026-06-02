"""Typed accessors for decoded JSON payloads (keeps parsers mypy-clean)."""
from collections.abc import Mapping


def as_map(payload: object) -> Mapping[str, object]:
    """Return *payload* as a mapping, or an empty mapping."""
    if isinstance(payload, Mapping):
        return payload
    return {}


def as_seq(payload: object) -> tuple[object, ...]:
    """Return *payload* as a tuple of items, or an empty tuple."""
    if isinstance(payload, list):
        return tuple(payload)
    return ()


def get_str(src: Mapping[str, object], key: str) -> str:
    """Read a required string field (missing → empty string)."""
    found = src.get(key)
    return found if isinstance(found, str) else ''


def opt_str(src: Mapping[str, object], key: str) -> str | None:
    """Read an optional string field."""
    found = src.get(key)
    return found if isinstance(found, str) else None


def get_bool(src: Mapping[str, object], key: str) -> bool:
    """Read a required boolean field (missing → False)."""
    return bool(src.get(key))


def get_int(src: Mapping[str, object], key: str) -> int:
    """Read a required integer field (missing -> 0)."""
    found = src.get(key)
    if isinstance(found, int) and not isinstance(found, bool):
        return found
    return 0


def opt_int(src: Mapping[str, object], key: str) -> int | None:
    """Read an optional integer field."""
    found = src.get(key)
    if isinstance(found, int) and not isinstance(found, bool):
        return found
    return None


def get_float(src: Mapping[str, object], key: str) -> float:
    """Read a required number field (missing → 0.0)."""
    found = src.get(key)
    if isinstance(found, (int, float)):
        return float(found)
    return float(0)


def str_tuple(payload: object) -> tuple[str, ...]:
    """Coerce a payload into a tuple of strings."""
    return tuple(entry for entry in as_seq(payload) if isinstance(entry, str))
