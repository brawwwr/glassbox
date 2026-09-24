# modelcontextprotocol/python-sdk — last 3 releases



## v2.2.0 — 2026-09-07

`pip install -U mcp`. Docs: https://py.sdk.modelcontextprotocol.io/

A few defaults changed in this release. If you run a server or client on 2.x, skim these first:

## Behaviour changes

**HTTP client redirects are only followed within the endpoint's origin** (#3397)
- `Client("https://...")`, `streamable_http_client` and `sse_client` follow a redirect only if it stays on the same scheme, host and port (or upgrades `http` to `https` on the same host).
- A redirect anywhere else is not followed: the call fails with `MCPError` and the session stays usable (an SSE connect fails with `httpx2.HTTPStatusError`). If that other URL is the server you meant, use it as the endpoint URL.
- The `follow_redirects` setting on an `httpx2.AsyncClient` you pass in is no longer used for MCP requests, so you don't need it for the trailing-slash redirect any more.
- The OAuth providers apply the same rule to their own requests.

**Idle Streamable HTTP sessions now expire (legacy <=2025-11-25 spec(** (#3395)
- A stateful session with nothing in flight for 30 minutes is closed. The client's next request gets a 404 and it has to initialize again.
- Clients that keep the GET stream open (the SDK's `Client` does) are not affected. Neither are stateless servers or 2026-07-28 connections.
- A server also holds at most 10 000 sessions at once; beyond that, new sessions get a 503.
- To turn either off: `mcp.run(transport="streamable-http", session_idle_timeout=None, max_sessions=None)` (also on `streamable_http_app()` and `run_streamable_http_async()`).

**The OAuth client checks the authorization server's `issuer` on the legacy path too** (#3398)
- For servers without protected resource metadata, authorization server metadata whose `issuer` isn't the server's own origin is now rejected with `OAuthFlowError: Authorization server metadata issuer mismatch`. The protected-resource-metadata path has done this since 2.0.
- A 403 that isn't an `insufficient_scope` challenge is returned to the caller instead of retried.
- If protected resource metadata can't be fetched because of a 5xx/429, the flow now stops instead of falling back to the legacy endpoints.

**Two new `MCPDeprecationWarning`s** (#3435, #3447)
- `ClientCredentialsOAuthProvider` / `PrivateKeyJWTOAuthProvider` without `issuer=`. Pass your authorization server's issuer URL; 3.0 will require it.
- `AuthSettings` with `resource_server_url` set but `validate_token_resource` unset. Set it to `True` or `False`; 3.0 defaults it to `True`.
- Both keep working as before in 2.x; this mostly matters if your tests turn warnings into errors.

## New

- `AuthSettings.validate_token_resource`: only accept tokens your `TokenVerifier` reports as issued for this server (#3447).
- `issuer=` on `ClientCredentialsOAuthProvider` and `PrivateKeyJWTOAuthProvider` (#3398).
- `session_idle_timeout=` and `max_sessions=` on the Streamable HTTP server entry points (#3395).

## Fixes

- A client `DELETE` frees its session immediately, and a refused opening request no longer leaves a session behind (#2455, #3228, #3300).
- `$ref`s in a tool's `outputSchema` resolve within that schema only; an unresolvable one surfaces as `RuntimeError: Invalid schema for tool ...` (#3394).

## Known gaps

The tasks extension (SEP-2663), DPoP (SEP-1932) and the `jwt-bearer` grant are not implemented yet; https://github.com/modelcontextprotocol/python-sdk/blob/main/ROADMAP.md tracks them.


## What's Changed
* Gate draft PRs too and rewrite the auto-close comment by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3378
* Resolve tool output-schema references within the schema document only by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3394
* Expire idle Streamable HTTP sessions by default and cap concurrent sessions by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3395
* Validate the authorization server metadata issuer on every discovery path by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3398
* Deprecate constructing the pre-provisioned OAuth clients without an issuer by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3435
* Exercise the SEP-2575 stateless probes and SEP-2243 resource/prompt headers in the conformance fixtures by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3442
* Bump the github-actions group with 6 updates by @dependabot[bot] in https://github.com/modelcontextprotocol/python-sdk/pull/3424
* Move the docs-preview workflow scripts out of the YAML into .github/scripts by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3446
* Skip automatic docs previews for fork PRs and drop the setup-uv retry steps by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3445
* Follow redirects only within the MCP endpoint's origin by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3397
* Bump pymdown-extensions from 11.0 to 11.0.1 by @dependabot[bot] in https://github.com/modelcontextprotocol/python-sdk/pull/3285
* Bump the locked versions of eight dev and test dependencies by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3449
* Keep following a relative redirect when the endpoint URL carries userinfo by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3450
* Add AuthSettings.validate_token_resource to check a bearer token's resource by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3447
* docs: stop presenting the in-memory client as the way to connect by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3443
* docs: ask for AI disclosure on comments too by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3459
* docs: refresh translations, and translate pages in parallel by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3458
* Replace RootModel wrappers with type aliases and TypeAdapter validation by @Kludex in https://github.com/modelcontextprotocol/python-sdk/pull/3470


**Full Changelog**: https://github.com/modelcontextprotocol/python-sdk/compare/v2.1.1...v2.2.0


## v1.30.0 — 2026-09-07

Maintenance release of the 1.x line. 2.x is the current line; 1.x docs are at https://py.sdk.modelcontextprotocol.io/v1/.

A few defaults changed in this release. If you run a server or client on 1.x, skim these first:

## Behaviour changes

**HTTP client redirects are only followed within the endpoint's origin** (#3448)
- `streamable_http_client` and `sse_client` follow a redirect only if it stays on the same scheme, host and port (or upgrades `http` to `https` on the same host).
- A redirect anywhere else now fails the request with `httpx.HTTPStatusError`. If that other URL is the server you meant, use it as the endpoint URL.
- The `follow_redirects` setting on an `httpx.AsyncClient` you pass in is no longer used for MCP requests, so you don't need it for the trailing-slash redirect any more.
- `OAuthClientProvider` applies the same rule to its own requests.

**Idle Streamable HTTP sessions now expire** (#3426)
- A stateful session with nothing in flight for 30 minutes is closed. The client's next request gets a 404 and it has to initialize again.
- Clients that keep the GET stream open (the SDK's client does) are not affected.
- A server also holds at most 10 000 sessions at once; beyond that, new sessions get a 503.
- To turn either off: `FastMCP(..., session_idle_timeout=None, max_sessions=None)`.

**The OAuth client checks the authorization server's `issuer`** (#3431)
- Authorization server metadata whose `issuer` doesn't match the server it was fetched for is now rejected with `OAuthFlowError: Authorization server metadata issuer mismatch`.
- Client registrations are now remembered per issuer; if the server later points at a different authorization server, the client registers again.
- If protected resource metadata can't be fetched because of a 5xx/429, the flow now stops instead of falling back to the legacy endpoints.

**Two new `DeprecationWarning`s** (#3431, #3451)
- `ClientCredentialsOAuthProvider` / `PrivateKeyJWTOAuthProvider` without `issuer=`. Pass your authorization server's issuer URL.
- `AuthSettings` with `resource_server_url` set but `validate_token_resource` unset. Set it to `True` or `False`.
- Both keep working as before in 1.x; this mostly matters if your tests turn warnings into errors.

## New

- `AuthSettings.validate_token_resource`: only accept tokens your `TokenVerifier` reports as issued for this server (#3451).
- `issuer=` on `ClientCredentialsOAuthProvider` and `PrivateKeyJWTOAuthProvider` (#3431).
- `session_idle_timeout=` and `max_sessions=` on `FastMCP` (#3426).


## What's Changed
* [v1.x] Resolve tool output-schema references within the schema document only by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3396
* [v1.x] Expire idle Streamable HTTP sessions by default and cap concurrent sessions by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3426
* [v1.x] Validate the authorization server metadata issuer on every discovery path by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3431
* [v1.x] Follow redirects only within the MCP endpoint's origin by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3448
* [v1.x] Add AuthSettings.validate_token_resource to check a bearer token's resource by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3451


**Full Changelog**: https://github.com/modelcontextprotocol/python-sdk/compare/v1.29.1...v1.30.0


## v2.0.1 — 2026-08-26

One off backport of the FastMCP import warning for `2.0.x`, this is due to a lot of people running into this error and making issues on other repos about it. Ideally either pin `mcp<2` or upgrade to 2.

## What's Changed
* [v2.0.x] Point imports of mcp.server.fastmcp at the migration guide by @maxisbey in https://github.com/modelcontextprotocol/python-sdk/pull/3393


**Full Changelog**: https://github.com/modelcontextprotocol/python-sdk/compare/v2.0.0...v2.0.1