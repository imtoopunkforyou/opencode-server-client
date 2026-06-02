"""Catalog list endpoints: agent and command."""

from collections.abc import Mapping

from opencode_server_client._decode import decode
from opencode_server_client._transport import (
    RawResponse,
    RequestSpec,
    build_query,
)
from opencode_server_client.models._catalog_responses import (
    OpencodeAgentsResponse,
    OpencodeCommandsResponse,
    agents_from_payload,
    commands_from_payload,
)
from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.resources._base import _AsyncResource, _SyncResource

_AgentsResult = OpencodeAgentsResponse | OpencodeErrorResponse
_CommandsResult = OpencodeCommandsResponse | OpencodeErrorResponse


def _build_agents(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/agent', query, None)


def _ok_agents(code: int, payload: object) -> OpencodeAgentsResponse:
    return OpencodeAgentsResponse(code=code, body=agents_from_payload(payload))


def _parse_agents(raw: RawResponse) -> _AgentsResult:
    return decode(raw, _ok_agents)


def _build_commands(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/command', query, None)


def _ok_commands(code: int, payload: object) -> OpencodeCommandsResponse:
    return OpencodeCommandsResponse(
        code=code, body=commands_from_payload(payload)
    )


def _parse_commands(raw: RawResponse) -> _CommandsResult:
    return decode(raw, _ok_commands)


class AgentResource(_SyncResource):
    """Agent endpoints (sync)."""

    def list(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _AgentsResult:
        """List agents."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_agents(self._transport.send(_build_agents(query)))


class AsyncAgentResource(_AsyncResource):
    """Agent endpoints (async)."""

    async def list(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _AgentsResult:
        """List agents."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_agents(await self._transport.send(_build_agents(query)))


class CommandResource(_SyncResource):
    """Command endpoints (sync)."""

    def list(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _CommandsResult:
        """List commands."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_commands(self._transport.send(_build_commands(query)))


class AsyncCommandResource(_AsyncResource):
    """Command endpoints (async)."""

    async def list(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _CommandsResult:
        """List commands."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_commands(
            await self._transport.send(_build_commands(query))
        )
