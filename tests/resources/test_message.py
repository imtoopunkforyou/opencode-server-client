"""Tests for the message namespace resource."""

import json

import httpx

from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.message import (
    OpencodeMessageResponse,
    OpencodeMessagesResponse,
)
from opencode_server_client.models.message_input import (
    OpencodeMessageCommand,
    OpencodeMessagePrompt,
    OpencodeMessageShell,
)
from tests.resources.conftest import make_async_client, make_client

_SESSION_ID = 'ses-abc123'
_MSG_ID = 'msg-xyz789'


def _bundle_payload(
    session_id: str = _SESSION_ID,
    msg_id: str = _MSG_ID,
) -> dict:
    """Return a minimal valid bundle payload {info, parts}."""
    return {
        'info': {
            'id': msg_id,
            'sessionID': session_id,
            'role': 'user',
            'time': {'created': 1000},
        },
        'parts': [
            {
                'id': 'part-1',
                'sessionID': session_id,
                'messageID': msg_id,
                'type': 'text',
            },
        ],
    }


def test_message_prompt_posts_parts_to_session():
    """message.prompt() POSTs parts to /session/{id}/message."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request and return a bundle payload."""
        captured['method'] = request.method
        captured['path'] = request.url.path
        captured['body'] = json.loads(request.content)
        return httpx.Response(200, json=_bundle_payload())

    prompt = OpencodeMessagePrompt(parts=[{'type': 'text', 'text': 'hello'}])
    with make_client(handler) as oc:
        resp = oc.message.prompt(_SESSION_ID, prompt)

    assert captured['method'] == 'POST'
    assert captured['path'] == '/session/ses-abc123/message'
    assert captured['body'] == {'parts': [{'type': 'text', 'text': 'hello'}]}
    assert isinstance(resp, OpencodeMessageResponse)
    assert resp.body.message.message_id == _MSG_ID
    assert len(resp.body.parts) == 1
    assert resp.body.parts[0].part_type == 'text'


def test_message_prompt_includes_optional_fields():
    """message.prompt() includes optional fields when set."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture body."""
        captured['body'] = json.loads(request.content)
        return httpx.Response(200, json=_bundle_payload())

    prompt = OpencodeMessagePrompt(
        parts=[{'type': 'text', 'text': 'hi'}],
        message_id='msg-001',
        agent='coder',
        system='be concise',
    )
    with make_client(handler) as oc:
        oc.message.prompt(_SESSION_ID, prompt)

    assert captured['body']['messageID'] == 'msg-001'
    assert captured['body']['agent'] == 'coder'
    assert captured['body']['system'] == 'be concise'


def test_message_get_interpolates_both_ids():
    """message.get() interpolates session_id and message_id into path."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture path."""
        captured['path'] = request.url.path
        return httpx.Response(200, json=_bundle_payload())

    with make_client(handler) as oc:
        resp = oc.message.get(_SESSION_ID, _MSG_ID)

    assert captured['path'] == '/session/ses-abc123/message/msg-xyz789'
    assert isinstance(resp, OpencodeMessageResponse)
    assert resp.body.message.session_id == _SESSION_ID


def test_message_list_parses_bundle_list():
    """message.list() returns OpencodeMessagesResponse with bundles."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Return a list of one bundle."""
        return httpx.Response(200, json=[_bundle_payload()])

    with make_client(handler) as oc:
        resp = oc.message.list(_SESSION_ID)

    assert isinstance(resp, OpencodeMessagesResponse)
    assert len(resp.body) == 1
    assert resp.body[0].message.role == 'user'
    assert resp.body[0].message.created == 1000


def test_message_list_empty_returns_empty_tuple():
    """message.list() with empty payload returns empty tuple body."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Return empty list."""
        return httpx.Response(200, json=[])

    with make_client(handler) as oc:
        resp = oc.message.list(_SESSION_ID)

    assert isinstance(resp, OpencodeMessagesResponse)
    assert resp.body == ()


