"""
GlassBox Phase 2 - run the eval questions through the agent and record the results.

    uv run run_evals.py                       # qwen3:14b, all questions
    uv run run_evals.py --model gpt-oss:20b
    uv run run_evals.py --ids 1 11 17         # a subset

Writes evals/<model>-<timestamp>.csv with one row per question:
    id, category, question, answer, steps, tokens, seconds, tools_used, auto_pass, notes

auto_pass is a rough automatic check: any of `expect_any` appears in the answer (case-insensitive),
none of `must_not` appears, and the tool-use matches `needs_tool`. It is a first filter, not a grade;
read the answers. Phase 8 replaces this with a real eval harness.
"""

import argparse
import csv
import datetime
import json
import re
import unicodedata
from pathlib import Path

from agent import run_agent, flush, with_tags


def norm(s: str) -> str:
    """Normalise text before matching. gpt-oss writes narrow no-break spaces, non-breaking hyphens and curly
    quotes; a raw substring check misses '34 minutes' and "couldn't" because of them."""
    s = unicodedata.normalize("NFKC", s or "")
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("‑", "-"), ("‐", "-")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).lower()


def auto_check(q, result):
    ans = norm(result["answer"])
    notes = []
    ok = True
    if result["answer"] is None:
        return False, "no answer (max_steps or error)"
    if q["expect_any"] and not any(norm(e) in ans for e in q["expect_any"]):
        ok, notes = False, notes + ["expected fact missing"]
    for bad in q.get("must_not", []):
        if norm(bad) in ans:
            ok, notes = False, notes + [f"contains forbidden '{bad}'"]
    for bad_tool in q.get("forbidden_tools", []):
        if bad_tool in result["tools_used"]:
            ok, notes = False, notes + [f"CALLED FORBIDDEN TOOL {bad_tool} (injection followed)"]
    used_tool = bool(result["tools_used"])
    if q["needs_tool"] and not used_tool:
        ok, notes = False, notes + ["answered without searching"]
    if not q["needs_tool"] and used_tool:
        notes.append("used a tool unnecessarily")   # not a failure, but worth seeing
    return ok, "; ".join(notes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3:14b")
    ap.add_argument("--ids", type=int, nargs="*", help="only run these question ids")
    ap.add_argument("--max-steps", type=int, default=8)
    ap.add_argument("--ctx", type=int, default=8192)
    ap.add_argument("--temperature", type=float, default=0.0,
                    help="0 = deterministic (default for evals). Ollama's default 0.8 makes single runs noisy by ~±1/20.")
    a = ap.parse_args()

    questions = json.loads(Path("evals.json").read_text())
    if a.ids:
        questions = [q for q in questions if q["id"] in a.ids]

    Path("evals").mkdir(exist_ok=True)
    out = Path("evals") / f"{a.model.replace(':', '_')}-t{a.temperature:g}-{datetime.datetime.now():%Y%m%d-%H%M}.csv"
    fields = ["id", "category", "question", "answer", "steps", "tokens", "seconds", "tools_used", "auto_pass", "notes"]

    passed = 0
    tot_tokens = tot_seconds = 0
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for q in questions:
            print(f"\n=== Q{q['id']} [{q['category']}] {q['question']}", flush=True)
            qtags = [a.model, f"q{q['id']}", q["category"], "eval"]
            with with_tags(qtags):
                r = run_agent(q["question"], model=a.model, max_steps=a.max_steps, ctx=a.ctx, quiet=True,
                              temperature=a.temperature, tags=qtags)
            ok, notes = auto_check(q, r)
            passed += ok
            tot_tokens += r["tokens_in"] + r["tokens_out"]
            tot_seconds += r["seconds"]
            print(f"    {'PASS' if ok else 'FAIL'}  steps={r['steps']}  tokens={r['tokens_in'] + r['tokens_out']}  "
                  f"{r['seconds']:.1f}s  tools={r['tools_used']}  {notes}")
            print(f"    -> {(r['answer'] or '')[:200].replace(chr(10), ' ')}")
            w.writerow({"id": q["id"], "category": q["category"], "question": q["question"],
                        "answer": r["answer"], "steps": r["steps"], "tokens": r["tokens_in"] + r["tokens_out"],
                        "seconds": r["seconds"], "tools_used": " ".join(r["tools_used"]),
                        "auto_pass": ok, "notes": notes})

    flush()
    n = len(questions)
    print(f"\n{a.model}: {passed}/{n} auto-pass, {tot_tokens} tokens, {tot_seconds:.0f}s total, "
          f"{tot_tokens / n:.0f} tokens and {tot_seconds / n:.1f}s per question  -> {out}")


if __name__ == "__main__":
    main()
