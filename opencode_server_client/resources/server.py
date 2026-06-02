"""Server-level (/global/*) endpoints."""

from opencode_server_client._decode import decode
from opencode_server_client._transport import RawResponse, RequestSpec
from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.config import (
    OpencodeConfig,
    OpencodeConfigResponse,
)
from opencode_server_client.models.health import (
    OpencodeHealthData,
    OpencodeHealthResponse,
)
from opencode_server_client.resources._base import _AsyncResource, _SyncResource

_HealthResult = OpencodeHealthResponse | OpencodeErrorResponse
_ConfigResult = OpencodeConfigResponse | OpencodeErrorResponse


def _build_health() -> RequestSpec:
    return RequestSpec('GET', '/global/health', {}, None)


def _ok_health(code: int, payload: object) -> OpencodeHealthResponse:
    return OpencodeHealthResponse(
        code=code, body=OpencodeHealthData.from_payload(payload)
    )


def _parse_health(raw: RawResponse) -> _HealthResult:
    return decode(raw, _ok_health)


def _build_config() -> RequestSpec:
    return RequestSpec('GET', '/global/config', {}, None)


def _ok_config(code: int, payload: object) -> OpencodeConfigResponse:
    return OpencodeConfigResponse(
        code=code, body=OpencodeConfig.from_payload(payload)
    )


def _parse_config(raw: RawResponse) -> _ConfigResult:
    return decode(raw, _ok_config)


def _build_update_config(document: dict[str, object]) -> RequestSpec:
    return RequestSpec('PATCH', '/global/config', {}, document)


class ServerResource(_SyncResource):
    """Server-level endpoints (sync)."""

    def health(self) -> _HealthResult:
        """Get server health."""
        return _parse_health(self._transport.send(_build_health()))

    def config(self) -> _ConfigResult:
        """Get the global configuration."""
        return _parse_config(self._transport.send(_build_config()))

    def update_config(self, document: dict[str, object]) -> _ConfigResult:
        """Patch the global configuration with *document*."""
        spec = _build_update_config(document)
        return _parse_config(self._transport.send(spec))


class AsyncServerResource(_AsyncResource):
    """Server-level endpoints (async)."""

    async def health(self) -> _HealthResult:
        """Get server health."""
        return _parse_health(await self._transport.send(_build_health()))

    async def config(self) -> _ConfigResult:
        """Get the global configuration."""
        return _parse_config(await self._transport.send(_build_config()))

    async def update_config(self, document: dict[str, object]) -> _ConfigResult:
        """Patch the global configuration with *document*."""
        return _parse_config(
            await self._transport.send(_build_update_config(document))
        )
