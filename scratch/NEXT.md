# NEXT — Phase 3, traces are flowing (updated 21 Sep 2026)

First traced run worked (backups question: search → read → answer, 3,763 tokens). Deprecated call removed.

## [PC-Ubuntu]

```bash
cd ~/glassbox && git pull
uv run run_evals.py --ids 1 11 12 17 20        # five traced questions, tagged q1/q11/q12/q17/q20
```

## [Browser on PC] — read the waterfall

1. Langfuse → Traces. Each row: Input = question, Output = answer, Latency, Usage (tokens), Tags.
2. Click the q12 trace (thermals August vs September). Left: the tree — `glassbox-agent` root, then
   alternating `ollama.chat` (generation) and `search_notes` / `read_note` (spans). Right: details of the
   selected row. Click an `ollama.chat` row: header shows latency and usage (input → output tokens);
   below, Input (the last message sent) and Output (the model's reply or the tool call it asked for).
3. Note for NOTES.md: where does the wall time go? Add up the `ollama.chat` durations vs the tool
   durations for one trace. Expect >95% model, <5% tools.

## [Browser on PC] — model prices (so Cost stops reading 0)

Settings (gear, bottom-left) → Models → New model definition, three times:

| match pattern (regex) | input $/1M tokens | output $/1M tokens | comparable hosted model |
|---|---|---|---|
| `(?i)^qwen3:14b$`    | 0.20 | 0.60 | a hosted 14B-class open model |
| `(?i)^ornith:9b$`    | 0.10 | 0.30 | a hosted 8–9B-class open model |
| `(?i)^gpt-oss:20b$`  | 0.10 | 0.50 | gpt-oss-20b on a hosted provider |

(Prices are illustrative; write down which provider's list price you used in NOTES.md. Only new
traces get costed.)

## [PC-Ubuntu] — compare the two traces of one run

```bash
ls -t runs/*.jsonl | head -1 | xargs cat
```

Every JSONL line (start / model / tool / end) corresponds to one row in the Langfuse tree. Tell Claude
the trace looks right and the mapping is clear → Claude writes the Phase 3 section of NOTES.md.
