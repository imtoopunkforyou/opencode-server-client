# Design: `opencode-server-client`

- **Date:** 2026-06-02
- **Status:** Approved-pending-review
- **Author:** Timur Valiev (with Claude)

## 1. Summary

A Python HTTP client library for the [OpenCode web server](https://opencode.ai/docs/server/),
built on [`httpx`](https://www.python-httpx.org/). It exposes both a **synchronous**
and an **asynchronous** client with identical method surfaces. Every method returns an
immutable dataclass carrying the HTTP `code` and a typed `body` payload.

> **Naming note:** the response payload field is `body`, not `data`. The project's
> wemake-python-styleguide (`WPS110`) forbids the identifier `data`, and disabling rules
> is prohibited by `AGENTS.md`. `body` is the lint-clean equivalent. The same constraint
> rules out internal use of `info`, `params`, `result`, `value`, `content`, `item`; their
> approved substitutes (`message`, `query`, `payload`, `text`, `entry`, …) are used instead.

## 2. Goals / Non-goals

**Goals**

- Two clients sharing one API surface: `OpencodeClient` (sync) and `OpencodeAsyncClient` (async).
- One method per endpoint, grouped into resource namespaces (`oc.session.create(...)`).
- Each method returns a `@dataclass(frozen=True, slots=True)` with `code: int` and a typed `data`.
- Hand-written, readable, fully typed models that pass the project's strict linters
  (ruff `ALL`, wemake-python-styleguide, `mypy` strict) without `noqa` or generated code.
- Cover the documented "core" surface (~46 methods); leave a clean extension path for the rest.

**Non-goals (v1)**

- No code generation from the OpenAPI spec; models are hand-written.
- No coverage of `v2`, `experimental`, `workspace`, `pty`, `sync` route groups, nor
  `tui`, `mcp` mutation/auth, OAuth, `auth set/remove`, `question`, `permission`,
  message `part` operations, `prompt_async`, `revert`/`unrevert`, `vcs/apply`,
  `global dispose`/`upgrade`/`event`. These are deferred to phase 2.
- No retry/backoff policy, no caching, no pagination helpers (server returns full lists).

## 3. Public API and naming

- `OpencodeClient` — synchronous; mirrors `httpx.Client`.
- `OpencodeAsyncClient` — asynchronous; mirrors `httpx.AsyncClient`.
- Resource namespaces are attributes on the client (e.g. `oc.session`, `oc.file`).
- Both are exported from the package root alongside the model dataclasses.

```python
from opencode_server_client import OpencodeClient

oc = OpencodeClient(base_url="http://127.0.0.1:8080")
resp = oc.session.create(OpencodeSessionCreate(title="demo"))
if resp.code == 200:
    session = resp.body          # typed OpencodeSession
oc.close()                       # or:  with OpencodeClient(...) as oc:
```

```python
from opencode_server_client import OpencodeAsyncClient

async with OpencodeAsyncClient(base_url="http://127.0.0.1:8080") as oc:
    resp = await oc.session.create(OpencodeSessionCreate(title="demo"))
```

> **Argument limits:** ruff `PLR0913` and wemake `WPS211` cap a callable at **5 parameters,
> counting `self`** (verified). Endpoints whose request body has many fields therefore take a
> single frozen *input* dataclass (e.g. `OpencodeSessionCreate`) plus optional
> `directory` / `workspace` overrides, instead of a long keyword list.

## 4. Scope — v1 core (~46 methods)

| Namespace | Methods → endpoints |
|---|---|
| `oc.server` | `health` `GET /global/health`, `config` `GET /global/config`, `update_config` `PATCH /global/config` |
| `oc.config` | `get` `GET /config`, `update` `PATCH /config`, `providers` `GET /config/providers` |
| `oc.session` | `list` `GET /session`, `create` `POST /session`, `status` `GET /session/status`, `get` `GET /session/{id}`, `update` `PATCH /session/{id}`, `delete` `DELETE /session/{id}`, `children` `GET /session/{id}/children`, `init` `POST /session/{id}/init`, `abort` `POST /session/{id}/abort`, `share` `POST /session/{id}/share`, `unshare` `DELETE /session/{id}/share`, `summarize` `POST /session/{id}/summarize`, `fork` `POST /session/{id}/fork`, `todo` `GET /session/{id}/todo`, `diff` `GET /session/{id}/diff` |
| `oc.message` | `list` `GET /session/{id}/message`, `prompt` `POST /session/{id}/message`, `get` `GET /session/{id}/message/{mid}`, `command` `POST /session/{id}/command`, `shell` `POST /session/{id}/shell` |
| `oc.file` | `list` `GET /file`, `read` `GET /file/content`, `status` `GET /file/status` |
| `oc.find` | `text` `GET /find`, `files` `GET /find/file`, `symbols` `GET /find/symbol` |
| `oc.project` | `list` `GET /project`, `current` `GET /project/current` |
| `oc.vcs` | `get` `GET /vcs`, `status` `GET /vcs/status`, `diff` `GET /vcs/diff` |
| `oc.provider` | `list` `GET /provider`, `auth` `GET /provider/auth` |
| `oc.agent` | `list` `GET /agent` |
| `oc.command` | `list` `GET /command` |
| `oc.skill` | `list` `GET /skill` |
| `oc.path` | `get` `GET /path` |
| `oc.lsp` | `status` `GET /lsp` |
| `oc.mcp` | `status` `GET /mcp` |
| `oc.event` | `subscribe` `GET /event` — SSE stream (special case, see §8) |

The exact request/response field sets are taken from the live OpenAPI spec at
`http://127.0.0.1:8080/doc` and verified against the running server during implementation.

## 5. Architecture / module layout

```
opencode_server_client/
├── __init__.py            # exports clients + models
├── version.py             # unchanged
├── _transport.py          # RequestSpec, RawResponse, SyncTransport, AsyncTransport
├── _decode.py             # httpx.Response → RawResponse; success/error selection
├── client.py              # OpencodeClient / OpencodeAsyncClient — wire up namespaces
├── models/
│   ├── __init__.py        # re-export all models
│   ├── base.py            # OpencodeBaseResponse, OpencodeError, OpencodeErrorResponse
│   ├── health.py
│   ├── session.py
│   ├── message.py
│   ├── file.py
│   ├── find.py
│   ├── config.py
│   ├── project.py
│   ├── vcs.py
│   ├── provider.py
│   ├── catalog.py         # agent / command / skill / lsp / mcp / path read models
│   └── event.py
└── resources/
    ├── __init__.py
    ├── _base.py           # _SyncResource / _AsyncResource (hold a transport)
    ├── server.py
    ├── config.py
    ├── session.py
    ├── message.py
    ├── file.py
    ├── find.py
    ├── project.py
    ├── vcs.py
    ├── provider.py
    ├── catalog.py         # agent / command / skill / lsp / mcp / path resources
    └── event.py
```

Small, focused modules keep functions within wemake's `max-complexity = 6` and the
80-column limit.

## 6. Transport core — shared logic, no duplication

The only difference between the sync and async paths is `await`. Each endpoint is
therefore written **once** as a pure "build request" function plus a pure "parse response"
function. The sync and async resource classes are thin wrappers that differ only in the
I/O call.

```python
@dataclass(frozen=True, slots=True)
class RequestSpec:
    method: str
    path: str
    params: Mapping[str, str] | None
    json_body: object | None

@dataclass(frozen=True, slots=True)
class RawResponse:
    code: int
    payload: object        # decoded JSON (dict / list) or None
```

```python
# resources/session.py
def _build_create(body, params) -> RequestSpec: ...
def _parse_session(raw: RawResponse) -> OpencodeSessionResponse | OpencodeErrorResponse: ...

class SessionResource(_SyncResource):
    def create(self, *, title=None, ...) -> OpencodeSessionResponse | OpencodeErrorResponse:
        return _parse_session(self._transport.send(_build_create(...)))

class AsyncSessionResource(_AsyncResource):
    async def create(self, *, title=None, ...) -> OpencodeSessionResponse | OpencodeErrorResponse:
        return _parse_session(await self._transport.send(_build_create(...)))
```

`SyncTransport`/`AsyncTransport` wrap a shared `httpx.Client`/`httpx.AsyncClient`, execute a
`RequestSpec`, and return a `RawResponse`. Parsers are shared between sync and async.

## 7. Response and error model

Follows the user-specified pattern: a base response with `code` + `data`, and per-endpoint
subclasses that narrow `data` to a typed model.

```python
@dataclass(frozen=True, slots=True)
class OpencodeBaseResponse:
    code: int
    body: object

@dataclass(frozen=True, slots=True)
class OpencodeHealthData:
    healthy: bool
    version: str

@dataclass(frozen=True, slots=True)
class OpencodeHealthResponse(OpencodeBaseResponse):
    body: OpencodeHealthData

@dataclass(frozen=True, slots=True)
class OpencodeError:
    name: str
    message: str | None
    payload: dict[str, object] | None     # remaining raw error fields

@dataclass(frozen=True, slots=True)
class OpencodeErrorResponse(OpencodeBaseResponse):
    body: OpencodeError
```

Rules:

- **2xx** → typed `Opencode<...>Response` (e.g. `OpencodeHealthResponse`).
- **4xx / 5xx** → `OpencodeErrorResponse` with a typed `OpencodeError`. No exception is
  raised on HTTP status (per design decision). The server uses two error envelope shapes —
  `{"name": ..., "data": {"message": ...}}` and `{"_tag": ..., "message": ...}`; the parser
  reads `name`/`_tag` and the nested-or-top-level `message`, keeping the full dict in
  `OpencodeError.payload`.
- **Transport failures** from httpx (`httpx.RequestError` — connection refused, timeout)
  propagate unchanged; they are not HTTP responses.
- HTTP status classification uses `http.HTTPStatus` (not integer literals) to satisfy
  wemake `WPS432`.
- Each method's return type is the union `Opencode<...>Response | OpencodeErrorResponse`;
  callers narrow on `resp.code`.
- Collections inside `body` use `tuple[...]` (immutability under `frozen=True`).

The `frozen + slots` inheritance with a redeclared `body` field, narrowing `object` to a
concrete type, is verified to pass `mypy --strict`, `ruff`, and `flake8`/wemake on the
target Python 3.10: no `__dict__`, immutability enforced, no override error.

## 8. Streaming — `oc.event.subscribe`

`GET /event` is a Server-Sent-Events stream and does not fit the `code + data` shape. It is
an explicit special case: the sync client returns a generator of typed events, the async
client returns an async iterator.

```python
for event in oc.event.subscribe():         # sync
    ...
async for event in oc.event.subscribe():    # async
    ...
```

Events are parsed into typed `OpencodeEvent` dataclasses. The stream is opened via
`httpx`'s streaming response API and yields parsed events until the caller stops iterating
or the connection closes.

## 9. Client configuration

To stay within the 5-parameter limit (`PLR0913`/`WPS211`, counting `self`), connection
settings live in a frozen options object:

```python
@dataclass(frozen=True, slots=True)
class OpencodeClientOptions:
    timeout: float = 30.0
    headers: Mapping[str, str] | None = None
    directory: str | None = None       # default for the ?directory= query param
    workspace: str | None = None        # default for the ?workspace= query param

class OpencodeClient:
    def __init__(
        self,
        base_url: str,
        *,
        options: OpencodeClientOptions | None = None,
        transport: httpx.BaseTransport | None = None,   # httpx.MockTransport in tests
    ) -> None: ...
```

- `OpencodeClient("http://127.0.0.1:8080")` works with all defaults.
- `directory` / `workspace` from the options become default query params on routes that
  accept them, and are overridable per call (each such method takes optional
  `directory` / `workspace` keyword arguments).
- `close()` / `aclose()` plus context-manager support (`__enter__`/`__exit__`,
  `__aenter__`/`__aexit__`).
- `OpencodeAsyncClient` has the same signature and accepts `httpx.MockTransport` too (it is
  transport-agnostic).

## 10. Testing

- Test tree mirrors the source tree; a `conftest.py` per directory, with the root
  `tests/conftest.py` (per AGENTS.md).
- HTTP is mocked with **`httpx.MockTransport`** injected via the client's `transport`
  argument. This mocks at the HTTP boundary, avoids brittle `patch`, and exercises both the
  sync and async clients with the same handler. (This deviates from the `AsyncMock`+`patch`
  snippet in AGENTS.md, which is unsuited to an httpx client; approved.)
- Each endpoint is tested for: correct request (method, path, params, body), 2xx parsing
  into the typed model, and 4xx/5xx parsing into `OpencodeErrorResponse`.
- The live server at `127.0.0.1:8080` is used during development to confirm exact field
  names; the test suite itself stays hermetic (no network).

## 11. Lint / type compliance

- All models and methods are hand-written, fully type-hinted, and pass `mypy` strict.
- Modules are kept small to satisfy wemake complexity limits and the 80-column width.
- No `noqa`, no rule disabling, no generated code.

## 12. Future (phase 2)

Remaining route groups and operations listed under §2 Non-goals, plus optional retry
policy, pagination helpers, and richer auth. The namespace architecture extends to these
without restructuring.
