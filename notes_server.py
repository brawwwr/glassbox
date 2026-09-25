"""
GlassBox Phase 6 — the notes tools as an MCP server.

    uv add "mcp[cli]"
    uv run mcp dev notes_server.py                              # opens MCP Inspector: call the tools by hand
    uv run mcp run notes_server.py --transport streamable-http  # serve at http://localhost:8000/mcp for the agent

Same two functions as tools.py (search_notes, read_note), reused verbatim. The type hints and docstrings become the
schema — compare what the Inspector shows to the hand-written TOOLS schemas in tools.py (Phase 2). fetch_url stays
in-process in the agent so the toolset is mixed: one MCP transport, one local call.

MCP Python SDK 2.x: `MCPServer` replaces 1.x's `FastMCP`; the decorator API is the same shape.
"""

try:                                   # SDK ≥ 2.x on main
    from mcp.server import MCPServer as _Server
except ImportError:                    # released 1.x / early 2.x
    from mcp.server.fastmcp import FastMCP as _Server

import tools as local_tools

mcp = _Server("glassbox-notes")


@mcp.tool()
def search_notes(query: str) -> str:
    """Search the user's personal markdown notes by keyword (case-insensitive, word order ignored).
    Returns the 10 best-matching lines as '[terms matched/total] path:line: text', best first.
    Use FIRST for any question about what the user wrote, did, decided, bought, measured or planned.
    If nothing matches, try one synonym, then say no notes were found. Never invent file names."""
    return local_tools.search_notes(query)


@mcp.tool()
def read_note(path: str) -> str:
    """Read the full text of one note by the relative path returned from search_notes
    (e.g. '2026-06-10-vlan-plan.md'). Only paths inside the notes folder are allowed."""
    return local_tools.read_note(path)


if __name__ == "__main__":
    mcp.run()
