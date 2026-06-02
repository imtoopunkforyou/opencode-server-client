"""Input dataclasses for message write endpoints."""
from dataclasses import dataclass

from opencode_server_client.models._convert import compact


@dataclass(frozen=True, slots=True)
class OpencodeMessagePrompt:
    """Body for POST /session/{id}/message (prompt)."""

    parts: list[dict[str, object]]
    message_id: str | None = None
    agent: str | None = None
    system: str | None = None
    variant: str | None = None
    model: dict[str, object] | None = None
    no_reply: bool | None = None
    tools: dict[str, object] | None = None
    output_format: dict[str, object] | None = None

    def to_body(self) -> dict[str, object]:
        """Build a JSON body; parts always included, rest compacted."""
        built: dict[str, object] = {'parts': self.parts}
        built.update(compact({
            'messageID': self.message_id,
            'model': self.model,
            'agent': self.agent,
            'noReply': self.no_reply,
            'tools': self.tools,
            'format': self.output_format,
            'system': self.system,
            'variant': self.variant,
        }))
        return built


@dataclass(frozen=True, slots=True)
class OpencodeMessageCommand:
    """Body for POST /session/{id}/command."""

    command: str
    arguments: str
    message_id: str | None = None
    agent: str | None = None
    model: str | None = None
    variant: str | None = None

    def to_body(self) -> dict[str, object]:
        """Build a JSON body; command/arguments always included."""
        built: dict[str, object] = {
            'command': self.command,
            'arguments': self.arguments,
        }
        built.update(compact({
            'messageID': self.message_id,
            'agent': self.agent,
            'model': self.model,
            'variant': self.variant,
        }))
        return built


@dataclass(frozen=True, slots=True)
class OpencodeMessageShell:
    """Body for POST /session/{id}/shell."""

    agent: str
    command: str
    message_id: str | None = None
    model: dict[str, object] | None = None

    def to_body(self) -> dict[str, object]:
        """Build a JSON body; agent/command always included."""
        built: dict[str, object] = {
            'agent': self.agent,
            'command': self.command,
        }
        built.update(compact({
            'messageID': self.message_id,
            'model': self.model,
        }))
        return built
