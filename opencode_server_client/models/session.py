"""Session domain models (nested types and the main session record)."""

from dataclasses import dataclass

from opencode_server_client.models._convert import (
    as_map,
    as_seq,
    get_float,
    get_int,
    get_str,
    opt_float,
    opt_int,
    opt_str,
)


@dataclass(frozen=True, slots=True)
class OpencodeSessionTime:
    """Timestamps for a session lifecycle."""

    created: int
    updated: int
    compacting: int | None
    archived: float | None

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeSessionTime':
        """Build from a decoded time object."""
        src = as_map(payload)
        return cls(
            created=get_int(src, 'created'),
            updated=get_int(src, 'updated'),
            compacting=opt_int(src, 'compacting'),
            archived=opt_float(src, 'archived'),
        )


@dataclass(frozen=True, slots=True)
class OpencodeTokenUsage:
    """Token usage counters for a session."""

    input: float
    output: float
    reasoning: float
    cache_read: float
    cache_write: float

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeTokenUsage':
        """Build token usage from a decoded payload (cache nested)."""
        src = as_map(payload)
        cache = as_map(src.get('cache'))
        return cls(
            input=get_float(src, 'input'),
            output=get_float(src, 'output'),
            reasoning=get_float(src, 'reasoning'),
            cache_read=get_float(cache, 'read'),
            cache_write=get_float(cache, 'write'),
        )


@dataclass(frozen=True, slots=True)
class OpencodeShareInfo:
    """Share URL for a published session."""

    url: str

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeShareInfo':
        """Build from a decoded share object."""
        src = as_map(payload)
        return cls(url=get_str(src, 'url'))


@dataclass(frozen=True, slots=True)
class OpencodeModelRef:
    """A model reference stored on a session."""

    model_id: str
    provider_id: str
    variant: str | None

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeModelRef':
        """Build from a decoded model-ref object."""
        src = as_map(payload)
        return cls(
            model_id=get_str(src, 'id'),
            provider_id=get_str(src, 'providerID'),
            variant=opt_str(src, 'variant'),
        )


@dataclass(frozen=True, slots=True)
class OpencodeSessionSummary:
    """Diff summary counters for a session."""

    additions: float
    deletions: float
    files: float

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeSessionSummary':
        """Build from a decoded summary object."""
        src = as_map(payload)
        return cls(
            additions=get_float(src, 'additions'),
            deletions=get_float(src, 'deletions'),
            files=get_float(src, 'files'),
        )


def _opt_tokens(src: object) -> 'OpencodeTokenUsage | None':
    found = as_map(src).get('tokens')
    if isinstance(found, dict):
        return OpencodeTokenUsage.from_payload(found)
    return None


def _opt_share(src: object) -> 'OpencodeShareInfo | None':
    found = as_map(src).get('share')
    if isinstance(found, dict):
        return OpencodeShareInfo.from_payload(found)
    return None


def _opt_model_ref(src: object) -> 'OpencodeModelRef | None':
    found = as_map(src).get('model')
    if isinstance(found, dict):
        return OpencodeModelRef.from_payload(found)
    return None


def _opt_summary(src: object) -> 'OpencodeSessionSummary | None':
    found = as_map(src).get('summary')
    if isinstance(found, dict):
        return OpencodeSessionSummary.from_payload(found)
    return None


@dataclass(frozen=True, slots=True)
class OpencodeSession:
    """A single session record returned by the session endpoints."""

    session_id: str
    slug: str
    project_id: str
    directory: str
    title: str
    version: str
    parent_id: str | None
    workspace_id: str | None
    path: str | None
    agent: str | None
    time: OpencodeSessionTime
    tokens: OpencodeTokenUsage | None
    cost: float | None
    share: OpencodeShareInfo | None
    model: OpencodeModelRef | None
    summary: OpencodeSessionSummary | None
    revert: dict[str, object] | None
    metadata: dict[str, object] | None
    permission: tuple[dict[str, object], ...]
    raw: dict[str, object]

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeSession':
        """Build a session record from a decoded payload."""
        src = as_map(payload)
        revert_found = src.get('revert')
        meta_found = src.get('metadata')
        return cls(
            session_id=get_str(src, 'id'),
            slug=get_str(src, 'slug'),
            project_id=get_str(src, 'projectID'),
            directory=get_str(src, 'directory'),
            title=get_str(src, 'title'),
            version=get_str(src, 'version'),
            parent_id=opt_str(src, 'parentID'),
            workspace_id=opt_str(src, 'workspaceID'),
            path=opt_str(src, 'path'),
            agent=opt_str(src, 'agent'),
            time=OpencodeSessionTime.from_payload(src.get('time')),
            tokens=_opt_tokens(src),
            cost=opt_float(src, 'cost'),
            share=_opt_share(src),
            model=_opt_model_ref(src),
            summary=_opt_summary(src),
            revert=(
                dict(as_map(revert_found))
                if isinstance(revert_found, dict)
                else None
            ),
            metadata=(
                dict(as_map(meta_found))
                if isinstance(meta_found, dict)
                else None
            ),
            permission=tuple(
                dict(as_map(entry)) for entry in as_seq(src.get('permission'))
            ),
            raw=dict(src),
        )
