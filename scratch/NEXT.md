# NEXT — close Phase 5, run Phase 6 (updated 25 Sep 2026)

Phase 5 works (app ran; live logit lens reproduced the Phase 4 result). Notes written. Only the page screenshot is missing.
Phase 6 code is written: notes_server.py (MCP server, SDK 2.x `MCPServer`), mcp_tools.py (client + discovery),
`agent.py --mcp` (swap in discovered tools; fetch_url stays local; trace spans tagged with transport).

## Phase 5 — screenshot (2 minutes)
[Browser on PC] with the app running (`uv run app.py`), run the VLAN question, wait for both pictures, then
Win+Shift+S over the whole page → save as `phase5-one-screen.png` in
`\\wsl.localhost\Ubuntu-24.04\home\administrator\glassbox\screenshots\`. Ctrl+C the app afterwards.

## Phase 6 — MCP (30 minutes)

[PC-Ubuntu, window 1] — install and inspect by hand first:
```bash
cd ~/glassbox && git pull
uv add "mcp[cli]"
uv run mcp dev notes_server.py
```
This starts the MCP Inspector (prints a URL; open it in the PC browser). In the Inspector: list tools → you should see
search_notes and read_note with schemas generated from the type hints and docstrings. Call search_notes with
query "VLAN". Look at the raw JSON-RPC request and response — that is the whole protocol. Screenshot →
`screenshots/phase6-inspector.png`. Ctrl+C.

[PC-Ubuntu, window 1] — serve it for the agent:
```bash
uv run mcp run notes_server.py --transport streamable-http
```
(leave running; it listens on http://localhost:8000/mcp)

[PC-Ubuntu, window 2] — discovery test, then the agent through MCP, then the evals through MCP:
```bash
cd ~/glassbox
uv run mcp_tools.py
uv run agent.py --mcp "What are my four VLANs and their subnets?"
```
Expect a `[mcp] 2 tool(s) discovered ... ms` line, then the usual step log. In Langfuse the tool spans are now
named `search_notes (mcp)` with `mcp_round_trip_ms` in metadata — the transport hop the plan talks about.

Then compare cost of the transport on the 20 questions (same model, temp 0):
```bash
uv run run_evals.py --ids 1 4 11 12 17 20 > evals/phase6-local.log 2>&1; tail -1 evals/phase6-local.log
```
(run_evals doesn't have --mcp yet — Claude adds it next if the agent run works.)

Report back:
```bash
git add -A && git commit -m "phase5 screenshot; phase6 mcp first run" && git push
```
[Mac] `git pull` → "pulled".

If `mcp_tools.py` errors on attribute names (`list_tools`, `structured_content`, …) paste the error — the SDK is
new and the script probes defensively but may need one rename.
