# NEXT — Phase 4 step 2, the logit lens (updated 24 Sep 2026, night)

Step 1 done and written up (NOTES.md Phase 4): the 1.7B makes the same tool-call decision as the 14B on token #1;
attention is dominated by the sink; the question is read 2× harder when answering directly; a few late heads look
at the search_notes schema. Attention alone is a weak "why" — step 2 asks WHERE IN DEPTH the decision forms.

## [PC-Ubuntu] — GPU must be free of Ollama (`ollama stop <model>` in PowerShell if `ollama ps` shows anything)

```bash
cd ~/glassbox && git pull
uv run scratch/04_replay.py                       # re-run: now also prints the top attended TOKENS by name
uv add transformer_lens                           # TransformerLens 4.x
uv run scratch/04b_logit_lens.py                  # tool question
uv run scratch/04b_logit_lens.py --question "What is 17 times 23?" --tag notool
git add -A && git commit -m "phase4: top tokens + logit lens" && git push
```

The logit-lens script discovers TransformerLens 4's residual-stream hook names at runtime. If it prints
"Could not find residual-stream hooks" followed by a list, copy that list into evals/ or paste it — one pattern
change fixes it. Same if `decode_resid` complains: it tries ln_final / ln_f / norm and unembed / lm_head.

Expected output: a table of P(<tool_call>) per layer and a crossover layer; PNG → screenshots/phase4-logitlens-<tag>.png.

## [Mac]
```bash
cd ~/projects/glassbox && git pull
```
Say "pulled". Claude reads the JSONs/PNGs, writes step 2 into NOTES.md, and the Phase 4 caveat paragraph.
