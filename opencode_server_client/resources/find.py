"""Find endpoints (/find, /find/file, /find/symbol)."""

from collections.abc import Mapping

from opencode_server_client._decode import decode
from opencode_server_client._transport import (
    RawResponse,
    RequestSpec,
    build_query,
)
from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.find import (
    OpencodeFindFilesQuery,
    OpencodeFindFilesResponse,
    OpencodeMatchesResponse,
    OpencodeSymbolsResponse,
    find_files_from_payload,
    matches_from_payload,
    symbols_from_payload,
)
from opencode_server_client.resources._base import _AsyncResource, _SyncResource

_TextResult = OpencodeMatchesResponse | OpencodeErrorResponse
_FilesResult = OpencodeFindFilesResponse | OpencodeErrorResponse
_SymbolsResult = OpencodeSymbolsResponse | OpencodeErrorResponse

_QUERY_KEY = 'query'


def _build_text(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/find', query, None)


def _ok_text(code: int, payload: object) -> OpencodeMatchesResponse:
    return OpencodeMatchesResponse(
        code=code, body=matches_from_payload(payload)
    )


def _parse_text(raw: RawResponse) -> _TextResult:
    return decode(raw, _ok_text)


def _build_files(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/find/file', query, None)


def _ok_files(code: int, payload: object) -> OpencodeFindFilesResponse:
    return OpencodeFindFilesResponse(
        code=code, body=find_files_from_payload(payload)
    )


def _parse_files(raw: RawResponse) -> _FilesResult:
    return decode(raw, _ok_files)


def _build_symbols(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/find/symbol', query, None)


def _ok_symbols(code: int, payload: object) -> OpencodeSymbolsResponse:
    return OpencodeSymbolsResponse(
        code=code, body=symbols_from_payload(payload)
    )


def _parse_symbols(raw: RawResponse) -> _SymbolsResult:
    return decode(raw, _ok_symbols)


class FindResource(_SyncResource):
    """Find endpoints (sync)."""

    def text(
        self,
        pattern: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _TextResult:
        """Search file contents for *pattern* using ripgrep."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
            extra={'pattern': pattern},
        )
        return _parse_text(self._transport.send(_build_text(query)))

    def files(
        self,
        criteria: OpencodeFindFilesQuery,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _FilesResult:
        """Find files matching *criteria*."""
        extra: dict[str, object] = {
            _QUERY_KEY: criteria.query,
            'dirs': criteria.dirs,
            'type': criteria.type_filter,
            'limit': criteria.limit,
        }
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
            extra=extra,
        )
        return _parse_files(self._transport.send(_build_files(query)))

    def symbols(
        self,
        query: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SymbolsResult:
        """Search for language-server symbols matching *query*."""
        built = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
            extra={_QUERY_KEY: query},
        )
        return _parse_symbols(self._transport.send(_build_symbols(built)))


class AsyncFindResource(_AsyncResource):
    """Find endpoints (async)."""

    async def text(
        self,
        pattern: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _TextResult:
        """Search file contents for *pattern* using ripgrep."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
            extra={'pattern': pattern},
        )
        return _parse_text(await self._transport.send(_build_text(query)))

    async def files(
        self,
        criteria: OpencodeFindFilesQuery,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _FilesResult:
        """Find files matching *criteria*."""
        extra: dict[str, object] = {
            _QUERY_KEY: criteria.query,
            'dirs': criteria.dirs,
            'type': criteria.type_filter,
            'limit': criteria.limit,
        }
        built = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
            extra=extra,
        )
        return _parse_files(await self._transport.send(_build_files(built)))

    async def symbols(
        self,
        query: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SymbolsResult:
        """Search for language-server symbols matching *query*."""
        built = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
            extra={_QUERY_KEY: query},
        )
        return _parse_symbols(await self._transport.send(_build_symbols(built)))
