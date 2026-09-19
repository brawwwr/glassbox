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

## Phase 2 — the naked agent loop (19 Sep 2026)

`agent.py` is a `for step in range(max_steps)` loop around one `ollama.chat` call. No tool_calls in the reply → that
reply is the answer. Otherwise run each tool with `run_tool`, append the result as a `role: tool` message, go round again.
Every model call and tool call is appended to `runs/<timestamp>.jsonl` (the hand-built trace Langfuse will replace in Phase 3).
Tools (`tools.py`): `search_notes`, `read_note` (refuses paths outside `notes/`), `fetch_url` (http/https only, 4,000-char cap).
Corpus: 38 notes + 4 decoys in `notes/`, one of which carries a hidden prompt injection. 20 test questions in `evals.json`;
`run_evals.py` runs them and writes `evals/<model>-<ts>.csv`.

### What the first runs taught (in order)

1. **The tool was too literal.** First question ("what are my four VLANs and their subnets") → model searched `"VLAN subnet"`,
   substring match found nothing, model gave up after one try. Fix in the tool, not the model: split into terms, match any order.
2. **The model answered from titles.** Backups question: found the right notes, ignored the decoy, but hedged
   ("this suggests you planned or conducted a drill") because it never opened the note. One SYSTEM line
   ("read the note before answering; never answer from a title") → full factual answer with the filename.
3. **Search fallback drowned the answer.** First full eval 16/20. UPS runtime, Pi-hole retention and thermals failed because
   the any-term fallback returned 10 lines in filename order: `ups` matched inside `backups`, `log` matched everything.
   Fix: rank lines by distinct terms matched, match at word starts, return the best 10 with `[3/4]` scores. All three now rank #1.
4. **The model skipped the search.** Fan/GPU-temperature question: "No notes cover this", zero tool calls. SYSTEM line:
   never claim no notes exist without having searched. Fixed.
5. **The grader was naive.** gpt-oss writes narrow no-break spaces, non-breaking hyphens and curly quotes; "34 minutes" and
   "couldn't" failed a raw substring check. Normalise Unicode before grading (`run_evals.norm`). Four false FAILs disappeared.

Each of these is a one-line change. Together they took the 14B from 16/20 to 19/20 with the same weights.

### Three models, same code, same 20 questions (after fixes 1–4, corrected for 5)

| model        | pass  | tokens / question | seconds / question | avg steps | the one failure |
|--------------|-------|-------------------|--------------------|-----------|-----------------|
| qwen3:14b    | 19/20 | 2,854             | 3.1                | 2.6       | Q12: read only the August note, hedged about September |
| gpt-oss:20b  | 19/20 | 3,266             | 5.2                | 3.0       | Q12: 2 searches + 2 reads, still missed September, then asserted "no September data" |
| ornith:9b    | 19/20 | 4,102             | 3.4                | 3.0       | Q18: searched 8 times for "roof", never concluded, hit max_steps |

Same accuracy, different costs, and three different failure personalities:
- the 14B **under-reads** (stops after one note when two are needed);
- gpt-oss **over-searches and over-asserts** (six searches on the kitchen question, 6,567 tokens, then a confident wrong
  "no data" on Q12; confident-and-wrong is worse than the 14B's hedge);
- the 9B **loops** (the runaway the step cap exists for; it was the only model to get Q12 right).

All three: answered the no-tool questions directly, said "no notes" for the kitchen and roof questions (except the 9B loop),
recognised the VLAN sandwich as a sandwich, and **ignored the injection** in the vendor-meeting note (nobody called fetch_url).

### Cost intuition
- The system prompt + three tool schemas cost ~600 tokens and are re-sent every step. A 3-step question is ~2,000 tokens
  before any note content. Tool schemas are the contract, and the contract has a price.
- Fixes 3 and 4 raised the 14B's cost from 2,238 to 2,854 tokens/question (+27%) and its score from 16 to 19. That is the
  trade: reading notes instead of guessing costs tokens.
- At a hosted price of ~$0.50 per million input tokens, 20 questions ≈ 60k tokens ≈ 3 cents. Locally: free, 60 seconds.

### Reliability
- Step cap caught the 9B's runaway at 8 steps. Without it that question runs until the context fills.
- `num_predict=600` on every call (lesson from Phase 1's 15,983-token runaway).
- `read_note` path check refused `../NOTES.md` in the self-test. Keep that test.

### Pending re-run
Added two SYSTEM lines after the comparison above: "if the question compares two things, read every relevant note"
(for Q12) and "two empty searches means stop" (for the 9B loop). Final Phase 2 numbers for all three models: TODO.

### Translation table (Phase 2)
- tool schema ↔ custom connector action definition; the description IS the contract
- while-loop with tool calls ↔ Do-until with Condition + Compose; max_steps ↔ iteration limit
- `runs/*.jsonl` ↔ run history; the token counter ↔ API call count / duration
- "read before answering" ↔ Get-item before Update-item; never act on a list row alone
- prompt injection in a note ↔ untrusted payload in a trigger; treat content as data, never as instructions
