"""Tests for provider namespace endpoints: list, auth."""

import httpx

from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.provider import (
    OpencodeProviderAuthResponse,
    OpencodeProviderList,
    OpencodeProviderListResponse,
)
from tests.resources.conftest import make_async_client, make_client

_MODEL_PAYLOAD = {
    'id': 'gpt-4o',
    'providerID': 'openai',
    'name': 'GPT-4o',
    'family': 'gpt-4',
    'status': 'ga',
    'release_date': '2024-05-13',
    'capabilities': {
        'temperature': True,
        'reasoning': False,
        'attachment': True,
        'toolcall': True,
        'input': {
            'text': True,
            'audio': False,
            'image': True,
            'video': False,
            'pdf': False,
        },
        'output': {
            'text': True,
            'audio': False,
            'image': False,
            'video': False,
            'pdf': False,
        },
    },
    'cost': {
        'input': 2.5e-06,
        'output': 1e-05,
        'cache': {
            'read': 1.25e-06,
            'write': 3.75e-06,
        },
    },
    'limit': {
        'context': 128000.0,
        'input': None,
        'output': 4096.0,
    },
    'options': {},
}

_PROVIDER_PAYLOAD = {
    'id': 'openai',
    'name': 'OpenAI',
    'source': 'official',
    'env': ['OPENAI_API_KEY'],
    'key': 'sk-test',
    'options': {},
    'models': {'gpt-4o': _MODEL_PAYLOAD},
}

_LIST_PAYLOAD = {
    'all': [_PROVIDER_PAYLOAD],
    'default': {'provider': 'openai', 'model': 'gpt-4o'},
    'connected': ['openai'],
}

_AUTH_PAYLOAD = {'openai': True, 'anthropic': False}


def _json_handler(payload, status=200):
    """Return an httpx handler that always responds with *payload*."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Handle the request by returning the configured JSON payload."""
        return httpx.Response(status, json=payload)

    return handler


def test_provider_list_response_type():
    """provider.list() returns OpencodeProviderListResponse."""
    with make_client(_json_handler(_LIST_PAYLOAD)) as oc:
        resp = oc.provider.list()
    assert isinstance(resp, OpencodeProviderListResponse)
    assert resp.code == 200


def test_provider_list_parses_providers():
    """provider.list() body is an OpencodeProviderList with providers."""
    with make_client(_json_handler(_LIST_PAYLOAD)) as oc:
        resp = oc.provider.list()
    assert isinstance(resp.body, OpencodeProviderList)
    assert len(resp.body.all_providers) == 1
    provider = resp.body.all_providers[0]
    assert provider.provider_id == 'openai'
    assert provider.name == 'OpenAI'
    assert provider.source == 'official'
    assert provider.env == ('OPENAI_API_KEY',)
    assert provider.key == 'sk-test'


def test_provider_list_models_dict():
    """provider.list() nested models dict is keyed by model name."""
    with make_client(_json_handler(_LIST_PAYLOAD)) as oc:
        resp = oc.provider.list()
    provider = resp.body.all_providers[0]
    assert 'gpt-4o' in provider.models
    model = provider.models['gpt-4o']
    assert model.model_id == 'gpt-4o'
    assert model.provider_id == 'openai'
    assert model.name == 'GPT-4o'
    assert model.family == 'gpt-4'
    assert model.status == 'ga'


def test_provider_list_model_cost_nested():
    """provider.list() parses nested cost.cache.read/write correctly."""
    with make_client(_json_handler(_LIST_PAYLOAD)) as oc:
        resp = oc.provider.list()
    cost = resp.body.all_providers[0].models['gpt-4o'].cost
    assert cost.input == 2.5e-06
    assert cost.output == 1e-05
    assert cost.cache_read == 1.25e-06
    assert cost.cache_write == 3.75e-06


def test_provider_list_model_limit():
    """provider.list() parses limit.context, output, and opt input."""
    with make_client(_json_handler(_LIST_PAYLOAD)) as oc:
        resp = oc.provider.list()
    limit = resp.body.all_providers[0].models['gpt-4o'].limit
    assert limit.context == 128000.0
    assert limit.input is None
    assert limit.output == 4096.0


def test_provider_list_model_capabilities_input_modalities():
    """provider.list() parses capabilities.input.text correctly."""
    with make_client(_json_handler(_LIST_PAYLOAD)) as oc:
        resp = oc.provider.list()
    caps = resp.body.all_providers[0].models['gpt-4o'].capabilities
    assert caps.temperature is True
    assert caps.reasoning is False
    assert caps.input.text is True
    assert caps.input.image is True
    assert caps.input.audio is False
    assert caps.output.text is True


def test_provider_list_default_and_connected():
    """provider.list() body has default map and connected tuple."""
    with make_client(_json_handler(_LIST_PAYLOAD)) as oc:
        resp = oc.provider.list()
    assert resp.body.default == {'provider': 'openai', 'model': 'gpt-4o'}
    assert resp.body.connected == ('openai',)


def test_provider_list_sends_get_to_provider():
    """provider.list() sends GET /provider."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture the request method and path."""
        captured['method'] = request.method
        captured['path'] = request.url.path
        return httpx.Response(200, json=_LIST_PAYLOAD)

    with make_client(handler) as oc:
        oc.provider.list()
    assert captured['method'] == 'GET'
    assert captured['path'] == '/provider'


def test_provider_auth_response_type():
    """provider.auth() returns OpencodeProviderAuthResponse."""
    with make_client(_json_handler(_AUTH_PAYLOAD)) as oc:
        resp = oc.provider.auth()
    assert isinstance(resp, OpencodeProviderAuthResponse)
    assert resp.code == 200
    assert resp.body == {'openai': True, 'anthropic': False}


def test_provider_auth_sends_get_to_provider_auth():
    """provider.auth() sends GET /provider/auth."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """Capture the request method and path."""
        captured['method'] = request.method
        captured['path'] = request.url.path
        return httpx.Response(200, json=_AUTH_PAYLOAD)

    with make_client(handler) as oc:
        oc.provider.auth()
    assert captured['method'] == 'GET'
    assert captured['path'] == '/provider/auth'


def test_provider_list_error_response():
    """A non-2xx response from provider.list() is an OpencodeErrorResponse."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Return a 500 error."""
        return httpx.Response(
            500,
            json={'name': 'InternalError', 'data': {'message': 'boom'}},
        )

    with make_client(handler) as oc:
        resp = oc.provider.list()
    assert isinstance(resp, OpencodeErrorResponse)
    assert resp.code == 500
    assert resp.body.name == 'InternalError'
    assert resp.body.message == 'boom'


async def test_provider_list_async():
    """provider.list() works through the async client."""
    async with make_async_client(_json_handler(_LIST_PAYLOAD)) as oc:
        resp = await oc.provider.list()
    assert isinstance(resp, OpencodeProviderListResponse)
    assert resp.code == 200
    assert len(resp.body.all_providers) == 1
    assert resp.body.all_providers[0].provider_id == 'openai'


async def test_provider_auth_async():
    """provider.auth() works through the async client."""
    async with make_async_client(_json_handler(_AUTH_PAYLOAD)) as oc:
        resp = await oc.provider.auth()
    assert isinstance(resp, OpencodeProviderAuthResponse)
    assert resp.body.get('openai') is True
