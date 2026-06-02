import httpx
import pytest

from opencode_server_client import OpencodeAsyncClient, OpencodeClient


def make_client(handler) -> OpencodeClient:
    """Sync client wired to a MockTransport handler."""
    return OpencodeClient('http://oc', transport=httpx.MockTransport(handler))


def make_async_client(handler) -> OpencodeAsyncClient:
    """Async client wired to a MockTransport handler."""
    return OpencodeAsyncClient(
        'http://oc',
        transport=httpx.MockTransport(handler),
    )


@pytest.fixture
def health_handler():
    """Return an httpx handler that always responds with a healthy payload."""
    def handler(request: httpx.Request) -> httpx.Response:
        """Handle the request by returning a healthy response."""
        return httpx.Response(200, json={'healthy': True, 'version': '1.15.13'})
    return handler
