# NEXT — challenger bench, then Phase 4 (updated 24 Sep 2026)

Ecosystem scan done → `research/assessment-2026-09-24.md`. Decision: keep `qwen3:14b` as baseline; bench five
challengers that fit the 12 GB card and pick the working model for Phases 5–8 on data.

## [PC-Ubuntu] — pull ~30 GB, then ~25 min of evals (walk away)

```bash
cd ~/glassbox && git pull
bash scratch/05_challengers.sh
git add -A && git commit -m "research: challenger bench" && git push
```

Candidates: gemma4:12b, lfm2.5:8b, granite4.1:8b, ornith-1.5:9b, nemotron-3.5-lightning.
If a pull fails, the tag differs — check ollama.com/library/<name> and edit MODELS in the script.

## [Mac]
```bash
cd ~/projects/glassbox && git pull
```
Say "pulled". Claude reads `evals/*t0*.csv`, `evals/challenger-fit.txt`, `evals/challenger-trace-summary.txt`.

## Then Phase 4 — with two cautions from the scan
- TransformerLens **4.0.0** (released 21 Sep) and transformers **5.x**: read release notes before writing code.
- CircuitsVis is unmaintained → matplotlib only.
Pre-run: `ollama stop <model>` in PowerShell; `uv add transformers accelerate matplotlib` in Ubuntu.
