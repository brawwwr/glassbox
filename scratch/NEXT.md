# NEXT — Phase 3, first trace (updated 21 Sep 2026)

Langfuse is up (SDK 4.15.4 installed). agent.py now traces to Langfuse when .env has the keys.

## [PC-Ubuntu]

```bash
cd ~/glassbox && git pull
uv run agent.py "What are my four VLANs and their subnets?"
```

Expected first line: `[trace] Langfuse tracing ON -> http://localhost:3000`, then the usual step log.
If you see any `[trace] langfuse.<method>(...) failed:` lines, copy them for Claude — that means the
SDK 4.x API renamed something and one line in agent.py needs changing. The agent still completes.

## [Browser on PC]

http://localhost:3000 → project glassbox → **Traces**. You should see one trace named `glassbox-agent`
with the question as input. Click it: a waterfall of `ollama.chat` generations (with token counts) and
`search_notes` / `read_note` spans.

Tell Claude: did the trace appear, does each generation show input/output tokens, and any `[trace]` warnings.

## Then (same session, if the trace looks right)

```bash
uv run run_evals.py --ids 1 11 12 17 20          # five traced questions, quick
```

and compare a run's `runs/<ts>.jsonl` with its Langfuse waterfall — every JSONL line should be a span.
