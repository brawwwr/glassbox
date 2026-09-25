"""
GlassBox Phase 4 — micro lens, step 2: at which LAYER does the decision to call a tool form?  (logit lens)

    uv add transformer_lens
    uv run scratch/04b_logit_lens.py                                       # tool-worthy question
    uv run scratch/04b_logit_lens.py --question "What is 17 times 23?" --tag notool

Idea: the residual stream after every layer can be decoded with the model's own final norm + unembedding, as if the
model stopped there. For each layer L we ask: if the model had to answer NOW, what probability would it put on
`<tool_call>` as the next token, versus the token it actually emits when NOT calling a tool? The layer where
P(<tool_call>) overtakes the alternative is where the decision "forms".

TransformerLens 4.0: HookedTransformer.from_pretrained is gone; TransformerBridge wraps the HF model. Hook names differ
between architectures, so this script DISCOVERS the residual-stream hooks by name pattern and prints what it found —
if the pattern misses, it tells you the candidates instead of crashing.
"""

import argparse
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("GLASSBOX_NO_TRACE", "1")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from agent import SYSTEM
from tools import TOOLS

ap = argparse.ArgumentParser()
ap.add_argument("--question", default="What are my four VLANs and their subnets?")
ap.add_argument("--model", default="Qwen/Qwen3-1.7B")
ap.add_argument("--tag", default="tool")
ap.add_argument("--alt", default=None, help="alternative first token to track (default: the model's own non-tool answer start)")
a = ap.parse_args()
Path("screenshots").mkdir(exist_ok=True); Path("research").mkdir(exist_ok=True)
dev = "cuda" if torch.cuda.is_available() else "cpu"

# ---------------------------------------------------------------------------------------------
# load via TransformerBridge (TL 4)
# ---------------------------------------------------------------------------------------------
try:
    from transformer_lens.model_bridge import TransformerBridge
except ImportError as e:
    sys.exit(f"transformer_lens not installed or too old for TransformerBridge: {e}\n  uv add transformer_lens")

print(f"booting TransformerBridge for {a.model} on {dev} ...")
bridge = TransformerBridge.boot_transformers(a.model, device=dev)
try:
    bridge = bridge.to(torch.bfloat16)
except Exception:
    pass
tok = bridge.tokenizer

messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": a.question}]
try:
    text = tok.apply_chat_template(messages, tools=TOOLS, add_generation_prompt=True, tokenize=False, enable_thinking=False)
except TypeError:
    text = tok.apply_chat_template(messages, tools=TOOLS, add_generation_prompt=True, tokenize=False)
ids = tok(text, return_tensors="pt", add_special_tokens=False)["input_ids"].to(dev)
n = ids.shape[1]
print(f"prompt tokens: {n}")

# ---------------------------------------------------------------------------------------------
# find residual-stream hooks
# ---------------------------------------------------------------------------------------------
all_hooks = []
try:
    all_hooks = list(bridge.hook_dict.keys())
except Exception:
    try:
        all_hooks = [name for name, _ in bridge.named_modules() if "hook" in name]
    except Exception:
        pass

cands = [h for h in all_hooks if "resid_post" in h] or [h for h in all_hooks if "resid" in h and "pre" not in h]
if not cands:
    print("Could not find residual-stream hooks. Hook names containing 'resid' or 'block':")
    for h in all_hooks:
        if "resid" in h or "block" in h:
            print("  ", h)
    sys.exit("edit the pattern in this script to match one of the above")
# sort by layer number embedded in the name
import re
def layer_of(h):
    m = re.search(r"\.(\d+)\.", h); return int(m.group(1)) if m else -1
cands = sorted(set(cands), key=layer_of)
L = len(cands)
print(f"found {L} residual hooks, e.g. {cands[0]} ... {cands[-1]}")

# ---------------------------------------------------------------------------------------------
# run with cache (only the hooks we need), decode each layer's last-position residual
# ---------------------------------------------------------------------------------------------
with torch.no_grad():
    logits, cache = bridge.run_with_cache(ids, names_filter=lambda name: name in cands)

