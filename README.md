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
- `app.py`, `replay.py` — Phase 5: the one-screen Gradio app and the micro-lens module it uses.
- `scratch/04_replay.py`, `scratch/04b_logit_lens.py` — Phase 4: attention-by-region from the decision position (plain transformers) and
  a logit lens on TransformerLens 4's `TransformerBridge`. `screenshots/phase4-checkpoint.png` is the composite.
- `scratch/` — hand-off scripts and `NEXT.md`, the live step list. `scratch/03_langfuse_env.sh` sets up Langfuse secrets;
  `scratch/03_trace_summary.py` reports time split and estimated cost from `runs/*.jsonl`.
- `agent.py` traces to a self-hosted Langfuse when `.env` has keys (Phase 3); `--no-trace` to disable.

## Phases

0. Plumbing — WSL2, CUDA, Ollama, Docker ✔
1. Baseline numbers — bench eight models, find the VRAM cliff ✔
2. Naked agent loop — ~100 lines, no framework ✔ (18–20/20 on three models; see NOTES.md)
3. Macro lens — Langfuse traces ✔ (99.9% of wall time is the model; cost is 88% input tokens; see NOTES.md)
   - Interlude (24 Sep): ecosystem scan + challenger bench. Working model is now **gemma4:12b** (20/20 at temp 0, fits with 16k
     headroom); ornith-1.5:9b (caught the prompt injection) and granite4.1:8b (fastest) as comparisons; qwen3:14b stays as baseline.
4. Micro lens — attention + logit lens on Qwen3-1.7B ✔ (decision copies the call format via induction; intent legible from layer 21 of 28, exact token at 26–27; see NOTES.md)
5. One screen — Gradio page showing both lenses ✔ (`uv run app.py` → localhost:7860; agent + Langfuse link left, live attention + logit lens right)
6. MCP — swap an in-process tool for an MCP server
7. Dissect Hermes Agent and OpenClaw
8. Evals and a cost-vs-accuracy comparison

## Rules

Build each phase by hand before reaching for a framework. Every phase ends with a checkpoint you can show on screen.
Numbers in `NOTES.md` were measured on this machine; that is the point.
