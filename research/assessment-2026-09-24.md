# Ecosystem assessment — 24 September 2026

Source: `research/scan-2026-09-24.md` (Ollama library, Hugging Face, GitHub releases and search), read against
the models and tools GlassBox uses today. Everything the plan assumed on 15 Sep has moved at least one version;
several of the plan's tools took a **major** version bump in the last two weeks.

## 1. Models

### Where we stand
| slot | current | status after scan |
|---|---|---|
| working model | `qwen3:14b` (9.3 GB, fits at 8k) | Qwen is now three generations on (3.5 → 3.6 → 3.8), but **none of the newer Qwen lines ship a 14B-class dense model on Ollama**: qwen3.6 is 27B dense / 35B MoE, qwen3.8 is 27B dense (we measured it: spills, 5–7 tok/s). For a 12 GB card `qwen3:14b` is still the best Qwen that fits. **Keep**, as the reproducibility baseline for Phases 1–3. |
| fast, fits fully | `ornith:9b` (5.6 GB, tools) | `ornith-1.5` exists (9b 6.6 GB, 35b 23 GB, 397b). Its library page shows only the `vision` capability tag — **no `tools` tag** — so Ollama may not parse its tool calls. HF: `Ornith-1.5-9B-GGUF` has 5.3M downloads. Test before trusting. |
| different lineage | `gpt-oss:20b` | unchanged; still the fastest of the spilled models. Keep. |
| MoE reference | `qwen3:30b-a3b` / `ornith:35b` | the "30B total / 3B active" class is now crowded: `nemotron-3.5-lightning` (NVIDIA, "built for always-on agents", 23 GB), `laguna-xs-2.1` (33B-A3B, q4 20 GB), `north-mini-code-1.0` (Cohere, 19 GB), `qwen3.6:35b`. All will spill ~50% and decode 40–60 tok/s like our two. One is enough; `nemotron-3.5-lightning` fits the project's theme best. |
| small/fast | `gemma4:latest` (3.2 GB, 105 tok/s) | `gemma4` is in Ollama's **top 10 by popularity** and has tools + thinking. Tags: e2b, e4b, **12b (~7.5 GB)**, 26b, 31b. **`gemma4:12b` fits entirely in 12 GB with room for a 16k context** — the strongest candidate to challenge `qwen3:14b` as the working model. |

