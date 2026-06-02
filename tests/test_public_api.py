"""Public-API surface test: every name in __all__ must be importable."""

import opencode_server_client

_REQUIRED_NAMES = (
    'OpencodeClient',
    'OpencodeAsyncClient',
    'OpencodeClientOptions',
    'OpencodeHealthResponse',
    'OpencodeErrorResponse',
    'OpencodeError',
    'OpencodeSession',
    'OpencodeSessionCreate',
    'OpencodeMessagePrompt',
    'OpencodeFindFilesQuery',
    'OpencodeBaseResponse',
    'OpencodeEvent',
    'OpencodeAgent',
    'OpencodeModel',
    'OpencodeVcsInfo',
    'OpencodeProject',
    'OpencodeProvider',
    'OpencodeConfig',
    'OpencodeFileNode',
    'OpencodeSessionFork',
    '__version__',
)


def test_required_attrs_present():
    """All required names are attributes of the package."""
    for name in _REQUIRED_NAMES:
        assert hasattr(opencode_server_client, name), name


def test_required_attrs_in_all():
    """All required names appear in __all__."""
    exported = set(opencode_server_client.__all__)
    for name in _REQUIRED_NAMES:
        assert name in exported, name


def test_all_names_are_importable():
    """Every name declared in __all__ is a non-None package attribute."""
    for name in opencode_server_client.__all__:
        assert getattr(opencode_server_client, name, None) is not None, name
