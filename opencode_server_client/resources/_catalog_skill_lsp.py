"""Catalog list endpoints: skill and lsp."""
from collections.abc import Mapping

from opencode_server_client._decode import decode
from opencode_server_client._transport import (
    RawResponse,
    RequestSpec,
    build_query,
)
from opencode_server_client.models._catalog_responses import (
    OpencodeLspStatusResponse,
    OpencodeSkillsResponse,
    lsp_statuses_from_payload,
    skills_from_payload,
)
from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.resources._base import _AsyncResource, _SyncResource

_SkillsResult = OpencodeSkillsResponse | OpencodeErrorResponse
_LspResult = OpencodeLspStatusResponse | OpencodeErrorResponse


def _build_skills(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/skill', query, None)


def _ok_skills(code: int, payload: object) -> OpencodeSkillsResponse:
    return OpencodeSkillsResponse(
        code=code, body=skills_from_payload(payload)
    )


def _parse_skills(raw: RawResponse) -> _SkillsResult:
    return decode(raw, _ok_skills)


def _build_lsp(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/lsp', query, None)


def _ok_lsp(code: int, payload: object) -> OpencodeLspStatusResponse:
    return OpencodeLspStatusResponse(
        code=code, body=lsp_statuses_from_payload(payload)
    )


def _parse_lsp(raw: RawResponse) -> _LspResult:
    return decode(raw, _ok_lsp)


class SkillResource(_SyncResource):
    """Skill endpoints (sync)."""

    def list(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SkillsResult:
        """List skills."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_skills(self._transport.send(_build_skills(query)))


class AsyncSkillResource(_AsyncResource):
    """Skill endpoints (async)."""

    async def list(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SkillsResult:
        """List skills."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_skills(
            await self._transport.send(_build_skills(query))
        )


class LspResource(_SyncResource):
    """LSP status endpoints (sync)."""

    def status(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _LspResult:
        """Get LSP status."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_lsp(self._transport.send(_build_lsp(query)))


class AsyncLspResource(_AsyncResource):
    """LSP status endpoints (async)."""

    async def status(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _LspResult:
        """Get LSP status."""
        query = build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
        )
        return _parse_lsp(await self._transport.send(_build_lsp(query)))
