"""Find domain models and response wrappers."""

from dataclasses import dataclass, field

from opencode_server_client.models._convert import (
    as_map,
    as_seq,
    get_int,
    get_str,
    str_tuple,
)
from opencode_server_client.models.base import OpencodeBaseResponse


@dataclass(frozen=True, slots=True)
class OpencodeRange:
    """A text range expressed as start/end line and character offsets."""

    start_line: int
    start_character: int
    end_line: int
    end_character: int

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeRange':
        """Build from a decoded payload with nested start/end objects."""
        src = as_map(payload)
        start = as_map(src.get('start'))
        end = as_map(src.get('end'))
        return cls(
            start_line=get_int(start, 'line'),
            start_character=get_int(start, 'character'),
            end_line=get_int(end, 'line'),
            end_character=get_int(end, 'character'),
        )


@dataclass(frozen=True, slots=True)
class OpencodeMatch:
    """A single ripgrep match from the find-text endpoint."""

    path: str
    lines: str
    line_number: int
    absolute_offset: int
    submatches: tuple[dict[str, object], ...]

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeMatch':
        """Build from a decoded payload with nested path and lines objects."""
        src = as_map(payload)
        path_obj = as_map(src.get('path'))
        lines_obj = as_map(src.get('lines'))
        raw_sub = as_seq(src.get('submatches'))
        return cls(
            path=get_str(path_obj, 'text'),
            lines=get_str(lines_obj, 'text'),
            line_number=get_int(src, 'line_number'),
            absolute_offset=get_int(src, 'absolute_offset'),
            submatches=tuple(dict(as_map(entry)) for entry in raw_sub),
        )


@dataclass(frozen=True, slots=True)
class OpencodeSymbol:
    """A language-server symbol from the find-symbols endpoint."""

    name: str
    kind: int
    uri: str
    symbol_range: OpencodeRange

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeSymbol':
        """Build from a decoded payload with a nested location object."""
        src = as_map(payload)
        loc = as_map(src.get('location'))
        return cls(
            name=get_str(src, 'name'),
            kind=get_int(src, 'kind'),
            uri=get_str(loc, 'uri'),
            symbol_range=OpencodeRange.from_payload(loc.get('range')),
        )


@dataclass(frozen=True, slots=True)
class OpencodeFindFilesQuery:
    """Input parameters for the find-files endpoint."""

    query: str
    include_dirs: bool | None = field(default=None)
    node_type: str | None = field(default=None)
    limit: int | None = field(default=None)


@dataclass(frozen=True, slots=True)
class OpencodeMatchesResponse(OpencodeBaseResponse):
    """Response for ``GET /find``."""

    body: tuple['OpencodeMatch', ...]


@dataclass(frozen=True, slots=True)
class OpencodeFindFilesResponse(OpencodeBaseResponse):
    """Response for ``GET /find/file``."""

    body: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class OpencodeSymbolsResponse(OpencodeBaseResponse):
    """Response for ``GET /find/symbol``."""

    body: tuple['OpencodeSymbol', ...]


def matches_from_payload(payload: object) -> tuple[OpencodeMatch, ...]:
    """Parse a list payload into a tuple of match objects."""
    return tuple(OpencodeMatch.from_payload(entry) for entry in as_seq(payload))


def symbols_from_payload(payload: object) -> tuple[OpencodeSymbol, ...]:
    """Parse a list payload into a tuple of symbol objects."""
    return tuple(
        OpencodeSymbol.from_payload(entry) for entry in as_seq(payload)
    )


def find_files_from_payload(payload: object) -> tuple[str, ...]:
    """Parse a list payload into a tuple of file path strings."""
    return str_tuple(payload)
