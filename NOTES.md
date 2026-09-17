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
(bench.py results table goes here)q!



