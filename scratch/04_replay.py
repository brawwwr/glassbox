"""
GlassBox Phase 4 — micro lens, step 1: where does a small model look when it decides to call a tool?

    uv run scratch/04_replay.py                                        # tool-worthy question (VLANs)
    uv run scratch/04_replay.py --question "What is 17 times 23?" --tag notool
    uv run scratch/04_replay.py --model Qwen/Qwen3-0.6B                # smaller fallback

What it does
  1. Renders EXACTLY the prompt the agent sends (SYSTEM from agent.py + TOOLS from tools.py + the question) with the
     model's own chat template — the same thing Ollama does server-side — so the tool schemas are really in the prompt.
  2. Greedy-generates a few tokens and reports whether the first thing the model does is open a <tool_call>.
  3. Runs one forward pass with attention outputs and reads the attention FROM the decision token (the <tool_call>
     token, or the first generated token if there was none) BACK to every prompt token.
  4. Saves two figures to screenshots/:
       phase4-attn-<tag>-heads.png    last 4 layers, heads × prompt positions, with the prompt regions marked
       phase4-attn-<tag>-regions.png  all layers: share of attention landing on system / tools / question / template
     and a JSON of the region shares to research/phase4-<tag>.json.

Needs the GPU free of Ollama (ollama stop <model>). transformers 5.x, torch, matplotlib. Plain transformers only —
TransformerLens 4 (TransformerBridge) comes in step 2 for the logit lens.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("GLASSBOX_NO_TRACE", "1")     # importing agent must not start Langfuse
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from transformers import AutoModelForCausalLM, AutoTokenizer

from agent import SYSTEM
from tools import TOOLS

ap = argparse.ArgumentParser()
ap.add_argument("--question", default="What are my four VLANs and their subnets?")
ap.add_argument("--model", default="Qwen/Qwen3-1.7B")
ap.add_argument("--tag", default="tool")
ap.add_argument("--max-new", type=int, default=40)
ap.add_argument("--layers", type=int, default=4, help="how many of the last layers to draw head-by-head")
a = ap.parse_args()

Path("screenshots").mkdir(exist_ok=True); Path("research").mkdir(exist_ok=True)
dev = "cuda" if torch.cuda.is_available() else "cpu"
print(f"device={dev}  model={a.model}")

# ---------------------------------------------------------------------------------------------
# 1. render the agent's prompt with the model's chat template
# ---------------------------------------------------------------------------------------------
tok = AutoTokenizer.from_pretrained(a.model)
messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": a.question}]
try:
    text = tok.apply_chat_template(messages, tools=TOOLS, add_generation_prompt=True, tokenize=False, enable_thinking=False)
except TypeError:                                   # template without enable_thinking
    text = tok.apply_chat_template(messages, tools=TOOLS, add_generation_prompt=True, tokenize=False)

assert "<tools>" in text, "tool schemas did not render — check the chat template"
enc = tok(text, return_tensors="pt", return_offsets_mapping=True, add_special_tokens=False)
ids = enc["input_ids"].to(dev)
offsets = enc["offset_mapping"][0].tolist()
n_prompt = ids.shape[1]
print(f"prompt: {len(text):,} chars, {n_prompt} tokens")

# regions of the prompt, by character span → token indices
q_start = text.rfind(a.question); q_span = (q_start, q_start + len(a.question))
# the template mentions "<tools></tools>" in a sentence BEFORE the real block, so take the LAST "<tools>" opener
t_open = text.rfind("<tools>"); t_close = text.find("</tools>", t_open + 7) if t_open >= 0 else -1
tools_span = (t_open, t_close + len("</tools>")) if t_open >= 0 and t_close >= 0 else None
sys_start = text.find(SYSTEM[:40]); sys_span = (sys_start, sys_start + len(SYSTEM)) if sys_start >= 0 else None

REG = ("sink", "system", "tools", "question", "template")

def region_of(i):
    if i == 0: return "sink"                          # first token: transformers park spare attention mass here
    cs, ce = offsets[i]
    mid = (cs + ce) / 2
    if q_span[0] <= mid < q_span[1]: return "question"
    if tools_span and tools_span[0] <= mid < tools_span[1]: return "tools"
    if sys_span and sys_span[0] <= mid < sys_span[1]: return "system"
    return "template"

regions = [region_of(i) for i in range(n_prompt)]
counts = {r: regions.count(r) for r in REG}
print("prompt tokens by region:", counts)
assert counts["tools"] > 50, "tools region looks wrong (expected a few hundred tokens of schema JSON)"

# ---------------------------------------------------------------------------------------------
# 2. load model, generate a few tokens greedily
# ---------------------------------------------------------------------------------------------
t0 = time.time()
try:
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, attn_implementation="eager").to(dev)
except TypeError:                                   # transformers < 5 spelling
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.bfloat16, attn_implementation="eager").to(dev)
model.eval()
print(f"loaded in {time.time() - t0:.1f}s; layers={model.config.num_hidden_layers} heads={model.config.num_attention_heads}")

with torch.no_grad():
    gen = model.generate(ids, max_new_tokens=a.max_new, do_sample=False, pad_token_id=tok.eos_token_id)
new_ids = gen[0, n_prompt:].tolist()
new_text = tok.decode(new_ids, skip_special_tokens=False)
print("\n--- generated ---\n" + new_text + "\n-----------------")

tool_call_id = tok.convert_tokens_to_ids("<tool_call>")
called = tool_call_id in new_ids
# The DECISION is made at the position that PREDICTS the next token, i.e. one before it. If <tool_call> is the
# first generated token, the decision position is the last prompt token — and that is also where the no-tool
# model decides to answer directly, so the two cases are measured at the same place.
if called:
    k = new_ids.index(tool_call_id)                 # index of <tool_call> among generated tokens
    decision_pos = n_prompt + k - 1                 # the token whose next-token prediction was <tool_call>
    verdict = f"<tool_call> emitted as generated token #{k + 1}"
else:
    decision_pos = n_prompt - 1                     # last prompt token: predicted a plain answer instead
    verdict = "no <tool_call> in the first tokens"
print("verdict:", verdict, f"| decision position = token {decision_pos} of {n_prompt} prompt tokens")

# ---------------------------------------------------------------------------------------------
# 3. one forward pass with attentions; attention FROM the decision position BACK to the prompt
# ---------------------------------------------------------------------------------------------
seq = gen[:, : decision_pos + 1]                    # everything up to and including the decision position
with torch.no_grad():
    out = model(seq, output_attentions=True)
attn = out.attentions                               # tuple(len=layers) of [1, heads, q, k]
L = len(attn)
# from the decision token (query row) to every earlier position (keys 0..decision_pos)
rows = torch.stack([attn[l][0, :, decision_pos, :n_prompt].float().cpu() for l in range(L)])   # [L, heads, n_prompt]
del out; torch.cuda.empty_cache()

# region shares per layer (averaged over heads)
reg_names = list(REG)
masks = {r: torch.tensor([x == r for x in regions]) for r in reg_names}
shares = {r: [float(rows[l].mean(0)[masks[r]].sum()) for l in range(L)] for r in reg_names}
gen_share = [float(1 - rows[l].mean(0).sum()) for l in range(L)]    # what went to generated tokens instead
# per-token density: share / tokens — the fair comparison across regions of very different size
density = {r: [shares[r][l] / max(counts[r], 1) * 100 for l in range(L)] for r in reg_names}
summary = {"model": a.model, "question": a.question, "tag": a.tag, "verdict": verdict, "generated": new_text,
           "prompt_tokens": n_prompt, "decision_pos": decision_pos, "region_token_counts": counts, "layers": L,
           "share_by_layer": shares, "share_generated_by_layer": gen_share,
           "mean_share_last4": {r: sum(shares[r][-4:]) / 4 for r in reg_names},
           "mean_share_all": {r: sum(shares[r]) / L for r in reg_names},
           "density_per_100tok_all": {r: sum(density[r]) / L for r in reg_names}}
Path(f"research/phase4-{a.tag}.json").write_text(json.dumps(summary, indent=1))
print("\nattention from the decision position (mean over heads):")
print(f"  {'region':9} {'tokens':>6} {'share last4':>12} {'share all':>10} {'per 100 tok':>12}")
for r in reg_names:
    print(f"  {r:9} {counts[r]:6} {summary['mean_share_last4'][r]:12.3f} {summary['mean_share_all'][r]:10.3f} "
          f"{summary['density_per_100tok_all'][r]:12.3f}")

# ---------------------------------------------------------------------------------------------
# 4. figures
# ---------------------------------------------------------------------------------------------
colors = {"sink": "#000000", "system": "#4e79a7", "tools": "#f28e2b", "question": "#e15759", "template": "#bab0ab"}

fig, axes = plt.subplots(a.layers, 1, figsize=(16, 2.2 * a.layers), sharex=True)
for ax, l in zip(axes, range(L - a.layers, L)):
    ax.imshow(rows[l].numpy(), aspect="auto", cmap="magma", vmin=0, vmax=float(rows[l].quantile(0.995)))
    ax.set_ylabel(f"L{l}\nheads")
    # region band along the bottom
    for i, r in enumerate(regions):
        ax.axvspan(i - 0.5, i + 0.5, ymin=0, ymax=0.06, color=colors[r], lw=0)
axes[-1].set_xlabel("prompt token position   (band: black=sink  blue=system  orange=tools  red=question  grey=template)")
fig.suptitle(f"Attention from the decision position back to the prompt — {a.model}\n{verdict} | Q: {a.question}", fontsize=11)
fig.tight_layout(); f1 = f"screenshots/phase4-attn-{a.tag}-heads.png"; fig.savefig(f1, dpi=110); plt.close(fig)

fig, (ax, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
bottom = [0.0] * L
for r in reg_names:
    ax.bar(range(L), shares[r], bottom=bottom, color=colors[r], label=f"{r} ({counts[r]} tok)")
    bottom = [b + s for b, s in zip(bottom, shares[r])]
ax.bar(range(L), gen_share, bottom=bottom, color="#59a14f", label="generated so far")
ax.set_ylabel("share of attention (mean over heads)"); ax.set_ylim(0, 1)
ax.set_title(f"Where the decision position looks, by layer — {a.model} — {verdict}")
ax.legend(loc="upper left", fontsize=8, ncol=6)
# lower panel: attention per 100 tokens, sink excluded — which region gets looked at HARDEST, size-adjusted
for r in ("system", "tools", "question", "template"):
    ax2.plot(range(L), density[r], marker="o", ms=3, color=colors[r], label=r)
ax2.set_xlabel("layer"); ax2.set_ylabel("attention per 100 tokens of region")
ax2.set_title("Size-adjusted: attention density by region (the 11-token question vs the 300-token system prompt)")
ax2.legend(fontsize=8, ncol=4); ax2.grid(alpha=0.3)
fig.tight_layout(); f2 = f"screenshots/phase4-attn-{a.tag}-regions.png"; fig.savefig(f2, dpi=110); plt.close(fig)

print(f"\nwrote {f1}\n      {f2}\n      research/phase4-{a.tag}.json")
print("commit and push; Claude reads the PNGs from the Mac clone.")
