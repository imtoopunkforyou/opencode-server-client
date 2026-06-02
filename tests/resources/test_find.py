"""Tests for find namespace endpoints: text, files, symbols."""

import httpx

from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.find import (
    OpencodeFindFilesQuery,
    OpencodeFindFilesResponse,
    OpencodeMatch,
    OpencodeMatchesResponse,
    OpencodeRange,
    OpencodeSymbol,
    OpencodeSymbolsResponse,
)
from tests.resources.conftest import make_async_client, make_client

_MATCH_PAYLOAD = [
    {
        'path': {'text': 'src/main.py'},
        'lines': {'text': 'def foo():'},
        'line_number': 10,
        'absolute_offset': 150,
        'submatches': [{'match': {'text': 'foo'}, 'start': 4, 'end': 7}],
    },
]

_SYMBOL_PAYLOAD = [
    {
        'name': 'MyClass',
        'kind': 5,
        'location': {
            'uri': 'file:///repo/src/main.py',
            'range': {
                'start': {'line': 0, 'character': 0},
                'end': {'line': 10, 'character': 0},
            },
        },
    },
]

_FILES_PAYLOAD = ['src/main.py', 'src/utils.py']


def _json_handler(payload, status=200):
    """Return an httpx handler that always responds with *payload*."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Handle the request by returning the configured JSON payload."""
        return httpx.Response(status, json=payload)

    return handler


def test_find_text_parses_matches():
    """find.text() returns OpencodeMatchesResponse with match objects."""
    with make_client(_json_handler(_MATCH_PAYLOAD)) as oc:
        resp = oc.find.text('foo')
    assert isinstance(resp, OpencodeMatchesResponse)
    assert resp.code == 200
    assert len(resp.body) == 1
    entry = resp.body[0]
    assert isinstance(entry, OpencodeMatch)
    assert entry.path == 'src/main.py'
    assert entry.lines == 'def foo():'
    assert entry.line_number == 10
    assert entry.absolute_offset == 150


def test_find_text_nested_path_maps_to_path():
    """find.text() maps nested path.text to the path field."""
    payload = [{'path': {'text': '/repo/lib.py'}, 'lines': {'text': 'x'}}]
    with make_client(_json_handler(payload)) as oc:
        resp = oc.find.text('x')
    assert resp.body[0].path == '/repo/lib.py'


def test_find_text_submatches_coerced_to_dicts():
    """find.text() coerces each submatch to a plain dict."""
    with make_client(_json_handler(_MATCH_PAYLOAD)) as oc:
        resp = oc.find.text('foo')
    assert isinstance(resp.body[0].submatches[0], dict)
    assert resp.body[0].submatches[0]['start'] == 4


def test_find_text_sends_pattern_in_query():
    """find.text() sends GET /find with pattern in the query string."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request details."""
        captured['method'] = request.method
        captured['path'] = request.url.path
        captured['query'] = dict(request.url.params)
        return httpx.Response(200, json=[])

    with make_client(handler) as oc:
        oc.find.text('hello')
    assert captured['method'] == 'GET'
    assert captured['path'] == '/find'
    assert captured['query'].get('pattern') == 'hello'  # type: ignore[union-attr]


def test_find_text_directory_override():
    """find.text() passes directory override in query string."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture query params."""
        captured['query'] = dict(request.url.params)
        return httpx.Response(200, json=[])

    with make_client(handler) as oc:
        oc.find.text('x', directory='/my/dir')
    query = captured['query']
    assert query.get('pattern') == 'x'  # type: ignore[union-attr]
    assert query.get('directory') == '/my/dir'  # type: ignore[union-attr]


def test_find_text_empty_result():
    """find.text() returns empty tuple when server returns []."""
    with make_client(_json_handler([])) as oc:
        resp = oc.find.text('nothing')
    assert resp.body == ()


def test_find_files_parses_string_list():
    """find.files() returns OpencodeFindFilesResponse with file paths."""
    criteria = OpencodeFindFilesQuery(query='main')
    with make_client(_json_handler(_FILES_PAYLOAD)) as oc:
        resp = oc.find.files(criteria)
    assert isinstance(resp, OpencodeFindFilesResponse)
    assert resp.code == 200
    assert resp.body == ('src/main.py', 'src/utils.py')


