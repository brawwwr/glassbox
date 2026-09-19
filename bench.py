"""
GlassBox Phase 1 - baseline benchmark (v4).

Sends the same prompt to each model at three context sizes and logs prefill
tok/s, decode tok/s, time-to-first-token, total time, and an `ollama ps`
snapshot (size / VRAM / GPU%) per model, to bench_results.txt.

Run from ~/glassbox in Ubuntu:   uv run bench.py
Comment out (put # in front of) any model that is not downloaded yet.

v4 changes: num_predict cap (stops runaway generations), retry after a
first-call CUDA crash, previous model unloaded before the next loads,
ps name matching handles ':latest' tags.
"""

import time
import datetime
import ollama

# ---- what to test ------------------------------------------------------------
MODELS = [
    "qwen3:14b",
    "qwen3:30b-a3b",
    "gpt-oss:20b",
    "ornith:9b",
    "ornith:35b",
   "gemma4",
]
CTX = 8192              # context window we ask Ollama for (try 8192 for the cliff comparison)
SIZES = [300, 4000, 8000]  # approx prompt tokens to test
MAX_OUT = 400            # cap on output tokens; stops runaway generations
OUT = "bench_results.txt"

# ---- the prompt ----------------------------------------------------------------
FILLER = "The quick brown fox jumps over the lazy dog. " * 5 + "\n"   # ~50 tokens
QUESTION = "Which animal jumps over the dog? Answer in about 150 words, describing the scene."


def log(line):
    print(line, flush=True)
    with open(OUT, "a") as f:
        f.write(line + "\n")


def make_prompt(tokens, run):
    body = FILLER * max(1, tokens // 50)
    return f"Run {run}.\n{body}\n{QUESTION}"    # 'Run N' at the front defeats Ollama's prefix cache


def think_arg(model):
    return "low" if model.startswith("gpt-oss") else False   # gpt-oss can't turn thinking off


# ---- one call, tolerant of models that reject the think parameter ---------------
def call(model, prompt):
    msgs = [{"role": "user", "content": prompt}]
    opts = {"num_ctx": CTX, "num_predict": MAX_OUT}
    try:
        return ollama.chat(model=model, messages=msgs, options=opts, think=think_arg(model))
    except Exception:
        return ollama.chat(model=model, messages=msgs, options=opts)


def call_with_retry(model, prompt, tries=3):
    """Some models (qwen3:30b-a3b) crash the runner on their first request; a retry works."""
    for i in range(tries):
        try:
            return call(model, prompt)
        except Exception as e:
            if i == tries - 1:
                raise
            log(f"{model:18} retry after: {str(e)[:60]}")
            time.sleep(5)


def unload(model):
    """Evict a model from VRAM so the next one loads onto a clean GPU."""
    try:
        ollama.generate(model=model, prompt="", keep_alive=0)
    except Exception:
        pass
    time.sleep(3)


def ps_line(model):
    """What `ollama ps` would show for this model: total size, VRAM share, GPU %."""
    try:
        for m in ollama.ps().models:
            name = m.model or m.name or ""
            if name == model or name.startswith(model + ":"):
                total_gb = m.size / 1e9
                vram_gb = (m.size_vram or 0) / 1e9
                pct = 100 * vram_gb / total_gb if total_gb else 0
                return (f"{model:18} PS: {name}  size={total_gb:5.1f} GB  vram={vram_gb:5.1f} GB  "
                        f"gpu={pct:3.0f}%  ctx={m.context_length}")
        return f"{model:18} PS: not resident"
    except Exception as e:
        return f"{model:18} PS: error {str(e)[:60]}"


# ---- main loop ------------------------------------------------------------------
log(f"\n===== {datetime.datetime.now():%Y-%m-%d %H:%M}  CTX={CTX}  SIZES={SIZES}  MAX_OUT={MAX_OUT} =====")
previous = None
for model in MODELS:
    if previous:
        unload(previous)
    first = True
    for size in SIZES:
        for run in range(2):                      # run 0 includes model load; run 1 is the clean number
            print(f"-> {model} ctx~{size} run{run} ...", flush=True)
            try:
                r = call_with_retry(model, make_prompt(size, run))
            except Exception as e:
                log(f"{model:18} ctx~{size:5} run{run}  CRASH: {str(e)[:90]}")
                break                             # skip the rest of this size, move on
            if first:
                log(ps_line(model))
                first = False
            prefill = r.prompt_eval_count / (r.prompt_eval_duration / 1e9)
            decode = r.eval_count / (r.eval_duration / 1e9)
            ttft = (r.load_duration + r.prompt_eval_duration) / 1e9
            total = r.total_duration / 1e9
            log(f"{model:18} ctx~{size:5} run{run}  in={r.prompt_eval_count:5} out={r.eval_count:4}  "
                f"prefill={prefill:7.0f} tok/s  decode={decode:6.1f} tok/s  ttft={ttft:5.1f}s  total={total:5.1f}s")
    previous = model
