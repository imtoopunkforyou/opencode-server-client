"""The synchronous and asynchronous OpenCode clients."""
from collections.abc import Mapping
from dataclasses import dataclass
from types import TracebackType

import httpx

from opencode_server_client._transport import AsyncTransport, SyncTransport
from opencode_server_client.resources.server import (
    AsyncServerResource,
    ServerResource,
)

_SyncTransportArg = httpx.BaseTransport | None
_AsyncTransportArg = httpx.AsyncBaseTransport | None


@dataclass(frozen=True, slots=True)
class OpencodeClientOptions:
    """Connection options shared by both clients."""

    timeout: float = 30.0
    headers: Mapping[str, str] | None = None
    directory: str | None = None
    workspace: str | None = None


def _defaults(options: OpencodeClientOptions) -> dict[str, str]:
    scope: dict[str, str | None] = {
        'directory': options.directory,
        'workspace': options.workspace,
    }
    return {key: found for key, found in scope.items() if found is not None}


class OpencodeClient:
    """Synchronous OpenCode server client."""

    def __init__(
        self,
        base_url: str,
        *,
        options: OpencodeClientOptions | None = None,
        transport: _SyncTransportArg = None,
    ) -> None:
        """Create a client for the server at *base_url*."""
        opts = options or OpencodeClientOptions()
        client = httpx.Client(
            base_url=base_url,
            timeout=opts.timeout,
            headers=dict(opts.headers or {}),
            transport=transport,
        )
        self._transport = SyncTransport(client, _defaults(opts))
        self.server = ServerResource(self._transport)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._transport.close()

    def __enter__(self) -> 'OpencodeClient':
        """Enter the context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the context manager, closing the client."""
        self.close()


class OpencodeAsyncClient:
    """Asynchronous OpenCode server client."""

    def __init__(
        self,
        base_url: str,
        *,
        options: OpencodeClientOptions | None = None,
        transport: _AsyncTransportArg = None,
    ) -> None:
        """Create a client for the server at *base_url*."""
        opts = options or OpencodeClientOptions()
        client = httpx.AsyncClient(
            base_url=base_url,
            timeout=opts.timeout,
            headers=dict(opts.headers or {}),
            transport=transport,
        )
        self._transport = AsyncTransport(client, _defaults(opts))
        self.server = AsyncServerResource(self._transport)

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        await self._transport.aclose()

    async def __aenter__(self) -> 'OpencodeAsyncClient':
        """Enter the async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the async context manager, closing the client."""
        await self.aclose()
