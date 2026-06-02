"""Catalog endpoints: path (no query) and mcp (open map)."""

from collections.abc import Mapping

from opencode_server_client._decode import decode
from opencode_server_client._transport import (
    RawResponse,
    RequestSpec,
    build_query,
)
from opencode_server_client.models._catalog_responses import (
    OpencodeMcpStatusResponse,
    OpencodePathResponse,
    mcp_status_from_payload,
)
from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.catalog import OpencodePath
from opencode_server_client.resources._base import _AsyncResource, _SyncResource

_PathResult = OpencodePathResponse | OpencodeErrorResponse
_McpResult = OpencodeMcpStatusResponse | OpencodeErrorResponse


def _build_path(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/path', query, None)


def _ok_path(code: int, payload: object) -> OpencodePathResponse:
    return OpencodePathResponse(
        code=code, body=OpencodePath.from_payload(payload)
    )


def _parse_path(raw: RawResponse) -> _PathResult:
    return decode(raw, _ok_path)


def _build_mcp(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/mcp', query, None)


def _ok_mcp(code: int, payload: object) -> OpencodeMcpStatusResponse:
    return OpencodeMcpStatusResponse(
        code=code, body=mcp_status_from_payload(payload)
    )


def _parse_mcp(raw: RawResponse) -> _McpResult:
    return decode(raw, _ok_mcp)


class PathResource(_SyncResource):
    """Path endpoints (sync)."""

    def get(self) -> _PathResult:
        """Get server filesystem paths."""
        query = build_query(self._transport.defaults)
        return _parse_path(self._transport.send(_build_path(query)))


class AsyncPathResource(_AsyncResource):
    """Path endpoints (async)."""

    async def get(self) -> _PathResult:
        """Get server filesystem paths."""
        query = build_query(self._transport.defaults)
        return _parse_path(await self._transport.send(_build_path(query)))


class McpResource(_SyncResource):
    """MCP status endpoints (sync)."""

    def status(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _McpResult:
        """Get MCP server status."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_mcp(self._transport.send(_build_mcp(query)))


class AsyncMcpResource(_AsyncResource):
    """MCP status endpoints (async)."""

    async def status(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _McpResult:
        """Get MCP server status."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_mcp(await self._transport.send(_build_mcp(query)))
