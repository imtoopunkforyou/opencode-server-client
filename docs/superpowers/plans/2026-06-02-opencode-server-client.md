# opencode-server-client Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `httpx`-based Python client for the OpenCode server exposing a sync
(`OpencodeClient`) and an async (`OpencodeAsyncClient`) client, one method per core
endpoint, each returning an immutable `code` + `body` dataclass.

**Architecture:** Each endpoint is written once as a pure `_build_*` (→ `RequestSpec`) and
`_parse_*` (`RawResponse` → typed response) pair; thin sync/async resource classes differ
only by `await`. A shared transport executes specs through one `httpx.Client`/`AsyncClient`;
a shared `decode` helper splits 2xx into typed responses and non-2xx into `OpencodeError`.

**Tech Stack:** Python 3.10+, `httpx ^0.28`, `dataclasses` (frozen + slots), `pytest`,
`httpx.MockTransport`. Linters: `ruff` (ALL), wemake-python-styleguide, `mypy --strict`.

---

## Conventions (read once, apply everywhere)

**Lint facts (verified against this repo's config):**
- Max **5** parameters per callable, **counting `self`** (`PLR0913`/`WPS211`). Methods get
  `self` + 4 at most. Multi-field request bodies → one frozen *input* dataclass argument.
- `WPS110` forbids the identifiers `data`, `info`, `params`, `result`, `value`, `content`,
  `item`. Use approved names: response field is **`body`**; raw error dict is **`payload`**;
  query mapping is **`query`**; message envelope field is **`message`**; file/skill text is
  **`text`**; list element loop var is **`entry`**. Never use `val`/`var` (also forbidden).
- No integer HTTP-code literals (`WPS432`). Use `http.HTTPStatus`.
- Line length **80**. `ruff.toml` has `fix = true`; `make lint` runs `ruff format` then
  `ruff check` (autofixes imports/TCH/quotes), then `flake8`(WPS), `mypy`, `deptry`,
  `codespell`, `pymarkdown`.
- Public classes/methods/functions need Google-style docstrings (`D101/D102/D103/D106/D107`).
  Underscore-prefixed (`_build_x`, `_parse_x`) are private → no docstring required.
- Tests ignore `S101/ANN/ARG/PLR0913/PLR2004` (see `ruff.toml`); `flake8`/`mypy` do **not**
  run on `tests/` (Makefile targets only the package).

**Per-endpoint code pattern (the single source of truth — every resource follows it):**

```python
# resources/<resource>.py
def _build_<op>(<args>) -> RequestSpec:
    return RequestSpec(
        method='GET',                     # or POST/PATCH/DELETE
        path='/...'.format(...),          # interpolate path params
        query=_query(directory, workspace, extra=...),   # helper drops None
        json_body=None,                   # or a dict built from the input dataclass
    )


def _parse_<op>(raw: RawResponse) -> Opencode<Op>Response | OpencodeErrorResponse:
    return decode(raw, _ok_<op>)


def _ok_<op>(code: int, payload: object) -> Opencode<Op>Response:
    return Opencode<Op>Response(code=code, body=<model>.from_payload(payload))


class <Resource>Resource(_SyncResource):
    """<Resource> endpoints (sync)."""

    def <op>(self, <args>) -> Opencode<Op>Response | OpencodeErrorResponse:
        """<summary>."""
        return _parse_<op>(self._transport.send(_build_<op>(<args>)))


class Async<Resource>Resource(_AsyncResource):
    """<Resource> endpoints (async)."""

    async def <op>(self, <args>) -> Opencode<Op>Response | OpencodeErrorResponse:
        """<summary>."""
        return _parse_<op>(await self._transport.send(_build_<op>(<args>)))
```

`directory`/`workspace` are always keyword-only optional overrides on routes that accept
them; when omitted the transport supplies the client-level defaults.

---

## Task 0: Branch, dependency check, package skeleton

**Files:**
- Create dirs: `opencode_server_client/models/`, `opencode_server_client/resources/`
- Create: `opencode_server_client/models/__init__.py`, `opencode_server_client/resources/__init__.py`

- [ ] **Step 1: Work directly on `main`**

Per the user's instruction (hot development), commit straight to `main`; no feature branch.

- [ ] **Step 2: Verify httpx is installed**

```bash
poetry install
poetry run python -c "import httpx; print(httpx.__version__)"
```
Expected: prints a `0.28.x` version.

- [ ] **Step 3: Create the two sub-package `__init__.py` files (empty)**

```bash
mkdir -p opencode_server_client/models opencode_server_client/resources
: > opencode_server_client/models/__init__.py
: > opencode_server_client/resources/__init__.py
```

- [ ] **Step 4: Mirror the test tree**

```bash
mkdir -p tests/models tests/resources
: > tests/models/__init__.py
: > tests/resources/__init__.py
```

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "chore: scaffold client package layout"
```

---

## Task 1: Base models + conversion helpers

**Files:**
- Create: `opencode_server_client/models/base.py`
- Create: `opencode_server_client/models/_convert.py`
- Test: `tests/models/test_base.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/models/test_base.py
from opencode_server_client.models.base import (
    OpencodeBaseResponse,
    OpencodeError,
    OpencodeErrorResponse,
    build_error,
)


def test_base_response_is_frozen_and_slotted():
    resp = OpencodeBaseResponse(code=200, body={'a': 1})
    assert resp.code == 200
    assert not hasattr(resp, '__dict__')


def test_build_error_reads_name_and_nested_message():
    resp = build_error(404, {'name': 'NotFoundError', 'data': {'message': 'nope'}})
    assert isinstance(resp, OpencodeErrorResponse)
    assert resp.code == 404
    assert resp.body == OpencodeError(
        name='NotFoundError',
        message='nope',
        payload={'name': 'NotFoundError', 'data': {'message': 'nope'}},
    )


def test_build_error_reads_tag_and_top_message():
    resp = build_error(409, {'_tag': 'SessionBusyError', 'message': 'busy'})
    assert resp.body.name == 'SessionBusyError'
    assert resp.body.message == 'busy'


def test_build_error_defaults_on_non_dict_payload():
    resp = build_error(500, None)
    assert resp.body.name == 'UnknownError'
    assert resp.body.message is None
    assert resp.body.payload is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `poetry run pytest tests/models/test_base.py -q`
Expected: FAIL (`ModuleNotFoundError: opencode_server_client.models.base`).

- [ ] **Step 3: Implement `models/base.py`**

```python
# opencode_server_client/models/base.py
"""Base response and error dataclasses."""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OpencodeBaseResponse:
    """Common response shape: an HTTP code and a typed body."""

    code: int
    body: object


@dataclass(frozen=True, slots=True)
class OpencodeError:
    """Normalised server error."""

    name: str
    message: str | None
    payload: dict[str, object] | None


@dataclass(frozen=True, slots=True)
class OpencodeErrorResponse(OpencodeBaseResponse):
    """Response returned for any non-2xx status."""

    body: OpencodeError


def build_error(code: int, payload: object) -> OpencodeErrorResponse:
    """Normalise an error payload into an :class:`OpencodeErrorResponse`."""
    name = 'UnknownError'
    message: str | None = None
    extra: dict[str, object] | None = None
    if isinstance(payload, dict):
        extra = payload
        tag = payload.get('name') or payload.get('_tag')
        if isinstance(tag, str):
            name = tag
        message = _error_message(payload)
    return OpencodeErrorResponse(
        code=code,
        body=OpencodeError(name=name, message=message, payload=extra),
    )


def _error_message(payload: dict[str, object]) -> str | None:
    top = payload.get('message')
    if isinstance(top, str):
        return top
    nested = payload.get('data')
    if isinstance(nested, dict):
        inner = nested.get('message')
        if isinstance(inner, str):
            return inner
    return None
```

- [ ] **Step 4: Implement `models/_convert.py` (typed payload getters, shared by all parsers)**

```python
# opencode_server_client/models/_convert.py
"""Typed accessors for decoded JSON payloads (keeps parsers mypy-clean)."""
from collections.abc import Mapping


def as_map(payload: object) -> Mapping[str, object]:
    """Return *payload* as a mapping, or an empty mapping."""
    if isinstance(payload, Mapping):
        return payload
    return {}


def as_seq(payload: object) -> tuple[object, ...]:
    """Return *payload* as a tuple of items, or an empty tuple."""
    if isinstance(payload, list):
        return tuple(payload)
    return ()


def get_str(src: Mapping[str, object], key: str) -> str:
    """Read a required string field (missing → empty string)."""
    found = src.get(key)
    return found if isinstance(found, str) else ''


def opt_str(src: Mapping[str, object], key: str) -> str | None:
    """Read an optional string field."""
    found = src.get(key)
    return found if isinstance(found, str) else None


def get_bool(src: Mapping[str, object], key: str) -> bool:
    """Read a required boolean field (missing → False)."""
    return bool(src.get(key))


def get_int(src: Mapping[str, object], key: str) -> int:
    """Read a required integer field (missing → 0)."""
    found = src.get(key)
    return found if isinstance(found, int) else 0


def opt_int(src: Mapping[str, object], key: str) -> int | None:
    """Read an optional integer field."""
    found = src.get(key)
    return found if isinstance(found, int) else None


def get_float(src: Mapping[str, object], key: str) -> float:
    """Read a required number field (missing → 0.0)."""
    found = src.get(key)
    if isinstance(found, (int, float)):
        return float(found)
    return 0.0


def str_tuple(payload: object) -> tuple[str, ...]:
    """Coerce a payload into a tuple of strings."""
    return tuple(entry for entry in as_seq(payload) if isinstance(entry, str))
```

Note: `bool` is a subclass of `int`; in `get_int` the `isinstance(found, int)` check
accepts bools, which is acceptable for this API. Keep `get_bool` for genuine booleans.

- [ ] **Step 5: Run tests + lint**

Run:
```bash
poetry run pytest tests/models/test_base.py -q
poetry run ruff check opencode_server_client/models/base.py opencode_server_client/models/_convert.py
poetry run flake8 opencode_server_client/models/base.py opencode_server_client/models/_convert.py
poetry run mypy opencode_server_client/models --no-pretty
```
Expected: tests PASS; ruff/flake8/mypy clean.

- [ ] **Step 6: Commit**

```bash
git add opencode_server_client/models tests/models && git commit -m "feat: base response, error, and payload-conversion models"
```

---

## Task 2: Transport core

**Files:**
- Create: `opencode_server_client/_transport.py`
- Test: `tests/test_transport.py`

- [ ] **Step 1: Write the failing test (uses httpx.MockTransport)**

```python
# tests/test_transport.py
import httpx

from opencode_server_client._transport import (
    RawResponse,
    RequestSpec,
    SyncTransport,
    build_query,
)


def _handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == '/echo':
        return httpx.Response(200, json={'path': request.url.path,
                                          'q': dict(request.url.params)})
    return httpx.Response(204)


def _sync_transport() -> SyncTransport:
    client = httpx.Client(base_url='http://t', transport=httpx.MockTransport(_handler))
    return SyncTransport(client, defaults={'directory': '/d'})


def test_build_query_drops_none_and_merges():
    assert build_query({'directory': '/d'}, directory='/o', extra={'path': 'x', 'k': None}) \
        == {'directory': '/o', 'path': 'x'}


def test_send_returns_rawresponse_with_decoded_json():
    transport = _sync_transport()
    raw = transport.send(RequestSpec('GET', '/echo', {'path': 'a'}, None))
    assert isinstance(raw, RawResponse)
    assert raw.code == 200
    assert raw.payload == {'path': '/echo', 'q': {'directory': '/d', 'path': 'a'}}


def test_send_empty_body_yields_none_payload():
    transport = _sync_transport()
    raw = transport.send(RequestSpec('GET', '/missing', {}, None))
    assert raw.code == 204
    assert raw.payload is None


async def test_async_send_works():
    client = httpx.AsyncClient(base_url='http://t', transport=httpx.MockTransport(_handler))
    from opencode_server_client._transport import AsyncTransport
    transport = AsyncTransport(client, defaults={})
    raw = await transport.send(RequestSpec('GET', '/echo', {}, None))
    assert raw.code == 200
    await transport.aclose()
```

Note: the async test needs `anyio`/`pytest-asyncio`. See Task 2a.

- [ ] **Step 2: Run to verify failure**

Run: `poetry run pytest tests/test_transport.py -q`
Expected: FAIL (module missing).

- [ ] **Step 3: Implement `_transport.py`**

```python
# opencode_server_client/_transport.py
"""Request specs and the sync/async httpx transports that execute them."""
from collections.abc import Mapping
from dataclasses import dataclass

import httpx


@dataclass(frozen=True, slots=True)
class RequestSpec:
    """An immutable plan for a single HTTP request."""

    method: str
    path: str
    query: Mapping[str, str]
    json_body: object


@dataclass(frozen=True, slots=True)
class RawResponse:
    """A decoded HTTP response: status code plus JSON/text payload."""

    code: int
    payload: object


def build_query(
    defaults: Mapping[str, str],
    *,
    directory: str | None = None,
    workspace: str | None = None,
    extra: Mapping[str, object] | None = None,
) -> dict[str, str]:
    """Merge client defaults, per-call scope overrides, and endpoint params."""
    merged: dict[str, str] = dict(defaults)
    overrides: dict[str, object] = {'directory': directory, 'workspace': workspace}
    overrides.update(extra or {})
    for key, found in overrides.items():
        if found is not None:
            merged[key] = str(found)
    return merged


def _decode(response: httpx.Response) -> RawResponse:
    payload: object = None
    if response.content:
        try:
            payload = response.json()
        except ValueError:
            payload = response.text
    return RawResponse(code=response.status_code, payload=payload)


class SyncTransport:
    """Executes :class:`RequestSpec` objects through one ``httpx.Client``."""

    def __init__(self, client: httpx.Client, defaults: Mapping[str, str]) -> None:
        """Wrap *client* and remember default query params."""
        self._client = client
        self._defaults = defaults

    def send(self, spec: RequestSpec) -> RawResponse:
        """Execute *spec* and return the decoded response."""
        response = self._client.request(
            spec.method,
            spec.path,
            params=dict(spec.query),
            json=spec.json_body,
        )
        return _decode(response)

    def close(self) -> None:
        """Close the underlying client."""
        self._client.close()


class AsyncTransport:
    """Executes :class:`RequestSpec` objects through one ``httpx.AsyncClient``."""

    def __init__(self, client: httpx.AsyncClient, defaults: Mapping[str, str]) -> None:
        """Wrap *client* and remember default query params."""
        self._client = client
        self._defaults = defaults

    async def send(self, spec: RequestSpec) -> RawResponse:
        """Execute *spec* and return the decoded response."""
        response = await self._client.request(
            spec.method,
            spec.path,
            params=dict(spec.query),
            json=spec.json_body,
        )
        return _decode(response)

    async def aclose(self) -> None:
        """Close the underlying client."""
        await self._client.aclose()
```

Note: `build_query` takes `defaults` explicitly so resource `_build_*` functions stay pure;
the transport stores defaults only to expose them. Resource builders call
`build_query(self._transport.defaults, ...)`. Add a read-only property:

```python
    @property
    def defaults(self) -> Mapping[str, str]:
        """Default query params applied to every request."""
        return self._defaults
```
Add this property to **both** transports.

- [ ] **Step 4: Run tests (sync ones) + lint/mypy**

Run:
```bash
poetry run pytest tests/test_transport.py -q -k "not async"
poetry run ruff check opencode_server_client/_transport.py
poetry run flake8 opencode_server_client/_transport.py
poetry run mypy opencode_server_client/_transport.py --no-pretty
```
Expected: sync tests PASS; lint/mypy clean.

- [ ] **Step 5: Commit**

```bash
git add opencode_server_client/_transport.py tests/test_transport.py && git commit -m "feat: request spec and sync/async transports"
```

---

## Task 2a: Enable async tests

**Files:**
- Modify: `pyproject.toml` (add `pytest-asyncio` to the tests group)
- Modify: `tests/pytest.ini`

- [ ] **Step 1: Add the dependency**

```bash
poetry add --group tests "pytest-asyncio@^0.24"
```

- [ ] **Step 2: Configure asyncio auto mode**

Edit `tests/pytest.ini` to:
```ini
[pytest]
python_files = test_*.py
python_functions = test_*
asyncio_mode = auto
```

- [ ] **Step 3: Run the async transport test**

Run: `poetry run pytest tests/test_transport.py -q`
Expected: all PASS (sync + async).

- [ ] **Step 4: Verify deptry still passes (pytest-asyncio is a dev dep)**

Run: `poetry run deptry .`
Expected: no issues.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml poetry.lock tests/pytest.ini && git commit -m "test: enable asyncio auto mode"
```

---

## Task 3: Decode helper (2xx → typed, non-2xx → error)

**Files:**
- Create: `opencode_server_client/_decode.py`
- Test: `tests/test_decode.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_decode.py
from opencode_server_client._decode import decode
from opencode_server_client._transport import RawResponse
from opencode_server_client.models.base import (
    OpencodeBaseResponse,
    OpencodeErrorResponse,
)


def _ok(code: int, payload: object) -> OpencodeBaseResponse:
    return OpencodeBaseResponse(code=code, body=payload)


def test_decode_success_calls_builder():
    out = decode(RawResponse(200, {'x': 1}), _ok)
    assert out == OpencodeBaseResponse(200, {'x': 1})


def test_decode_201_is_success():
    out = decode(RawResponse(201, None), _ok)
    assert isinstance(out, OpencodeBaseResponse)
    assert not isinstance(out, OpencodeErrorResponse)


def test_decode_error_status_builds_error():
    out = decode(RawResponse(404, {'name': 'NotFoundError'}), _ok)
    assert isinstance(out, OpencodeErrorResponse)
    assert out.body.name == 'NotFoundError'
```

- [ ] **Step 2: Run to verify failure**

Run: `poetry run pytest tests/test_decode.py -q`
Expected: FAIL (module missing).

- [ ] **Step 3: Implement `_decode.py`**

```python
# opencode_server_client/_decode.py
"""Split a RawResponse into a typed success response or an error response."""
from collections.abc import Callable
from http import HTTPStatus
from typing import TypeVar

from opencode_server_client._transport import RawResponse
from opencode_server_client.models.base import (
    OpencodeBaseResponse,
    OpencodeErrorResponse,
    build_error,
)

_Response = TypeVar('_Response', bound=OpencodeBaseResponse)


def decode(
    raw: RawResponse,
    success: Callable[[int, object], _Response],
) -> _Response | OpencodeErrorResponse:
    """Build a typed response on 2xx, otherwise an :class:`OpencodeErrorResponse`."""
    if HTTPStatus.OK <= raw.code < HTTPStatus.MULTIPLE_CHOICES:
        return success(raw.code, raw.payload)
    return build_error(raw.code, raw.payload)
```

- [ ] **Step 4: Run tests + lint/mypy**

Run:
```bash
poetry run pytest tests/test_decode.py -q
poetry run ruff check opencode_server_client/_decode.py
poetry run flake8 opencode_server_client/_decode.py
poetry run mypy opencode_server_client/_decode.py --no-pretty
```
Expected: PASS; clean.

- [ ] **Step 5: Commit**

```bash
git add opencode_server_client/_decode.py tests/test_decode.py && git commit -m "feat: response decode helper"
```

---

## Task 4: Base resource classes

**Files:**
- Create: `opencode_server_client/resources/_base.py`

- [ ] **Step 1: Implement (no separate test; exercised via Task 6)**

```python
# opencode_server_client/resources/_base.py
"""Base classes that give resources access to a transport."""
from opencode_server_client._transport import AsyncTransport, SyncTransport


class _SyncResource:
    """Holds a sync transport for a group of endpoints."""

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport


class _AsyncResource:
    """Holds an async transport for a group of endpoints."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport
```

- [ ] **Step 2: Lint/mypy**

Run:
```bash
poetry run ruff check opencode_server_client/resources/_base.py
poetry run flake8 opencode_server_client/resources/_base.py
poetry run mypy opencode_server_client/resources --no-pretty
```
Expected: clean (D-rules satisfied; `_SyncResource` is private so class docstring optional,
but included).

- [ ] **Step 3: Commit**

```bash
git add opencode_server_client/resources/_base.py && git commit -m "feat: base resource classes"
```

---

## Task 5: Health model + `server` resource (first full vertical slice)

This task establishes the end-to-end pattern (model → build/parse → sync+async resource →
client wiring → tests with MockTransport). Every later resource repeats this shape.

**Files:**
- Create: `opencode_server_client/models/health.py`
- Create: `opencode_server_client/models/config.py`
- Create: `opencode_server_client/resources/server.py`
- Create: `opencode_server_client/client.py`
- Modify: `opencode_server_client/__init__.py`
- Test: `tests/resources/conftest.py`, `tests/resources/test_server.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/resources/conftest.py
import httpx
import pytest

from opencode_server_client import OpencodeAsyncClient, OpencodeClient


def make_client(handler) -> OpencodeClient:
    """Sync client wired to a MockTransport handler."""
    return OpencodeClient('http://oc', transport=httpx.MockTransport(handler))


def make_async_client(handler) -> OpencodeAsyncClient:
    """Async client wired to a MockTransport handler."""
    return OpencodeAsyncClient('http://oc', transport=httpx.MockTransport(handler))


@pytest.fixture
def health_handler():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={'healthy': True, 'version': '1.15.13'})
    return handler
```

```python
# tests/resources/test_server.py
import httpx

from opencode_server_client.models.health import (
    OpencodeHealthData,
    OpencodeHealthResponse,
)
from opencode_server_client.models.base import OpencodeErrorResponse
from tests.resources.conftest import make_async_client, make_client


def test_health_sync(health_handler):
    with make_client(health_handler) as oc:
        resp = oc.server.health()
    assert isinstance(resp, OpencodeHealthResponse)
    assert resp.code == 200
    assert resp.body == OpencodeHealthData(healthy=True, version='1.15.13')


async def test_health_async(health_handler):
    async with make_async_client(health_handler) as oc:
        resp = await oc.server.health()
    assert resp.body.version == '1.15.13'


def test_health_error_maps_to_error_response():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={'name': 'BadRequest',
                                         'data': {'message': 'bad'}})
    with make_client(handler) as oc:
        resp = oc.server.health()
    assert isinstance(resp, OpencodeErrorResponse)
    assert resp.code == 400
    assert resp.body.message == 'bad'
```

- [ ] **Step 2: Run to verify failure**

Run: `poetry run pytest tests/resources/test_server.py -q`
Expected: FAIL (imports missing).

- [ ] **Step 3: Implement `models/health.py`**

```python
# opencode_server_client/models/health.py
"""Health endpoint models."""
from dataclasses import dataclass

from opencode_server_client.models._convert import as_map, get_bool, get_str
from opencode_server_client.models.base import OpencodeBaseResponse


@dataclass(frozen=True, slots=True)
class OpencodeHealthData:
    """Server health information."""

    healthy: bool
    version: str

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeHealthData':
        """Build from a decoded payload."""
        src = as_map(payload)
        return cls(healthy=get_bool(src, 'healthy'), version=get_str(src, 'version'))


@dataclass(frozen=True, slots=True)
class OpencodeHealthResponse(OpencodeBaseResponse):
    """Response for ``GET /global/health``."""

    body: OpencodeHealthData
```

- [ ] **Step 4: Implement `models/config.py`**

Config is a large, open-ended schema; model it as a raw map with convenience fields.

```python
# opencode_server_client/models/config.py
"""Configuration models (the server's Config schema is large and open-ended)."""
from dataclasses import dataclass

from opencode_server_client.models._convert import as_map, get_bool, opt_str
from opencode_server_client.models.base import OpencodeBaseResponse


@dataclass(frozen=True, slots=True)
class OpencodeConfig:
    """A configuration document; full contents kept in ``raw``."""

    username: str | None
    autoupdate: bool
    schema: str | None
    raw: dict[str, object]

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeConfig':
        """Build from a decoded payload."""
        src = as_map(payload)
        return cls(
            username=opt_str(src, 'username'),
            autoupdate=get_bool(src, 'autoupdate'),
            schema=opt_str(src, '$schema'),
            raw=dict(src),
        )


@dataclass(frozen=True, slots=True)
class OpencodeConfigResponse(OpencodeBaseResponse):
    """Response for the config GET/PATCH endpoints."""

    body: OpencodeConfig
```

- [ ] **Step 5: Implement `resources/server.py`**

```python
# opencode_server_client/resources/server.py
"""Server-level (/global/*) endpoints."""
from opencode_server_client._decode import decode
from opencode_server_client._transport import RawResponse, RequestSpec, build_query
from opencode_server_client.models.base import OpencodeErrorResponse
from opencode_server_client.models.config import (
    OpencodeConfig,
    OpencodeConfigResponse,
)
from opencode_server_client.models.health import (
    OpencodeHealthData,
    OpencodeHealthResponse,
)
from opencode_server_client.resources._base import _AsyncResource, _SyncResource

_HealthResult = OpencodeHealthResponse | OpencodeErrorResponse
_ConfigResult = OpencodeConfigResponse | OpencodeErrorResponse


def _build_health() -> RequestSpec:
    return RequestSpec('GET', '/global/health', {}, None)


def _ok_health(code: int, payload: object) -> OpencodeHealthResponse:
    return OpencodeHealthResponse(code=code, body=OpencodeHealthData.from_payload(payload))


def _parse_health(raw: RawResponse) -> _HealthResult:
    return decode(raw, _ok_health)


def _build_config() -> RequestSpec:
    return RequestSpec('GET', '/global/config', {}, None)


def _ok_config(code: int, payload: object) -> OpencodeConfigResponse:
    return OpencodeConfigResponse(code=code, body=OpencodeConfig.from_payload(payload))


def _parse_config(raw: RawResponse) -> _ConfigResult:
    return decode(raw, _ok_config)


def _build_update_config(document: dict[str, object]) -> RequestSpec:
    return RequestSpec('PATCH', '/global/config', {}, document)


class ServerResource(_SyncResource):
    """Server-level endpoints (sync)."""

    def health(self) -> _HealthResult:
        """Get server health."""
        return _parse_health(self._transport.send(_build_health()))

    def config(self) -> _ConfigResult:
        """Get the global configuration."""
        return _parse_config(self._transport.send(_build_config()))

    def update_config(self, document: dict[str, object]) -> _ConfigResult:
        """Patch the global configuration with *document*."""
        return _parse_config(self._transport.send(_build_update_config(document)))


class AsyncServerResource(_AsyncResource):
    """Server-level endpoints (async)."""

    async def health(self) -> _HealthResult:
        """Get server health."""
        return _parse_health(await self._transport.send(_build_health()))

    async def config(self) -> _ConfigResult:
        """Get the global configuration."""
        return _parse_config(await self._transport.send(_build_config()))

    async def update_config(self, document: dict[str, object]) -> _ConfigResult:
        """Patch the global configuration with *document*."""
        return _parse_config(await self._transport.send(_build_update_config(document)))
```

Note: `build_query` is unused here (no query params); it appears from Task 7 onward.

- [ ] **Step 6: Implement `client.py`**

```python
# opencode_server_client/client.py
"""The synchronous and asynchronous OpenCode clients."""
from collections.abc import Mapping
from dataclasses import dataclass
from types import TracebackType

import httpx

from opencode_server_client._transport import AsyncTransport, SyncTransport
from opencode_server_client.resources.server import (
    AsyncServerResource,
    ServerResource,
)


@dataclass(frozen=True, slots=True)
class OpencodeClientOptions:
    """Connection options shared by both clients."""

    timeout: float = 30.0
    headers: Mapping[str, str] | None = None
    directory: str | None = None
    workspace: str | None = None


def _defaults(options: OpencodeClientOptions) -> dict[str, str]:
    scope: dict[str, str | None] = {
        'directory': options.directory,
        'workspace': options.workspace,
    }
    return {key: found for key, found in scope.items() if found is not None}


class OpencodeClient:
    """Synchronous OpenCode server client."""

    def __init__(
        self,
        base_url: str,
        *,
        options: OpencodeClientOptions | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        """Create a client for the server at *base_url*."""
        opts = options or OpencodeClientOptions()
        client = httpx.Client(
            base_url=base_url,
            timeout=opts.timeout,
            headers=dict(opts.headers or {}),
            transport=transport,
        )
        self._transport = SyncTransport(client, _defaults(opts))
        self.server = ServerResource(self._transport)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._transport.close()

    def __enter__(self) -> 'OpencodeClient':
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


class OpencodeAsyncClient:
    """Asynchronous OpenCode server client."""

    def __init__(
        self,
        base_url: str,
        *,
        options: OpencodeClientOptions | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        """Create a client for the server at *base_url*."""
        opts = options or OpencodeClientOptions()
        client = httpx.AsyncClient(
            base_url=base_url,
            timeout=opts.timeout,
            headers=dict(opts.headers or {}),
            transport=transport,
        )
        self._transport = AsyncTransport(client, _defaults(opts))
        self.server = AsyncServerResource(self._transport)

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        await self._transport.aclose()

    async def __aenter__(self) -> 'OpencodeAsyncClient':
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()
```

As later resource tasks land, add one attribute per namespace in each `__init__`
(e.g. `self.session = SessionResource(self._transport)`).

- [ ] **Step 7: Update `opencode_server_client/__init__.py`**

```python
# opencode_server_client/__init__.py
from opencode_server_client.client import (
    OpencodeAsyncClient,
    OpencodeClient,
    OpencodeClientOptions,
)
from opencode_server_client.version import VERSION

__version__ = VERSION

__all__ = [
    'OpencodeAsyncClient',
    'OpencodeClient',
    'OpencodeClientOptions',
    '__version__',
]
```

- [ ] **Step 8: Run tests + full lint/mypy on the package**

Run:
```bash
poetry run pytest tests/resources/test_server.py -q
poetry run ruff check opencode_server_client tests
poetry run flake8 opencode_server_client
poetry run mypy opencode_server_client --no-pretty
```
Expected: PASS; clean. (If `ruff` reports import-order/`TCH`, run `poetry run ruff check
--fix opencode_server_client tests` — `fix=true` already auto-fixes on `make lint`.)

- [ ] **Step 9: Verify against the live server (optional sanity check)**

Run:
```bash
poetry run python -c "from opencode_server_client import OpencodeClient; \
oc=OpencodeClient('http://127.0.0.1:8080'); print(oc.server.health()); oc.close()"
```
Expected: `OpencodeHealthResponse(code=200, body=OpencodeHealthData(healthy=True, version=...))`.

- [ ] **Step 10: Commit**

```bash
git add opencode_server_client tests && git commit -m "feat: server namespace, clients, end-to-end health slice"
```

---

## Task 6: Catalog read endpoints (`agent`, `command`, `skill`, `path`, `lsp`, `mcp`)

These are simple GET endpoints. Each follows the Task 5 pattern. Models go in
`models/catalog.py`; resources in `resources/catalog.py` (six small namespaces).

**Endpoint table:**

| Namespace.method | HTTP | Path | Query | Response body type |
|---|---|---|---|---|
| `agent.list` | GET | `/agent` | directory, workspace | `tuple[OpencodeAgent, ...]` |
| `command.list` | GET | `/command` | directory, workspace | `tuple[OpencodeCommand, ...]` |
| `skill.list` | GET | `/skill` | directory, workspace | `tuple[OpencodeSkill, ...]` |
| `path.get` | GET | `/path` | (none) | `OpencodePath` |
| `lsp.status` | GET | `/lsp` | directory, workspace | `tuple[OpencodeLspStatus, ...]` |
| `mcp.status` | GET | `/mcp` | directory, workspace | `dict[str, dict[str, object]]` (open map of MCPStatus) |

**Model field definitions (from the OpenAPI spec):**

- `OpencodeAgent`: `name: str`, `description: str | None`, `mode: str`,
  `native: bool`, `temperature: float | None`, `prompt: str | None`,
  `options: dict[str, object]`, `raw: dict[str, object]`. (`permission`, `model` kept inside
  `raw` for v1.)
- `OpencodeCommand`: `name: str`, `description: str | None`, `agent: str | None`,
  `model: str | None`, `source: str | None`, `template: str`,
  `subtask: bool`, `hints: tuple[str, ...]`.
- `OpencodeSkill`: `name: str`, `description: str | None`, `location: str`, `text: str`
  (server field `content`).
- `OpencodePath`: `home: str`, `state: str`, `config: str`, `worktree: str`, `directory: str`.
- `OpencodeLspStatus`: `lsp_id: str` (server field `id`), `name: str`, `root: str`,
  `status: str`.

- [ ] **Step 1: Write the failing test**

```python
# tests/resources/test_catalog.py
import httpx

from opencode_server_client.models.catalog import OpencodePath
from tests.resources.conftest import make_client


def _json_handler(payload, status=200):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json=payload)
    return handler


def test_path_get():
    handler = _json_handler({
        'home': '/root', 'state': '/s', 'config': '/c',
        'worktree': '/w', 'directory': '/d',
    })
    with make_client(handler) as oc:
        resp = oc.path.get()
    assert resp.code == 200
    assert resp.body == OpencodePath(home='/root', state='/s', config='/c',
                                     worktree='/w', directory='/d')


def test_agent_list_parses_each_entry():
    handler = _json_handler([{'name': 'build', 'mode': 'primary', 'native': True,
                              'options': {}}])
    with make_client(handler) as oc:
        resp = oc.agent.list()
    assert resp.code == 200
    assert len(resp.body) == 1
    assert resp.body[0].name == 'build'
    assert resp.body[0].mode == 'primary'


def test_skill_list_maps_content_to_text():
    handler = _json_handler([{'name': 's', 'location': '/l', 'content': 'hi'}])
    with make_client(handler) as oc:
        resp = oc.skill.list()
    assert resp.body[0].text == 'hi'


def test_mcp_status_returns_raw_map():
    handler = _json_handler({'srv': {'type': 'connected'}})
    with make_client(handler) as oc:
        resp = oc.mcp.status()
    assert resp.body == {'srv': {'type': 'connected'}}
```

- [ ] **Step 2: Run to verify failure**

Run: `poetry run pytest tests/resources/test_catalog.py -q`
Expected: FAIL (modules missing).

- [ ] **Step 3: Implement `models/catalog.py`**

Define each dataclass above with a `from_payload` classmethod using the `_convert` helpers,
plus the response wrappers:
- `OpencodeAgentsResponse(body: tuple[OpencodeAgent, ...])`
- `OpencodeCommandsResponse(body: tuple[OpencodeCommand, ...])`
- `OpencodeSkillsResponse(body: tuple[OpencodeSkill, ...])`
- `OpencodePathResponse(body: OpencodePath)`
- `OpencodeLspStatusResponse(body: tuple[OpencodeLspStatus, ...])`
- `OpencodeMcpStatusResponse(body: dict[str, dict[str, object]])`

Example (replicate the shape for the others):

```python
@dataclass(frozen=True, slots=True)
class OpencodePath:
    """Server filesystem paths."""

    home: str
    state: str
    config: str
    worktree: str
    directory: str

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodePath':
        """Build from a decoded payload."""
        src = as_map(payload)
        return cls(
            home=get_str(src, 'home'),
            state=get_str(src, 'state'),
            config=get_str(src, 'config'),
            worktree=get_str(src, 'worktree'),
            directory=get_str(src, 'directory'),
        )
```

For list bodies, parse with a helper, e.g.:

```python
def agents_from_payload(payload: object) -> tuple[OpencodeAgent, ...]:
    """Parse a list payload into agents."""
    return tuple(OpencodeAgent.from_payload(entry) for entry in as_seq(payload))
```

For `mcp.status` the body is the raw object coerced to `dict[str, dict[str, object]]`:

```python
def mcp_status_from_payload(payload: object) -> dict[str, dict[str, object]]:
    """Coerce the MCP status open-map payload."""
    src = as_map(payload)
    return {key: dict(as_map(found)) for key, found in src.items()}
```

- [ ] **Step 4: Implement `resources/catalog.py`**

Six sync classes + six async classes, each one method, following the Task 5 pattern. For
endpoints with `directory`/`workspace`, the method signature and builder are:

```python
def _build_agents(query: Mapping[str, str]) -> RequestSpec:
    return RequestSpec('GET', '/agent', query, None)


class AgentResource(_SyncResource):
    """Agent endpoints (sync)."""

    def list(
        self,
        *,
        directory: str | None = None,
        workspace: str | None = None,
    ) -> OpencodeAgentsResponse | OpencodeErrorResponse:
        """List agents."""
        query = build_query(self._transport.defaults,
                            directory=directory, workspace=workspace)
        return _parse_agents(self._transport.send(_build_agents(query)))
```

Verified: a **method** named `list` and dataclass **fields** named `type`/`id` do NOT
trigger ruff `A002`/`A003` under this repo's config. The only builtin-shadowing rule that
fires is `A002` on a **function argument** named `id`/`type`/etc. — so never name an
argument `id` or `type`; use `session_id`, `message_id`, `provider_id`, … (already done
throughout this plan). Field/key strings and method names are unaffected.

- [ ] **Step 5: Wire namespaces into `client.py`**

Add to both clients' `__init__`:
```python
        self.agent = AgentResource(self._transport)       # Async* in async client
        self.command = CommandResource(self._transport)
        self.skill = SkillResource(self._transport)
        self.path = PathResource(self._transport)
        self.lsp = LspResource(self._transport)
        self.mcp = McpResource(self._transport)
```

- [ ] **Step 6: Run tests + lint/mypy**

Run:
```bash
poetry run pytest tests/resources/test_catalog.py -q
poetry run ruff check opencode_server_client tests
poetry run flake8 opencode_server_client
poetry run mypy opencode_server_client --no-pretty
```
Expected: PASS; clean.

- [ ] **Step 7: Commit**

```bash
git add opencode_server_client tests && git commit -m "feat: catalog read endpoints (agent/command/skill/path/lsp/mcp)"
```

---

## Task 7: `config` namespace (`get`, `update`, `providers`)

Reuses `OpencodeConfig`/`OpencodeConfigResponse` from Task 5. Add `OpencodeProvidersConfig`
response in `models/config.py` for `/config/providers`.

**Endpoint table:**

| Method | HTTP | Path | Query | Body | Response |
|---|---|---|---|---|---|
| `config.get` | GET | `/config` | directory, workspace | — | `OpencodeConfigResponse` |
| `config.update` | PATCH | `/config` | directory, workspace | full config dict | `OpencodeConfigResponse` |
| `config.providers` | GET | `/config/providers` | directory, workspace | — | `OpencodeProvidersConfigResponse` |

`/config/providers` 200 body: `{providers: [Provider], default: {open map}}`. Model
`OpencodeProvidersConfig`: `providers: tuple[OpencodeProvider, ...]`,
`default: dict[str, object]`. (Defer until Task 10 defines `OpencodeProvider`; or model
`providers` as `tuple[dict[str, object], ...]` here and enrich in Task 10 — choose typing
once `OpencodeProvider` exists; to avoid a forward dependency, **do Task 10 before this
task** or keep providers raw here.)

- [ ] **Step 1: Write failing tests** (sync `get`, `update` sends PATCH body, `providers`).
  Use a handler that asserts `request.method` and echoes a config dict.
- [ ] **Step 2: Run → fail.**
- [ ] **Step 3: Implement builders/parsers/resources** following the pattern.
- [ ] **Step 4: Wire `self.config = ConfigResource(...)` in both clients.**
- [ ] **Step 5: Run tests + lint/mypy → clean.**
- [ ] **Step 6: Commit** `feat: config namespace`.

Concrete test for the PATCH body:
```python
def test_config_update_sends_patch_body():
    seen = {}
    def handler(request: httpx.Request) -> httpx.Response:
        seen['method'] = request.method
        seen['body'] = json.loads(request.content)
        return httpx.Response(200, json={'username': 'u', 'autoupdate': False})
    with make_client(handler) as oc:
        resp = oc.config.update({'autoupdate': True})
    assert seen['method'] == 'PATCH'
    assert seen['body'] == {'autoupdate': True}
    assert resp.body.username == 'u'
```

---

## Task 8: `project` namespace (`list`, `current`)

**Models** (`models/project.py`):
- `OpencodeProject`: `project_id: str` (server `id`), `worktree: str`, `vcs: str | None`,
  `name: str | None`, `sandboxes: tuple[str, ...]`, `time: OpencodeTimestamps`,
  `raw: dict[str, object]`.
- `OpencodeTimestamps` (shared, put in `models/common.py`): `created: int | None`,
  `updated: int | None` — built from a `{created, updated}` object.

**Endpoint table:**

| Method | HTTP | Path | Query | Response |
|---|---|---|---|---|
| `project.list` | GET | `/project` | directory, workspace | `tuple[OpencodeProject, ...]` |
| `project.current` | GET | `/project/current` | directory, workspace | `OpencodeProject` |

- [ ] **Step 1: Create `models/common.py` with `OpencodeTimestamps` + test.**
- [ ] **Step 2: Failing test for `project.current` (assert id/worktree/time).**
- [ ] **Step 3: Implement models + resource.**
- [ ] **Step 4: Wire `self.project = ProjectResource(...)`.**
- [ ] **Step 5: Tests + lint/mypy clean.**
- [ ] **Step 6: Commit** `feat: project namespace`.

```python
# models/common.py
@dataclass(frozen=True, slots=True)
class OpencodeTimestamps:
    """Created/updated millisecond timestamps."""

    created: int | None
    updated: int | None

    @classmethod
    def from_payload(cls, payload: object) -> 'OpencodeTimestamps':
        """Build from a {created, updated} object."""
        src = as_map(payload)
        return cls(created=opt_int(src, 'created'), updated=opt_int(src, 'updated'))
```

---

## Task 9: `vcs` namespace (`get`, `status`, `diff`)

**Models** (`models/vcs.py`):
- `OpencodeVcsInfo`: `branch: str | None`, `default_branch: str | None`.
- `OpencodeVcsFileStatus`: `file: str`, `additions: float`, `deletions: float`, `status: str`.

**Endpoint table:**

| Method | HTTP | Path | Query | Response |
|---|---|---|---|---|
| `vcs.get` | GET | `/vcs` | directory, workspace | `OpencodeVcsInfo` |
| `vcs.status` | GET | `/vcs/status` | directory, workspace | `tuple[OpencodeVcsFileStatus, ...]` |
| `vcs.diff` | GET | `/vcs/diff` | directory, workspace | `OpencodeVcsDiffData` |

Inspect `/vcs/diff` response shape first:
```bash
poetry run python -c "import json,urllib.request as u; \
print(json.load(u.urlopen('http://127.0.0.1:8080/doc'))['paths']['/vcs/diff']['get']['responses'])"
```
Model `OpencodeVcsDiff` accordingly (likely `{files: [...], ...}` or a string diff). If it is
a plain string/array, wrap as `OpencodeVcsDiffData(raw: object)`.

- [ ] Steps 1–6: failing test → implement → wire `self.vcs` → tests/lint clean → commit
  `feat: vcs namespace`.

---

## Task 10: `provider` namespace (`list`, `auth`) + Provider/Model models

**Models** (`models/provider.py`):
- `OpencodeModel`: full typed model — `model_id: str` (server `id`), `provider_id: str`,
  `name: str`, `family: str | None`, `status: str`, `release_date: str`,
  `capabilities: OpencodeModelCapabilities`, `cost: OpencodeModelCost`,
  `limit: OpencodeModelLimit`, `options: dict[str, object]`. Nested:
  - `OpencodeModelCapabilities`: `temperature, reasoning, attachment, toolcall: bool`,
    `input: OpencodeModalities`, `output: OpencodeModalities`.
  - `OpencodeModalities`: `text, audio, image, video, pdf: bool`.
  - `OpencodeModelCost`: `input: float`, `output: float`, `cache_read: float`,
    `cache_write: float` (from nested `cache.read`/`cache.write`).
  - `OpencodeModelLimit`: `context: float`, `input: float | None`, `output: float`.
- `OpencodeProvider`: `provider_id: str` (server `id`), `name: str`, `source: str`,
  `env: tuple[str, ...]`, `key: str | None`, `options: dict[str, object]`,
  `models: dict[str, OpencodeModel]`.

**Endpoint table:**

| Method | HTTP | Path | Query | Response |
|---|---|---|---|---|
| `provider.list` | GET | `/provider` | directory, workspace | `OpencodeProviderList` |
| `provider.auth` | GET | `/provider/auth` | directory, workspace | `dict[str, object]` (open map) |

`/provider` 200 body: `{all: [Provider], default: {open map}, connected: [str]}` →
`OpencodeProviderList`: `all: tuple[OpencodeProvider, ...]`, `default: dict[str, object]`,
`connected: tuple[str, ...]`.

- [ ] Step 1: failing test (build a small provider+model payload; assert nested cost/limit).
- [ ] Step 2: run → fail.
- [ ] Step 3: implement nested models with `from_payload` each (keep each `from_payload`
  under complexity 6 — straight field reads).
- [ ] Step 4: implement resource + wire `self.provider`.
- [ ] Step 5: tests + lint/mypy clean.
- [ ] Step 6: commit `feat: provider namespace with typed models`.

---

## Task 11: `file` namespace (`list`, `read`, `status`)

**Models** (`models/file.py`):
- `OpencodeFileNode`: `name: str`, `path: str`, `absolute: str`, `type: str`, `ignored: bool`.
- `OpencodeFileContent`: `type: str`, `text: str` (server `content`), `diff: str | None`,
  `encoding: str | None`, `mime_type: str | None` (server `mimeType`),
  `patch: dict[str, object] | None`.
- `OpencodeFileStatus`: `path: str`, `added: int`, `removed: int`, `status: str`.

**Endpoint table:**

| Method | HTTP | Path | Query (required\*) | Response |
|---|---|---|---|---|
| `file.list` | GET | `/file` | directory, workspace, `path`\* | `tuple[OpencodeFileNode, ...]` |
| `file.read` | GET | `/file/content` | directory, workspace, `path`\* | `OpencodeFileContent` |
| `file.status` | GET | `/file/status` | directory, workspace | `tuple[OpencodeFileStatus, ...]` |

`file.list` / `file.read` take a required `path: str` first positional arg:
```python
def list(self, path: str, *, directory=None, workspace=None) -> ...:
    """List files under *path*."""
    query = build_query(self._transport.defaults, directory=directory,
                        workspace=workspace, extra={'path': path})
    return _parse_files(self._transport.send(_build_files(query)))
```
(`self` + `path` + 2 kw = 4 params ≤ 5 OK.)

- [ ] Steps 1–6: failing test (assert `path` becomes a query param; `content`→`text`) →
  implement → wire `self.file` → tests/lint clean → commit `feat: file namespace`.

---

## Task 12: `find` namespace (`text`, `files`, `symbols`)

**Models** (`models/find.py`):
- `OpencodeMatch` (find.text element): `path: str` (from `path.text`),
  `lines: str` (from `lines.text`), `line_number: int`, `absolute_offset: int`,
  `submatches: tuple[dict[str, object], ...]`.
- `OpencodeSymbol`: `name: str`, `kind: int`, `uri: str` (from `location.uri`),
  `range: OpencodeRange` (from `location.range`).
- `OpencodeRange`: `start_line, start_character, end_line, end_character: int`
  (from `start.line` etc.).

**Endpoint table:**

| Method | HTTP | Path | Required query | Optional query | Response |
|---|---|---|---|---|---|
| `find.text` | GET | `/find` | `pattern` | directory, workspace | `tuple[OpencodeMatch, ...]` |
| `find.files` | GET | `/find/file` | `query` | dirs, type, limit, directory, workspace | `tuple[str, ...]` |
| `find.symbols` | GET | `/find/symbol` | `query` | directory, workspace | `tuple[OpencodeSymbol, ...]` |

`find.files` has 4 optional filters + 2 scope params → exceeds the arg budget. Use an input
dataclass:
```python
@dataclass(frozen=True, slots=True)
class OpencodeFindFilesQuery:
    """Parameters for the find-files endpoint."""

    query: str
    dirs: str | None = None
    type: str | None = None
    limit: int | None = None
```
Method: `files(self, params: OpencodeFindFilesQuery, *, directory=None, workspace=None)`.
(`params` is a forbidden name — call the argument `criteria`.)

- [ ] Steps 1–6: failing tests (find.text nested `path.text`→`path`; find.files passes all
  filters as query) → implement → wire `self.find` → tests/lint clean → commit
  `feat: find namespace`.

---

## Task 13: Session models

**Files:**
- Create: `opencode_server_client/models/session.py`
- Test: `tests/models/test_session.py`

`OpencodeSession` (typed; nested objects typed, freeform kept raw):
- `session_id: str` (server `id`), `slug: str`, `project_id: str` (server `projectID`),
  `directory: str`, `title: str`, `version: str`,
  `parent_id: str | None` (server `parentID`),
  `workspace_id: str | None` (server `workspaceID`),
  `path: str | None`, `agent: str | None`,
  `time: OpencodeSessionTime`, `tokens: OpencodeTokenUsage | None`,
  `cost: float | None`, `share: OpencodeShareInfo | None`,
  `model: OpencodeModelRef | None`, `summary: OpencodeSessionSummary | None`,
  `revert: dict[str, object] | None`, `metadata: dict[str, object] | None`,
  `permission: tuple[dict[str, object], ...]`, `raw: dict[str, object]`.

Nested:
- `OpencodeSessionTime`: `created: int`, `updated: int`, `compacting: int | None`,
  `archived: float | None`.
- `OpencodeTokenUsage`: `input: float`, `output: float`, `reasoning: float`,
  `cache_read: float`, `cache_write: float`.
- `OpencodeShareInfo`: `url: str`.
- `OpencodeModelRef`: `model_id: str` (server `id`), `provider_id: str`, `variant: str | None`.
- `OpencodeSessionSummary`: `additions: float`, `deletions: float`, `files: float`.

Response wrappers:
- `OpencodeSessionResponse(body: OpencodeSession)`
- `OpencodeSessionsResponse(body: tuple[OpencodeSession, ...])`
- `OpencodeSessionStatusResponse(body: dict[str, dict[str, object]])`
- `OpencodeBoolResponse(body: bool)` (shared — for abort/delete/init/summarize; put in
  `models/base.py` and reuse)
- `OpencodeTodosResponse(body: tuple[OpencodeTodo, ...])`,
  `OpencodeTodo`: `content: str`→ field `text`, `status: str`, `priority: str`.
- `OpencodeDiffResponse(body: tuple[OpencodeSnapshotDiff, ...])`,
  `OpencodeSnapshotDiff`: `file: str | None`, `patch: str | None`, `additions: float`,
  `deletions: float`, `status: str | None`.

- [ ] **Step 1: Failing test** building a representative Session payload (from the live
  server — create one to capture the real shape):
```bash
poetry run python -c "import json,urllib.request as u; \
r=u.Request('http://127.0.0.1:8080/session', method='POST', \
data=b'{}', headers={'content-type':'application/json'}); \
print(json.dumps(json.load(u.urlopen(r)), indent=2))"
```
Use the printed shape to assert in the test (id, title, time.created, version).
- [ ] **Step 2: run → fail.**
- [ ] **Step 3: Implement models** (each nested `from_payload` is straight reads).
- [ ] **Step 4: run tests + lint/mypy clean.**
- [ ] **Step 5: Commit** `feat: session models`.

Add to `models/base.py`:
```python
@dataclass(frozen=True, slots=True)
class OpencodeBoolResponse(OpencodeBaseResponse):
    """Response whose body is a single boolean flag."""

    body: bool


def ok_bool(code: int, payload: object) -> OpencodeBoolResponse:
    """Build a boolean response from a payload."""
    return OpencodeBoolResponse(code=code, body=bool(payload))
```

---

## Task 14: Session input dataclasses + `session` resource

**Files:**
- Create: `opencode_server_client/models/session_input.py`
- Create: `opencode_server_client/resources/session.py`
- Test: `tests/resources/test_session.py`

**Input dataclasses** (each with a `to_body() -> dict[str, object]` that drops `None`):
- `OpencodeSessionCreate`: `title, parent_id, agent, workspace_id: str | None`,
  `model: OpencodeModelRefInput | None`, `metadata: dict | None`,
  `permission: list | None`. → POST `/session` body keys: `title`, `parentID`, `agent`,
  `workspaceID`, `model`, `metadata`, `permission`.
- `OpencodeSessionUpdate`: `title: str | None`, `metadata: dict | None`,
  `permission: list | None`, `archived: float | None` (→ body `{title, metadata, permission,
  time: {archived}}`).
- `OpencodeSessionInit`: `model_id: str`, `provider_id: str`, `message_id: str`
  (all required) → body `{modelID, providerID, messageID}`.
- `OpencodeSessionSummarize`: `provider_id: str`, `model_id: str`, `auto: bool | None`.
- `OpencodeSessionFork`: `message_id: str | None` → body `{messageID}`.

A small helper for `to_body` (in `models/_convert.py`):
```python
def compact(pairs: Mapping[str, object]) -> dict[str, object]:
    """Drop keys whose value is None."""
    return {key: found for key, found in pairs.items() if found is not None}
```

**Endpoint table** (all under `/session`; all accept directory/workspace; 200 unless noted):

| Method | HTTP | Path | Input / args | Response |
|---|---|---|---|---|
| `list` | GET | `/session` | — | `OpencodeSessionsResponse` |
| `create` | POST | `/session` | `OpencodeSessionCreate` | `OpencodeSessionResponse` |
| `status` | GET | `/session/status` | — | `OpencodeSessionStatusResponse` |
| `get` | GET | `/session/{id}` | `session_id` | `OpencodeSessionResponse` |
| `update` | PATCH | `/session/{id}` | `session_id`, `OpencodeSessionUpdate` | `OpencodeSessionResponse` |
| `delete` | DELETE | `/session/{id}` | `session_id` | `OpencodeBoolResponse` |
| `children` | GET | `/session/{id}/children` | `session_id` | `OpencodeSessionsResponse` |
| `init` | POST | `/session/{id}/init` | `session_id`, `OpencodeSessionInit` | `OpencodeBoolResponse` |
| `abort` | POST | `/session/{id}/abort` | `session_id` | `OpencodeBoolResponse` |
| `share` | POST | `/session/{id}/share` | `session_id` | `OpencodeSessionResponse` |
| `unshare` | DELETE | `/session/{id}/share` | `session_id` | `OpencodeSessionResponse` |
| `summarize` | POST | `/session/{id}/summarize` | `session_id`, `OpencodeSessionSummarize` | `OpencodeBoolResponse` |
| `fork` | POST | `/session/{id}/fork` | `session_id`, `OpencodeSessionFork` | `OpencodeSessionResponse` |
| `todo` | GET | `/session/{id}/todo` | `session_id` | `OpencodeTodosResponse` |
| `diff` | GET | `/session/{id}/diff` | `session_id`, `message_id: str | None` (query) | `OpencodeDiffResponse` |

Path building: `'/session/{sid}'.format(sid=session_id)` — but f-strings/`.format` with
braces are fine; prefer `'/session/{0}'.format(session_id)` to avoid WPS. Verify no WPS
issues with the chosen style during lint.

Signature budget: methods with an input dataclass = `self` + `session_id` + `body` +
`directory` + `workspace` = 5 (OK, exactly at the limit). `create` has no `session_id`:
`self` + `body` + `directory` + `workspace` = 4.

- [ ] **Step 1: Write failing tests** — at minimum:
  - `create` sends POST `/session` with a JSON body equal to the compacted input;
  - `get` interpolates the id into the path;
  - `delete` returns `OpencodeBoolResponse(body=True)` from a `true` payload;
  - `diff` adds `messageID` to the query when provided;
  - one error case (`get` on 404 → `OpencodeErrorResponse`).
  Example:
```python
def test_session_create_posts_compacted_body():
    seen = {}
    def handler(request):
        seen['method'] = request.method
        seen['path'] = request.url.path
        seen['body'] = json.loads(request.content)
        return httpx.Response(200, json=_session_payload())
    with make_client(handler) as oc:
        resp = oc.session.create(OpencodeSessionCreate(title='demo'))
    assert (seen['method'], seen['path']) == ('POST', '/session')
    assert seen['body'] == {'title': 'demo'}
    assert resp.body.title == 'demo'
```
  (`_session_payload()` is a fixture returning the real shape captured in Task 13.)
- [ ] **Step 2: run → fail.**
- [ ] **Step 3: Implement** input dataclasses, builders/parsers, `SessionResource` +
  `AsyncSessionResource` (15 methods each, following the pattern). Keep each method 3–5
  lines.
- [ ] **Step 4: Wire `self.session` into both clients.**
- [ ] **Step 5: run tests + lint/mypy clean.**
- [ ] **Step 6: Commit** `feat: session namespace`.

---

## Task 15: Message models + `message` resource

**Files:**
- Create: `opencode_server_client/models/message.py`
- Create: `opencode_server_client/resources/message.py`
- Test: `tests/resources/test_message.py`

**Modeling decision (polymorphic union — pragmatic depth for v1):**
- `OpencodeMessage`: common typed fields + `raw`:
  `message_id: str` (server `id`), `session_id: str`, `role: str`,
  `created: int | None` (from `time.created`), `agent: str | None`,
  `provider_id: str | None`, `model_id: str | None`, `cost: float | None`,
  `error: dict[str, object] | None`, `raw: dict[str, object]`.
  (User vs assistant distinguished by `role`; assistant-only fields read from `raw` when
  needed. Full per-role typing is deferred to phase 2 — note this in the docstring.)
- `OpencodePart`: `part_id: str` (server `id`), `session_id: str`, `message_id: str`,
  `type: str`, `raw: dict[str, object]`. (12-way discriminated union kept as typed common
  fields + `raw`; richer part types deferred to phase 2 — note in docstring.)
- `OpencodeMessageBundle`: `message: OpencodeMessage`, `parts: tuple[OpencodePart, ...]`
  (server `{info, parts}` → field `message`, not `info`).

Response wrappers:
- `OpencodeMessageResponse(body: OpencodeMessageBundle)` — for `get`, `prompt`, `command`, `shell`.
- `OpencodeMessagesResponse(body: tuple[OpencodeMessageBundle, ...])` — for `list`.

**Input dataclasses:**
- `OpencodeMessagePrompt`: `parts: list[dict[str, object]]` (required),
  `message_id, agent, system, variant: str | None`,
  `model: OpencodeModelInput | None` (`{providerID, modelID}`), `no_reply: bool | None`,
  `tools: dict | None`, `format: dict | None`. Body keys: `parts`, `messageID`, `model`,
  `agent`, `noReply`, `tools`, `format`, `system`, `variant`.
  `OpencodeModelInput`: `provider_id: str`, `model_id: str` → `{providerID, modelID}`.
- `OpencodeMessageCommand`: `command: str`, `arguments: str` (both required),
  `message_id, agent, model, variant: str | None`. Body keys: `command`, `arguments`,
  `messageID`, `agent`, `model`, `variant`.
- `OpencodeMessageShell`: `agent: str`, `command: str` (required),
  `message_id: str | None`, `model: OpencodeModelInput | None`. Body keys: `agent`,
  `command`, `messageID`, `model`.

**Endpoint table** (all under `/session/{id}`; accept directory/workspace):

| Method | HTTP | Path | Input / args | Response |
|---|---|---|---|---|
| `list` | GET | `/session/{id}/message` | `session_id` (+ optional `limit`,`before` via input) | `OpencodeMessagesResponse` |
| `prompt` | POST | `/session/{id}/message` | `session_id`, `OpencodeMessagePrompt` | `OpencodeMessageResponse` |
| `get` | GET | `/session/{id}/message/{mid}` | `session_id`, `message_id` | `OpencodeMessageResponse` |
| `command` | POST | `/session/{id}/command` | `session_id`, `OpencodeMessageCommand` | `OpencodeMessageResponse` |
| `shell` | POST | `/session/{id}/shell` | `session_id`, `OpencodeMessageShell` | `OpencodeMessageResponse` |

`message.get` budget: `self` + `session_id` + `message_id` + `directory` + `workspace` = 5
(OK). `list` optional `limit`/`before`: bundle into an optional input dataclass
`OpencodeMessageListQuery(limit: int | None, before: str | None)` to stay within budget, or
omit them in v1 (note the omission via `log` in the plan execution — they're rarely needed).
Decision: **omit `limit`/`before` in v1** for `list` (documented limitation); add in phase 2.

- [ ] **Step 1: Failing tests** — `prompt` posts `{parts: [...]}` and parses
  `{info, parts}` into `message`+`parts`; `get` interpolates both ids; one error case.
- [ ] **Step 2: run → fail.**
- [ ] **Step 3: Implement** models (with `from_payload`), input dataclasses, resource.
- [ ] **Step 4: Wire `self.message` into both clients.**
- [ ] **Step 5: run tests + lint/mypy clean.**
- [ ] **Step 6: Commit** `feat: message namespace`.

---

## Task 16: `event` namespace (SSE streaming)

**Files:**
- Create: `opencode_server_client/models/event.py`
- Create: `opencode_server_client/resources/event.py`
- Test: `tests/resources/test_event.py`

`OpencodeEvent`: `type: str`, `properties: dict[str, object]`, `raw: dict[str, object]`.
Built from each SSE `data:` JSON line: `{type, properties}`.

**Streaming design (does not use `code`+`body`):**
- Sync: `subscribe()` returns an `Iterator[OpencodeEvent]`.
- Async: `subscribe()` returns an `AsyncIterator[OpencodeEvent]`.

Implementation reads the stream line by line, parsing lines that start with `data:` as JSON.

```python
# resources/event.py
"""Event stream endpoint (Server-Sent Events)."""
import json
from collections.abc import AsyncIterator, Iterator

from opencode_server_client.models.event import OpencodeEvent
from opencode_server_client.resources._base import _AsyncResource, _SyncResource

_DATA_PREFIX = 'data:'


def _parse_line(line: str) -> OpencodeEvent | None:
    if not line.startswith(_DATA_PREFIX):
        return None
    chunk = line[len(_DATA_PREFIX):].strip()
    if not chunk:
        return None
    try:
        decoded = json.loads(chunk)
    except ValueError:
        return None
    return OpencodeEvent.from_payload(decoded)


class EventResource(_SyncResource):
    """Event stream (sync)."""

    def subscribe(self) -> Iterator[OpencodeEvent]:
        """Yield server events until the stream closes."""
        with self._transport.stream('GET', '/event') as lines:
            for line in lines:
                event = _parse_line(line)
                if event is not None:
                    yield event


class AsyncEventResource(_AsyncResource):
    """Event stream (async)."""

    async def subscribe(self) -> AsyncIterator[OpencodeEvent]:
        """Yield server events until the stream closes."""
        async with self._transport.stream('GET', '/event') as lines:
            async for line in lines:
                event = _parse_line(line)
                if event is not None:
                    yield event
```

This requires adding streaming helpers to the transports:

```python
# add to SyncTransport
    @contextlib.contextmanager
    def stream(self, method: str, path: str) -> Iterator[Iterator[str]]:
        """Open a streaming request, yielding decoded text lines."""
        with self._client.stream(method, path) as response:
            yield response.iter_lines()

# add to AsyncTransport
    @contextlib.asynccontextmanager
    async def stream(self, method: str, path: str) -> AsyncIterator[AsyncIterator[str]]:
        """Open a streaming request, yielding decoded text lines."""
        async with self._client.stream(method, path) as response:
            yield response.aiter_lines()
```

- [ ] **Step 1: Failing test** with a MockTransport handler returning an SSE body:
```python
def test_event_subscribe_yields_parsed_events():
    body = 'data: {"type":"server.connected","properties":{}}\n\n'
    def handler(request):
        return httpx.Response(200, text=body,
                              headers={'content-type': 'text/event-stream'})
    with make_client(handler) as oc:
        events = list(oc.event.subscribe())
    assert events[0].type == 'server.connected'
    assert events[0].properties == {}
```
- [ ] **Step 2: run → fail.**
- [ ] **Step 3: Implement** event model, transport `stream` helpers, resource.
- [ ] **Step 4: Wire `self.event` into both clients.**
- [ ] **Step 5: run tests + lint/mypy clean** (`import contextlib` at top of `_transport`).
- [ ] **Step 6: Commit** `feat: event SSE namespace`.

---

## Task 17: Public exports, README, full sweep

**Files:**
- Modify: `opencode_server_client/__init__.py`, `opencode_server_client/models/__init__.py`
- Modify: `README.md`

- [ ] **Step 1: Re-export models** from `models/__init__.py` (all `Opencode*` response and
  domain dataclasses + input dataclasses) and from the package root, with `__all__` kept
  alphabetised. Add a test that imports the public names:
```python
# tests/test_public_api.py
import opencode_server_client as oc


def test_public_exports_present():
    for name in ('OpencodeClient', 'OpencodeAsyncClient', 'OpencodeClientOptions',
                 'OpencodeHealthResponse', 'OpencodeErrorResponse', 'OpencodeSession',
                 'OpencodeSessionCreate'):
        assert hasattr(oc, name)
```
- [ ] **Step 2: run → fail → add exports → pass.**
- [ ] **Step 3: Update `README.md`** with sync + async usage examples (using `resp.code` /
  `resp.body`, `OpencodeSessionCreate`, context managers). Run
  `poetry run pymarkdown scan README.md` and fix any findings.
- [ ] **Step 4: Full project gate**

Run:
```bash
make all
```
Expected: `✓ All checks have been successfully completed!` (ruff, flake8, mypy, deptry,
codespell, pymarkdown, then pytest — all green).

- [ ] **Step 5: Final live smoke test against the running server**

```bash
poetry run python -c "
from opencode_server_client import OpencodeClient
oc = OpencodeClient('http://127.0.0.1:8080')
print(oc.server.health())
print(oc.agent.list().code, len(oc.agent.list().body))
print(oc.path.get().body.directory)
oc.close()
"
```
Expected: a health response, agent count, and the worktree directory printed without error.

- [ ] **Step 6: Commit (push only when the user asks)**

```bash
git add -A && git commit -m "feat: public exports, README, final sweep"
```

---

## Self-review checklist (completed during planning)

- **Spec coverage:** every namespace in spec §4 has a task (server T5, config T7, session
  T13–14, message T15, file T11, find T12, project T8, vcs T9, provider T10, agent/command/
  skill/path/lsp/mcp T6, event T16). Base models/transport/decode/client = T1–T5. ✓
- **Error handling** (spec §7): `build_error` (T1) + `decode` (T3), covered by tests in
  every resource task. ✓
- **Streaming** (spec §8): T16. ✓
- **Client config / options** (spec §9): T5 `OpencodeClientOptions`. ✓
- **Testing with MockTransport** (spec §10): conftest in T5, used throughout. ✓
- **Lint constraints** (spec §11): documented in Conventions; `body` name, 5-arg limit via
  input dataclasses, `HTTPStatus`, no `noqa`. ✓
- **Builtin-shadowing (verified):** method `list` and fields `type`/`id` are fine; only
  function **arguments** named `id`/`type` trigger `A002` — the plan uses `session_id`,
  `message_id`, etc. throughout, so no conflict.
- **Verified lint/type facts:** `frozen+slots` field narrowing passes `mypy --strict`/ruff/
  flake8 (Py3.10); 5-arg limit counts `self`; WPS110 forbids `data`→use `body`; `WPS432`→
  use `HTTPStatus`. All confirmed by probe before writing this plan.
