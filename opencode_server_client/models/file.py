"""File domain models and response wrappers."""

from dataclasses import dataclass

from opencode_server_client.models._convert import (
    as_map,
    as_seq,
    get_bool,
    get_int,
    get_str,
    opt_str,
)
from opencode_server_client.models.base import OpencodeBaseResponse


@dataclass(frozen=True, slots=True)
class OpencodeFileNode:
    """A single node in a directory listing."""

    name: str
    path: str
    absolute: str
    type: str
    ignored: bool

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeFileNode':
        """Build from a decoded payload."""
        src = as_map(payload)
        return cls(
            name=get_str(src, 'name'),
            path=get_str(src, 'path'),
            absolute=get_str(src, 'absolute'),
            type=get_str(src, 'type'),
            ignored=get_bool(src, 'ignored'),
        )


@dataclass(frozen=True, slots=True)
class OpencodeFileContent:
    """Contents of a single file."""

    type: str
    text: str
    diff: str | None
    encoding: str | None
    mime_type: str | None
    patch: dict[str, object] | None

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeFileContent':
        """Build from a decoded payload."""
        src = as_map(payload)
        raw_patch = src.get('patch')
        resolved_patch: dict[str, object] | None = None
        if isinstance(raw_patch, dict):
            resolved_patch = dict(as_map(raw_patch))
        return cls(
            type=get_str(src, 'type'),
            text=get_str(src, 'content'),
            diff=opt_str(src, 'diff'),
            encoding=opt_str(src, 'encoding'),
            mime_type=opt_str(src, 'mimeType'),
            patch=resolved_patch,
        )


@dataclass(frozen=True, slots=True)
class OpencodeFileStatus:
    """File change status entry."""

    path: str
    added: int
    removed: int
    status: str

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeFileStatus':
        """Build from a decoded payload."""
        src = as_map(payload)
        return cls(
            path=get_str(src, 'path'),
            added=get_int(src, 'added'),
            removed=get_int(src, 'removed'),
            status=get_str(src, 'status'),
        )


@dataclass(frozen=True, slots=True)
class OpencodeFilesResponse(OpencodeBaseResponse):
    """Response for ``GET /file``."""

    body: tuple['OpencodeFileNode', ...]


@dataclass(frozen=True, slots=True)
class OpencodeFileContentResponse(OpencodeBaseResponse):
    """Response for ``GET /file/content``."""

    body: OpencodeFileContent


@dataclass(frozen=True, slots=True)
class OpencodeFileStatusResponse(OpencodeBaseResponse):
    """Response for ``GET /file/status``."""

    body: tuple['OpencodeFileStatus', ...]


def files_from_payload(payload: object) -> tuple[OpencodeFileNode, ...]:
    """Parse a list payload into a tuple of file nodes."""
    return tuple(
        OpencodeFileNode.from_payload(entry) for entry in as_seq(payload)
    )


def file_status_from_payload(
    payload: object,
) -> tuple[OpencodeFileStatus, ...]:
    """Parse a list payload into a tuple of file status entries."""
    return tuple(
        OpencodeFileStatus.from_payload(entry) for entry in as_seq(payload)
    )
