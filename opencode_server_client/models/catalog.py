"""Catalog domain models: agent, command, skill, path, lsp."""
from dataclasses import dataclass

from opencode_server_client.models._convert import (
    as_map,
    get_bool,
    get_str,
    opt_float,
    opt_str,
    str_tuple,
)

_KEY_NAME = 'name'


@dataclass(frozen=True, slots=True)
class OpencodeAgent:
    """An OpenCode agent definition."""

    name: str
    description: str | None
    mode: str
    native: bool
    temperature: float | None
    prompt: str | None
    options: dict[str, object]
    raw: dict[str, object]

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeAgent':
        """Build an agent from a decoded payload."""
        src = as_map(payload)
        return cls(
            name=get_str(src, _KEY_NAME),
            description=opt_str(src, 'description'),
            mode=get_str(src, 'mode'),
            native=get_bool(src, 'native'),
            temperature=opt_float(src, 'temperature'),
            prompt=opt_str(src, 'prompt'),
            options=dict(as_map(src.get('options'))),
            raw=dict(src),
        )


@dataclass(frozen=True, slots=True)
class OpencodeCommand:
    """An OpenCode command definition."""

    name: str
    description: str | None
    agent: str | None
    model: str | None
    source: str | None
    template: str
    subtask: bool
    hints: tuple[str, ...]

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeCommand':
        """Build a command from a decoded payload."""
        src = as_map(payload)
        return cls(
            name=get_str(src, _KEY_NAME),
            description=opt_str(src, 'description'),
            agent=opt_str(src, 'agent'),
            model=opt_str(src, 'model'),
            source=opt_str(src, 'source'),
            template=get_str(src, 'template'),
            subtask=get_bool(src, 'subtask'),
            hints=str_tuple(src.get('hints')),
        )


@dataclass(frozen=True, slots=True)
class OpencodeSkill:
    """An OpenCode skill definition."""

    name: str
    description: str | None
    location: str
    text: str

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeSkill':
        """Build a skill from a decoded payload."""
        src = as_map(payload)
        return cls(
            name=get_str(src, _KEY_NAME),
            description=opt_str(src, 'description'),
            location=get_str(src, 'location'),
            text=get_str(src, 'content'),
        )


@dataclass(frozen=True, slots=True)
class OpencodePath:
    """Server filesystem paths."""

    home: str
    state: str
    config: str
    worktree: str
    directory: str

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodePath':
        """Build a path record from a decoded payload."""
        src = as_map(payload)
        return cls(
            home=get_str(src, 'home'),
            state=get_str(src, 'state'),
            config=get_str(src, 'config'),
            worktree=get_str(src, 'worktree'),
            directory=get_str(src, 'directory'),
        )


@dataclass(frozen=True, slots=True)
class OpencodeLspStatus:
    """Status of a Language Server Protocol instance."""

    lsp_id: str
    name: str
    root: str
    status: str

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeLspStatus':
        """Build an LSP status from a decoded payload."""
        src = as_map(payload)
        return cls(
            lsp_id=get_str(src, 'id'),
            name=get_str(src, _KEY_NAME),
            root=get_str(src, 'root'),
            status=get_str(src, 'status'),
        )
