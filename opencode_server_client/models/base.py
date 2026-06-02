"""Base response and error dataclasses."""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OpencodeBaseResponse:
    """Common response shape: an HTTP code and a typed body."""

    code: int
    body: object


@dataclass(frozen=True, slots=True)
class OpencodeError:
    """Normalised server error."""

    name: str
    message: str | None
    payload: dict[str, object] | None


@dataclass(frozen=True, slots=True)
class OpencodeErrorResponse(OpencodeBaseResponse):
    """Response returned for any non-2xx status."""

    body: OpencodeError


def build_error(code: int, payload: object) -> OpencodeErrorResponse:
    """Normalise an error payload into an :class:`OpencodeErrorResponse`."""
    name = 'UnknownError'
    message: str | None = None
    extra: dict[str, object] | None = None
    if isinstance(payload, dict):
        extra = payload
        tag = payload.get('name') or payload.get('_tag')
        if isinstance(tag, str):
            name = tag
        message = _error_message(payload)
    return OpencodeErrorResponse(
        code=code,
        body=OpencodeError(name=name, message=message, payload=extra),
    )


@dataclass(frozen=True, slots=True)
class OpencodeBoolResponse(OpencodeBaseResponse):
    """Response whose body is a single boolean flag."""

    body: bool


def ok_bool(code: int, payload: object) -> OpencodeBoolResponse:
    """Build a boolean response from a payload."""
    return OpencodeBoolResponse(code=code, body=bool(payload))


def _error_message(payload: dict[str, object]) -> str | None:
    top = payload.get('message')
    if isinstance(top, str):
        return top
    nested = payload.get('data')
    if isinstance(nested, dict):
        inner = nested.get('message')
        if isinstance(inner, str):
            return inner
    return None
