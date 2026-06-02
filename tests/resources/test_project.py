"""Tests for project namespace endpoints: list and current."""
import httpx

from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.common import OpencodeTimestamps
from opencode_server_client.models.project import OpencodeProject
from tests.resources.conftest import make_async_client, make_client

_PROJECT_PAYLOAD = {
    'id': 'proj-1',
    'worktree': '/home/user/repo',
    'vcs': 'git',
    'name': 'my-repo',
    'sandboxes': ['sandbox-a'],
    'time': {'created': 1700000000000, 'updated': 1700000001000},
}


def _json_handler(payload, status=200):
    """Return an httpx handler that always responds with *payload*."""
    def handler(request: httpx.Request) -> httpx.Response:
        """Handle request by returning the configured JSON payload."""
        return httpx.Response(status, json=payload)
    return handler


def test_project_current_parses_all_fields():
    """project.current() returns an OpencodeProject with all fields."""
    with make_client(_json_handler(_PROJECT_PAYLOAD)) as oc:
        resp = oc.project.current()
    assert resp.code == 200
    assert isinstance(resp.body, OpencodeProject)
    assert resp.body.project_id == 'proj-1'
    assert resp.body.worktree == '/home/user/repo'
    assert resp.body.vcs == 'git'
    assert resp.body.name == 'my-repo'
    assert resp.body.sandboxes == ('sandbox-a',)
    assert resp.body.time == OpencodeTimestamps(
        created=1700000000000,
        updated=1700000001000,
    )


def test_project_current_request_path_and_method():
    """project.current() sends GET to /project/current."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request details."""
        captured['method'] = request.method
        captured['path'] = request.url.path
        return httpx.Response(200, json=_PROJECT_PAYLOAD)

    with make_client(handler) as oc:
        oc.project.current()
    assert captured['method'] == 'GET'
    assert captured['path'] == '/project/current'


def test_project_list_returns_tuple():
    """project.list() returns a tuple of OpencodeProject entries."""
    handler = _json_handler([_PROJECT_PAYLOAD])
    with make_client(handler) as oc:
        resp = oc.project.list()
    assert resp.code == 200
    assert len(resp.body) == 1
    assert resp.body[0].project_id == 'proj-1'
    assert resp.body[0].worktree == '/home/user/repo'


def test_project_list_request_path_and_method():
    """project.list() sends GET to /project."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request details."""
        captured['method'] = request.method
        captured['path'] = request.url.path
        return httpx.Response(200, json=[])

    with make_client(handler) as oc:
        oc.project.list()
    assert captured['method'] == 'GET'
    assert captured['path'] == '/project'


def test_project_current_optional_fields_none():
    """project.current() tolerates missing optional fields."""
    minimal = {'id': 'p2', 'worktree': '/w'}
    with make_client(_json_handler(minimal)) as oc:
        resp = oc.project.current()
    assert resp.body.vcs is None
    assert resp.body.name is None
    assert resp.body.sandboxes == ()
    assert resp.body.time == OpencodeTimestamps(created=None, updated=None)


def test_project_list_empty():
    """project.list() returns an empty tuple when server returns []."""
    with make_client(_json_handler([])) as oc:
        resp = oc.project.list()
    assert resp.body == ()


def test_project_list_directory_override():
    """project.list() passes directory override in query string."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture query params."""
        captured['query'] = dict(request.url.params)
        return httpx.Response(200, json=[])

    with make_client(handler) as oc:
        oc.project.list(directory='/override')
    assert captured['query'].get('directory') == '/override'


def test_project_error_maps_to_error_response():
    """A 404 response is decoded as OpencodeErrorResponse."""
    def handler(request: httpx.Request) -> httpx.Response:
        """Return a 404 error payload."""
        return httpx.Response(
            404,
            json={'name': 'NotFoundError', 'data': {'message': 'no project'}},
        )

    with make_client(handler) as oc:
        resp = oc.project.current()
    assert isinstance(resp, OpencodeErrorResponse)
    assert resp.code == 404
    assert resp.body.name == 'NotFoundError'
    assert resp.body.message == 'no project'


async def test_project_current_async():
    """project.current() works through the async client."""
    async with make_async_client(_json_handler(_PROJECT_PAYLOAD)) as oc:
        resp = await oc.project.current()
    assert resp.code == 200
    assert resp.body.project_id == 'proj-1'


async def test_project_list_async():
    """project.list() works through the async client."""
    async with make_async_client(_json_handler([_PROJECT_PAYLOAD])) as oc:
        resp = await oc.project.list()
    assert resp.body[0].name == 'my-repo'
