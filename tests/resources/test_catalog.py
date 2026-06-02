"""Tests for catalog read endpoints: agent, command, skill, path, lsp, mcp."""
import httpx

from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.catalog import OpencodePath
from tests.resources.conftest import make_async_client, make_client


def _json_handler(payload, status=200):
    """Return an httpx handler that always responds with *payload*."""
    def handler(request: httpx.Request) -> httpx.Response:
        """Handle request by returning the configured JSON payload."""
        return httpx.Response(status, json=payload)
    return handler


def test_path_get_parses_all_fields():
    """path.get() returns an OpencodePath with all fields populated."""
    handler = _json_handler({
        'home': '/root',
        'state': '/s',
        'config': '/c',
        'worktree': '/w',
        'directory': '/d',
    })
    with make_client(handler) as oc:
        resp = oc.path.get()
    assert resp.code == 200
    assert resp.body == OpencodePath(
        home='/root',
        state='/s',
        config='/c',
        worktree='/w',
        directory='/d',
    )


def test_path_get_request_path_and_method():
    """path.get() sends a GET to /path with no query params."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request details."""
        captured['method'] = request.method
        captured['path'] = request.url.path
        captured['query'] = dict(request.url.params)
        return httpx.Response(200, json={
            'home': '/h', 'state': '/s', 'config': '/c',
            'worktree': '/w', 'directory': '/d',
        })

    with make_client(handler) as oc:
        oc.path.get()
    assert captured['method'] == 'GET'
    assert captured['path'] == '/path'
    assert captured['query'] == {}


def test_agent_list_parses_each_entry():
    """agent.list() returns a tuple of OpencodeAgent entries."""
    handler = _json_handler([
        {
            'name': 'build',
            'mode': 'primary',
            'native': True,
            'options': {},
        },
    ])
    with make_client(handler) as oc:
        resp = oc.agent.list()
    assert resp.code == 200
    assert len(resp.body) == 1
    assert resp.body[0].name == 'build'
    assert resp.body[0].mode == 'primary'
    assert resp.body[0].native is True
    assert resp.body[0].options == {}


def test_agent_list_request_path_and_method():
    """agent.list() sends a GET to /agent."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request details."""
        captured['method'] = request.method
        captured['path'] = request.url.path
        return httpx.Response(200, json=[])

    with make_client(handler) as oc:
        oc.agent.list()
    assert captured['method'] == 'GET'
    assert captured['path'] == '/agent'


def test_command_list_parses_hints():
    """command.list() parses hints as a tuple of strings."""
    handler = _json_handler([
        {
            'name': 'deploy',
            'template': 'deploy {{target}}',
            'subtask': False,
            'hints': ['prod', 'staging'],
        },
    ])
    with make_client(handler) as oc:
        resp = oc.command.list()
    assert resp.body[0].name == 'deploy'
    assert resp.body[0].hints == ('prod', 'staging')
    assert resp.body[0].subtask is False
    assert resp.body[0].template == 'deploy {{target}}'


def test_skill_list_maps_content_to_text():
    """skill.list() exposes server field 'content' as 'text'."""
    handler = _json_handler([
        {'name': 's', 'location': '/l', 'content': 'hi'},
    ])
    with make_client(handler) as oc:
        resp = oc.skill.list()
    assert resp.body[0].text == 'hi'
    assert resp.body[0].name == 's'
    assert resp.body[0].location == '/l'


def test_lsp_status_parses_id_as_lsp_id():
    """lsp.status() maps server field 'id' to 'lsp_id'."""
    handler = _json_handler([
        {
            'id': 'lsp-1',
            'name': 'pyright',
            'root': '/repo',
            'status': 'running',
        },
    ])
    with make_client(handler) as oc:
        resp = oc.lsp.status()
    assert resp.body[0].lsp_id == 'lsp-1'
    assert resp.body[0].name == 'pyright'
    assert resp.body[0].root == '/repo'
    assert resp.body[0].status == 'running'


def test_mcp_status_returns_raw_map():
    """mcp.status() returns a dict[str, dict[str, object]] without modelling."""
    handler = _json_handler({'srv': {'type': 'connected'}})
    with make_client(handler) as oc:
        resp = oc.mcp.status()
    assert resp.body == {'srv': {'type': 'connected'}}


def test_error_response_propagated():
    """A 404 response from the server is decoded as OpencodeErrorResponse."""
    def handler(request: httpx.Request) -> httpx.Response:
        """Return a 404 error payload."""
        return httpx.Response(
            404,
            json={'name': 'NotFoundError', 'data': {'message': 'not found'}},
        )

    with make_client(handler) as oc:
        resp = oc.path.get()
    assert isinstance(resp, OpencodeErrorResponse)
    assert resp.code == 404
    assert resp.body.name == 'NotFoundError'
    assert resp.body.message == 'not found'


async def test_path_get_async():
    """path.get() also works through the async client."""
    handler = _json_handler({
        'home': '/h', 'state': '/s', 'config': '/c',
        'worktree': '/w', 'directory': '/d',
    })
    async with make_async_client(handler) as oc:
        resp = await oc.path.get()
    assert resp.code == 200
    assert resp.body.home == '/h'


async def test_agent_list_async():
    """agent.list() also works through the async client."""
    handler = _json_handler([
        {'name': 'a', 'mode': 'secondary', 'native': False, 'options': {}},
    ])
    async with make_async_client(handler) as oc:
        resp = await oc.agent.list()
    assert resp.body[0].name == 'a'
