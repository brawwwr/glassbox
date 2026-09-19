# GlassBox

A glass-box research agent built by hand on a home PC (RTX 4070, 12 GB), to learn how LLM agents
actually work rather than how frameworks present them.

Two lenses on one agent:

- **Macro lens** — Langfuse traces: which tool was called, how long each step took, what it would cost on a hosted API.
- **Micro lens** — TransformerLens on a small model: what the network attended to when it decided to call a tool.

Everything runs locally and free: Ollama on Windows, Python in WSL2, Docker for Langfuse.

## Contents

- `NOTES.md` — the lab notebook. Measured numbers, what they mean, and what went wrong. Start here.
- `bench.py` — Phase 1 benchmark: prefill/decode tok/s and VRAM fit per model, logged to `bench_results.txt`.
- `bench_results.txt` — raw benchmark output, timestamped per run.
- `notes/` — the markdown corpus the agent searches (Phase 2+). `notes_corpus_README.md` lists the decoys and test questions.
- `tools.py`, `agent.py` — Phase 2: three tools and the ~40-line agent loop. `uv run agent.py "your question"`.
- `evals.json`, `run_evals.py` — 20 test questions and a runner that writes `evals/<model>-<ts>.csv`.

## Phases

0. Plumbing — WSL2, CUDA, Ollama, Docker ✔
1. Baseline numbers — bench eight models, find the VRAM cliff ✔
2. Naked agent loop — ~100 lines, no framework ✔ (19/20 on three models; see NOTES.md)
3. Macro lens — Langfuse traces
4. Micro lens — TransformerLens attention and logit lens
5. One screen — Gradio page showing both lenses
6. MCP — swap an in-process tool for an MCP server
7. Dissect Hermes Agent and OpenClaw
8. Evals and a cost-vs-accuracy comparison

## Rules

Build each phase by hand before reaching for a framework. Every phase ends with a checkpoint you can show on screen.
Numbers in `NOTES.md` were measured on this machine; that is the point.
