"""Tests for the config namespace resource."""

import json

import httpx

from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.config import (
    OpencodeConfigResponse,
    OpencodeProvidersConfigResponse,
)
from tests.resources.conftest import make_async_client, make_client

_PROVIDERS_PAYLOAD = {
    'providers': [
        {
            'id': 'anthropic',
            'name': 'Anthropic',
            'source': 'opencode',
            'env': ['ANTHROPIC_API_KEY'],
            'models': {},
        }
    ],
    'default': {'model': 'claude-3-5-sonnet'},
}


def test_config_get_sends_get_to_config():
    """config.get() sends GET to /config and returns OpencodeConfigResponse."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request and return a config payload."""
        captured['method'] = request.method
        captured['path'] = request.url.path
        return httpx.Response(
            200, json={'username': 'alice', 'autoupdate': True}
        )

    with make_client(handler) as oc:
        resp = oc.config.get()
    assert captured['method'] == 'GET'
    assert captured['path'] == '/config'
    assert isinstance(resp, OpencodeConfigResponse)
    assert resp.code == 200
    assert resp.body.username == 'alice'


def test_config_update_sends_patch_body():
    """config.update() sends PATCH to /config with document as JSON body."""
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request method and body then return updated config."""
        seen['method'] = request.method
        seen['body'] = json.loads(request.content)
        return httpx.Response(200, json={'username': 'u', 'autoupdate': False})

    with make_client(handler) as oc:
        resp = oc.config.update({'autoupdate': True})
    assert seen['method'] == 'PATCH'
    assert seen['body'] == {'autoupdate': True}
    assert isinstance(resp, OpencodeConfigResponse)
    assert resp.body.username == 'u'


def test_config_providers_parses_providers_and_default():
    """config.providers() parses providers list and default map."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Return a providers config payload."""
        return httpx.Response(200, json=_PROVIDERS_PAYLOAD)

    with make_client(handler) as oc:
        resp = oc.config.providers()
    assert isinstance(resp, OpencodeProvidersConfigResponse)
    assert resp.code == 200
    assert len(resp.body.providers) == 1
    assert resp.body.providers[0].provider_id == 'anthropic'
    assert resp.body.providers[0].name == 'Anthropic'
    assert resp.body.default == {'model': 'claude-3-5-sonnet'}


def test_config_providers_sends_get_to_config_providers():
    """config.providers() sends GET to /config/providers."""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture request path and return providers payload."""
        captured['path'] = request.url.path
        captured['method'] = request.method
        return httpx.Response(200, json=_PROVIDERS_PAYLOAD)

    with make_client(handler) as oc:
        oc.config.providers()
    assert captured['method'] == 'GET'
    assert captured['path'] == '/config/providers'


def test_config_get_error_returns_error_response():
    """config.get() returns OpencodeErrorResponse on non-2xx status."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Return a 403 error."""
        return httpx.Response(
            403, json={'name': 'ForbiddenError', 'data': {'message': 'denied'}}
        )

    with make_client(handler) as oc:
        resp = oc.config.get()
    assert isinstance(resp, OpencodeErrorResponse)
    assert resp.code == 403
    assert resp.body.name == 'ForbiddenError'
    assert resp.body.message == 'denied'


async def test_config_get_async():
    """config.get() works via the async client."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Return a config payload."""
        return httpx.Response(
            200, json={'username': 'bob', 'autoupdate': False}
        )

    async with make_async_client(handler) as oc:
        resp = await oc.config.get()
    assert isinstance(resp, OpencodeConfigResponse)
    assert resp.body.username == 'bob'


async def test_config_update_async():
    """config.update() sends PATCH via the async client."""
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture method and return updated config."""
        seen['method'] = request.method
        seen['body'] = json.loads(request.content)
        return httpx.Response(200, json={'username': 'bob', 'autoupdate': True})

    async with make_async_client(handler) as oc:
        resp = await oc.config.update({'autoupdate': True})
    assert seen['method'] == 'PATCH'
    assert seen['body'] == {'autoupdate': True}
    assert isinstance(resp, OpencodeConfigResponse)


async def test_config_providers_async():
    """config.providers() parses providers via the async client."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Return a providers payload."""
        return httpx.Response(200, json=_PROVIDERS_PAYLOAD)

    async with make_async_client(handler) as oc:
        resp = await oc.config.providers()
    assert isinstance(resp, OpencodeProvidersConfigResponse)
    assert resp.body.providers[0].provider_id == 'anthropic'
    assert resp.body.default == {'model': 'claude-3-5-sonnet'}
