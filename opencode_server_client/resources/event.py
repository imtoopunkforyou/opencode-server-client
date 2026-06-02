"""Event stream endpoint (Server-Sent Events)."""
import json
from collections.abc import AsyncIterator, Iterator

from opencode_server_client.models.event import OpencodeEvent
from opencode_server_client.resources._base import _AsyncResource, _SyncResource

_DATA_PREFIX = 'data:'

_GET = 'GET'
_EVENT_PATH = '/event'


def _parse_line(line: str) -> OpencodeEvent | None:
    if not line.startswith(_DATA_PREFIX):
        return None
    chunk = line[len(_DATA_PREFIX):].strip()
    if not chunk:
        return None
    try:
        decoded = json.loads(chunk)
    except ValueError:
        return None
    return OpencodeEvent.from_payload(decoded)


class EventResource(_SyncResource):
    """Event stream (sync)."""

    def subscribe(self) -> Iterator[OpencodeEvent]:
        """Yield server events until the stream closes."""
        with self._transport.stream(_GET, _EVENT_PATH) as lines:
            for line in lines:
                event = _parse_line(line)
                if event is not None:
                    yield event


class AsyncEventResource(_AsyncResource):
    """Event stream (async)."""

    async def subscribe(self) -> AsyncIterator[OpencodeEvent]:
        """Yield server events until the stream closes."""
        async with self._transport.stream(_GET, _EVENT_PATH) as lines:
            async for line in lines:
                event = _parse_line(line)
                if event is not None:
                    yield event
