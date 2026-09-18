import time
import datetime
import ollama

MODELS = [
    "qwen3:14b",
    "qwen3:30b-a3b",
    "gpt-oss:20b",
    "qwen3.8:27b",
    "muse-glimmer:30b",
    "ornith:9b",
    "ornith:35b",
    "gemma4",            # change to the exact tag you pulled, e.g. "gemma4:12b"
]
CTX = 16384              # try 8192 if spilled models crash
SIZES = [300, 4000, 8000]
OUT = "bench_results.txt"

FILLER = "The quick brown fox jumps over the lazy dog. " * 5 + "\n"
QUESTION = "Which animal jumps over the dog? Answer in about 150 words, describing the scene."

def log(line):
    print(line, flush=True)
    with open(OUT, "a") as f:
        f.write(line + "\n")

def make_prompt(tokens, run):
    body = FILLER * max(1, tokens // 50)
    return f"Run {run}.\n{body}\n{QUESTION}"

def think_arg(model):
    return "low" if model.startswith("gpt-oss") else False

def call(model, prompt):
    msgs = [{"role": "user", "content": prompt}]
    try:
        return ollama.chat(model=model, messages=msgs, options={"num_ctx": CTX}, think=think_arg(model))
    except Exception:
        return ollama.chat(model=model, messages=msgs, options={"num_ctx": CTX})

def unload(model):
    try:
        ollama.generate(model=model, prompt="", keep_alive=0)
    except Exception:
        pass
    time.sleep(3)

def ps_line(model):
    """What `ollama ps` would show for this model: total size, VRAM share, GPU %."""
    try:
        for m in ollama.ps().models:
            if m.model == model or m.name == model:
                total_gb = m.size / 1e9
                vram_gb = (m.size_vram or 0) / 1e9
                pct = 100 * vram_gb / total_gb if total_gb else 0
                return f"{model:18} PS: size={total_gb:5.1f} GB  vram={vram_gb:5.1f} GB  gpu={pct:3.0f}%  ctx={m.context_length}"
        return f"{model:18} PS: not resident"
    except Exception as e:
        return f"{model:18} PS: error {str(e)[:60]}"

log(f"\n===== {datetime.datetime.now():%Y-%m-%d %H:%M}  CTX={CTX}  SIZES={SIZES} =====")
previous = None
for model in MODELS:
    if previous:
        unload(previous)
    first = True
    for size in SIZES:
        for run in range(2):
            print(f"-> {model} ctx~{size} run{run} ...", flush=True)
            try:
                r = call(model, make_prompt(size, run))
            except Exception as e:
                log(f"{model:18} ctx~{size:5} run{run}  CRASH: {str(e)[:90]}")
                break
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
