"""Message endpoints (/session/{id}/message and variants)."""
from collections.abc import Callable
from typing import TypeVar

from opencode_server_client._decode import decode
from opencode_server_client._transport import (
    RequestSpec,
    build_query,
)
from opencode_server_client.models.base import (
    OpencodeBaseResponse,
    OpencodeErrorResponse,
)
from opencode_server_client.models.message import (
    OpencodeMessageBundle,
    OpencodeMessageResponse,
    OpencodeMessagesResponse,
    bundles_from_payload,
)
from opencode_server_client.models.message_input import (
    OpencodeMessageCommand,
    OpencodeMessagePrompt,
    OpencodeMessageShell,
)
from opencode_server_client.resources._base import (
    _AsyncResource,
    _SyncResource,
)

_RT = TypeVar('_RT', bound=OpencodeBaseResponse)

_GET = 'GET'
_POST = 'POST'

_P_MESSAGE = '/session/{0}/message'
_P_ONE = '/session/{0}/message/{1}'
_P_COMMAND = '/session/{0}/command'
_P_SHELL = '/session/{0}/shell'

_MessageResult = OpencodeMessageResponse | OpencodeErrorResponse
_MessagesResult = OpencodeMessagesResponse | OpencodeErrorResponse


def _ok_message(code: int, payload: object) -> OpencodeMessageResponse:
    return OpencodeMessageResponse(
        code=code, body=OpencodeMessageBundle.from_payload(payload)
    )


def _ok_messages(code: int, payload: object) -> OpencodeMessagesResponse:
    return OpencodeMessagesResponse(
        code=code, body=bundles_from_payload(payload)
    )


class MessageResource(_SyncResource):
    """Message endpoints (sync)."""

    def list(
        self,
        session_id: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _MessagesResult:
        """List all messages for a session."""
        spec = RequestSpec(
            _GET,
            _P_MESSAGE.format(session_id),
            self._query(directory, workspace),
            None,
        )
        return self._send(spec, _ok_messages)

    def prompt(
        self,
        session_id: str,
        body: OpencodeMessagePrompt,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _MessageResult:
        """Send a prompt message to a session."""
        spec = RequestSpec(
            _POST,
            _P_MESSAGE.format(session_id),
            self._query(directory, workspace),
            body.to_body(),
        )
        return self._send(spec, _ok_message)

    def get(
        self,
        session_id: str,
        message_id: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _MessageResult:
        """Get a single message by id."""
        spec = RequestSpec(
            _GET,
            _P_ONE.format(session_id, message_id),
            self._query(directory, workspace),
            None,
        )
        return self._send(spec, _ok_message)

    def command(
        self,
        session_id: str,
        body: OpencodeMessageCommand,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _MessageResult:
        """Send a slash-command message to a session."""
        spec = RequestSpec(
            _POST,
            _P_COMMAND.format(session_id),
            self._query(directory, workspace),
            body.to_body(),
        )
        return self._send(spec, _ok_message)

    def shell(
        self,
        session_id: str,
        body: OpencodeMessageShell,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _MessageResult:
        """Send a shell-command message to a session."""
        spec = RequestSpec(
            _POST,
            _P_SHELL.format(session_id),
            self._query(directory, workspace),
            body.to_body(),
        )
        return self._send(spec, _ok_message)

    def _query(
        self,
        directory: str | None,
        workspace: str | None,
        extra: dict[str, object] | None = None,
    ) -> dict[str, str]:
        return build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
            extra=extra,
        )

    def _send(
        self,
        spec: RequestSpec,
        parser: Callable[[int, object], _RT],
    ) -> _RT | OpencodeErrorResponse:
        return decode(self._transport.send(spec), parser)


class AsyncMessageResource(_AsyncResource):
    """Message endpoints (async)."""

    async def list(
        self,
        session_id: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _MessagesResult:
        """List all messages for a session."""
        spec = RequestSpec(
            _GET,
            _P_MESSAGE.format(session_id),
            self._query(directory, workspace),
            None,
        )
        return await self._send(spec, _ok_messages)

    async def prompt(
        self,
        session_id: str,
        body: OpencodeMessagePrompt,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _MessageResult:
        """Send a prompt message to a session."""
        spec = RequestSpec(
            _POST,
            _P_MESSAGE.format(session_id),
            self._query(directory, workspace),
            body.to_body(),
        )
        return await self._send(spec, _ok_message)

    async def get(
        self,
        session_id: str,
        message_id: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _MessageResult:
        """Get a single message by id."""
        spec = RequestSpec(
            _GET,
            _P_ONE.format(session_id, message_id),
            self._query(directory, workspace),
            None,
        )
        return await self._send(spec, _ok_message)

    async def command(
        self,
        session_id: str,
        body: OpencodeMessageCommand,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _MessageResult:
        """Send a slash-command message to a session."""
        spec = RequestSpec(
            _POST,
            _P_COMMAND.format(session_id),
            self._query(directory, workspace),
            body.to_body(),
        )
        return await self._send(spec, _ok_message)

    async def shell(
        self,
        session_id: str,
        body: OpencodeMessageShell,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _MessageResult:
        """Send a shell-command message to a session."""
        spec = RequestSpec(
            _POST,
            _P_SHELL.format(session_id),
            self._query(directory, workspace),
            body.to_body(),
        )
        return await self._send(spec, _ok_message)

    def _query(
        self,
        directory: str | None,
        workspace: str | None,
        extra: dict[str, object] | None = None,
    ) -> dict[str, str]:
        return build_query(
            self._transport.defaults,
            directory=directory,
            workspace=workspace,
            extra=extra,
        )

    async def _send(
        self,
        spec: RequestSpec,
        parser: Callable[[int, object], _RT],
    ) -> _RT | OpencodeErrorResponse:
        return decode(await self._transport.send(spec), parser)
