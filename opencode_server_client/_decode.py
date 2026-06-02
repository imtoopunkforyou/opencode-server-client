"""Split a RawResponse into a typed success response or an error response."""

from collections.abc import Callable
from http import HTTPStatus
from typing import TypeVar

from opencode_server_client._transport import RawResponse
from opencode_server_client.models.base import (
    OpencodeBaseResponse,
    OpencodeErrorResponse,
    build_error,
)

_Response = TypeVar('_Response', bound=OpencodeBaseResponse)


def decode(
    raw: RawResponse,
    success: Callable[[int, object], _Response],
) -> _Response | OpencodeErrorResponse:
    """Build a typed response on 2xx, else an :class:`OpencodeErrorResponse`.

    Args:
        raw: The raw HTTP response containing status code and payload.
        success: Callable that builds a typed response from code and payload.

    Returns:
        A typed success response for 2xx status codes, or an
        :class:`OpencodeErrorResponse` for non-2xx status codes.
    """
    if HTTPStatus.OK <= raw.code < HTTPStatus.MULTIPLE_CHOICES:
        return success(raw.code, raw.payload)
    return build_error(raw.code, raw.payload)
