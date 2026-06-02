"""Project endpoints (/project, /project/current)."""

from collections.abc import Mapping

from opencode_server_client._decode import decode
from opencode_server_client._transport import (
    RawResponse,
    RequestSpec,
    build_query,
)
from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.project import (
    OpencodeProject,
    OpencodeProjectResponse,
    OpencodeProjectsResponse,
    projects_from_payload,
)
from opencode_server_client.resources._base import _AsyncResource, _SyncResource

_ListResult = OpencodeProjectsResponse | OpencodeErrorResponse
_CurrentResult = OpencodeProjectResponse | OpencodeErrorResponse


def _build_list(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/project', query, None)


def _ok_list(code: int, payload: object) -> OpencodeProjectsResponse:
    return OpencodeProjectsResponse(
        code=code, body=projects_from_payload(payload)
    )


def _parse_list(raw: RawResponse) -> _ListResult:
    return decode(raw, _ok_list)


def _build_current(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/project/current', query, None)


def _ok_current(code: int, payload: object) -> OpencodeProjectResponse:
    return OpencodeProjectResponse(
        code=code, body=OpencodeProject.from_payload(payload)
    )


def _parse_current(raw: RawResponse) -> _CurrentResult:
    return decode(raw, _ok_current)


class ProjectResource(_SyncResource):
    """Project endpoints (sync)."""

    def list(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _ListResult:
        """List all projects."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_list(self._transport.send(_build_list(query)))

    def current(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _CurrentResult:
        """Get the current project."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_current(self._transport.send(_build_current(query)))


class AsyncProjectResource(_AsyncResource):
    """Project endpoints (async)."""

    async def list(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _ListResult:
        """List all projects."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_list(await self._transport.send(_build_list(query)))

    async def current(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _CurrentResult:
        """Get the current project."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_current(await self._transport.send(_build_current(query)))
