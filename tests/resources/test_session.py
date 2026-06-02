"""Tests for the session namespace resource."""
import json

import httpx

from opencode_server_client.models.base import (
    OpencodeBoolResponse,
    OpencodeErrorResponse,
)
from opencode_server_client.models.session_extra import (
    OpencodeDiffResponse,
    OpencodeSessionResponse,
    OpencodeSessionsResponse,
    OpencodeTodosResponse,
)
from opencode_server_client.models.session_input import (
    OpencodeSessionCreate,
    OpencodeSessionFork,
    OpencodeSessionInit,
    OpencodeSessionSummarize,
    OpencodeSessionUpdate,
)
from tests.resources.conftest import make_async_client, make_client

_SESSION_ID = 'ses-abc123'
_MSG_ID = 'msg-xyz'


def _session_payload(
    session_id: str = _SESSION_ID,
    title: str = 'demo',
) -> dict:
    """Return a minimal valid session payload."""
    return {
        'id': session_id,
        'slug': 'demo-slug',
        'projectID': 'proj-1',
        'directory': '/home/user',
        'title': title,
        'version': '1.0',
        'parentID': None,
        'workspaceID': None,
        'path': None,
        'agent': None,
        'time': {'created': 1000, 'updated': 2000},
        'permission': [],
    }


def test_session_list_sends_get_to_base():
    """session.list() sends GET /session; returns OpencodeSessionsResponse."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request and return empty list."""
        captured['method'] = request.method
        captured['path'] = request.url.path
        return httpx.Response(200, json=[])

    with make_client(handler) as oc:
        resp = oc.session.list()
    assert captured['method'] == 'GET'
    assert captured['path'] == '/session'
    assert isinstance(resp, OpencodeSessionsResponse)
    assert resp.body == ()


def test_session_create_posts_compacted_body():
    """session.create() POSTs compacted body to /session."""
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request and return a session payload."""
        seen['method'] = request.method
        seen['path'] = request.url.path
        seen['body'] = json.loads(request.content)
        return httpx.Response(200, json=_session_payload())

    with make_client(handler) as oc:
        body = OpencodeSessionCreate(title='demo')
        resp = oc.session.create(body)
    assert (seen['method'], seen['path']) == ('POST', '/session')
    assert seen['body'] == {'title': 'demo'}
    assert isinstance(resp, OpencodeSessionResponse)
    assert resp.body.title == 'demo'


def test_session_create_omits_none_fields():
    """session.create() without args sends empty body."""
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture JSON body."""
        seen['body'] = json.loads(request.content)
        return httpx.Response(200, json=_session_payload())

    with make_client(handler) as oc:
        oc.session.create()
    assert seen['body'] == {}


def test_session_get_interpolates_id():
    """session.get() interpolates session_id into /session/{id}."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture path and return a session payload."""
        captured['path'] = request.url.path
        return httpx.Response(200, json=_session_payload())

    with make_client(handler) as oc:
        resp = oc.session.get(_SESSION_ID)
    assert captured['path'] == '/session/ses-abc123'
    assert isinstance(resp, OpencodeSessionResponse)
    assert resp.body.session_id == _SESSION_ID


def test_session_delete_returns_bool_true():
    """session.delete() returns OpencodeBoolResponse(body=True) on success."""
    def handler(request: httpx.Request) -> httpx.Response:
        """Return true payload."""
        return httpx.Response(200, json=True)

    with make_client(handler) as oc:
        resp = oc.session.delete(_SESSION_ID)
    assert isinstance(resp, OpencodeBoolResponse)
    assert resp.body is True


def test_session_update_sends_patch_body():
    """session.update() sends PATCH to /session/{id} with body."""
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture method and body."""
        seen['method'] = request.method
        seen['body'] = json.loads(request.content)
        return httpx.Response(200, json=_session_payload(title='renamed'))

    with make_client(handler) as oc:
        resp = oc.session.update(
            _SESSION_ID, OpencodeSessionUpdate(title='renamed')
        )
    assert seen['method'] == 'PATCH'
    assert seen['body'] == {'title': 'renamed'}
    assert isinstance(resp, OpencodeSessionResponse)
    assert resp.body.title == 'renamed'


def test_session_update_with_archived():
    """session.update() includes time.archived when archived is set."""
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture body."""
        seen['body'] = json.loads(request.content)
        return httpx.Response(200, json=_session_payload())

    with make_client(handler) as oc:
        oc.session.update(
            _SESSION_ID, OpencodeSessionUpdate(archived=999.0)
        )
    assert seen['body'] == {'time': {'archived': 999.0}}


