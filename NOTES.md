# GlassBox lab notebook

## Phase 0 — plumbing (15–17 Sep 2026)

- NVIDIA driver: ...
- WSL: ... (from `wsl --version`)
- Ubuntu 24.04 on F:\WSL, WSL 2. `.wslconfig`: 80 GB / 16 procs / mirrored.
- `free -g` total: 77 GB. `nproc`: 16.
- Ollama: ... (from `ollama.exe --version`), models at F:\ollama\models
- Ollama env: KEEP_ALIVE=10m, CONTEXT_LENGTH=16384, FLASH_ATTENTION=..., KV_CACHE_TYPE=...
- `ollama ps` with qwen3:14b loaded: SIZE ..., PROCESSOR 98–99% GPU, CONTEXT 16384
  → ~1–2% spilled to CPU at 16k context. Measure 8k vs 16k in Phase 1.
- Docker Desktop, image on F:\Docker. `docker info` total memory: ...
- CUDA PyTorch (cu128) in ~/glassbox: `torch.cuda.is_available()` = True, RTX 4070
- `curl localhost:11434/api/tags` from Ubuntu: works (mirrored networking OK)

### Things that bit
- Notepad saved .wslconfig.txt; PowerShell wrote UTF-16. Fixed via Notepad Save As / All Files / UTF-8.
- wsl --install --location ignored on post-reboot re-run; moved with export/import.
- Ollama tray app ignored OLLAMA_MODELS; set Model location in app Settings.
- ollama/wsl = PowerShell; from Ubuntu use .exe.

## Phase 1 — baseline numbers
Qwen3:14b,CTX=16834

qwen3:14b      ctx~  300 run0  in=  338 out=   8  prefill=    920 tok/s  decode=  35.7 tok/s  ttft= 14.0s  total= 14.2s
qwen3:14b      ctx~  300 run1  in=  338 out=   8  prefill=   2311 tok/s  decode=  51.0 tok/s  ttft=  0.1s  total=  0.3s
qwen3:14b      ctx~ 4000 run0  in= 4112 out=   8  prefill=   2352 tok/s  decode=  46.3 tok/s  ttft=  1.8s  total=  2.0s
qwen3:14b      ctx~ 4000 run1  in= 4112 out=   8  prefill=   2434 tok/s  decode=  47.6 tok/s  ttft=  1.7s  total=  2.0s
qwen3:14b      ctx~ 8000 run0  in= 8192 out=   8  prefill=   2124 tok/s  decode=  44.5 tok/s  ttft=  3.9s  total=  4.2s
qwen3:14b      ctx~ 8000 run1  in= 8192 out=   8  prefill=   3835 tok/s  decode=  45.2 tok/s  ttft=  2.1s  total=  2.6s
