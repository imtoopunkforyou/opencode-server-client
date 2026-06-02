"""OpenCode server client — public API surface."""

from opencode_server_client.client import (
    OpencodeAsyncClient,
    OpencodeClient,
    OpencodeClientOptions,
)
from opencode_server_client.models._catalog_responses import (
    OpencodeAgentsResponse,
    OpencodeCommandsResponse,
    OpencodeLspStatusResponse,
    OpencodeMcpStatusResponse,
    OpencodePathResponse,
    OpencodeSkillsResponse,
)
from opencode_server_client.models._model import (
    OpencodeModel,
    OpencodeModelCapabilities,
    OpencodeModelCost,
    OpencodeModelLimit,
    OpencodeModelModalities,
)
from opencode_server_client.models.base import (
    OpencodeBaseResponse,
    OpencodeBoolResponse,
    OpencodeError,
    OpencodeErrorResponse,
)
from opencode_server_client.models.catalog import (
    OpencodeAgent,
    OpencodeCommand,
    OpencodeLspStatus,
    OpencodePath,
    OpencodeSkill,
)
from opencode_server_client.models.common import OpencodeTimestamps
from opencode_server_client.models.config import (
    OpencodeConfig,
    OpencodeConfigResponse,
    OpencodeProvidersConfig,
    OpencodeProvidersConfigResponse,
)
from opencode_server_client.models.event import OpencodeEvent
from opencode_server_client.models.file import (
    OpencodeFileContent,
    OpencodeFileContentResponse,
    OpencodeFileNode,
    OpencodeFilesResponse,
    OpencodeFileStatus,
    OpencodeFileStatusResponse,
)
from opencode_server_client.models.find import (
    OpencodeFindFilesQuery,
    OpencodeFindFilesResponse,
    OpencodeMatch,
    OpencodeMatchesResponse,
    OpencodeRange,
    OpencodeSymbol,
    OpencodeSymbolsResponse,
)
from opencode_server_client.models.health import (
    OpencodeHealthData,
    OpencodeHealthResponse,
)
from opencode_server_client.models.message import (
    OpencodeMessage,
    OpencodeMessageBundle,
    OpencodeMessageResponse,
    OpencodeMessagesResponse,
    OpencodePart,
)
from opencode_server_client.models.message_input import (
    OpencodeMessageCommand,
    OpencodeMessagePrompt,
    OpencodeMessageShell,
)
from opencode_server_client.models.project import (
    OpencodeProject,
    OpencodeProjectResponse,
    OpencodeProjectsResponse,
)
from opencode_server_client.models.provider import (
    OpencodeProvider,
    OpencodeProviderAuthResponse,
    OpencodeProviderList,
    OpencodeProviderListResponse,
)
from opencode_server_client.models.session import (
    OpencodeModelRef,
    OpencodeSession,
    OpencodeSessionSummary,
    OpencodeSessionTime,
    OpencodeShareInfo,
    OpencodeTokenUsage,
)
from opencode_server_client.models.session_extra import (
    OpencodeDiffResponse,
    OpencodeSessionResponse,
    OpencodeSessionsResponse,
    OpencodeSessionStatusResponse,
    OpencodeSnapshotDiff,
    OpencodeTodo,
    OpencodeTodosResponse,
)
from opencode_server_client.models.session_input import (
    OpencodeSessionCreate,
    OpencodeSessionFork,
    OpencodeSessionInit,
    OpencodeSessionSummarize,
    OpencodeSessionUpdate,
)
from opencode_server_client.models.vcs import (
    OpencodeVcsDiffResponse,
    OpencodeVcsFileDiff,
    OpencodeVcsFileStatus,
    OpencodeVcsInfo,
    OpencodeVcsInfoResponse,
    OpencodeVcsStatusResponse,
)
from opencode_server_client.version import VERSION

__version__ = VERSION

__all__ = [
    'OpencodeAgent',
    'OpencodeAgentsResponse',
    'OpencodeAsyncClient',
    'OpencodeBaseResponse',
    'OpencodeBoolResponse',
    'OpencodeClient',
    'OpencodeClientOptions',
    'OpencodeCommand',
    'OpencodeCommandsResponse',
    'OpencodeConfig',
    'OpencodeConfigResponse',
    'OpencodeDiffResponse',
    'OpencodeError',
    'OpencodeErrorResponse',
    'OpencodeEvent',
    'OpencodeFileContent',
    'OpencodeFileContentResponse',
    'OpencodeFileNode',
    'OpencodeFileStatus',
    'OpencodeFileStatusResponse',
    'OpencodeFilesResponse',
    'OpencodeFindFilesQuery',
    'OpencodeFindFilesResponse',
    'OpencodeHealthData',
    'OpencodeHealthResponse',
    'OpencodeLspStatus',
    'OpencodeLspStatusResponse',
    'OpencodeMatch',
    'OpencodeMatchesResponse',
    'OpencodeMcpStatusResponse',
    'OpencodeMessage',
    'OpencodeMessageBundle',
    'OpencodeMessageCommand',
    'OpencodeMessagePrompt',
    'OpencodeMessageResponse',
    'OpencodeMessageShell',
    'OpencodeMessagesResponse',
    'OpencodeModel',
    'OpencodeModelCapabilities',
    'OpencodeModelCost',
    'OpencodeModelLimit',
    'OpencodeModelModalities',
    'OpencodeModelRef',
    'OpencodePart',
    'OpencodePath',
    'OpencodePathResponse',
    'OpencodeProject',
    'OpencodeProjectResponse',
    'OpencodeProjectsResponse',
    'OpencodeProvider',
    'OpencodeProviderAuthResponse',
    'OpencodeProviderList',
    'OpencodeProviderListResponse',
    'OpencodeProvidersConfig',
    'OpencodeProvidersConfigResponse',
    'OpencodeRange',
    'OpencodeSession',
    'OpencodeSessionCreate',
    'OpencodeSessionFork',
    'OpencodeSessionInit',
    'OpencodeSessionResponse',
    'OpencodeSessionStatusResponse',
    'OpencodeSessionSummarize',
    'OpencodeSessionSummary',
    'OpencodeSessionTime',
    'OpencodeSessionUpdate',
    'OpencodeSessionsResponse',
    'OpencodeShareInfo',
    'OpencodeSkill',
    'OpencodeSkillsResponse',
    'OpencodeSnapshotDiff',
    'OpencodeSymbol',
    'OpencodeSymbolsResponse',
    'OpencodeTimestamps',
    'OpencodeTodo',
    'OpencodeTodosResponse',
    'OpencodeTokenUsage',
    'OpencodeVcsDiffResponse',
    'OpencodeVcsFileDiff',
    'OpencodeVcsFileStatus',
    'OpencodeVcsInfo',
    'OpencodeVcsInfoResponse',
    'OpencodeVcsStatusResponse',
    '__version__',
]
