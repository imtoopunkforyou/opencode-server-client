"""Session response wrappers plus todo and snapshot-diff models."""
from dataclasses import dataclass

from opencode_server_client.models._convert import (
    as_map,
    as_seq,
    get_float,
    get_str,
    opt_str,
)
from opencode_server_client.models.base import OpencodeBaseResponse
from opencode_server_client.models.session import OpencodeSession


@dataclass(frozen=True, slots=True)
class OpencodeSessionResponse(OpencodeBaseResponse):
    """Response for a single-session endpoint."""

    body: OpencodeSession


@dataclass(frozen=True, slots=True)
class OpencodeSessionsResponse(OpencodeBaseResponse):
    """Response for a list-of-sessions endpoint."""

    body: tuple[OpencodeSession, ...]


def sessions_from_payload(payload: object) -> tuple[OpencodeSession, ...]:
    """Parse a list payload into a tuple of sessions."""
    return tuple(
        OpencodeSession.from_payload(entry) for entry in as_seq(payload)
    )


@dataclass(frozen=True, slots=True)
class OpencodeSessionStatusResponse(OpencodeBaseResponse):
    """Response for the session-status endpoint (open map)."""

    body: dict[str, dict[str, object]]


@dataclass(frozen=True, slots=True)
class OpencodeTodo:
    """A to-do item attached to a session."""

    text: str
    status: str
    priority: str

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeTodo':
        """Build from a decoded todo object.

        Server key ``content`` maps to field ``text``.
        """
        src = as_map(payload)
        return cls(
            text=get_str(src, 'content'),
            status=get_str(src, 'status'),
            priority=get_str(src, 'priority'),
        )


@dataclass(frozen=True, slots=True)
class OpencodeTodosResponse(OpencodeBaseResponse):
    """Response for the session todo endpoint."""

    body: tuple[OpencodeTodo, ...]


def todos_from_payload(payload: object) -> tuple[OpencodeTodo, ...]:
    """Parse a list payload into a tuple of todos."""
    return tuple(OpencodeTodo.from_payload(entry) for entry in as_seq(payload))


@dataclass(frozen=True, slots=True)
class OpencodeSnapshotDiff:
    """A single file diff entry from a session snapshot."""

    filepath: str | None
    patch: str | None
    additions: float
    deletions: float
    status: str | None

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeSnapshotDiff':
        """Build from a decoded diff object.

        Server key ``file`` maps to field ``filepath``.
        """
        src = as_map(payload)
        return cls(
            filepath=opt_str(src, 'file'),
            patch=opt_str(src, 'patch'),
            additions=get_float(src, 'additions'),
            deletions=get_float(src, 'deletions'),
            status=opt_str(src, 'status'),
        )


@dataclass(frozen=True, slots=True)
class OpencodeDiffResponse(OpencodeBaseResponse):
    """Response for the session diff endpoint."""

    body: tuple[OpencodeSnapshotDiff, ...]


def diffs_from_payload(payload: object) -> tuple[OpencodeSnapshotDiff, ...]:
    """Parse a list payload into a tuple of snapshot diffs."""
    return tuple(
        OpencodeSnapshotDiff.from_payload(entry) for entry in as_seq(payload)
    )
