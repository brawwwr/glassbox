"""
Phase 3 — summarise recent agent runs from runs/*.jsonl: where did the time go, what would it cost.

    uv run scratch/03_trace_summary.py            # last 8 runs
    uv run scratch/03_trace_summary.py 20         # last 20

Uses the same illustrative prices as the Langfuse model definitions ($ per 1M tokens).
Also tries to pull the matching cost from Langfuse's API as a cross-check; if the SDK's API
shape differs, that column just says n/a.
"""

import glob
import json
import os
import sys

PRICES = {  # $ per 1M tokens: (input, output). Same numbers as entered in Langfuse → Settings → Models.
    "qwen3:14b": (0.20, 0.60),
    "ornith:9b": (0.10, 0.30),
    "gpt-oss:20b": (0.10, 0.50),
}

n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
files = sorted(glob.glob("runs/*.jsonl"), key=os.path.getmtime)[-n:]

tot = {"model_s": 0.0, "tool_s": 0.0, "wall_s": 0.0, "tin": 0, "tout": 0, "cost": 0.0}
print(f"{'run':17} {'model':12} {'steps':>5} {'wall s':>7} {'model s':>8} {'tool s':>7} {'model%':>6} {'tok in':>7} {'tok out':>7} {'est $':>8}  question")
for f in files:
    recs = [json.loads(l) for l in open(f)]
    start = next((r for r in recs if r["kind"] == "start"), {})
    end = next((r for r in recs if r["kind"] == "end"), {})
    model = start.get("model", "?")
    model_s = sum(r.get("seconds", 0) for r in recs if r["kind"] == "model")
    tool_s = sum(r.get("seconds", 0) for r in recs if r["kind"] == "tool")
    wall = end.get("seconds", model_s + tool_s)
    tin, tout = end.get("tokens_in", 0), end.get("tokens_out", 0)
    pin, pout = PRICES.get(model, (0, 0))
    cost = tin / 1e6 * pin + tout / 1e6 * pout
    pct = 100 * model_s / wall if wall else 0
    q = (start.get("question") or "")[:45]
    print(f"{os.path.basename(f)[:-6]:17} {model:12} {end.get('steps', '?'):>5} {wall:7.1f} {model_s:8.1f} {tool_s:7.3f} {pct:5.0f}% {tin:7} {tout:7} {cost:8.5f}  {q}")
    for k, v in (("model_s", model_s), ("tool_s", tool_s), ("wall_s", wall), ("tin", tin), ("tout", tout), ("cost", cost)):
        tot[k] += v

if files:
    print("-" * 120)
    pct = 100 * tot["model_s"] / tot["wall_s"] if tot["wall_s"] else 0
    print(f"{'TOTAL':17} {'':12} {'':>5} {tot['wall_s']:7.1f} {tot['model_s']:8.1f} {tot['tool_s']:7.3f} {pct:5.0f}% "
          f"{tot['tin']:7} {tot['tout']:7} {tot['cost']:8.5f}")
    print(f"\nModel time {pct:.1f}% of wall time; tools {100 * tot['tool_s'] / tot['wall_s']:.2f}%; "
          f"the rest is Python/HTTP overhead. Estimated hosted cost for these {len(files)} runs: ${tot['cost']:.4f} "
          f"(${tot['cost'] / len(files):.5f} per question).")

# ---- optional cross-check against Langfuse's own cost figures -----------------------------
try:
    from dotenv import load_dotenv
    load_dotenv()
    from langfuse import get_client
    api = get_client().api
    traces = api.trace.list(limit=n)
    rows = getattr(traces, "data", traces)
    print("\nLangfuse says (most recent traces):")
    for t in rows:
        name = getattr(t, "name", "?")
        cost = getattr(t, "total_cost", getattr(t, "totalCost", None))
        lat = getattr(t, "latency", None)
        print(f"  {name:16} cost={cost}  latency_s={lat}")
except Exception as e:
    print(f"\n(Langfuse API cross-check skipped: {type(e).__name__}: {str(e)[:80]})")
