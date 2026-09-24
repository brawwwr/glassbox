# NEXT — confirm the lineup, then Phase 4 (updated 24 Sep 2026, evening)

Crash diagnosis done: ornith-1.5:9b fixed by Ollama 0.34.4 (20/20; only model to flag the injection);
nemotron-3.5-lightning runs at ctx ≤ 6144 but loops. Grader widened. Details in NOTES.md "Interlude".

Proposed lineup: gemma4:12b (working) · ornith-1.5:9b (security-aware comparison) · granite4.1:8b (fast) ·
qwen3:14b (baseline). One confirmation run left.

## [PC-Ubuntu] — ~10 minutes, unattended
```bash
cd ~/glassbox && git pull
bash scratch/06_confirm_lineup.sh
git add -A && git commit -m "research: lineup confirmation" && git push
```
(It runs the 14B's full temp-0 eval, bench.py on 14b/gemma4:12b/granite4.1:8b/lfm2.5:8b, retries — now moot — and
pulls granite4.1-guardian. The retry step will just re-run 3 questions on the two models; harmless.)

## [Mac]
```bash
cd ~/projects/glassbox && git pull
```
Say "pulled". Claude finalises: adds ornith-1.5:9b to the bench list result table, sets agent.py's default model,
updates NOTES.md and the checklist.

## Then Phase 4 — micro lens
Pre-run: `ollama stop gemma4:12b` (or whatever is resident) [PC-PowerShell]; `uv add transformers accelerate matplotlib`
[PC-Ubuntu]. Claude writes scratch/04_replay.py after reading TransformerLens 4.0 / transformers 5 release notes
(fetched to the repo by a scratch script if the Mac still has no web access).
