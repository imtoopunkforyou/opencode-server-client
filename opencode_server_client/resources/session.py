"""Session endpoints (/session and /session/{id}/*)."""
from collections.abc import Callable
from typing import TypeVar

from opencode_server_client._decode import decode
from opencode_server_client._transport import (
    RequestSpec,
    build_query,
)
from opencode_server_client.models.base import (
    OpencodeBaseResponse,
    OpencodeBoolResponse,
    OpencodeErrorResponse,
    ok_bool,
)
from opencode_server_client.models.session import OpencodeSession
from opencode_server_client.models.session_extra import (
    OpencodeDiffResponse,
    OpencodeSessionResponse,
    OpencodeSessionsResponse,
    OpencodeSessionStatusResponse,
    OpencodeTodosResponse,
    diffs_from_payload,
    sessions_from_payload,
    todos_from_payload,
)
from opencode_server_client.models.session_input import (
    OpencodeSessionCreate,
    OpencodeSessionFork,
    OpencodeSessionInit,
    OpencodeSessionSummarize,
    OpencodeSessionUpdate,
)
from opencode_server_client.resources._base import (
    _AsyncResource,
    _SyncResource,
)

_RT = TypeVar('_RT', bound=OpencodeBaseResponse)

# HTTP method constants (avoid WPS226 string-literal overuse).
_GET = 'GET'
_POST = 'POST'
_PATCH = 'PATCH'
_DELETE = 'DELETE'

# Path templates.
_P_BASE = '/session'
_P_STATUS = '/session/status'
_P_ONE = '/session/{0}'
_P_CHILDREN = '/session/{0}/children'
_P_INIT = '/session/{0}/init'
_P_ABORT = '/session/{0}/abort'
_P_SHARE = '/session/{0}/share'
_P_SUMMARIZE = '/session/{0}/summarize'
_P_FORK = '/session/{0}/fork'
_P_TODO = '/session/{0}/todo'
_P_DIFF = '/session/{0}/diff'

# Result union aliases.
_SessionResult = OpencodeSessionResponse | OpencodeErrorResponse
_SessionsResult = OpencodeSessionsResponse | OpencodeErrorResponse
_StatusResult = OpencodeSessionStatusResponse | OpencodeErrorResponse
_BoolResult = OpencodeBoolResponse | OpencodeErrorResponse
_TodosResult = OpencodeTodosResponse | OpencodeErrorResponse
_DiffResult = OpencodeDiffResponse | OpencodeErrorResponse


def _ok_session(code: int, payload: object) -> OpencodeSessionResponse:
    return OpencodeSessionResponse(
        code=code, body=OpencodeSession.from_payload(payload)
    )


def _ok_sessions(code: int, payload: object) -> OpencodeSessionsResponse:
    return OpencodeSessionsResponse(
        code=code, body=sessions_from_payload(payload)
    )


def _ok_status(
    code: int, payload: object
) -> OpencodeSessionStatusResponse:
    if isinstance(payload, dict):
        body: dict[str, dict[str, object]] = {
            key: dict(found) if isinstance(found, dict) else {}
            for key, found in payload.items()
        }
    else:
        body = {}
    return OpencodeSessionStatusResponse(code=code, body=body)


def _ok_todos(code: int, payload: object) -> OpencodeTodosResponse:
    return OpencodeTodosResponse(
        code=code, body=todos_from_payload(payload)
    )


def _ok_diff(code: int, payload: object) -> OpencodeDiffResponse:
    return OpencodeDiffResponse(
        code=code, body=diffs_from_payload(payload)
    )


