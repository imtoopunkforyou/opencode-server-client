"""Message domain models (polymorphic union, pragmatic v1 depth).

User vs assistant messages differ in which fields are populated;
full per-role typing is deferred to phase 2.  All raw payload kept
in ``raw`` for forward-compatibility.
"""
from dataclasses import dataclass

from opencode_server_client.models._convert import (
    as_map,
    as_seq,
    get_str,
    opt_float,
    opt_int,
    opt_str,
)
from opencode_server_client.models.base import OpencodeBaseResponse


@dataclass(frozen=True, slots=True)
class OpencodeMessage:
    """A single message record.

    User and assistant messages share this schema; assistant-only
    fields (providerID, modelID, cost, error) are None for user
    messages.  Full per-role typed sub-classes are deferred to
    phase 2.  Complete server payload is preserved in ``raw``.
    """

    message_id: str
    session_id: str
    role: str
    created: int | None
    agent: str | None
    provider_id: str | None
    model_id: str | None
    cost: float | None
    error: dict[str, object] | None
    raw: dict[str, object]

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeMessage':
        """Build from a decoded message object."""
        src = as_map(payload)
        time_map = as_map(src.get('time'))
        err_found = src.get('error')
        return cls(
            message_id=get_str(src, 'id'),
            session_id=get_str(src, 'sessionID'),
            role=get_str(src, 'role'),
            created=opt_int(time_map, 'created'),
            agent=opt_str(src, 'agent'),
            provider_id=opt_str(src, 'providerID'),
            model_id=opt_str(src, 'modelID'),
            cost=opt_float(src, 'cost'),
            error=(
                dict(as_map(err_found))
                if isinstance(err_found, dict) else None
            ),
            raw=dict(src),
        )


@dataclass(frozen=True, slots=True)
class OpencodePart:
    """A message part (one of a 12-way discriminated union).

    Common fields are typed; the full per-part-type schema is kept
    in ``raw`` for forward-compatibility.  Richer typed sub-classes
    are deferred to phase 2.
    """

    part_id: str
    session_id: str
    message_id: str
    part_type: str
    raw: dict[str, object]

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodePart':
        """Build from a decoded part object."""
        src = as_map(payload)
        return cls(
            part_id=get_str(src, 'id'),
            session_id=get_str(src, 'sessionID'),
            message_id=get_str(src, 'messageID'),
            part_type=get_str(src, 'type'),
            raw=dict(src),
        )


@dataclass(frozen=True, slots=True)
class OpencodeMessageBundle:
    """A message paired with its parts.

    Server envelope uses key ``info`` for the message object;
    field is renamed ``message`` (WPS110 forbids ``info``).
    """

    message: OpencodeMessage
    parts: tuple[OpencodePart, ...]

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeMessageBundle':
        """Build from a decoded bundle object {info, parts}."""
        src = as_map(payload)
        return cls(
            message=OpencodeMessage.from_payload(src.get('info')),
            parts=tuple(
                OpencodePart.from_payload(entry)
                for entry in as_seq(src.get('parts'))
            ),
        )


def bundles_from_payload(
    payload: object,
) -> 'tuple[OpencodeMessageBundle, ...]':
    """Parse a list payload into a tuple of message bundles."""
    return tuple(
        OpencodeMessageBundle.from_payload(entry)
        for entry in as_seq(payload)
    )


@dataclass(frozen=True, slots=True)
class OpencodeMessageResponse(OpencodeBaseResponse):
    """Response for a single-message endpoint."""

    body: OpencodeMessageBundle


@dataclass(frozen=True, slots=True)
class OpencodeMessagesResponse(OpencodeBaseResponse):
    """Response for a list-of-messages endpoint."""

    body: tuple[OpencodeMessageBundle, ...]
