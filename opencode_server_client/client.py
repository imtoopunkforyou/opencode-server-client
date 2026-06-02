"""The synchronous and asynchronous OpenCode clients."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from collections.abc import Mapping
    from types import TracebackType

    from typing_extensions import Self

from opencode_server_client._transport import AsyncTransport, SyncTransport
from opencode_server_client.resources import (
    AgentResource,
    CommandResource,
    ConfigResource,
    EventResource,
    FileResource,
    FindResource,
    LspResource,
    McpResource,
    MessageResource,
    PathResource,
    ProjectResource,
    ProviderResource,
    ServerResource,
    SessionResource,
    SkillResource,
    VcsResource,
)
from opencode_server_client.resources._async import (
    AsyncAgentResource,
    AsyncCommandResource,
    AsyncConfigResource,
    AsyncEventResource,
    AsyncFileResource,
    AsyncFindResource,
    AsyncLspResource,
    AsyncMcpResource,
    AsyncMessageResource,
    AsyncPathResource,
    AsyncProjectResource,
    AsyncProviderResource,
    AsyncServerResource,
    AsyncSessionResource,
    AsyncSkillResource,
    AsyncVcsResource,
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
        self.event = EventResource(self._transport)
        self.agent = AgentResource(self._transport)
        self.command = CommandResource(self._transport)
        self.config = ConfigResource(self._transport)
        self.files = FileResource(self._transport)
        self.find = FindResource(self._transport)
        self.skill = SkillResource(self._transport)
        self.path = PathResource(self._transport)
        self.lsp = LspResource(self._transport)
        self.mcp = McpResource(self._transport)
        self.project = ProjectResource(self._transport)
        self.provider = ProviderResource(self._transport)
        self.message = MessageResource(self._transport)
        self.session = SessionResource(self._transport)
        self.vcs = VcsResource(self._transport)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._transport.close()

    def __enter__(self) -> Self:
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
        self.event = AsyncEventResource(self._transport)
        self.agent = AsyncAgentResource(self._transport)
        self.command = AsyncCommandResource(self._transport)
        self.config = AsyncConfigResource(self._transport)
        self.files = AsyncFileResource(self._transport)
        self.find = AsyncFindResource(self._transport)
        self.skill = AsyncSkillResource(self._transport)
        self.path = AsyncPathResource(self._transport)
        self.lsp = AsyncLspResource(self._transport)
        self.mcp = AsyncMcpResource(self._transport)
        self.project = AsyncProjectResource(self._transport)
        self.provider = AsyncProviderResource(self._transport)
        self.message = AsyncMessageResource(self._transport)
        self.session = AsyncSessionResource(self._transport)
        self.vcs = AsyncVcsResource(self._transport)

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        await self._transport.aclose()

    async def __aenter__(self) -> Self:
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
