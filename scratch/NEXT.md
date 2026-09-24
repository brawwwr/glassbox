# NEXT — Phase 4, first pictures (updated 24 Sep 2026, night)

Release notes read (research/docs/). Key facts: TransformerLens 4.0 removed `HookedTransformer.from_pretrained`;
the new path is `TransformerBridge.boot_transformers("Qwen/Qwen3-1.7B")` + `run_with_cache`. transformers 5.17:
nothing breaking for us (`torch_dtype` → `dtype`). Qwen3-1.7B: 28 layers, 16 heads; its template renders tools
and has `<tool_call>` as a real token. `scratch/04_replay.py` is written against these.

## [PC-PowerShell] — free the GPU
```powershell
ollama ps
ollama stop <whatever is listed>       # e.g. ollama stop gemma4:12b
```

## [PC-Ubuntu] — first run downloads Qwen3-1.7B (~3.4 GB), then ~1 minute
```bash
cd ~/glassbox && git pull
uv run scratch/04_replay.py
uv run scratch/04_replay.py --question "What is 17 times 23?" --tag notool
git add -A && git commit -m "phase4: first attention maps" && git push
```
Each run prints: prompt token count by region (system / tools / question / template), the first ~40 generated
tokens, a verdict ("<tool_call> emitted as generated token #N" or "no <tool_call>"), and the attention share the
decision token gives each region in the last 4 layers. PNGs → screenshots/, JSON → research/.

If the tool-worthy question does NOT produce a <tool_call>, try `--model Qwen/Qwen3-4B` (8 GB, still fits with
Ollama unloaded) — the observation only works if the behaviour happens.

## [Mac]
```bash
cd ~/projects/glassbox && git pull
```
Say "pulled". Claude reads the two PNG pairs and the JSONs and writes the Phase 4 step-1 notes.

## Step 2 (next sitting): TransformerLens 4 logit lens
`uv add transformer_lens` → `TransformerBridge.boot_transformers(...)` → `run_with_cache` → P(<tool_call>) per layer.
