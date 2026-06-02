"""Config endpoints (/config, /config/providers)."""
from collections.abc import Mapping

from opencode_server_client._decode import decode
from opencode_server_client._transport import (
    RawResponse,
    RequestSpec,
    build_query,
)
from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.config import (
    OpencodeConfig,
    OpencodeConfigResponse,
    OpencodeProvidersConfig,
    OpencodeProvidersConfigResponse,
)
from opencode_server_client.resources._base import _AsyncResource, _SyncResource

_ConfigResult = OpencodeConfigResponse | OpencodeErrorResponse
_ProvidersResult = OpencodeProvidersConfigResponse | OpencodeErrorResponse


def _build_get(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/config', query, None)


def _ok_config(code: int, payload: object) -> OpencodeConfigResponse:
    return OpencodeConfigResponse(
        code=code, body=OpencodeConfig.from_payload(payload)
    )


def _parse_config(raw: RawResponse) -> _ConfigResult:
    return decode(raw, _ok_config)


def _build_update(
    query: Mapping[str, str],
    document: dict[str, object],
) -> RequestSpec:
    return RequestSpec('PATCH', '/config', query, document)


def _build_providers(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/config/providers', query, None)


def _ok_providers(
    code: int, payload: object
) -> OpencodeProvidersConfigResponse:
    return OpencodeProvidersConfigResponse(
        code=code, body=OpencodeProvidersConfig.from_payload(payload)
    )


def _parse_providers(raw: RawResponse) -> _ProvidersResult:
    return decode(raw, _ok_providers)


class ConfigResource(_SyncResource):
    """Config endpoints (sync)."""

    def get(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _ConfigResult:
        """Get the current configuration."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_config(self._transport.send(_build_get(query)))

    def update(
        self,
        document: dict[str, object],
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _ConfigResult:
        """Patch the configuration with *document*."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_config(
            self._transport.send(_build_update(query, document))
        )

    def providers(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _ProvidersResult:
        """Get the providers configuration."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_providers(
            self._transport.send(_build_providers(query))
        )


class AsyncConfigResource(_AsyncResource):
    """Config endpoints (async)."""

    async def get(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _ConfigResult:
        """Get the current configuration."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_config(
            await self._transport.send(_build_get(query))
        )

    async def update(
        self,
        document: dict[str, object],
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _ConfigResult:
        """Patch the configuration with *document*."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_config(
            await self._transport.send(_build_update(query, document))
        )

    async def providers(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _ProvidersResult:
        """Get the providers configuration."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_providers(
            await self._transport.send(_build_providers(query))
        )
