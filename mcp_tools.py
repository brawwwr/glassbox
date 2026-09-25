"""
GlassBox Phase 6 — discover tools from an MCP server and expose them to the agent loop.

    from mcp_tools import MCPTools
    mt = MCPTools("http://localhost:8000/mcp")
    schemas = mt.ollama_tools()          # list of OpenAI/Ollama-style tool dicts, built from the server's schemas
    text = mt.call("search_notes", {"query": "VLAN"})

The agent is synchronous; the MCP client is async. Each call spins a short event loop — fine for a demo, and it
keeps the loop in agent.py unchanged in shape. Every MCP round trip is timed so Phase 3's tracing can show the
transport hop.

Written against the MCP Python SDK 2.x README (`from mcp import Client`). Attribute names on the returned objects
are probed defensively because the SDK is new.
"""

import asyncio
import json
import time
from contextlib import asynccontextmanager

try:                                    # SDK ≥ 2.x on main: one Client object
    from mcp import Client as _NewClient
    _HAVE_NEW = True
except ImportError:                     # released 1.x / early 2.x: transport + ClientSession
    _HAVE_NEW = False
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client


@asynccontextmanager
async def _session(url):
    """Yield an object with .list_tools() and .call_tool(name, args) on either SDK generation."""
    if _HAVE_NEW:
        async with _NewClient(url) as c:
            yield c
    else:
        async with streamablehttp_client(url) as (read, write, *_):
            async with ClientSession(read, write) as s:
                await s.initialize()
                yield s


def _run(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    return asyncio.run_coroutine_threadsafe(coro, loop).result()


class MCPTools:
    def __init__(self, url="http://localhost:8000/mcp"):
        self.url = url
        self.last_ms = None
        self._tools = None

    # ---- discovery ------------------------------------------------------------------------
    async def _list(self):
        async with _session(self.url) as c:
            res = await c.list_tools()
        return getattr(res, "tools", res)

    def discover(self):
        t0 = time.time()
        raw = _run(self._list())
        self.last_ms = round((time.time() - t0) * 1000)
        self._tools = []
        for t in raw:
            name = getattr(t, "name", None) or t.get("name")
            desc = getattr(t, "description", None) or (t.get("description") if isinstance(t, dict) else "") or ""
            schema = (getattr(t, "inputSchema", None) or getattr(t, "input_schema", None)
                      or (t.get("inputSchema") if isinstance(t, dict) else None) or {"type": "object", "properties": {}})
            self._tools.append({"name": name, "description": desc, "schema": schema})
        return self._tools

    def ollama_tools(self):
        """The server's schemas in the shape ollama.chat(tools=...) expects."""
        if self._tools is None:
            self.discover()
        return [{"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["schema"]}}
                for t in self._tools]

    def names(self):
        if self._tools is None:
            self.discover()
        return [t["name"] for t in self._tools]

    # ---- calling --------------------------------------------------------------------------
    async def _call(self, name, args):
        async with _session(self.url) as c:
            return await c.call_tool(name, args or {})

    def call(self, name, args):
        t0 = time.time()
        try:
            res = _run(self._call(name, args))
        except Exception as e:
            self.last_ms = round((time.time() - t0) * 1000)
            return f"ERROR: MCP call {name} failed: {type(e).__name__}: {str(e)[:160]}"
        self.last_ms = round((time.time() - t0) * 1000)
        # result shapes: structured_content dict, or content blocks with .text
        sc = getattr(res, "structured_content", None) or getattr(res, "structuredContent", None)
        if isinstance(sc, dict) and "result" in sc:
            return str(sc["result"])
        blocks = getattr(res, "content", None) or []
        texts = [getattr(b, "text", None) for b in blocks if getattr(b, "text", None)]
        if texts:
            return "\n".join(texts)
        return json.dumps(sc) if sc is not None else str(res)


if __name__ == "__main__":
    mt = MCPTools()
    print("tools:", mt.names(), f"(discovery {mt.last_ms} ms)")
    print(json.dumps(mt.ollama_tools()[0], indent=1)[:600])
    print(mt.call("search_notes", {"query": "VLAN"})[:300], f"\n({mt.last_ms} ms round trip)")
