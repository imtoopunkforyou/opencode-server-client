import json

import httpx

from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.config import (
    OpencodeConfig,
    OpencodeConfigResponse,
)
from opencode_server_client.models.health import (
    OpencodeHealthData,
    OpencodeHealthResponse,
)
from tests.resources.conftest import make_async_client, make_client


def test_health_sync(health_handler):
    """server.health() returns a typed OpencodeHealthResponse."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request and return healthy payload."""
        captured['request'] = request
        return httpx.Response(200, json={'healthy': True, 'version': '1.15.13'})

    with make_client(handler) as oc:
        resp = oc.server.health()
    assert captured['request'].method == 'GET'
    assert captured['request'].url.path == '/global/health'
    assert isinstance(resp, OpencodeHealthResponse)
    assert resp.code == 200
    assert resp.body == OpencodeHealthData(healthy=True, version='1.15.13')


async def test_health_async(health_handler):
    """server.health() returns a typed response via the async client."""
    async with make_async_client(health_handler) as oc:
        resp = await oc.server.health()
    assert isinstance(resp, OpencodeHealthResponse)
    assert resp.code == 200
    assert resp.body.version == '1.15.13'


def test_health_error_maps_to_error_response():
    """A 400 response from the server is decoded as OpencodeErrorResponse."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Return a 400 error payload."""
        return httpx.Response(
            400,
            json={'name': 'BadRequest', 'data': {'message': 'bad'}},
        )

    with make_client(handler) as oc:
        resp = oc.server.health()
    assert isinstance(resp, OpencodeErrorResponse)
    assert resp.code == 400
    assert resp.body.message == 'bad'


def test_server_config_sync():
    """server.config() returns a typed OpencodeConfigResponse."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request and return a config payload."""
        captured['request'] = request
        return httpx.Response(200, json={'username': 'u', 'autoupdate': False})

    with make_client(handler) as oc:
        resp = oc.server.config()
    assert captured['request'].url.path == '/global/config'
    assert captured['request'].method == 'GET'
    assert resp.code == 200
    assert isinstance(resp, OpencodeConfigResponse)
    assert resp.body.username == 'u'


def test_server_update_config_sync():
    """server.update_config() sends PATCH and returns a typed response."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request and return updated config payload."""
        captured['request'] = request
        return httpx.Response(200, json={'username': 'u', 'autoupdate': True})

    with make_client(handler) as oc:
        resp = oc.server.update_config({'autoupdate': True})
    assert captured['request'].method == 'PATCH'
    assert captured['request'].url.path == '/global/config'
    assert json.loads(captured['request'].content) == {'autoupdate': True}
    assert isinstance(resp.body, OpencodeConfig)


async def test_server_update_config_async():
    """update_config() sends PATCH via async client, returns OpencodeConfig."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request and return updated config payload."""
        captured['request'] = request
        return httpx.Response(200, json={'username': 'u', 'autoupdate': True})

    async with make_async_client(handler) as oc:
        resp = await oc.server.update_config({'autoupdate': True})
    assert captured['request'].method == 'PATCH'
    assert captured['request'].url.path == '/global/config'
    assert json.loads(captured['request'].content) == {'autoupdate': True}
    assert isinstance(resp.body, OpencodeConfig)
