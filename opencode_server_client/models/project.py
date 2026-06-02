"""Project domain models and response wrappers."""

from dataclasses import dataclass

from opencode_server_client.models._convert import (
    as_map,
    as_seq,
    get_str,
    opt_str,
    str_tuple,
)
from opencode_server_client.models.base import OpencodeBaseResponse
from opencode_server_client.models.common import OpencodeTimestamps


@dataclass(frozen=True, slots=True)
class OpencodeProject:
    """A single OpenCode project (worktree) record."""

    project_id: str
    worktree: str
    vcs: str | None
    name: str | None
    sandboxes: tuple[str, ...]
    time: OpencodeTimestamps
    raw: dict[str, object]

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeProject':
        """Build a project from a decoded payload."""
        src = as_map(payload)
        return cls(
            project_id=get_str(src, 'id'),
            worktree=get_str(src, 'worktree'),
            vcs=opt_str(src, 'vcs'),
            name=opt_str(src, 'name'),
            sandboxes=str_tuple(src.get('sandboxes')),
            time=OpencodeTimestamps.from_payload(src.get('time')),
            raw=dict(src),
        )


@dataclass(frozen=True, slots=True)
class OpencodeProjectResponse(OpencodeBaseResponse):
    """Response for ``GET /project/current``."""

    body: OpencodeProject


@dataclass(frozen=True, slots=True)
class OpencodeProjectsResponse(OpencodeBaseResponse):
    """Response for ``GET /project``."""

    body: tuple[OpencodeProject, ...]


def projects_from_payload(
    payload: object,
) -> tuple[OpencodeProject, ...]:
    """Parse a list payload into a tuple of projects."""
    return tuple(
        OpencodeProject.from_payload(entry) for entry in as_seq(payload)
    )
