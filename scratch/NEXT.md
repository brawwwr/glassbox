# NEXT — Phase 4 closed; Phase 5 next (updated 24 Sep 2026, late)

Phase 4 checkpoint reached. Write-up in NOTES.md (steps 1, 1b, 2, caveat paragraph, translation table).
Composite figure: screenshots/phase4-checkpoint.png.

## [Mac] — land it
```bash
cd ~/projects/glassbox && git add -A && git commit -m "phase4: checkpoint — notes, composite figure" && git push
```

## Phase 5 preview — one screen (Gradio 6.x)
Goal: a local web page: question box → left column live step log + Langfuse link + cost; right column the Phase 4
pictures for the same prompt (attention-by-region + logit lens) from the 1.7B replay.

Before the first run:
- [PC-Ubuntu] `uv add gradio` (Gradio 6 — Claude has the release notes in research/docs/gradio-releases.md)
- VRAM plan: gemma4:12b (8.4 GB) + Qwen3-1.7B (3.4 GB + attention buffers) will NOT both fit in 12 GB. Sequence per
  request: run the agent via Ollama → `ollama stop gemma4:12b` (or rely on keep_alive=0 for that call) → load the 1.7B
  for the replay. Or keep the 1.7B on CPU (112 GB RAM; ~10× slower but fine for one forward pass). Claude will
  write `app.py` with a `--replay-device` flag so both can be tried.
- Reuse: run_agent() already returns steps/tokens/cost/trace path; 04_replay.py's functions will be factored into
  `replay.py` so the app can import them.

Claude writes app.py + replay.py next session; you pull and `uv run app.py`, then open http://localhost:7860.
