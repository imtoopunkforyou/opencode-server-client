"""File endpoints (/file, /file/content, /file/status)."""

from collections.abc import Mapping

from opencode_server_client._decode import decode
from opencode_server_client._transport import (
    RawResponse,
    RequestSpec,
    build_query,
)
from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.file import (
    OpencodeFileContent,
    OpencodeFileContentResponse,
    OpencodeFilesResponse,
    OpencodeFileStatusResponse,
    file_status_from_payload,
    files_from_payload,
)
from opencode_server_client.resources._base import _AsyncResource, _SyncResource

_ListResult = OpencodeFilesResponse | OpencodeErrorResponse
_ReadResult = OpencodeFileContentResponse | OpencodeErrorResponse
_StatusResult = OpencodeFileStatusResponse | OpencodeErrorResponse

_PATH_KEY = 'path'


def _build_list(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/file', query, None)


def _ok_list(code: int, payload: object) -> OpencodeFilesResponse:
    return OpencodeFilesResponse(code=code, body=files_from_payload(payload))


def _parse_list(raw: RawResponse) -> _ListResult:
    return decode(raw, _ok_list)


def _build_read(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/file/content', query, None)


def _ok_read(code: int, payload: object) -> OpencodeFileContentResponse:
    return OpencodeFileContentResponse(
        code=code, body=OpencodeFileContent.from_payload(payload)
    )


def _parse_read(raw: RawResponse) -> _ReadResult:
    return decode(raw, _ok_read)


def _build_status(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/file/status', query, None)


def _ok_status(code: int, payload: object) -> OpencodeFileStatusResponse:
    return OpencodeFileStatusResponse(
        code=code, body=file_status_from_payload(payload)
    )


def _parse_status(raw: RawResponse) -> _StatusResult:
    return decode(raw, _ok_status)


class FileResource(_SyncResource):
    """File endpoints (sync)."""

    def list(
        self,
        path: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _ListResult:
        """List files under *path*."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
            extra={_PATH_KEY: path},
        )
        return _parse_list(self._transport.send(_build_list(query)))

    def read(
        self,
        path: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _ReadResult:
        """Read the contents of the file at *path*."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
            extra={_PATH_KEY: path},
        )
        return _parse_read(self._transport.send(_build_read(query)))

    def status(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _StatusResult:
        """Get file change status list."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_status(self._transport.send(_build_status(query)))


class AsyncFileResource(_AsyncResource):
    """File endpoints (async)."""

    async def list(
        self,
        path: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _ListResult:
        """List files under *path*."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
            extra={_PATH_KEY: path},
        )
        return _parse_list(await self._transport.send(_build_list(query)))

    async def read(
        self,
        path: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _ReadResult:
        """Read the contents of the file at *path*."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
            extra={_PATH_KEY: path},
        )
        return _parse_read(await self._transport.send(_build_read(query)))

    async def status(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _StatusResult:
        """Get file change status list."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_status(await self._transport.send(_build_status(query)))
