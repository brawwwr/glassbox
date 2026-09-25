"""
GlassBox Phase 5 — one screen. Both lenses for the same question.

    uv add gradio
    uv run app.py                        # replay on GPU (unloads the Ollama model first)
    uv run app.py --replay-device cpu    # keep Ollama's model resident; replay the 1.7B on CPU (~30-60 s)
    → http://localhost:7860

Left: the agent (gemma4:12b via Ollama) — live step log, answer, tokens, est. cost, Langfuse link.
Right: the micro lens — the same prompt replayed through Qwen3-1.7B: where the decision position looks,
and at which layer P(<tool_call>) forms.

VRAM: gemma4:12b (8.4 GB) + Qwen3-1.7B (3.4 GB + attention buffers) do not both fit in 12 GB, so with
--replay-device cuda the app asks Ollama to unload its model (keep_alive=0) before the replay runs. The next
agent call pays a ~10 s reload. On CPU the replay is slower but nothing is evicted.
"""

import argparse
import queue
import threading
import time

import gradio as gr
import ollama

from agent import run_agent, flush, with_tags, PRICES
from replay import Replay

ap = argparse.ArgumentParser()
ap.add_argument("--replay-device", default="cuda", choices=["cuda", "cpu"])
ap.add_argument("--port", type=int, default=7860)
ap.add_argument("--models", default="gemma4:12b,ornith-1.5:9b,granite4.1:8b,qwen3:14b")
args = ap.parse_args()

MODELS = args.models.split(",")
replay = Replay(device=args.replay_device)     # lazy: nothing loads until the first replay


def unload_ollama(model):
    try:
        ollama.generate(model=model, prompt="", keep_alive=0)
    except Exception:
        pass


def run(question, model, do_replay):
    """Generator: yields (log, answer_md, stats_md, attn_png, lens_png) as things happen."""
    if not question.strip():
        yield "type a question", "", "", None, None
        return
    q = queue.Queue(); log_lines = []
    result = {}

    def worker():
        with with_tags([model, "app"]):
            result.update(run_agent(question, model=model, quiet=True, on_event=q.put))
        flush(); q.put(None)

    threading.Thread(target=worker, daemon=True).start()
    while True:
        item = q.get()
        if item is None:
            break
        log_lines.append(item)
        yield "\n".join(log_lines), "", "", None, None

    ans = result.get("answer") or "*(no answer — max steps reached)*"
    trace = f"[open trace in Langfuse]({result['trace_url']})" if result.get("trace_url") else "_(tracing off)_"
    stats = (f"**{model}** · {result.get('steps')} steps · {result.get('tokens_in', 0) + result.get('tokens_out', 0)} tokens "
             f"({result.get('tokens_in', 0)} in / {result.get('tokens_out', 0)} out) · {result.get('seconds')} s · "
             f"est. hosted cost **${result.get('est_cost_usd', 0):.5f}** · tools: {', '.join(result.get('tools_used') or []) or 'none'} · {trace}")
    yield "\n".join(log_lines), ans, stats, None, None

    if not do_replay:
        return
    log_lines.append("\n— micro lens —")
    if args.replay_device == "cuda":
        log_lines.append(f"unloading {model} from VRAM for the replay …"); unload_ollama(model)
        yield "\n".join(log_lines), ans, stats, None, None
    log_lines.append(f"replaying the prompt through {replay.model_name} on {args.replay_device} …")
    yield "\n".join(log_lines), ans, stats, None, None
    t0 = time.time()
    r = replay.analyse(question, tag="live")
    log_lines.append(f"replay done in {time.time() - t0:.1f}s: {r['verdict']}")
    log_lines.append(f"attention (mean over layers): sink {r['share_sink']:.2f} · question {r['share_question']:.3f} · tools {r['share_tools']:.3f}")
    log_lines.append("top attended tokens: " + ", ".join(f"{t['token']!r}@{t['pos']}({t['region']})" for t in r["top_tokens"][:5]))
    if r.get("crossover_layer") is not None:
        log_lines.append(f"logit lens: P(<tool_call>) takes the lead at layer {r['crossover_layer']} of {len(r.get('p_tool_by_layer', []))}")
    elif r.get("logit_lens_error"):
        log_lines.append("logit lens error: " + r["logit_lens_error"])
    yield "\n".join(log_lines), ans, stats, r["attention_png"], r.get("logitlens_png")


with gr.Blocks(title="GlassBox — one agent, two lenses") as demo:
    gr.Markdown("## GlassBox — one agent, two lenses\n"
                "Left: what the agent **did** (Ollama + Langfuse). Right: what a small proxy model **attended to** and **when it decided** "
                "(Qwen3-1.7B replay). Same prompt, both views.")
    with gr.Row():
        question = gr.Textbox(label="Question", value="What are my four VLANs and their subnets?", scale=5)
        model = gr.Dropdown(MODELS, value=MODELS[0], label="agent model", scale=2)
        do_replay = gr.Checkbox(value=True, label="micro lens", scale=1)
        go = gr.Button("Run", variant="primary", scale=1)
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Macro lens — the agent")
            log = gr.Textbox(label="step log", lines=18, max_lines=30, interactive=False)
            answer = gr.Markdown(label="answer")
            stats = gr.Markdown()
        with gr.Column(scale=1):
            gr.Markdown("### Micro lens — the network")
            attn = gr.Image(label="where the decision position looks (by layer)", type="filepath", interactive=False)
            lens = gr.Image(label="logit lens: when the decision forms", type="filepath", interactive=False)
    go.click(run, [question, model, do_replay], [log, answer, stats, attn, lens])
    question.submit(run, [question, model, do_replay], [log, answer, stats, attn, lens])
    gr.Markdown(f"Prices for the cost estimate are illustrative hosted rates ($/1M tokens): "
                + ", ".join(f"{m} {PRICES.get(m, ('?', '?'))}" for m in MODELS))

if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=args.port, show_error=True)
