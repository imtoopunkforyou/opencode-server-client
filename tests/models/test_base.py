from opencode_server_client.models.base import (
    OpencodeBaseResponse,
    OpencodeError,
    OpencodeErrorResponse,
    build_error,
)


def test_base_response_is_frozen_and_slotted():
    resp = OpencodeBaseResponse(code=200, body={'a': 1})
    assert resp.code == 200
    assert not hasattr(resp, '__dict__')


def test_build_error_reads_name_and_nested_message():
    resp = build_error(404, {'name': 'NotFoundError', 'data': {'message': 'nope'}})
    assert isinstance(resp, OpencodeErrorResponse)
    assert resp.code == 404
    assert resp.body == OpencodeError(
        name='NotFoundError',
        message='nope',
        payload={'name': 'NotFoundError', 'data': {'message': 'nope'}},
    )


def test_build_error_reads_tag_and_top_message():
    resp = build_error(409, {'_tag': 'SessionBusyError', 'message': 'busy'})
    assert resp.body.name == 'SessionBusyError'
    assert resp.body.message == 'busy'


def test_build_error_defaults_on_non_dict_payload():
    resp = build_error(500, None)
    assert resp.body.name == 'UnknownError'
    assert resp.body.message is None
    assert resp.body.payload is None
