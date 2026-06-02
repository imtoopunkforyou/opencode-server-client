from opencode_server_client._decode import decode
from opencode_server_client._transport import RawResponse
from opencode_server_client.models.base import (
    OpencodeBaseResponse,
    OpencodeErrorResponse,
)


def _ok(code: int, payload: object) -> OpencodeBaseResponse:
    return OpencodeBaseResponse(code=code, body=payload)


def test_decode_success_calls_builder():
    out = decode(RawResponse(200, {'x': 1}), _ok)
    assert out == OpencodeBaseResponse(200, {'x': 1})


def test_decode_201_is_success():
    out = decode(RawResponse(201, None), _ok)
    assert isinstance(out, OpencodeBaseResponse)
    assert not isinstance(out, OpencodeErrorResponse)


def test_decode_error_status_builds_error():
    out = decode(RawResponse(404, {'name': 'NotFoundError'}), _ok)
    assert isinstance(out, OpencodeErrorResponse)
    assert out.body.name == 'NotFoundError'