def test_session_diff_adds_message_id_to_query():
    """session.diff() adds messageID to query when provided."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture query params."""
        captured['query'] = str(request.url.query)
        return httpx.Response(200, json=[])

    with make_client(handler) as oc:
        resp = oc.session.diff(_SESSION_ID, message_id=_MSG_ID)
    assert 'messageID=msg-xyz' in captured['query']
    assert isinstance(resp, OpencodeDiffResponse)


def test_session_diff_omits_message_id_when_none():
    """session.diff() does not add messageID when not given."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture query."""
        captured['query'] = str(request.url.query)
        return httpx.Response(200, json=[])

    with make_client(handler) as oc:
        oc.session.diff(_SESSION_ID)
    assert 'messageID' not in captured['query']


def test_session_todo_returns_todos():
    """session.todo() returns OpencodeTodosResponse."""
    def handler(request: httpx.Request) -> httpx.Response:
        """Return a list of todos."""
        return httpx.Response(
            200,
            json=[{
                'content': 'write tests',
                'status': 'pending',
                'priority': 'high',
            }],
        )

    with make_client(handler) as oc:
        resp = oc.session.todo(_SESSION_ID)
    assert isinstance(resp, OpencodeTodosResponse)
    assert len(resp.body) == 1
    assert resp.body[0].text == 'write tests'


def test_session_get_returns_error_on_404():
    """session.get() returns OpencodeErrorResponse on 404."""
    def handler(request: httpx.Request) -> httpx.Response:
        """Return 404 error."""
        return httpx.Response(
            404, json={'name': 'NotFoundError', 'message': 'missing'}
        )

    with make_client(handler) as oc:
        resp = oc.session.get(_SESSION_ID)
    assert isinstance(resp, OpencodeErrorResponse)
    assert resp.code == 404
    assert resp.body.name == 'NotFoundError'


def test_session_init_sends_correct_body():
    """session.init() POSTs modelID, providerID, messageID body."""
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture body."""
        seen['body'] = json.loads(request.content)
        seen['path'] = request.url.path
        return httpx.Response(200, json=True)

    with make_client(handler) as oc:
        resp = oc.session.init(
            _SESSION_ID,
            OpencodeSessionInit(
                model_id='claude-3',
                provider_id='anthropic',
                message_id=_MSG_ID,
            ),
        )
    assert seen['path'] == '/session/ses-abc123/init'
    assert seen['body'] == {
        'modelID': 'claude-3',
        'providerID': 'anthropic',
        'messageID': _MSG_ID,
    }
    assert isinstance(resp, OpencodeBoolResponse)
    assert resp.body is True


def test_session_fork_sends_message_id_when_given():
    """session.fork() sends messageID body when provided."""
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture body."""
        seen['body'] = json.loads(request.content)
        return httpx.Response(200, json=_session_payload())

    with make_client(handler) as oc:
        oc.session.fork(_SESSION_ID, OpencodeSessionFork(message_id=_MSG_ID))
    assert seen['body'] == {'messageID': _MSG_ID}


def test_session_summarize_sends_body():
    """session.summarize() sends providerID and modelID body."""
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture body."""
        seen['body'] = json.loads(request.content)
        return httpx.Response(200, json=True)

    with make_client(handler) as oc:
        oc.session.summarize(
            _SESSION_ID,
            OpencodeSessionSummarize(
                provider_id='anthropic', model_id='claude-3'
            ),
        )
    assert seen['body'] == {
        'providerID': 'anthropic',
        'modelID': 'claude-3',
    }


async def test_session_list_async():
    """session.list() works via the async client."""
    def handler(request: httpx.Request) -> httpx.Response:
        """Return an empty session list."""
        return httpx.Response(200, json=[])

    async with make_async_client(handler) as oc:
        resp = await oc.session.list()
    assert isinstance(resp, OpencodeSessionsResponse)
    assert resp.body == ()


async def test_session_get_async():
    """session.get() works via the async client."""
    def handler(request: httpx.Request) -> httpx.Response:
        """Return a session payload."""
        return httpx.Response(200, json=_session_payload())

    async with make_async_client(handler) as oc:
        resp = await oc.session.get(_SESSION_ID)
    assert isinstance(resp, OpencodeSessionResponse)
    assert resp.body.session_id == _SESSION_ID


async def test_session_delete_async():
    """session.delete() returns bool via the async client."""
    def handler(request: httpx.Request) -> httpx.Response:
        """Return true."""
        return httpx.Response(200, json=True)

    async with make_async_client(handler) as oc:
        resp = await oc.session.delete(_SESSION_ID)
    assert isinstance(resp, OpencodeBoolResponse)
    assert resp.body is True