def test_message_command_sends_correct_body():
    """message.command() POSTs command/arguments to /session/{id}/command."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture method, path, and body."""
        captured['method'] = request.method
        captured['path'] = request.url.path
        captured['body'] = json.loads(request.content)
        return httpx.Response(200, json=_bundle_payload())

    cmd = OpencodeMessageCommand(
        command='test', arguments='--watch', agent='runner'
    )
    with make_client(handler) as oc:
        resp = oc.message.command(_SESSION_ID, cmd)

    assert captured['method'] == 'POST'
    assert captured['path'] == '/session/ses-abc123/command'
    assert captured['body']['command'] == 'test'
    assert captured['body']['arguments'] == '--watch'
    assert captured['body']['agent'] == 'runner'
    assert isinstance(resp, OpencodeMessageResponse)


def test_message_command_omits_none_fields():
    """message.command() omits optional fields when None."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture body."""
        captured['body'] = json.loads(request.content)
        return httpx.Response(200, json=_bundle_payload())

    cmd = OpencodeMessageCommand(command='build', arguments='')
    with make_client(handler) as oc:
        oc.message.command(_SESSION_ID, cmd)

    assert set(captured['body'].keys()) == {'command', 'arguments'}


def test_message_shell_sends_correct_body():
    """message.shell() POSTs to /session/{id}/shell."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture path and body."""
        captured['path'] = request.url.path
        captured['body'] = json.loads(request.content)
        return httpx.Response(200, json=_bundle_payload())

    shell = OpencodeMessageShell(agent='coder', command='ls -la')
    with make_client(handler) as oc:
        resp = oc.message.shell(_SESSION_ID, shell)

    assert captured['path'] == '/session/ses-abc123/shell'
    assert captured['body'] == {'agent': 'coder', 'command': 'ls -la'}
    assert isinstance(resp, OpencodeMessageResponse)


def test_message_get_returns_error_on_404():
    """message.get() returns OpencodeErrorResponse on 404."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Return 404 error."""
        return httpx.Response(
            404, json={'name': 'NotFoundError', 'message': 'not found'}
        )

    with make_client(handler) as oc:
        resp = oc.message.get(_SESSION_ID, _MSG_ID)

    assert isinstance(resp, OpencodeErrorResponse)
    assert resp.code == 404
    assert resp.body.name == 'NotFoundError'


def test_message_bundle_error_field_parsed():
    """OpencodeMessage.error is a dict when error key is a dict."""
    payload = _bundle_payload()
    payload['info']['error'] = {'code': 'E001', 'detail': 'bad'}

    def handler(request: httpx.Request) -> httpx.Response:
        """Return bundle with error field."""
        return httpx.Response(200, json=payload)

    with make_client(handler) as oc:
        resp = oc.message.get(_SESSION_ID, _MSG_ID)

    assert isinstance(resp, OpencodeMessageResponse)
    assert resp.body.message.error == {'code': 'E001', 'detail': 'bad'}


async def test_message_prompt_async():
    """message.prompt() works via the async client."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Return a bundle payload."""
        return httpx.Response(200, json=_bundle_payload())

    prompt = OpencodeMessagePrompt(parts=[{'type': 'text', 'text': 'hey'}])
    async with make_async_client(handler) as oc:
        resp = await oc.message.prompt(_SESSION_ID, prompt)

    assert isinstance(resp, OpencodeMessageResponse)
    assert resp.body.message.message_id == _MSG_ID


async def test_message_list_async():
    """message.list() works via the async client."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Return a list of bundles."""
        return httpx.Response(
            200, json=[_bundle_payload(), _bundle_payload(msg_id='msg-2')]
        )

    async with make_async_client(handler) as oc:
        resp = await oc.message.list(_SESSION_ID)

    assert isinstance(resp, OpencodeMessagesResponse)
    assert len(resp.body) == 2


async def test_message_get_async():
    """message.get() works via the async client."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Return a bundle payload."""
        return httpx.Response(200, json=_bundle_payload())

    async with make_async_client(handler) as oc:
        resp = await oc.message.get(_SESSION_ID, _MSG_ID)

    assert isinstance(resp, OpencodeMessageResponse)
    assert resp.body.message.role == 'user'
