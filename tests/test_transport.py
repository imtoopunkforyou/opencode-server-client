import httpx

from opencode_server_client._transport import (
    RawResponse,
    RequestSpec,
    SyncTransport,
    build_query,
)


def _handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == '/echo':
        return httpx.Response(200, json={'path': request.url.path,
                                          'q': dict(request.url.params)})
    return httpx.Response(204)


def _sync_transport() -> SyncTransport:
    client = httpx.Client(base_url='http://t', transport=httpx.MockTransport(_handler))
    return SyncTransport(client, defaults={'directory': '/d'})


def test_build_query_drops_none_and_merges():
    assert build_query({'directory': '/d'}, directory='/o', extra={'path': 'x', 'k': None}) \
        == {'directory': '/o', 'path': 'x'}


def test_send_returns_rawresponse_with_decoded_json():
    transport = _sync_transport()
    raw = transport.send(RequestSpec('GET', '/echo', {'path': 'a'}, None))
    assert isinstance(raw, RawResponse)
    assert raw.code == 200
    assert raw.payload == {'path': '/echo', 'q': {'directory': '/d', 'path': 'a'}}


def test_send_empty_body_yields_none_payload():
    transport = _sync_transport()
    raw = transport.send(RequestSpec('GET', '/missing', {}, None))
    assert raw.code == 204
    assert raw.payload is None


async def test_async_send_works():
    client = httpx.AsyncClient(base_url='http://t', transport=httpx.MockTransport(_handler))
    from opencode_server_client._transport import AsyncTransport
    transport = AsyncTransport(client, defaults={})
    raw = await transport.send(RequestSpec('GET', '/echo', {}, None))
    assert raw.code == 200
    await transport.aclose()
