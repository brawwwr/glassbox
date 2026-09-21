# NEXT — Phase 3 wrap-up, then Phase 4 (updated 21 Sep 2026)

Phase 3 write-up is in NOTES.md. Two small things close the phase.

## [Browser on PC] — the checkpoint screenshot

Langfuse → Traces → click the row "How did my desktop thermals change…" (the 4-step one).
Win+Shift+S, drag over the waterfall (tree + time bars). Save as `phase3-q12-waterfall.png` into
`\\wsl.localhost\Ubuntu-24.04\home\administrator\glassbox\screenshots\` (paste that path into the Save dialog),
or save anywhere on Windows and copy later.

## [PC-Ubuntu] — optional: the same question on two other models, traced (2 minutes)

```bash
cd ~/glassbox && git pull
uv run run_evals.py --ids 12 --model ornith:9b
uv run run_evals.py --ids 12 --model gpt-oss:20b
uv run scratch/03_trace_summary.py 3 > evals/trace_summary_q12_3models.txt
git add -A && git commit -m "phase3: q12 on three models, traced" && git push
```

Then in Langfuse → Traces, filter/search for `q12`: three traces, three models, same question. Compare steps,
latency, tokens, cost in the list view. That is the two-lens comparison slide in miniature.

## Then: PHASE 3 CHECKPOINT commit

```bash
cd ~/glassbox && git add -A && git commit -m "phase3: checkpoint" && git push
```

## Phase 4 preview (next session) — micro lens

Claude writes `scratch/04_replay.py`: loads a small Qwen3 (1.7B or 0.6B) with plain transformers, renders the exact
Phase 2 prompt with `apply_chat_template(tools=TOOLS)`, and plots attention from the `<tool_call>` token back to
the question. Needs `uv add transformers accelerate matplotlib` (torch is already there). ~3 GB model download from
Hugging Face. Ollama's KEEP_ALIVE will free VRAM after 10 min, or `ollama stop qwen3:14b` first.
