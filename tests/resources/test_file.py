"""Tests for file namespace endpoints: list, read, status."""
import httpx

from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.file import (
    OpencodeFileContent,
    OpencodeFileContentResponse,
    OpencodeFileNode,
    OpencodeFilesResponse,
    OpencodeFileStatus,
    OpencodeFileStatusResponse,
)
from tests.resources.conftest import make_async_client, make_client

_FILE_NODE_PAYLOAD = [
    {
        'name': 'main.py',
        'path': 'src/main.py',
        'absolute': '/repo/src/main.py',
        'type': 'file',
        'ignored': False,
    },
]

_FILE_CONTENT_PAYLOAD = {
    'type': 'text',
    'content': 'print("hello")',
    'diff': None,
    'encoding': 'utf-8',
    'mimeType': 'text/x-python',
    'patch': None,
}

_FILE_STATUS_PAYLOAD = [
    {'path': 'src/main.py', 'added': 10, 'removed': 2, 'status': 'M'},
]


def _json_handler(payload, status=200):
    """Return an httpx handler that always responds with *payload*."""
    def handler(request: httpx.Request) -> httpx.Response:
        """Handle request by returning the configured JSON payload."""
        return httpx.Response(status, json=payload)
    return handler


def test_file_list_parses_nodes():
    """file.list() returns OpencodeFilesResponse with file nodes."""
    with make_client(_json_handler(_FILE_NODE_PAYLOAD)) as oc:
        resp = oc.files.list('src/')
    assert isinstance(resp, OpencodeFilesResponse)
    assert resp.code == 200
    assert len(resp.body) == 1
    entry = resp.body[0]
    assert isinstance(entry, OpencodeFileNode)
    assert entry.name == 'main.py'
    assert entry.path == 'src/main.py'
    assert entry.absolute == '/repo/src/main.py'
    assert entry.type == 'file'
    assert entry.ignored is False


def test_file_list_sends_path_as_query_param():
    """file.list() sends the required path as a query parameter."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request details."""
        captured['method'] = request.method
        captured['path'] = request.url.path
        captured['query'] = dict(request.url.params)
        return httpx.Response(200, json=[])

    with make_client(handler) as oc:
        oc.files.list('/src')
    assert captured['method'] == 'GET'
    assert captured['path'] == '/file'
    assert captured['query'].get('path') == '/src'  # type: ignore[union-attr]


def test_file_list_directory_override():
    """file.list() passes directory override in query string."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture query params."""
        captured['query'] = dict(request.url.params)
        return httpx.Response(200, json=[])

    with make_client(handler) as oc:
        oc.files.list('/src', directory='/my/repo')
    query = captured['query']
    assert query.get('path') == '/src'  # type: ignore[union-attr]
    assert query.get('directory') == '/my/repo'  # type: ignore[union-attr]


def test_file_list_empty():
    """file.list() returns an empty tuple when server returns []."""
    with make_client(_json_handler([])) as oc:
        resp = oc.files.list('.')
    assert resp.body == ()


def test_file_read_parses_content():
    """file.read() returns OpencodeFileContentResponse with mapped fields."""
    with make_client(_json_handler(_FILE_CONTENT_PAYLOAD)) as oc:
        resp = oc.files.read('src/main.py')
    assert isinstance(resp, OpencodeFileContentResponse)
    assert resp.code == 200
    assert isinstance(resp.body, OpencodeFileContent)
    assert resp.body.type == 'text'
    assert resp.body.text == 'print("hello")'
    assert resp.body.encoding == 'utf-8'
    assert resp.body.mime_type == 'text/x-python'
    assert resp.body.diff is None
    assert resp.body.patch is None


def test_file_read_content_maps_to_text():
    """file.read() maps server key 'content' to the text field."""
    payload = {'type': 'text', 'content': 'hello world'}
    with make_client(_json_handler(payload)) as oc:
        resp = oc.files.read('README.md')
    assert resp.body.text == 'hello world'


def test_file_read_sends_path_as_query_param():
    """file.read() sends path as a query param to /file/content."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request details."""
        captured['method'] = request.method
        captured['endpoint'] = request.url.path
        captured['query'] = dict(request.url.params)
        return httpx.Response(200, json=_FILE_CONTENT_PAYLOAD)

    with make_client(handler) as oc:
        oc.files.read('/repo/main.py')
    assert captured['method'] == 'GET'
    assert captured['endpoint'] == '/file/content'
    assert captured['query'].get('path') == '/repo/main.py'  # type: ignore[union-attr]


def test_file_read_with_patch_dict():
    """file.read() parses patch dict when present."""
    payload = {
        'type': 'text',
        'content': 'abc',
        'patch': {'key': 'val'},
    }
    with make_client(_json_handler(payload)) as oc:
        resp = oc.files.read('a.py')
    assert resp.body.patch == {'key': 'val'}


def test_file_status_parses_entries():
    """file.status() returns OpencodeFileStatusResponse with entries."""
    with make_client(_json_handler(_FILE_STATUS_PAYLOAD)) as oc:
        resp = oc.files.status()
    assert isinstance(resp, OpencodeFileStatusResponse)
    assert resp.code == 200
    assert len(resp.body) == 1
    entry = resp.body[0]
    assert isinstance(entry, OpencodeFileStatus)
    assert entry.path == 'src/main.py'
    assert entry.added == 10
    assert entry.removed == 2
    assert entry.status == 'M'


def test_file_status_request_path_and_method():
    """file.status() sends GET to /file/status."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request details."""
        captured['method'] = request.method
        captured['path'] = request.url.path
        return httpx.Response(200, json=[])

    with make_client(handler) as oc:
        oc.files.status()
    assert captured['method'] == 'GET'
    assert captured['path'] == '/file/status'


def test_file_status_empty():
    """file.status() returns an empty tuple when server returns []."""
    with make_client(_json_handler([])) as oc:
        resp = oc.files.status()
    assert resp.body == ()


def test_file_error_maps_to_error_response():
    """A non-2xx response is decoded as OpencodeErrorResponse."""
    def handler(request: httpx.Request) -> httpx.Response:
        """Return a 404 error payload."""
        return httpx.Response(
            404,
            json={'name': 'NotFoundError', 'data': {'message': 'no file'}},
        )

    with make_client(handler) as oc:
        resp = oc.files.read('missing.py')
    assert isinstance(resp, OpencodeErrorResponse)
    assert resp.code == 404
    assert resp.body.name == 'NotFoundError'
    assert resp.body.message == 'no file'


async def test_file_list_async():
    """file.list() works through the async client."""
    async with make_async_client(_json_handler(_FILE_NODE_PAYLOAD)) as oc:
        resp = await oc.files.list('src/')
    assert resp.code == 200
    assert resp.body[0].name == 'main.py'


async def test_file_read_async():
    """file.read() works through the async client."""
    async with make_async_client(_json_handler(_FILE_CONTENT_PAYLOAD)) as oc:
        resp = await oc.files.read('src/main.py')
    assert resp.code == 200
    assert resp.body.text == 'print("hello")'


async def test_file_status_async():
    """file.status() works through the async client."""
    async with make_async_client(_json_handler(_FILE_STATUS_PAYLOAD)) as oc:
        resp = await oc.files.status()
    assert resp.code == 200
    assert resp.body[0].path == 'src/main.py'
