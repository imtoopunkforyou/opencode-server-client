"""Shared timestamp model reused across multiple domain models."""
from dataclasses import dataclass

from opencode_server_client.models._convert import as_map, opt_int


@dataclass(frozen=True, slots=True)
class OpencodeTimestamps:
    """Created/updated millisecond timestamps."""

    created: int | None
    updated: int | None

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeTimestamps':
        """Build from a {created, updated} object."""
        src = as_map(payload)
        return cls(
            created=opt_int(src, 'created'),
            updated=opt_int(src, 'updated'),
        )