### New candidates that fit the card (≤ ~10 GB) — worth a bench + eval run each
| model | size | why |
|---|---|---|
| **`gemma4:12b`** | ~7.5 GB | top-10 model, tools+thinking, 12B class fully resident. The obvious challenger. |
| **`lfm2.5:8b`** | 5.2 GB | Liquid's 8B-A1B, described as "built for fast, reliable tool calling on consumer hardware". Only 1B active → should decode >100 tok/s. Exactly this project's use case. |
| **`granite4.1:8b`** / `granite4.2:8b` | 5.3 GB | IBM, enterprise-oriented, tools, structured JSON. Relevant for a work audience. (4.2's page showed no capability tags — check; description says tool use.) |
| `ornith-1.5:9b` | 6.6 GB | successor to our 9b; verify tool calling works (no `tools` tag). |
| `granite4.1-guardian` | 6.9 GB | not an agent — a **safety/judge model**. Candidate LLM-judge for Phase 8 evals and for scoring injection resistance. |
| experimental: `hf.co/prism-ml/Ternary-Bonsai-2-27B-gguf` | ~7–8 GB at ~2 bits | HF's #1 trending: a 27B at ternary precision that would *fit* a 12 GB card. Whether llama.cpp/Ollama run it well is unknown; if it does, it is a fascinating data point for the VRAM-cliff story (27B quality at 8B footprint?). Try via `ollama run hf.co/prism-ml/Ternary-Bonsai-2-27B-gguf` once; expect rough edges. |

Skip: anything tagged `cloud` (deepseek-v4.1-flash, glm-5.3, kimi-k3, minimax-m3, nemotron-3-ultra) — those are Ollama-hosted, not local; the plan rules out hosted models. Skip `*-abliterated/uncensored` HF variants. `qwen3.8-flash-next` (125B) and `laguna-s-2.1` (118B) are far beyond 12 GB.

### Recommendation
Keep `qwen3:14b` as the fixed baseline so Phases 1–3 remain comparable. Add a **"challengers" bracket** and run the
existing harness on each (`bench.py` for speed/fit, `run_evals.py` for the 20 questions, both traced): `gemma4:12b`,
`lfm2.5:8b`, `granite4.1:8b`, `ornith-1.5:9b`, `nemotron-3.5-lightning`. ~5 minutes per model. If `gemma4:12b` or
`lfm2.5:8b` matches the 14B's 18–20/20 while fitting at 16k, it becomes the working model for Phases 5–8 and the
switch itself is a Phase-8 finding. This is exactly what the eval harness was built for.

## 2. Tools — version changes that affect the remaining phases

| tool | plan assumed | now | impact |
|---|---|---|---|
| Ollama | 0.34.2 (ours) | **0.34.4** (23 Sep) | minor; update, re-check the qwen3:30b-a3b first-call crash |
| Langfuse / Python SDK | 4.45 / 4.15.4 | 4.45.2 / 4.15.6 | none |
| **TransformerLens** | v2/v3 API in my head | **v4.0.0, released 21 Sep 2026** | Phase 4: a major bump three days old. `HookedTransformer.from_pretrained`, `run_with_cache`, hook names may have changed. **Read the v4 release notes before writing the logit-lens code.** Plan's "attention with plain transformers first" ordering is now doubly right. |
| **transformers** | 4.x | **v5.17** | Phase 4: also a major bump. Watch for `torch_dtype` → `dtype`, `attn_implementation`, generation API changes. |
| CircuitsVis | 1.43 | 1.43.3 — **last release Dec 2024** | effectively unmaintained; may not work with TL 4 / Python 3.12. Use matplotlib for heatmaps (already the plan's fallback). |
| nnsight | 0.4 | 0.7.0 (May 2026) | alive; the fallback if TL 4 is rough |
| Arize Phoenix | — | v20.16 | alive; Plan B stands |
| **MCP Python SDK** | 1.x (`FastMCP`) | **v2.2.0** | Phase 6: major bump; check whether `mcp.server.fastmcp.FastMCP` still exists or moved. Inspector is 2.8. |
| **Gradio** | 5.x | **6.28** | Phase 5: major bump; component API mostly stable but check `gr.Plot` / `gr.Textbox` signatures |
| Promptfoo | — | 0.123.1 | alive; Phase 8 fine. `deepeval` (18k★) and Inspect (UK AISI, active) are the alternatives. |
| Hermes Agent / OpenClaw | — | v2026.9.24 / v2026.9.6 | both actively released this month; Phase 7 specimens are current |
| uv | 0.12.15 | 0.12.18 | none |
| llama.cpp | — | v0.5.0 | (Ollama's engine) |

## 3. Repos worth a look (from the search results)
- **`LLM-Interp/CLT-Forge`** — cross-layer transcoder training + attribution-graph visualisation. A step beyond logit lens for Phase 4 stretch goals.
- **`AI-in-Transportation-Lab/awesome-mechanistic-interpretability`** — curated list; use to check TL 4 tutorials.
- **`2akouwu/reverify`** (1.2k★) — "it proposes, deterministic tools decide, every claim checked against ground truth". Directly relevant to our Phase 2 hallucination/decoy tests; compare its approach to our `read_note before answering` rule.
- **`okf-memory/okf-agent-memory`** — git-native persistent memory for agents (BM25 search). Relevant when Phase 7 asks "how is memory built?" in Hermes/OpenClaw.
- **`truefoundry/trueforge`** (6k★) — "the runtime layer that turns an LLM into a working agent". A framework to *read*, not adopt: compare its loop to our 40 lines.
- **`cobusgreyling/loop-engineering`** (11k★) — patterns for agent loops. Same use.
- **`redhat-et/ripwire`** — MCP server for code search; a well-built MCP server to read alongside our Phase 6 notes server.
- **`ornith-ai/Ornith-1.5-*`**, **`XHToken/Spark-X2.5-4B`** ("agentic capabilities in on-device models") — small agentic models; Spark-X2.5-4B has a GGUF and could be a 4B challenger.
- `future-agi/future-agi` — another tracing+evals platform; not needed, but shows the category is converging on the same trace/eval loop we built by hand.
- Ignore the very-high-star novelty repos (`ponytail`, `hypit`) — not relevant.

## 4. What to change in the plan
1. **Insert a "challenger bench" step before Phase 4** (one evening): pull the five candidates, `bench.py` them, `run_evals.py` them traced. Decide the Phase 5–8 working model on data.
2. **Phase 4**: read TransformerLens 4.0 release notes and transformers 5 migration notes first; do the attention map with plain transformers (as planned), then TL. Budget an extra evening for API drift. Drop CircuitsVis; matplotlib only.
3. **Phase 6**: check MCP SDK 2.x for the FastMCP import path before writing the server.
4. **Phase 8**: add `granite4.1-guardian` as a local judge model option; keep Promptfoo as the harness.
5. `agent.py` `PRICES`: add entries for the challengers so cost shows for them too.