class SessionResource(_SyncResource):
    """Session endpoints (sync)."""

    def list(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SessionsResult:
        """List all sessions."""
        spec = RequestSpec(
            _GET, _P_BASE, self._query(directory, workspace), None
        )
        return self._send(spec, _ok_sessions)

    def create(
        self,
        body: OpencodeSessionCreate | None = None,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SessionResult:
        """Create a new session."""
        json_body: object = body.to_body() if body else {}
        spec = RequestSpec(
            _POST, _P_BASE, self._query(directory, workspace), json_body
        )
        return self._send(spec, _ok_session)

    def status(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _StatusResult:
        """Get the status of all active sessions."""
        spec = RequestSpec(
            _GET, _P_STATUS, self._query(directory, workspace), None
        )
        return self._send(spec, _ok_status)

    def get(
        self,
        session_id: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SessionResult:
        """Get a session by id."""
        spec = RequestSpec(
            _GET,
            _P_ONE.format(session_id),
            self._query(directory, workspace),
            None,
        )
        return self._send(spec, _ok_session)

    def update(
        self,
        session_id: str,
        body: OpencodeSessionUpdate,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SessionResult:
        """Update a session by id."""
        spec = RequestSpec(
            _PATCH,
            _P_ONE.format(session_id),
            self._query(directory, workspace),
            body.to_body(),
        )
        return self._send(spec, _ok_session)

    def delete(
        self,
        session_id: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _BoolResult:
        """Delete a session by id."""
        spec = RequestSpec(
            _DELETE,
            _P_ONE.format(session_id),
            self._query(directory, workspace),
            None,
        )
        return self._send(spec, ok_bool)

    def children(
        self,
        session_id: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SessionsResult:
        """List child sessions of a session."""
        spec = RequestSpec(
            _GET,
            _P_CHILDREN.format(session_id),
            self._query(directory, workspace),
            None,
        )
        return self._send(spec, _ok_sessions)

    def init(
        self,
        session_id: str,
        body: OpencodeSessionInit,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _BoolResult:
        """Initialise a session with a model and message."""
        spec = RequestSpec(
            _POST,
            _P_INIT.format(session_id),
            self._query(directory, workspace),
            body.to_body(),
        )
        return self._send(spec, ok_bool)

    def abort(
        self,
        session_id: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _BoolResult:
        """Abort a running session."""
        spec = RequestSpec(
            _POST,
            _P_ABORT.format(session_id),
            self._query(directory, workspace),
            None,
        )
        return self._send(spec, ok_bool)

    def share(
        self,
        session_id: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SessionResult:
        """Publish a session share link."""
        spec = RequestSpec(
            _POST,
            _P_SHARE.format(session_id),
            self._query(directory, workspace),
            None,
        )
        return self._send(spec, _ok_session)

    def unshare(
        self,
        session_id: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SessionResult:
        """Remove a session share link."""
        spec = RequestSpec(
            _DELETE,
            _P_SHARE.format(session_id),
            self._query(directory, workspace),
            None,
        )
        return self._send(spec, _ok_session)

    def summarize(
        self,
        session_id: str,
        body: OpencodeSessionSummarize,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _BoolResult:
        """Summarise a session."""
        spec = RequestSpec(
            _POST,
            _P_SUMMARIZE.format(session_id),
            self._query(directory, workspace),
            body.to_body(),
        )
        return self._send(spec, ok_bool)

    def fork(
        self,
        session_id: str,
        body: OpencodeSessionFork | None = None,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SessionResult:
        """Fork a session, optionally from a message."""
        json_body: object = body.to_body() if body else {}
        spec = RequestSpec(
            _POST,
            _P_FORK.format(session_id),
            self._query(directory, workspace),
            json_body,
        )
        return self._send(spec, _ok_session)

    def todo(
        self,
        session_id: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _TodosResult:
        """Get the to-do list for a session."""
        spec = RequestSpec(
            _GET,
            _P_TODO.format(session_id),
            self._query(directory, workspace),
            None,
        )
        return self._send(spec, _ok_todos)

    def diff(
        self,
        session_id: str,
        *,
        message_id: str | None = None,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _DiffResult:
        """Get snapshot diffs for a session."""
        spec = RequestSpec(
            _GET,
            _P_DIFF.format(session_id),
            self._query(
                directory,
                workspace,
                extra={'messageID': message_id},
            ),
            None,
        )
        return self._send(spec, _ok_diff)

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


class AsyncSessionResource(_AsyncResource):
    """Session endpoints (async)."""

    async def list(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SessionsResult:
        """List all sessions."""
        spec = RequestSpec(
            _GET, _P_BASE, self._query(directory, workspace), None
        )
        return await self._send(spec, _ok_sessions)

    async def create(
        self,
        body: OpencodeSessionCreate | None = None,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SessionResult:
        """Create a new session."""
        json_body: object = body.to_body() if body else {}
        spec = RequestSpec(
            _POST, _P_BASE, self._query(directory, workspace), json_body
        )
        return await self._send(spec, _ok_session)

    async def status(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _StatusResult:
        """Get the status of all active sessions."""
        spec = RequestSpec(
            _GET, _P_STATUS, self._query(directory, workspace), None
        )
        return await self._send(spec, _ok_status)

    async def get(
        self,
        session_id: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SessionResult:
        """Get a session by id."""
        spec = RequestSpec(
            _GET,
            _P_ONE.format(session_id),
            self._query(directory, workspace),
            None,
        )
        return await self._send(spec, _ok_session)

    async def update(
        self,
        session_id: str,
        body: OpencodeSessionUpdate,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SessionResult:
        """Update a session by id."""
        spec = RequestSpec(
            _PATCH,
            _P_ONE.format(session_id),
            self._query(directory, workspace),
            body.to_body(),
        )
        return await self._send(spec, _ok_session)

    async def delete(
        self,
        session_id: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _BoolResult:
        """Delete a session by id."""
        spec = RequestSpec(
            _DELETE,
            _P_ONE.format(session_id),
            self._query(directory, workspace),
            None,
        )
        return await self._send(spec, ok_bool)

    async def children(
        self,
        session_id: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SessionsResult:
        """List child sessions of a session."""
        spec = RequestSpec(
            _GET,
            _P_CHILDREN.format(session_id),
            self._query(directory, workspace),
            None,
        )
        return await self._send(spec, _ok_sessions)

    async def init(
        self,
        session_id: str,
        body: OpencodeSessionInit,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _BoolResult:
        """Initialise a session with a model and message."""
        spec = RequestSpec(
            _POST,
            _P_INIT.format(session_id),
            self._query(directory, workspace),
            body.to_body(),
        )
        return await self._send(spec, ok_bool)

    async def abort(
        self,
        session_id: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _BoolResult:
        """Abort a running session."""
        spec = RequestSpec(
            _POST,
            _P_ABORT.format(session_id),
            self._query(directory, workspace),
            None,
        )
        return await self._send(spec, ok_bool)

    async def share(
        self,
        session_id: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SessionResult:
        """Publish a session share link."""
        spec = RequestSpec(
            _POST,
            _P_SHARE.format(session_id),
            self._query(directory, workspace),
            None,
        )
        return await self._send(spec, _ok_session)

    async def unshare(
        self,
        session_id: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SessionResult:
        """Remove a session share link."""
        spec = RequestSpec(
            _DELETE,
            _P_SHARE.format(session_id),
            self._query(directory, workspace),
            None,
        )
        return await self._send(spec, _ok_session)

    async def summarize(
        self,
        session_id: str,
        body: OpencodeSessionSummarize,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _BoolResult:
        """Summarise a session."""
        spec = RequestSpec(
            _POST,
            _P_SUMMARIZE.format(session_id),
            self._query(directory, workspace),
            body.to_body(),
        )
        return await self._send(spec, ok_bool)

    async def fork(
        self,
        session_id: str,
        body: OpencodeSessionFork | None = None,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _SessionResult:
        """Fork a session, optionally from a message."""
        json_body: object = body.to_body() if body else {}
        spec = RequestSpec(
            _POST,
            _P_FORK.format(session_id),
            self._query(directory, workspace),
            json_body,
        )
        return await self._send(spec, _ok_session)

    async def todo(
        self,
        session_id: str,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _TodosResult:
        """Get the to-do list for a session."""
        spec = RequestSpec(
            _GET,
            _P_TODO.format(session_id),
            self._query(directory, workspace),
            None,
        )
        return await self._send(spec, _ok_todos)

    async def diff(
        self,
        session_id: str,
        *,
        message_id: str | None = None,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> _DiffResult:
        """Get snapshot diffs for a session."""
        spec = RequestSpec(
            _GET,
            _P_DIFF.format(session_id),
            self._query(
                directory,
                workspace,
                extra={'messageID': message_id},
            ),
            None,
        )
        return await self._send(spec, _ok_diff)

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
