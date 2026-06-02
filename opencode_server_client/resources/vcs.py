"""VCS endpoints (/vcs, /vcs/status, /vcs/diff)."""
from collections.abc import Mapping

from opencode_server_client._decode import decode
from opencode_server_client._transport import (
    RawResponse,
    RequestSpec,
    build_query,
)
from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.vcs import (
    OpencodeVcsDiffResponse,
    OpencodeVcsInfo,
    OpencodeVcsInfoResponse,
    OpencodeVcsStatusResponse,
    vcs_diff_from_payload,
    vcs_status_from_payload,
)
from opencode_server_client.resources._base import _AsyncResource, _SyncResource

_GetResult = OpencodeVcsInfoResponse | OpencodeErrorResponse
_StatusResult = OpencodeVcsStatusResponse | OpencodeErrorResponse
_DiffResult = OpencodeVcsDiffResponse | OpencodeErrorResponse


def _build_get(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/vcs', query, None)


def _ok_get(code: int, payload: object) -> OpencodeVcsInfoResponse:
    return OpencodeVcsInfoResponse(
        code=code, body=OpencodeVcsInfo.from_payload(payload)
    )


def _parse_get(raw: RawResponse) -> _GetResult:
    return decode(raw, _ok_get)


def _build_status(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/vcs/status', query, None)


def _ok_status(code: int, payload: object) -> OpencodeVcsStatusResponse:
    return OpencodeVcsStatusResponse(
        code=code, body=vcs_status_from_payload(payload)
    )


def _parse_status(raw: RawResponse) -> _StatusResult:
    return decode(raw, _ok_status)


def _build_diff(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/vcs/diff', query, None)


def _ok_diff(code: int, payload: object) -> OpencodeVcsDiffResponse:
    return OpencodeVcsDiffResponse(
        code=code, body=vcs_diff_from_payload(payload)
    )


def _parse_diff(raw: RawResponse) -> _DiffResult:
    return decode(raw, _ok_diff)


class VcsResource(_SyncResource):
    """VCS endpoints (sync)."""

    def get(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _GetResult:
        """Get VCS branch information."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_get(self._transport.send(_build_get(query)))

    def status(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _StatusResult:
        """Get VCS file status list."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_status(self._transport.send(_build_status(query)))

    def diff(
        self,
        mode: str,
        *,
        context: int | None = None,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _DiffResult:
        """Get VCS diff for all changed files."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
            extra={'mode': mode, 'context': context},
        )
        return _parse_diff(self._transport.send(_build_diff(query)))


class AsyncVcsResource(_AsyncResource):
    """VCS endpoints (async)."""

    async def get(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _GetResult:
        """Get VCS branch information."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_get(await self._transport.send(_build_get(query)))

    async def status(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _StatusResult:
        """Get VCS file status list."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_status(
            await self._transport.send(_build_status(query))
        )

    async def diff(
        self,
        mode: str,
        *,
        context: int | None = None,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _DiffResult:
        """Get VCS diff for all changed files."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
            extra={'mode': mode, 'context': context},
        )
        return _parse_diff(await self._transport.send(_build_diff(query)))
