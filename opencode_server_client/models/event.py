"""Server-Sent Event model."""
from dataclasses import dataclass

from opencode_server_client.models._convert import as_map, get_str


@dataclass(frozen=True, slots=True)
class OpencodeEvent:
    """A single parsed server-sent event."""

    event_type: str
    properties: dict[str, object]
    raw: dict[str, object]

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeEvent':
        """Build from a decoded SSE JSON payload."""
        src = as_map(payload)
        props = as_map(src.get('properties'))
        return cls(
            event_type=get_str(src, 'type'),
            properties=dict(props),
            raw=dict(src),
        )
