"""Provider endpoints (/provider, /provider/auth)."""
from collections.abc import Mapping

from opencode_server_client._decode import decode
from opencode_server_client._transport import (
    RawResponse,
    RequestSpec,
    build_query,
)
from opencode_server_client.models._convert import as_map
from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.provider import (
    OpencodeProviderAuthResponse,
    OpencodeProviderList,
    OpencodeProviderListResponse,
)
from opencode_server_client.resources._base import _AsyncResource, _SyncResource

_ListResult = OpencodeProviderListResponse | OpencodeErrorResponse
_AuthResult = OpencodeProviderAuthResponse | OpencodeErrorResponse


def _build_list(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/provider', query, None)


def _ok_list(code: int, payload: object) -> OpencodeProviderListResponse:
    return OpencodeProviderListResponse(
        code=code,
        body=OpencodeProviderList.from_payload(payload),
    )


def _parse_list(raw: RawResponse) -> _ListResult:
    return decode(raw, _ok_list)


def _build_auth(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/provider/auth', query, None)


def _ok_auth(code: int, payload: object) -> OpencodeProviderAuthResponse:
    return OpencodeProviderAuthResponse(
        code=code,
        body=dict(as_map(payload)),
    )


def _parse_auth(raw: RawResponse) -> _AuthResult:
    return decode(raw, _ok_auth)


class ProviderResource(_SyncResource):
    """Provider endpoints (sync)."""

    def list(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _ListResult:
        """List all providers and their models."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_list(self._transport.send(_build_list(query)))

    def auth(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _AuthResult:
        """Get provider authentication status."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_auth(self._transport.send(_build_auth(query)))


class AsyncProviderResource(_AsyncResource):
    """Provider endpoints (async)."""

    async def list(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _ListResult:
        """List all providers and their models."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_list(
            await self._transport.send(_build_list(query))
        )

    async def auth(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _AuthResult:
        """Get provider authentication status."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_auth(
            await self._transport.send(_build_auth(query))
        )
