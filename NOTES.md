# GlassBox lab notebook

One agent, two lenses. Macro lens: Langfuse traces (what tool was called, how long, what it cost).
Micro lens: TransformerLens on a small model (what the network attended to when it decided).
Everything runs locally on the home rig. Numbers below are measured, not quoted.

Rig: i9 (32 threads), 112 GB DDR5, RTX 4070 12 GB, NVMe. Windows 11 + WSL2 Ubuntu 24.04.
Ollama 0.34.1 on Windows; Python in WSL via uv; Docker Desktop (WSL2 backend).

---

## Phase 0 — plumbing (15–17 Sep 2026)

- WSL 2, Ubuntu 24.04, disk image on `F:\WSL\Ubuntu-24.04`. `.wslconfig`: 80 GB / 16 processors / swap 0 / mirrored networking.
  `free -g` → 77 GB total; `nproc` → 16.
- Ollama for Windows. Models at `F:\ollama\models` (set via the app's Settings → Model location).
  Env: `OLLAMA_KEEP_ALIVE=10m`, `OLLAMA_CONTEXT_LENGTH=8192` (was 16384; see Phase 1).
- Docker Desktop, disk image on `F:\Docker`, WSL integration on for Ubuntu-24.04. `docker run hello-world` OK from Ubuntu.
- `~/glassbox`: uv, Python 3.12, git. CUDA PyTorch (cu128): `torch.cuda.is_available()` → True, `NVIDIA GeForce RTX 4070`.
- `curl localhost:11434/api/tags` from Ubuntu lists the models → WSL reaches Windows Ollama over mirrored networking.
- First `ollama ps` with qwen3:14b at 16k context: 98–99% GPU (that run still had a quantized KV cache; see Phase 1).

### Things that bit (Phase 0)
- Notepad saved `.wslconfig.txt`; PowerShell `Out-File` wrote UTF-16. WSL rejects both with a line-1 parse error.
  Fix: Notepad → Save As → All Files → UTF-8, or `printf` from inside Ubuntu.
- `wsl --install --location F:\...` was ignored on the post-reboot re-run. Moved with export / unregister / import.
- Ollama env vars only apply when the **server** restarts. Quitting the tray app leaves the server running.
  Real restart: tray Quit → `Stop-Process -Name "ollama app" -Force` → relaunch → check the `server config` line in
  `%LOCALAPPDATA%\Ollama\server.log`. This explained two separate "the setting was ignored" episodes.
- `ollama`, `wsl`, `notepad` = PowerShell. `sudo`, `apt`, `uv`, `curl`, `git` = Ubuntu. From Ubuntu, Windows programs run as `ollama.exe`, `wsl.exe`.
- Pasting Python into nano mangles indentation (auto-indent). Use `cat > file << 'EOF' … EOF` at the bash prompt.

---

## Phase 1 — baseline numbers (17–19 Sep 2026)

Ollama 0.34.1. Flash attention is automatic in this version (runner logs `Flash Attention enabled`);
`OLLAMA_KV_CACHE_TYPE` is read but **not applied**, so the KV cache is f16.
Each model was loaded onto an empty GPU (previous model unloaded with `keep_alive=0`). Four full runs; numbers agree within ~3%.
Raw data: `bench_results.txt`. Script: `bench.py` (v4: num_predict cap, retry after first-call crash, per-model `ollama ps` snapshot).

### All models, CTX=16384, ~150-word answer

| model            | size    | GPU% | decode tok/s | prefill @8k tok/s | notes |
|------------------|---------|------|--------------|-------------------|-------|
| gemma4:latest    | 3.2 GB  | 100  | 100–108      | 10,500            | fastest; ~4B class |
| ornith:9b        | 5.9 GB  | 100  | 72–77        | 5,700             | fits fully at 16k |
| ornith:35b       | 21.9 GB | 48   | 57–60        | 1,750             | MoE; one runaway to 15,983 tokens |
| gpt-oss:20b      | 14.1 GB | 71   | 54–56        | 6,000             | best of the spilled models |
| qwen3:30b-a3b    | 20.4 GB | 51   | 39–42        | 3,500             | MoE; crashes on first 1–2 calls, then fine |
| qwen3:14b        | 12.2 GB | 87   | 20–27        | 3,000             | spilled — see the cliff |
| qwen3.8:27b      | 18.7 GB | 45   | 5–7          | 780               | dense, half in RAM |
| muse-glimmer:30b | 17.5 GB | 52   | 4.5–5        | 1,200             | dense, half in RAM |

### The VRAM cliff — qwen3:14b, same model, two context windows (19 Sep)

| CTX   | KV cache (f16) | footprint | GPU% | decode @300 | decode @4k |
|-------|----------------|-----------|------|-------------|------------|
| 16384 | 2,560 MiB      | 12.2 GB   | 87   | 26 tok/s    | 23 tok/s   |
| 8192  | 1,280 MiB      | 10.3 GB   | 100  | 46 tok/s    | 42 tok/s   |

KV cache for this model = 160 KB per token (2,560 MiB ÷ 16,384; 40 layers, K and V 1,280 MiB each).
Weights 9.3 GB + 0.16 MB × context tokens must stay under ~11 GB usable → the edge is ~10k tokens.
**Working context for qwen3:14b on this card: 8192.** A 13% spill to CPU cost 43% of decode speed.

### What the numbers say

1. **Decode is memory-bandwidth-bound.** ornith:9b: 5.9 GB × 76 tok/s ≈ 450 GB/s ≈ 89% of the 4070's rated 504 GB/s.
   qwen3:14b when it fits: 9.3 GB × 46 ≈ 430 GB/s. The card is doing what physics allows; a faster GPU helps only via bandwidth.
   Small models fall off this line: gemma4 at 3.2 GB × 105 ≈ 340 GB/s (67%), because per-token overhead dominates once weights are small.
2. **Prefill is compute-bound** and 50–100× faster per token than decode (thousands vs tens of tok/s). Long prompts are cheap; long answers cost.
3. **Dense vs MoE at the same ~50% spill.** Dense 27B/30B → 5–7 tok/s, limited by DDR5 bandwidth (~10 GB per token at ~60 GB/s).
   MoE 30B/35B → 40–58 tok/s, because only a few billion parameters are active per token. Architecture beats parameter count on 12 GB.
4. **Decode slows with context**: qwen3:14b 46 → 42 tok/s from 300 → 4k tokens at CTX 8192 (KV-cache attention cost).
5. **Load time dominates the first request**: 7–28 s (run0 ttft) depending on size, then 0.1–0.2 s once resident. `KEEP_ALIVE` is what hides this.
6. **Silent truncation.** An 8,200-token prompt into an 8,192 window came back as `in=4098`: Ollama dropped the first half with no error.
   Then the prompt cache served the identical remainder at "166,673 tok/s", ttft 0.0 s. Truncation and caching, one line each.

### Reliability findings (matter for Phase 2+)

- **Runaway generation.** ornith:35b once produced 15,983 tokens (282 s) without stopping. Always set `num_predict`.
  The step cap and token counter in the agent loop exist for exactly this.
- **First-call crash.** qwen3:30b-a3b: `CUDA error: an illegal memory access` on its first 1–2 requests after load, every run, then normal.
  Runner bug; retry up to 3× works. Check for an Ollama update.
- **Model-switching crash.** Loading a half-fitting model while another was resident gave the same CUDA error.
  Fix: unload the previous model (`keep_alive=0`) before loading the next.
- **Env vars need a real server restart** (see Phase 0 bites). The `server config` log line is the source of truth.
- qwen3:30b-a3b answers were ~2.5× longer than other models' for the same request → its `think=False` may not be honored. Verify in Phase 2.

### Keep / test-only

Keep: **qwen3:14b** (main model, CTX 8192), **gpt-oss:20b** (different lineage, fastest spilled model),
**ornith:9b or gemma4** (fits fully; tools support decides — TODO check library pages), one MoE reference (qwen3:30b-a3b or ornith:35b).
Test-only, left on disk: qwen3.8:27b, muse-glimmer:30b.

### Translation table (agent concept ↔ Power Automate)

- decode tok/s ↔ how long a flow step waits on an AI action
- VRAM spill ↔ a flow on an under-provisioned connector: works, silently ~2× slower
- `num_predict` / step cap ↔ Do-until iteration limit
- silent prompt truncation ↔ a trigger payload exceeding a connector limit with no error raised
- `KEEP_ALIVE` ↔ connection pooling: first call pays the setup cost, the rest don't

---

## Phase 2 — the naked agent loop
(pending)