def test_find_files_sends_all_query_params():
    """find.files() sends query, dirs, type, and limit to /find/file."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request details."""
        captured['method'] = request.method
        captured['path'] = request.url.path
        captured['query'] = dict(request.url.params)
        return httpx.Response(200, json=[])

    criteria = OpencodeFindFilesQuery(
        query='foo',
        dirs='/src',
        type_filter='py',
        limit=5,
    )
    with make_client(handler) as oc:
        oc.find.files(criteria)
    assert captured['method'] == 'GET'
    assert captured['path'] == '/find/file'
    params = captured['query']
    assert params.get('query') == 'foo'  # type: ignore[union-attr]
    assert params.get('dirs') == '/src'  # type: ignore[union-attr]
    assert params.get('type') == 'py'  # type: ignore[union-attr]
    assert params.get('limit') == '5'  # type: ignore[union-attr]


def test_find_files_optional_params_omitted():
    """find.files() does not send None query params."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture query params."""
        captured['query'] = dict(request.url.params)
        return httpx.Response(200, json=[])

    criteria = OpencodeFindFilesQuery(query='main')
    with make_client(handler) as oc:
        oc.find.files(criteria)
    params = captured['query']
    assert 'dirs' not in params  # type: ignore[operator]
    assert 'type' not in params  # type: ignore[operator]
    assert 'limit' not in params  # type: ignore[operator]


def test_find_symbols_parses_symbols():
    """find.symbols() returns OpencodeSymbolsResponse with symbol objects."""
    with make_client(_json_handler(_SYMBOL_PAYLOAD)) as oc:
        resp = oc.find.symbols('MyClass')
    assert isinstance(resp, OpencodeSymbolsResponse)
    assert resp.code == 200
    assert len(resp.body) == 1
    sym = resp.body[0]
    assert isinstance(sym, OpencodeSymbol)
    assert sym.name == 'MyClass'
    assert sym.kind == 5
    assert sym.uri == 'file:///repo/src/main.py'


def test_find_symbols_range_parsed():
    """find.symbols() correctly parses nested location.range."""
    with make_client(_json_handler(_SYMBOL_PAYLOAD)) as oc:
        resp = oc.find.symbols('MyClass')
    sym_range = resp.body[0].symbol_range
    assert isinstance(sym_range, OpencodeRange)
    assert sym_range.start_line == 0
    assert sym_range.start_character == 0
    assert sym_range.end_line == 10
    assert sym_range.end_character == 0


def test_find_symbols_sends_query_param():
    """find.symbols() sends GET /find/symbol with query in query string."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request details."""
        captured['method'] = request.method
        captured['path'] = request.url.path
        captured['query'] = dict(request.url.params)
        return httpx.Response(200, json=[])

    with make_client(handler) as oc:
        oc.find.symbols('Foo')
    assert captured['method'] == 'GET'
    assert captured['path'] == '/find/symbol'
    assert captured['query'].get('query') == 'Foo'  # type: ignore[union-attr]


def test_find_error_maps_to_error_response():
    """A non-2xx response is decoded as OpencodeErrorResponse."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Return a 500 error payload."""
        return httpx.Response(
            500,
            json={'name': 'InternalError', 'data': {'message': 'boom'}},
        )

    with make_client(handler) as oc:
        resp = oc.find.text('err')
    assert isinstance(resp, OpencodeErrorResponse)
    assert resp.code == 500
    assert resp.body.name == 'InternalError'
    assert resp.body.message == 'boom'


async def test_find_text_async():
    """find.text() works through the async client."""
    async with make_async_client(_json_handler(_MATCH_PAYLOAD)) as oc:
        resp = await oc.find.text('foo')
    assert resp.code == 200
    assert resp.body[0].path == 'src/main.py'


async def test_find_files_async():
    """find.files() works through the async client."""
    criteria = OpencodeFindFilesQuery(query='main')
    async with make_async_client(_json_handler(_FILES_PAYLOAD)) as oc:
        resp = await oc.find.files(criteria)
    assert resp.code == 200
    assert 'src/main.py' in resp.body


async def test_find_symbols_async():
    """find.symbols() works through the async client."""
    async with make_async_client(_json_handler(_SYMBOL_PAYLOAD)) as oc:
        resp = await oc.find.symbols('MyClass')
    assert resp.code == 200
    assert resp.body[0].name == 'MyClass'
