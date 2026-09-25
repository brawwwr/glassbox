"""
GlassBox — the micro lens as an importable module (Phase 4 code, factored for Phase 5's app).

    from replay import Replay
    rp = Replay(device="cuda")                       # or "cpu": ~10× slower, no VRAM needed
    out = rp.analyse("What are my four VLANs?")      # dict with verdict, figures (PNG paths), numbers

Loads Qwen/Qwen3-1.7B once (plain transformers for attention; TransformerLens 4 bridge for the logit lens is loaded
lazily on first use). Both figures are written to screenshots/live-*.png and returned as paths.
"""

import json
import os
import re
import time
from pathlib import Path

os.environ.setdefault("GLASSBOX_NO_TRACE", "1")

import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from agent import SYSTEM
from tools import TOOLS

REG = ("sink", "system", "tools", "question", "template")
COLORS = {"sink": "#000000", "system": "#4e79a7", "tools": "#f28e2b", "question": "#e15759", "template": "#bab0ab"}


class Replay:
    def __init__(self, model_name="Qwen/Qwen3-1.7B", device=None):
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tok = None; self.model = None; self.bridge = None
        Path("screenshots").mkdir(exist_ok=True)

    # ------------------------------------------------------------------ loading
    def _load_hf(self):
        if self.model is not None:
            return
        from transformers import AutoModelForCausalLM, AutoTokenizer
        t0 = time.time()
        self.tok = AutoTokenizer.from_pretrained(self.model_name)
        try:
            m = AutoModelForCausalLM.from_pretrained(self.model_name, dtype=torch.bfloat16, attn_implementation="eager")
        except TypeError:
            m = AutoModelForCausalLM.from_pretrained(self.model_name, torch_dtype=torch.bfloat16, attn_implementation="eager")
        self.model = m.to(self.device).eval()
        self.load_seconds = round(time.time() - t0, 1)

    def _load_bridge(self):
        if self.bridge is not None:
            return
        from transformer_lens.model_bridge import TransformerBridge
        b = TransformerBridge.boot_transformers(self.model_name, device=self.device)
        try:
            b = b.to(torch.bfloat16)
        except Exception:
            pass
        self.bridge = b

    def unload(self):
        self.model = None; self.bridge = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # ------------------------------------------------------------------ prompt
    def render(self, question):
        messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
        try:
            return self.tok.apply_chat_template(messages, tools=TOOLS, add_generation_prompt=True, tokenize=False, enable_thinking=False)
        except TypeError:
            return self.tok.apply_chat_template(messages, tools=TOOLS, add_generation_prompt=True, tokenize=False)

    def _regions(self, text, offsets, question):
        q0 = text.rfind(question); q_span = (q0, q0 + len(question))
        t_open = text.rfind("<tools>"); t_close = text.find("</tools>", t_open + 7) if t_open >= 0 else -1
        tools_span = (t_open, t_close + 8) if t_open >= 0 and t_close >= 0 else None
        s0 = text.find(SYSTEM[:40]); sys_span = (s0, s0 + len(SYSTEM)) if s0 >= 0 else None
        out = []
        for i, (cs, ce) in enumerate(offsets):
            mid = (cs + ce) / 2
            if i == 0: out.append("sink")
            elif q_span[0] <= mid < q_span[1]: out.append("question")
            elif tools_span and tools_span[0] <= mid < tools_span[1]: out.append("tools")
            elif sys_span and sys_span[0] <= mid < sys_span[1]: out.append("system")
            else: out.append("template")
        return out

    # ------------------------------------------------------------------ analysis
    @torch.no_grad()
    def analyse(self, question, tag="live", max_new=40, do_logit_lens=True):
        self._load_hf()
        text = self.render(question)
        enc = self.tok(text, return_tensors="pt", return_offsets_mapping=True, add_special_tokens=False)
        ids = enc["input_ids"].to(self.device)
        offsets = enc["offset_mapping"][0].tolist()
        n = ids.shape[1]
        regions = self._regions(text, offsets, question)
        counts = {r: regions.count(r) for r in REG}

        gen = self.model.generate(ids, max_new_tokens=max_new, do_sample=False, pad_token_id=self.tok.eos_token_id)
        new_ids = gen[0, n:].tolist()
        new_text = self.tok.decode(new_ids, skip_special_tokens=False)
        tc = self.tok.convert_tokens_to_ids("<tool_call>")
        called = tc in new_ids
        decision_pos = (n + new_ids.index(tc) - 1) if called else (n - 1)
        verdict = f"<tool_call> emitted as generated token #{new_ids.index(tc) + 1}" if called else "no <tool_call> — answered directly"

        out = self.model(gen[:, : decision_pos + 1], output_attentions=True)
        L = len(out.attentions)
        rows = torch.stack([out.attentions[l][0, :, decision_pos, :n].float().cpu() for l in range(L)])
        del out
        masks = {r: torch.tensor([x == r for x in regions]) for r in REG}
        shares = {r: [float(rows[l].mean(0)[masks[r]].sum()) for l in range(L)] for r in REG}
        density = {r: [shares[r][l] / max(counts[r], 1) * 100 for l in range(L)] for r in REG}
        toks = self.tok.convert_ids_to_tokens(ids[0].tolist())
        v = rows[-4:].mean(0).mean(0).clone(); v[0] = 0
        top = [{"pos": i, "token": toks[i].replace("Ġ", " ").replace("Ċ", "\\n"), "region": regions[i], "attn": round(float(v[i]), 4)}
               for i in torch.topk(v, 8).indices.tolist()]

        # figure 1: regions by layer + density
        fig, (ax, ax2) = plt.subplots(2, 1, figsize=(9, 6.2), sharex=True)
        bottom = [0.0] * L
        for r in REG:
            ax.bar(range(L), shares[r], bottom=bottom, color=COLORS[r], label=f"{r} ({counts[r]})")
            bottom = [b + s for b, s in zip(bottom, shares[r])]
        ax.set_ylim(0, 1); ax.set_ylabel("attention share"); ax.legend(fontsize=7, ncol=5, loc="upper left")
        ax.set_title(f"Where the decision looks — {verdict}", fontsize=10)
        for r in ("system", "tools", "question", "template"):
            ax2.plot(range(L), density[r], marker="o", ms=2.5, color=COLORS[r], label=r)
        ax2.set_xlabel("layer"); ax2.set_ylabel("attention per 100 tokens"); ax2.grid(alpha=.3); ax2.legend(fontsize=7, ncol=4)
        fig.tight_layout(); f_attn = f"screenshots/live-{tag}-attention.png"; fig.savefig(f_attn, dpi=100); plt.close(fig)

        result = {"question": question, "verdict": verdict, "generated": new_text, "prompt_tokens": n, "counts": counts,
                  "top_tokens": top, "share_question": round(sum(shares["question"]) / L, 4),
                  "share_tools": round(sum(shares["tools"]) / L, 4), "share_sink": round(sum(shares["sink"]) / L, 4),
                  "attention_png": f_attn, "logitlens_png": None, "crossover_layer": None}

        if do_logit_lens:
            try:
                result.update(self._logit_lens(text, tag))
            except Exception as e:
                result["logit_lens_error"] = f"{type(e).__name__}: {str(e)[:120]}"
        return result

    @torch.no_grad()
    def _logit_lens(self, text, tag):
        self._load_bridge()
        b = self.bridge; tok = b.tokenizer
        ids = tok(text, return_tensors="pt", add_special_tokens=False)["input_ids"].to(self.device)
        hooks = sorted({h for h in b.hook_dict.keys() if "resid_post" in h},
                       key=lambda h: int(re.search(r"\.(\d+)\.", h).group(1)))
        logits, cache = b.run_with_cache(ids, names_filter=lambda nme: nme in hooks)
        wdt = next(b.parameters()).dtype
        tc = tok.convert_tokens_to_ids("<tool_call>")
        final = logits[0, -1].float(); top_id = int(final.argmax())
        alt_id = top_id if top_id != tc else None

        def decode(resid):
            x = resid.to(wdt).unsqueeze(0).unsqueeze(0)
            for attr in ("ln_final", "ln_f", "norm"):
                mod = getattr(b, attr, None)
                if mod is not None: x = mod(x); break
            for attr in ("unembed", "lm_head"):
                mod = getattr(b, attr, None)
                if mod is not None: return mod(x)[0, 0].float()
            raise RuntimeError("no unembed found on bridge")

        p_tool, p_alt, tops = [], [], []
        for h in hooks:
            pr = torch.softmax(decode(cache[h][0, -1]), -1)
            p_tool.append(float(pr[tc])); p_alt.append(float(pr[alt_id]) if alt_id is not None else 0.0)
            tops.append(tok.decode([int(pr.argmax())]))
        L = len(hooks)
        cross = next((i for i in range(L) if p_tool[i] > max(p_alt[i], 0.05)), None)
        alt_name = tok.decode([alt_id]) if alt_id is not None else "(none)"

        fig, ax = plt.subplots(figsize=(9, 3.6))
        ax.plot(range(L), p_tool, marker="o", ms=3, color="#e15759", label="P(<tool_call>)")
        ax.plot(range(L), p_alt, marker="s", ms=2.5, color="#4e79a7", label=f"P({alt_name!r})")
        if cross is not None:
            ax.axvline(cross, color="grey", ls="--", lw=1); ax.text(cross + .2, .9, f"L{cross}", fontsize=8)
        for i in range(0, L, 3):
            ax.text(i, -0.12, tops[i][:6], fontsize=6, ha="center", rotation=45, color="#555", transform=ax.get_xaxis_transform())
        ax.set_ylim(0, 1); ax.set_xlabel("layer (top predicted token shown below)", labelpad=18); ax.set_ylabel("P(next token)")
        ax.set_title(f"Logit lens — decision forms at layer {cross}" if cross is not None else "Logit lens — no tool call", fontsize=10)
        ax.grid(alpha=.3); ax.legend(fontsize=8)
        fig.tight_layout(); f = f"screenshots/live-{tag}-logitlens.png"; fig.savefig(f, dpi=100); plt.close(fig)
        del cache
        return {"logitlens_png": f, "crossover_layer": cross, "p_tool_by_layer": [round(x, 3) for x in p_tool],
                "top_by_layer": tops, "final_next_token": tok.decode([top_id])}


if __name__ == "__main__":
    import sys
    rp = Replay(device=sys.argv[2] if len(sys.argv) > 2 else None)
    r = rp.analyse(sys.argv[1] if len(sys.argv) > 1 else "What are my four VLANs and their subnets?")
    print(json.dumps({k: v for k, v in r.items() if k not in ("p_tool_by_layer", "top_by_layer")}, indent=1))
