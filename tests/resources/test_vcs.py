"""Tests for vcs namespace endpoints: get, status, diff."""
import httpx

from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.vcs import (
    OpencodeVcsDiffResponse,
    OpencodeVcsFileDiff,
    OpencodeVcsFileStatus,
    OpencodeVcsInfo,
    OpencodeVcsInfoResponse,
    OpencodeVcsStatusResponse,
)
from tests.resources.conftest import make_async_client, make_client

_VCS_INFO_PAYLOAD = {'branch': 'main', 'default_branch': 'main'}

_FILE_STATUS_PAYLOAD = [
    {'file': 'src/foo.py', 'additions': 5.0, 'deletions': 2.0, 'status': 'M'},
]

_FILE_DIFF_PAYLOAD = [
    {
        'file': 'src/foo.py',
        'patch': '@@ -1 +1 @@\n-old\n+new',
        'additions': 5.0,
        'deletions': 2.0,
        'status': 'M',
    },
]


def _json_handler(payload, status=200):
    """Return an httpx handler that always responds with *payload*."""
    def handler(request: httpx.Request) -> httpx.Response:
        """Handle request by returning the configured JSON payload."""
        return httpx.Response(status, json=payload)
    return handler


def test_vcs_get_parses_branch_and_default_branch():
    """vcs.get() returns OpencodeVcsInfoResponse with branch fields."""
    with make_client(_json_handler(_VCS_INFO_PAYLOAD)) as oc:
        resp = oc.vcs.get()
    assert isinstance(resp, OpencodeVcsInfoResponse)
    assert resp.code == 200
    assert resp.body == OpencodeVcsInfo(branch='main', default_branch='main')


def test_vcs_get_optional_fields_none():
    """vcs.get() tolerates missing optional branch fields."""
    with make_client(_json_handler({})) as oc:
        resp = oc.vcs.get()
    assert resp.body.branch is None
    assert resp.body.default_branch is None


def test_vcs_get_request_path_and_method():
    """vcs.get() sends GET to /vcs."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request details."""
        captured['method'] = request.method
        captured['path'] = request.url.path
        return httpx.Response(200, json=_VCS_INFO_PAYLOAD)

    with make_client(handler) as oc:
        oc.vcs.get()
    assert captured['method'] == 'GET'
    assert captured['path'] == '/vcs'


def test_vcs_get_directory_override():
    """vcs.get() passes directory override in query string."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture query params."""
        captured['query'] = dict(request.url.params)
        return httpx.Response(200, json=_VCS_INFO_PAYLOAD)

    with make_client(handler) as oc:
        oc.vcs.get(directory='/my/repo')
    assert captured['query'].get('directory') == '/my/repo'  # type: ignore[union-attr]


def test_vcs_status_parses_entries():
    """vcs.status() returns OpencodeVcsStatusResponse with file entries."""
    with make_client(_json_handler(_FILE_STATUS_PAYLOAD)) as oc:
        resp = oc.vcs.status()
    assert isinstance(resp, OpencodeVcsStatusResponse)
    assert resp.code == 200
    assert len(resp.body) == 1
    entry = resp.body[0]
    assert isinstance(entry, OpencodeVcsFileStatus)
    assert entry.filepath == 'src/foo.py'
    assert entry.additions == 5.0
    assert entry.deletions == 2.0
    assert entry.status == 'M'


def test_vcs_status_request_path_and_method():
    """vcs.status() sends GET to /vcs/status."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request details."""
        captured['method'] = request.method
        captured['path'] = request.url.path
        return httpx.Response(200, json=[])

    with make_client(handler) as oc:
        oc.vcs.status()
    assert captured['method'] == 'GET'
    assert captured['path'] == '/vcs/status'


def test_vcs_status_empty():
    """vcs.status() returns an empty tuple when server returns []."""
    with make_client(_json_handler([])) as oc:
        resp = oc.vcs.status()
    assert resp.body == ()


def test_vcs_diff_sends_required_mode_param():
    """vcs.diff() sends the required mode query param to /vcs/diff."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request details."""
        captured['method'] = request.method
        captured['path'] = request.url.path
        captured['query'] = dict(request.url.params)
        return httpx.Response(200, json=_FILE_DIFF_PAYLOAD)

    with make_client(handler) as oc:
        oc.vcs.diff('git')
    assert captured['method'] == 'GET'
    assert captured['path'] == '/vcs/diff'
    assert captured['query'].get('mode') == 'git'  # type: ignore[union-attr]
    assert 'context' not in captured['query']  # type: ignore[operator]


def test_vcs_diff_sends_optional_context_param():
    """vcs.diff() includes context query param when provided."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture query params."""
        captured['query'] = dict(request.url.params)
        return httpx.Response(200, json=[])

    with make_client(handler) as oc:
        oc.vcs.diff('branch', context=5)
    query = captured['query']
    assert query.get('mode') == 'branch'  # type: ignore[union-attr]
    assert query.get('context') == '5'  # type: ignore[union-attr]


def test_vcs_diff_parses_entries():
    """vcs.diff() returns OpencodeVcsDiffResponse with diff entries."""
    with make_client(_json_handler(_FILE_DIFF_PAYLOAD)) as oc:
        resp = oc.vcs.diff('git')
    assert isinstance(resp, OpencodeVcsDiffResponse)
    assert resp.code == 200
    assert len(resp.body) == 1
    entry = resp.body[0]
    assert isinstance(entry, OpencodeVcsFileDiff)
    assert entry.filepath == 'src/foo.py'
    assert entry.patch == '@@ -1 +1 @@\n-old\n+new'
    assert entry.additions == 5.0
    assert entry.deletions == 2.0
    assert entry.status == 'M'


def test_vcs_diff_patch_none():
    """vcs.diff() tolerates a missing patch field."""
    payload = [{'file': 'a.py', 'additions': 1.0, 'deletions': 0.0}]
    with make_client(_json_handler(payload)) as oc:
        resp = oc.vcs.diff('git')
    assert resp.body[0].patch is None
    assert resp.body[0].status is None
    assert resp.body[0].filepath == 'a.py'


def test_vcs_error_maps_to_error_response():
    """A non-2xx response is decoded as OpencodeErrorResponse."""
    def handler(request: httpx.Request) -> httpx.Response:
        """Return a 500 error payload."""
        return httpx.Response(
            500,
            json={'name': 'InternalError', 'data': {'message': 'oops'}},
        )

    with make_client(handler) as oc:
        resp = oc.vcs.get()
    assert isinstance(resp, OpencodeErrorResponse)
    assert resp.code == 500
    assert resp.body.name == 'InternalError'
    assert resp.body.message == 'oops'


async def test_vcs_get_async():
    """vcs.get() works through the async client."""
    async with make_async_client(_json_handler(_VCS_INFO_PAYLOAD)) as oc:
        resp = await oc.vcs.get()
    assert resp.code == 200
    assert resp.body.branch == 'main'


async def test_vcs_diff_async():
    """vcs.diff() works through the async client."""
    async with make_async_client(_json_handler(_FILE_DIFF_PAYLOAD)) as oc:
        resp = await oc.vcs.diff('git', context=3)
    assert resp.code == 200
    assert resp.body[0].filepath == 'src/foo.py'
