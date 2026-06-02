"""Catalog response wrappers and payload-to-domain parse helpers."""

from dataclasses import dataclass

from opencode_server_client.models._convert import as_map, as_seq
from opencode_server_client.models.base import OpencodeBaseResponse
from opencode_server_client.models.catalog import (
    OpencodeAgent,
    OpencodeCommand,
    OpencodeLspStatus,
    OpencodePath,
    OpencodeSkill,
)


@dataclass(frozen=True, slots=True)
class OpencodeAgentsResponse(OpencodeBaseResponse):
    """Response for ``GET /agent``."""

    body: tuple[OpencodeAgent, ...]


@dataclass(frozen=True, slots=True)
class OpencodeCommandsResponse(OpencodeBaseResponse):
    """Response for ``GET /command``."""

    body: tuple[OpencodeCommand, ...]


@dataclass(frozen=True, slots=True)
class OpencodeSkillsResponse(OpencodeBaseResponse):
    """Response for ``GET /skill``."""

    body: tuple[OpencodeSkill, ...]


@dataclass(frozen=True, slots=True)
class OpencodePathResponse(OpencodeBaseResponse):
    """Response for ``GET /path``."""

    body: OpencodePath


@dataclass(frozen=True, slots=True)
class OpencodeLspStatusResponse(OpencodeBaseResponse):
    """Response for ``GET /lsp``."""

    body: tuple[OpencodeLspStatus, ...]


@dataclass(frozen=True, slots=True)
class OpencodeMcpStatusResponse(OpencodeBaseResponse):
    """Response for ``GET /mcp``."""

    body: dict[str, dict[str, object]]


def agents_from_payload(
    payload: object,
) -> tuple[OpencodeAgent, ...]:
    """Parse a list payload into a tuple of agents."""
    return tuple(OpencodeAgent.from_payload(entry) for entry in as_seq(payload))


def commands_from_payload(
    payload: object,
) -> tuple[OpencodeCommand, ...]:
    """Parse a list payload into a tuple of commands."""
    return tuple(
        OpencodeCommand.from_payload(entry) for entry in as_seq(payload)
    )


def skills_from_payload(
    payload: object,
) -> tuple[OpencodeSkill, ...]:
    """Parse a list payload into a tuple of skills."""
    return tuple(OpencodeSkill.from_payload(entry) for entry in as_seq(payload))


def lsp_statuses_from_payload(
    payload: object,
) -> tuple[OpencodeLspStatus, ...]:
    """Parse a list payload into a tuple of LSP statuses."""
    return tuple(
        OpencodeLspStatus.from_payload(entry) for entry in as_seq(payload)
    )


def mcp_status_from_payload(
    payload: object,
) -> dict[str, dict[str, object]]:
    """Coerce the MCP status open-map payload."""
    src = as_map(payload)
    return {key: dict(as_map(found)) for key, found in src.items()}
