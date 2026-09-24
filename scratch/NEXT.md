# NEXT — ecosystem scan, then Phase 4 (updated 24 Sep 2026)

Claude's session cannot reach the web, so the PC does the looking. One script, one push.

## [PC-Ubuntu] — run the scan (~3 minutes, no keys needed)

```bash
cd ~/glassbox && git pull
uv run scratch/model_scan.py
git add -A && git commit -m "research: ecosystem scan" && git push
```

It writes `research/scan-<date>.md`: newest Ollama models with capability tags and sizes, our current models
re-checked, Hugging Face trending/newest, latest releases of every tool in the plan, and recently active GitHub
repos for agents / interpretability / tracing / MCP / evals. Claude reads it from the Mac clone and writes up
what changed and what (if anything) to swap.

If a section says "rate-limited", just re-run in ten minutes; GitHub search allows 10 requests/minute anonymously.

## Then Phase 4 (unchanged) — see previous NEXT: `ollama stop qwen3:14b`, `uv add transformers accelerate matplotlib`,
Claude writes `scratch/04_replay.py`.
