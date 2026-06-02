"""OpenCode model dataclasses (capabilities, cost, limits, and the model)."""

from dataclasses import dataclass

from opencode_server_client.models._convert import (
    as_map,
    get_bool,
    get_float,
    get_str,
    opt_float,
    opt_str,
)


@dataclass(frozen=True, slots=True)
class OpencodeModelModalities:
    """Modality flags for a model's input or output."""

    text: bool
    audio: bool
    image: bool
    video: bool
    pdf: bool

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeModelModalities':
        """Build modalities from a decoded payload."""
        src = as_map(payload)
        return cls(
            text=get_bool(src, 'text'),
            audio=get_bool(src, 'audio'),
            image=get_bool(src, 'image'),
            video=get_bool(src, 'video'),
            pdf=get_bool(src, 'pdf'),
        )


@dataclass(frozen=True, slots=True)
class OpencodeModelCapabilities:
    """Capability flags for a model."""

    temperature: bool
    reasoning: bool
    attachment: bool
    toolcall: bool
    input: OpencodeModelModalities
    output: OpencodeModelModalities

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeModelCapabilities':
        """Build capabilities from a decoded payload."""
        src = as_map(payload)
        return cls(
            temperature=get_bool(src, 'temperature'),
            reasoning=get_bool(src, 'reasoning'),
            attachment=get_bool(src, 'attachment'),
            toolcall=get_bool(src, 'toolcall'),
            input=OpencodeModelModalities.from_payload(src.get('input')),
            output=OpencodeModelModalities.from_payload(src.get('output')),
        )


@dataclass(frozen=True, slots=True)
class OpencodeModelCost:
    """Per-token cost figures for a model."""

    input: float
    output: float
    cache_read: float
    cache_write: float

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeModelCost':
        """Build cost from a decoded payload (cache nested under ``cache``)."""
        src = as_map(payload)
        cache = as_map(src.get('cache'))
        return cls(
            input=get_float(src, 'input'),
            output=get_float(src, 'output'),
            cache_read=get_float(cache, 'read'),
            cache_write=get_float(cache, 'write'),
        )


@dataclass(frozen=True, slots=True)
class OpencodeModelLimit:
    """Token-count limits for a model."""

    context: float
    input: float | None
    output: float

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeModelLimit':
        """Build limits from a decoded payload."""
        src = as_map(payload)
        return cls(
            context=get_float(src, 'context'),
            input=opt_float(src, 'input'),
            output=get_float(src, 'output'),
        )


@dataclass(frozen=True, slots=True)
class OpencodeModel:
    """A single model record returned by the provider endpoints."""

    model_id: str
    provider_id: str
    name: str
    family: str | None
    status: str
    release_date: str
    capabilities: OpencodeModelCapabilities
    cost: OpencodeModelCost
    limit: OpencodeModelLimit
    options: dict[str, object]

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeModel':
        """Build a model record from a decoded payload."""
        src = as_map(payload)
        return cls(
            model_id=get_str(src, 'id'),
            provider_id=get_str(src, 'providerID'),
            name=get_str(src, 'name'),
            family=opt_str(src, 'family'),
            status=get_str(src, 'status'),
            release_date=get_str(src, 'release_date'),
            capabilities=OpencodeModelCapabilities.from_payload(
                src.get('capabilities'),
            ),
            cost=OpencodeModelCost.from_payload(src.get('cost')),
            limit=OpencodeModelLimit.from_payload(src.get('limit')),
            options=dict(as_map(src.get('options'))),
        )
