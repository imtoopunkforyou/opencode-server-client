"""Input dataclasses for session write endpoints."""

from dataclasses import dataclass

from opencode_server_client.models._convert import compact


@dataclass(frozen=True, slots=True)
class OpencodeSessionCreate:
    """Body for POST /session (all fields optional)."""

    title: str | None = None
    parent_id: str | None = None
    agent: str | None = None
    workspace_id: str | None = None
    model: dict[str, object] | None = None
    metadata: dict[str, object] | None = None
    permission: list[object] | None = None

    def to_body(self) -> dict[str, object]:
        """Build a compacted JSON body, omitting None fields."""
        return compact(
            {
                'title': self.title,
                'parentID': self.parent_id,
                'agent': self.agent,
                'workspaceID': self.workspace_id,
                'model': self.model,
                'metadata': self.metadata,
                'permission': self.permission,
            }
        )


@dataclass(frozen=True, slots=True)
class OpencodeSessionUpdate:
    """Body for PATCH /session/{id} (all fields optional)."""

    title: str | None = None
    metadata: dict[str, object] | None = None
    permission: list[object] | None = None
    archived: float | None = None

    def to_body(self) -> dict[str, object]:
        """Build the PATCH body; injects time.archived when set."""
        built: dict[str, object] = compact(
            {
                'title': self.title,
                'metadata': self.metadata,
                'permission': self.permission,
            }
        )
        if self.archived is not None:
            built['time'] = {'archived': self.archived}
        return built


@dataclass(frozen=True, slots=True)
class OpencodeSessionInit:
    """Body for POST /session/{id}/init (all fields required)."""

    model_id: str
    provider_id: str
    message_id: str

    def to_body(self) -> dict[str, object]:
        """Serialise to a JSON-ready dict."""
        return {
            'modelID': self.model_id,
            'providerID': self.provider_id,
            'messageID': self.message_id,
        }


@dataclass(frozen=True, slots=True)
class OpencodeSessionSummarize:
    """Body for POST /session/{id}/summarize."""

    provider_id: str
    model_id: str
    auto: bool | None = None

    def to_body(self) -> dict[str, object]:
        """Compact JSON body for the summarize request."""
        return compact(
            {
                'providerID': self.provider_id,
                'modelID': self.model_id,
                'auto': self.auto,
            }
        )


@dataclass(frozen=True, slots=True)
class OpencodeSessionFork:
    """Body for POST /session/{id}/fork (all fields optional)."""

    message_id: str | None = None

    def to_body(self) -> dict[str, object]:
        """Compact JSON body with messageID when set."""
        return compact({'messageID': self.message_id})