final_logits = logits[0, -1].float()
top_id = int(final_logits.argmax())
tool_id = tok.convert_tokens_to_ids("<tool_call>")
alt_id = tok.convert_tokens_to_ids(a.alt) if a.alt else (top_id if top_id != tool_id else None)
print(f"model's actual next token: {tok.decode([top_id])!r}   P(<tool_call>)={torch.softmax(final_logits, -1)[tool_id]:.3f}")

# the model's own final norm + unembed, found defensively
def _weight_dtype():
    for p in bridge.parameters():
        return p.dtype
    return torch.bfloat16

def decode_resid(resid_last):
    """Apply final norm + unembedding to a [d_model] residual vector → logits (in the model's own dtype)."""
    x = resid_last.to(_weight_dtype()).unsqueeze(0).unsqueeze(0)
    for attr in ("ln_final", "ln_f", "norm"):
        mod = getattr(bridge, attr, None)
        if mod is not None:
            x = mod(x); break
    else:
        hf = getattr(bridge, "original_model", None) or getattr(bridge, "hf_model", None)
        if hf is not None:
            x = hf.model.norm(x)
    for attr in ("unembed", "lm_head"):
        mod = getattr(bridge, attr, None)
        if mod is not None:
            return mod(x)[0, 0].float()
    hf = getattr(bridge, "original_model", None) or getattr(bridge, "hf_model", None)
    return hf.lm_head(x)[0, 0].float()

p_tool, p_alt, top_by_layer = [], [], []
for h in cands:
    resid = cache[h][0, -1]
    lg = decode_resid(resid)
    pr = torch.softmax(lg.float(), -1)
    p_tool.append(float(pr[tool_id]))
    p_alt.append(float(pr[alt_id]) if alt_id is not None else 0.0)
    top_by_layer.append(tok.decode([int(pr.argmax())]))

alt_name = tok.decode([alt_id]) if alt_id is not None else "(none)"
cross = next((i for i in range(L) if p_tool[i] > max(p_alt[i], 0.05)), None)
print("\nlayer  P(<tool_call>)  P(alt)   top token")
for i in range(L):
    print(f"{i:5}  {p_tool[i]:14.3f}  {p_alt[i]:6.3f}   {top_by_layer[i]!r}")
print(f"\nalt token: {alt_name!r}. <tool_call> first leads (and >5%) at layer: {cross}")

summary = {"model": a.model, "question": a.question, "tag": a.tag, "layers": L, "hooks": cands,
           "p_tool_call": p_tool, "p_alt": p_alt, "alt_token": alt_name, "top_by_layer": top_by_layer,
           "crossover_layer": cross, "final_next_token": tok.decode([top_id]), "final_p_tool": float(torch.softmax(final_logits, -1)[tool_id])}
Path(f"research/phase4-logitlens-{a.tag}.json").write_text(json.dumps(summary, indent=1))

fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(range(L), p_tool, marker="o", ms=4, color="#e15759", label="P(<tool_call>)")
ax.plot(range(L), p_alt, marker="s", ms=3, color="#4e79a7", label=f"P({alt_name!r})")
if cross is not None:
    ax.axvline(cross, color="grey", ls="--", lw=1); ax.text(cross + 0.2, 0.9, f"crossover L{cross}", fontsize=9)
ax.set_xlabel("layer (residual stream decoded as if the model stopped here)"); ax.set_ylabel("probability of next token")
ax.set_ylim(0, 1); ax.grid(alpha=0.3); ax.legend()
ax.set_title(f"Logit lens at the decision position — {a.model}\nQ: {a.question}   |   actual next token: {tok.decode([top_id])!r}")
fig.tight_layout(); f = f"screenshots/phase4-logitlens-{a.tag}.png"; fig.savefig(f, dpi=110)
print(f"\nwrote {f} and research/phase4-logitlens-{a.tag}.json")
