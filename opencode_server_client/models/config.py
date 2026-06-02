"""Configuration models (the server's Config schema is large and open-ended)."""
from dataclasses import dataclass

from opencode_server_client.models._convert import as_map, get_bool, opt_str
from opencode_server_client.models.base import OpencodeBaseResponse


@dataclass(frozen=True, slots=True)
class OpencodeConfig:
    """A configuration document; full contents kept in ``raw``."""

    username: str | None
    autoupdate: bool
    schema: str | None
    raw: dict[str, object]

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeConfig':
        """Build from a decoded payload."""
        src = as_map(payload)
        return cls(
            username=opt_str(src, 'username'),
            autoupdate=get_bool(src, 'autoupdate'),
            schema=opt_str(src, '$schema'),
            raw=dict(src),
        )


@dataclass(frozen=True, slots=True)
class OpencodeConfigResponse(OpencodeBaseResponse):
    """Response for the config GET/PATCH endpoints."""

    body: OpencodeConfig
