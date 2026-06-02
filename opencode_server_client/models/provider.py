"""Provider domain models and response wrappers."""

from dataclasses import dataclass

from opencode_server_client.models._convert import (
    as_map,
    as_seq,
    get_str,
    opt_str,
    str_tuple,
)
from opencode_server_client.models._model import OpencodeModel
from opencode_server_client.models.base import OpencodeBaseResponse


@dataclass(frozen=True, slots=True)
class OpencodeProvider:
    """A single provider record with its model catalogue."""

    provider_id: str
    name: str
    source: str
    env: tuple[str, ...]
    key: str | None
    options: dict[str, object]
    models: dict[str, OpencodeModel]

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeProvider':
        """Build a provider record from a decoded payload."""
        src = as_map(payload)
        raw_models = as_map(src.get('models'))
        return cls(
            provider_id=get_str(src, 'id'),
            name=get_str(src, 'name'),
            source=get_str(src, 'source'),
            env=str_tuple(src.get('env')),
            key=opt_str(src, 'key'),
            options=dict(as_map(src.get('options'))),
            models={
                name: OpencodeModel.from_payload(found)
                for name, found in raw_models.items()
            },
        )


@dataclass(frozen=True, slots=True)
class OpencodeProviderList:
    """The body of the ``GET /provider`` response."""

    all_providers: tuple[OpencodeProvider, ...]
    default: dict[str, object]
    connected: tuple[str, ...]

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeProviderList':
        """Build provider list from a decoded payload."""
        src = as_map(payload)
        providers = tuple(
            OpencodeProvider.from_payload(entry)
            for entry in as_seq(src.get('all'))
        )
        return cls(
            all_providers=providers,
            default=dict(as_map(src.get('default'))),
            connected=str_tuple(src.get('connected')),
        )


@dataclass(frozen=True, slots=True)
class OpencodeProviderListResponse(OpencodeBaseResponse):
    """Response for ``GET /provider``."""

    body: OpencodeProviderList


@dataclass(frozen=True, slots=True)
class OpencodeProviderAuthResponse(OpencodeBaseResponse):
    """Response for ``GET /provider/auth``."""

    body: dict[str, object]
