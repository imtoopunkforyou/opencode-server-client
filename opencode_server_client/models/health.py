"""Health endpoint models."""

from dataclasses import dataclass

from opencode_server_client.models._convert import as_map, get_bool, get_str
from opencode_server_client.models.base import OpencodeBaseResponse


@dataclass(frozen=True, slots=True)
class OpencodeHealthData:
    """Server health information."""

    healthy: bool
    version: str

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeHealthData':
        """Build from a decoded payload."""
        src = as_map(payload)
        return cls(
            healthy=get_bool(src, 'healthy'),
            version=get_str(src, 'version'),
        )


@dataclass(frozen=True, slots=True)
class OpencodeHealthResponse(OpencodeBaseResponse):
    """Response for ``GET /global/health``."""

    body: OpencodeHealthData
