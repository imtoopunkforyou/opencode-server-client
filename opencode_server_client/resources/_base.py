"""Base classes that give resources access to a transport."""

from opencode_server_client._transport import AsyncTransport, SyncTransport


class _SyncResource:
    """Holds a sync transport for a group of endpoints."""

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport


class _AsyncResource:
    """Holds an async transport for a group of endpoints."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport
