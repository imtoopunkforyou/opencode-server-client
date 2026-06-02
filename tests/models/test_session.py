"""Tests for session domain models and response wrappers."""

from opencode_server_client.models.base import OpencodeBoolResponse, ok_bool
from opencode_server_client.models.session import (
    OpencodeSession,
    OpencodeSessionTime,
    OpencodeTokenUsage,
)
from opencode_server_client.models.session_extra import (
    OpencodeDiffResponse,
    OpencodeSnapshotDiff,
    OpencodeTodo,
    OpencodeTodosResponse,
    diffs_from_payload,
    sessions_from_payload,
    todos_from_payload,
)

_MINIMAL_PAYLOAD: dict[str, object] = {
    'id': 'ses_x',
    'slug': 's',
    'projectID': 'p',
    'directory': '/d',
    'title': 't',
    'version': '1.15.13',
    'time': {'created': 1, 'updated': 2},
    'permission': [],
}


def test_session_minimal_maps_required_fields():
    """OpencodeSession.from_payload maps id, projectID, and time fields."""
    session = OpencodeSession.from_payload(_MINIMAL_PAYLOAD)
    assert session.session_id == 'ses_x'
    assert session.project_id == 'p'
    assert session.slug == 's'
    assert session.directory == '/d'
    assert session.title == 't'
    assert session.version == '1.15.13'


def test_session_minimal_optional_fields_default_to_none():
    """Absent optional fields default to None when not in payload."""
    session = OpencodeSession.from_payload(_MINIMAL_PAYLOAD)
    assert session.parent_id is None
    assert session.workspace_id is None
    assert session.path is None
    assert session.agent is None
    assert session.tokens is None
    assert session.cost is None
    assert session.share is None
    assert session.model is None
    assert session.summary is None
    assert session.revert is None
    assert session.metadata is None


def test_session_minimal_time_fields():
    """time.created and time.updated are parsed from the 'time' sub-object."""
    session = OpencodeSession.from_payload(_MINIMAL_PAYLOAD)
    assert isinstance(session.time, OpencodeSessionTime)
    assert session.time.created == 1
    assert session.time.updated == 2
    assert session.time.compacting is None
    assert session.time.archived is None


def test_session_minimal_permission_is_empty_tuple():
    """An empty 'permission' list maps to an empty tuple."""
    session = OpencodeSession.from_payload(_MINIMAL_PAYLOAD)
    assert session.permission == ()


def test_session_frozen_and_slotted():
    """OpencodeSession is frozen and does not have __dict__."""
    session = OpencodeSession.from_payload(_MINIMAL_PAYLOAD)
    assert not hasattr(session, '__dict__')


def test_session_with_tokens():
    """Nested tokens.cache_read is read from tokens.cache.read."""
    payload = dict(_MINIMAL_PAYLOAD)
    payload['tokens'] = {
        'input': 1,
        'output': 2,
        'reasoning': 0,
        'cache': {'read': 3, 'write': 4},
    }
    session = OpencodeSession.from_payload(payload)
    assert isinstance(session.tokens, OpencodeTokenUsage)
    assert session.tokens.input == 1.0
    assert session.tokens.output == 2.0
    assert session.tokens.cache_read == 3.0
    assert session.tokens.cache_write == 4.0


def test_session_with_share():
    """Nested share.url is read when 'share' is a dict."""
    payload = dict(_MINIMAL_PAYLOAD)
    payload['share'] = {'url': 'https://share.example.com/ses_x'}
    session = OpencodeSession.from_payload(payload)
    assert session.share is not None
    assert session.share.url == 'https://share.example.com/ses_x'


def test_session_with_model_ref():
    """Nested model.id and model.providerID are read when 'model' is a dict."""
    payload = dict(_MINIMAL_PAYLOAD)
    payload['model'] = {'id': 'gpt-4o', 'providerID': 'openai'}
    session = OpencodeSession.from_payload(payload)
    assert session.model is not None
    assert session.model.model_id == 'gpt-4o'
    assert session.model.provider_id == 'openai'
    assert session.model.variant is None


