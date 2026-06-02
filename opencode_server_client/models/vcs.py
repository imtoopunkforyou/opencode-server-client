"""VCS domain models and response wrappers."""
from dataclasses import dataclass

from opencode_server_client.models._convert import (
    as_map,
    as_seq,
    get_float,
    get_str,
    opt_str,
)
from opencode_server_client.models.base import OpencodeBaseResponse


@dataclass(frozen=True, slots=True)
class OpencodeVcsInfo:
    """VCS branch information for a project."""

    branch: str | None
    default_branch: str | None

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeVcsInfo':
        """Build from a decoded payload."""
        src = as_map(payload)
        return cls(
            branch=opt_str(src, 'branch'),
            default_branch=opt_str(src, 'default_branch'),
        )


@dataclass(frozen=True, slots=True)
class OpencodeVcsFileStatus:
    """VCS status entry for a single file."""

    filepath: str
    additions: float
    deletions: float
    status: str | None

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeVcsFileStatus':
        """Build from a decoded payload."""
        src = as_map(payload)
        return cls(
            filepath=get_str(src, 'file'),
            additions=get_float(src, 'additions'),
            deletions=get_float(src, 'deletions'),
            status=opt_str(src, 'status'),
        )


@dataclass(frozen=True, slots=True)
class OpencodeVcsFileDiff:
    """VCS diff entry for a single file."""

    filepath: str
    patch: str | None
    additions: float
    deletions: float
    status: str | None

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeVcsFileDiff':
        """Build from a decoded payload."""
        src = as_map(payload)
        return cls(
            filepath=get_str(src, 'file'),
            patch=opt_str(src, 'patch'),
            additions=get_float(src, 'additions'),
            deletions=get_float(src, 'deletions'),
            status=opt_str(src, 'status'),
        )


@dataclass(frozen=True, slots=True)
class OpencodeVcsInfoResponse(OpencodeBaseResponse):
    """Response for ``GET /vcs``."""

    body: OpencodeVcsInfo


@dataclass(frozen=True, slots=True)
class OpencodeVcsStatusResponse(OpencodeBaseResponse):
    """Response for ``GET /vcs/status``."""

    body: tuple[OpencodeVcsFileStatus, ...]


@dataclass(frozen=True, slots=True)
class OpencodeVcsDiffResponse(OpencodeBaseResponse):
    """Response for ``GET /vcs/diff``."""

    body: tuple[OpencodeVcsFileDiff, ...]


def vcs_status_from_payload(
    payload: object,
) -> tuple[OpencodeVcsFileStatus, ...]:
    """Parse a list payload into a tuple of file status entries."""
    return tuple(
        OpencodeVcsFileStatus.from_payload(entry) for entry in as_seq(payload)
    )


def vcs_diff_from_payload(
    payload: object,
) -> tuple[OpencodeVcsFileDiff, ...]:
    """Parse a list payload into a tuple of file diff entries."""
    return tuple(
        OpencodeVcsFileDiff.from_payload(entry) for entry in as_seq(payload)
    )
