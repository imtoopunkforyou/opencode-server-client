import httpx
import pytest

from opencode_server_client import OpencodeAsyncClient, OpencodeClient


def make_client(handler) -> OpencodeClient:
    """Sync client wired to a MockTransport handler."""
    return OpencodeClient('http://oc', transport=httpx.MockTransport(handler))


def make_async_client(handler) -> OpencodeAsyncClient:
    """Async client wired to a MockTransport handler."""
    return OpencodeAsyncClient('http://oc', transport=httpx.MockTransport(handler))


@pytest.fixture
def health_handler():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={'healthy': True, 'version': '1.15.13'})
    return handler
