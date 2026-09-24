# NEXT — Phase 4, micro lens (updated 24 Sep 2026, night)

Interlude closed. Working model is **gemma4:12b** (agent.py / run_evals.py defaults changed). Comparisons: ornith-1.5:9b,
granite4.1:8b; baseline qwen3:14b. Details: NOTES.md "Interlude".

## Before Phase 4's first run

[PC-PowerShell]
```powershell
ollama stop gemma4:12b
ollama ps                 # empty — the Hugging Face model needs the VRAM
```

[PC-Ubuntu]
```bash
cd ~/glassbox && git pull
uv add transformers accelerate matplotlib
uv pip show transformers | head -2      # tell Claude the version (expect 5.x)
```

## Release notes Claude needs (the Mac has no web) — one script, one push
Claude will write `scratch/fetch_docs.py` to save the TransformerLens 4.0 release notes and the transformers 5 migration
guide into `research/`. Run it, push, pull on the Mac. Then Claude writes `scratch/04_replay.py`.

## Phase 4 plan (unchanged in shape)
1. Attention map with plain transformers on Qwen3-1.7B (or 0.6B): render the Phase 2 prompt with
   `apply_chat_template(tools=TOOLS, enable_thinking=False)`, greedy-generate ~30 tokens, confirm `<tool_call>`, plot
   attention from that token back to the question. PNGs → screenshots/. Then the same for a no-tool question.
2. TransformerLens 4.0: logit lens (P(<tool_call>) per layer), crossover layer. Second weekend.
3. Caveat paragraph: the small model is a proxy for gemma4:12b / qwen3:14b, not the same thing.
