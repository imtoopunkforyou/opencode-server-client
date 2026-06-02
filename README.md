# opencode-server-client

Python client for the OpenCode Server REST API.

## Warning

- In development.
- May not work as you expect and may cause errors.
- Currently not published on PyPI.

## Installation

```bash
pip install opencode-server-client
```

## Quick start

### Sync client

```python
from opencode_server_client import OpencodeClient, OpencodeClientOptions

options = OpencodeClientOptions(timeout=10.0)
oc = OpencodeClient("http://127.0.0.1:8080", options=options)

resp = oc.server.health()
if resp.code == 200:
    print(resp.body.version)

oc.close()
```

### Sessions

```python
from opencode_server_client import OpencodeClient, OpencodeSessionCreate

oc = OpencodeClient("http://127.0.0.1:8080")

create_resp = oc.session.create(OpencodeSessionCreate(title="demo"))
if create_resp.code == 200:
    session = create_resp.body
    print(session.session_id, session.title)

sessions_resp = oc.session.list()
if sessions_resp.code == 200:
    for entry in sessions_resp.body:
        print(entry.session_id)

oc.close()
```

### Files

The file namespace is `oc.files` (plural).

```python
from opencode_server_client import OpencodeClient

oc = OpencodeClient("http://127.0.0.1:8080")

resp = oc.files.list()
if resp.code == 200:
    for node in resp.body:
        print(node.path)

oc.close()
```

### Response shape

Every method returns an object with `.code` (HTTP status integer) and `.body`:

- 2xx: `.body` is a typed dataclass (e.g. `OpencodeHealthData`, `OpencodeSession`).
- Non-2xx: the return type is `OpencodeErrorResponse`; `.body` is `OpencodeError`
  with `.name`, `.message`, and `.payload`.

```python
from opencode_server_client import OpencodeClient, OpencodeErrorResponse

oc = OpencodeClient("http://127.0.0.1:8080")
resp = oc.server.health()
if isinstance(resp, OpencodeErrorResponse):
    print("error:", resp.body.name, resp.body.message)
else:
    print("ok:", resp.body.version)
oc.close()
```

### Event stream

```python
from opencode_server_client import OpencodeClient

oc = OpencodeClient("http://127.0.0.1:8080")
for event in oc.event.subscribe():
    print(event.event_type, event.session_id)
oc.close()
```

### Async client

```python
import asyncio
from opencode_server_client import OpencodeAsyncClient


async def main() -> None:
    """Run async example."""
    async with OpencodeAsyncClient("http://127.0.0.1:8080") as oc:
        resp = await oc.session.list()
        if resp.code == 200:
            print(len(resp.body), "sessions")


asyncio.run(main())
```

## API overview

| Namespace | Methods |
| --------- | ------- |
| `oc.server` | `health()` |
| `oc.session` | `list()`, `get()`, `create()`, `update()`, `delete()`, ... |
| `oc.message` | `list()`, `create()` |
| `oc.files` | `list()`, `read()`, `status()` |
| `oc.find` | `matches()`, `files()`, `symbols()` |
| `oc.agent` | `list()` |
| `oc.command` | `list()` |
| `oc.skill` | `list()` |
| `oc.path` | `get()` |
| `oc.lsp` | `status()` |
| `oc.mcp` | `status()` |
| `oc.config` | `get()`, `providers()` |
| `oc.project` | `list()`, `get()` |
| `oc.vcs` | `info()`, `status()`, `diff()` |
| `oc.provider` | `list()`, `auth()` |
| `oc.event` | `subscribe()` |
