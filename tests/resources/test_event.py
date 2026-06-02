"""Tests for the event SSE streaming resource."""
import httpx

from opencode_server_client.models.event import OpencodeEvent
from tests.resources.conftest import make_async_client, make_client

_SSE_TYPE = 'server.connected'
_SSE_BODY = (
    'data: {"type":"server.connected","properties":{}}\n\n'
)


def _sse_handler(request: httpx.Request) -> httpx.Response:
    """Return a single SSE event."""
    return httpx.Response(
        200,
        text=_SSE_BODY,
        headers={'content-type': 'text/event-stream'},
    )


def test_event_subscribe_yields_parsed_events():
    """subscribe() yields typed OpencodeEvent objects."""
    with make_client(_sse_handler) as oc:
        found = list(oc.event.subscribe())
    assert len(found) == 1
    assert isinstance(found[0], OpencodeEvent)
    assert found[0].event_type == _SSE_TYPE
    assert found[0].properties == {}


def test_event_subscribe_raw_contains_type():
    """subscribe() raw field equals the decoded JSON dict."""
    with make_client(_sse_handler) as oc:
        found = list(oc.event.subscribe())
    assert found[0].raw.get('type') == _SSE_TYPE


async def test_event_subscribe_async_yields_events():
    """Async subscribe() yields typed events via the async client."""
    async with make_async_client(_sse_handler) as oc:
        collected = [
            entry async for entry in oc.event.subscribe()
        ]
    assert len(collected) == 1
    assert collected[0].event_type == _SSE_TYPE
    assert collected[0].properties == {}


def test_event_subscribe_skips_non_data_lines():
    """Non-data: SSE lines (event:, comment, blank) are ignored."""
    def handler(request: httpx.Request) -> httpx.Response:
        """Return SSE with metadata lines mixed in."""
        body = (
            'event: message\n'
            ': this is a comment\n'
            '\n'
            'data: {"type":"ping","properties":{}}\n\n'
        )
        return httpx.Response(
            200,
            text=body,
            headers={'content-type': 'text/event-stream'},
        )

    with make_client(handler) as oc:
        found = list(oc.event.subscribe())
    assert len(found) == 1
    assert found[0].event_type == 'ping'


def test_event_subscribe_skips_invalid_json():
    """Lines with invalid JSON after data: are silently dropped."""
    def handler(request: httpx.Request) -> httpx.Response:
        """Return SSE with one broken and one valid line."""
        body = (
            'data: not-valid-json\n'
            'data: {"type":"ok","properties":{}}\n\n'
        )
        return httpx.Response(
            200,
            text=body,
            headers={'content-type': 'text/event-stream'},
        )

    with make_client(handler) as oc:
        found = list(oc.event.subscribe())
    assert len(found) == 1
    assert found[0].event_type == 'ok'


def test_event_subscribe_skips_blank_data_lines():
    """data: lines with only whitespace produce no event."""
    def handler(request: httpx.Request) -> httpx.Response:
        """Return SSE with a blank data line."""
        body = (
            'data: \n'
            'data: {"type":"hello","properties":{}}\n\n'
        )
        return httpx.Response(
            200,
            text=body,
            headers={'content-type': 'text/event-stream'},
        )

    with make_client(handler) as oc:
        found = list(oc.event.subscribe())
    assert len(found) == 1
    assert found[0].event_type == 'hello'
