import httpx

from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.health import (
    OpencodeHealthData,
    OpencodeHealthResponse,
)
from tests.resources.conftest import make_async_client, make_client


def test_health_sync(health_handler):
    with make_client(health_handler) as oc:
        resp = oc.server.health()
    assert isinstance(resp, OpencodeHealthResponse)
    assert resp.code == 200
    assert resp.body == OpencodeHealthData(healthy=True, version='1.15.13')


async def test_health_async(health_handler):
    async with make_async_client(health_handler) as oc:
        resp = await oc.server.health()
    assert resp.body.version == '1.15.13'


def test_health_error_maps_to_error_response():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={'name': 'BadRequest',
                                         'data': {'message': 'bad'}})
    with make_client(handler) as oc:
        resp = oc.server.health()
    assert isinstance(resp, OpencodeErrorResponse)
    assert resp.code == 400
    assert resp.body.message == 'bad'