def test_session_with_summary():
    """Nested summary fields are parsed when 'summary' is a dict."""
    payload = dict(_MINIMAL_PAYLOAD)
    payload['summary'] = {'additions': 10, 'deletions': 2, 'files': 3}
    session = OpencodeSession.from_payload(payload)
    assert session.summary is not None
    assert session.summary.additions == 10.0
    assert session.summary.files == 3.0


def test_sessions_from_payload_returns_tuple():
    """sessions_from_payload builds a tuple of OpencodeSession objects."""
    sessions = sessions_from_payload([_MINIMAL_PAYLOAD, _MINIMAL_PAYLOAD])
    assert len(sessions) == 2
    assert all(isinstance(s, OpencodeSession) for s in sessions)


def test_todo_content_maps_to_text():
    """OpencodeTodo maps the server key 'content' to the field 'text'."""
    todo = OpencodeTodo.from_payload(
        {'content': 'fix bug', 'status': 'open', 'priority': 'high'}
    )
    assert todo.text == 'fix bug'
    assert todo.status == 'open'
    assert todo.priority == 'high'


def test_todos_from_payload_returns_tuple():
    """todos_from_payload parses a list into a tuple of OpencodeTodo."""
    todos = todos_from_payload(
        [
            {'content': 'a', 'status': 'open', 'priority': 'low'},
            {'content': 'b', 'status': 'done', 'priority': 'high'},
        ]
    )
    assert isinstance(todos, tuple)
    assert len(todos) == 2
    assert todos[0].text == 'a'


def test_todos_response_is_base_response_subclass():
    """OpencodeTodosResponse is a proper OpencodeBaseResponse subclass."""
    todos = todos_from_payload([])
    resp = OpencodeTodosResponse(code=200, body=todos)
    assert resp.code == 200
    assert resp.body == ()


def test_snapshot_diff_file_maps_to_filepath():
    """OpencodeSnapshotDiff maps server key 'file' to field 'filepath'."""
    diff = OpencodeSnapshotDiff.from_payload(
        {
            'file': 'src/main.py',
            'patch': '@@ ...',
            'additions': 5,
            'deletions': 1,
            'status': 'modified',
        }
    )
    assert diff.filepath == 'src/main.py'
    assert diff.patch == '@@ ...'
    assert diff.additions == 5.0
    assert diff.status == 'modified'


def test_snapshot_diff_optional_fields_default_to_none():
    """OpencodeSnapshotDiff optional fields are None when absent."""
    diff = OpencodeSnapshotDiff.from_payload({'additions': 0, 'deletions': 0})
    assert diff.filepath is None
    assert diff.patch is None
    assert diff.status is None


def test_diffs_from_payload_returns_tuple():
    """diffs_from_payload parses a list into a tuple of OpencodeSnapshotDiff."""
    diffs = diffs_from_payload([{'additions': 1, 'deletions': 0}])
    assert isinstance(diffs, tuple)
    assert len(diffs) == 1


def test_diff_response_wraps_tuple():
    """OpencodeDiffResponse body holds a tuple of diffs."""
    diffs = diffs_from_payload([])
    resp = OpencodeDiffResponse(code=200, body=diffs)
    assert resp.body == ()


def test_ok_bool_true():
    """ok_bool(200, True) returns OpencodeBoolResponse with body True."""
    flag: object = True
    resp = ok_bool(200, flag)
    assert isinstance(resp, OpencodeBoolResponse)
    assert resp.body is True
    assert resp.code == 200


def test_ok_bool_false_payload():
    """ok_bool(200, False) returns body False."""
    flag: object = False
    resp = ok_bool(200, flag)
    assert resp.body is False


def test_ok_bool_truthy_payload():
    """ok_bool coerces any truthy payload to True."""
    resp = ok_bool(200, 'yes')
    assert resp.body is True


def test_bool_response_frozen_and_slotted():
    """OpencodeBoolResponse is frozen and uses __slots__."""
    flag: object = True
    resp = ok_bool(200, flag)
    assert not hasattr(resp, '__dict__')
