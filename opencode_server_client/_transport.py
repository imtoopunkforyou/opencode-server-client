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
    overrides: dict[str, object] = {
        'directory': directory,
        'workspace': workspace,
    }
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

    def __init__(
        self, client: httpx.Client, defaults: Mapping[str, str],
    ) -> None:
        """Wrap *client* and remember default query params."""
        self._client = client
        self._defaults = defaults

    @property
    def defaults(self) -> Mapping[str, str]:
        """Default query params applied to every request."""
        return self._defaults

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
    """Executes :class:`RequestSpec` via one ``httpx.AsyncClient``."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        defaults: Mapping[str, str],
    ) -> None:
        """Wrap *client* and remember default query params."""
        self._client = client
        self._defaults = defaults

    @property
    def defaults(self) -> Mapping[str, str]:
        """Default query params applied to every request."""
        return self._defaults

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
