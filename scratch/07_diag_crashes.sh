#!/usr/bin/env bash
# Isolate why ornith-1.5:9b and nemotron-3.5-lightning crash in Ollama's runner.
#
#   [PC-PowerShell] update Ollama first (tray → updates, or reinstall) — then:
#   [PC-Ubuntu]     cd ~/glassbox && git pull && bash scratch/07_diag_crashes.sh
#
# For each model, in order of increasing complexity:
#   A. plain `ollama run` with a 3-word prompt (does the model load and generate at all?)
#   B. same via the Python client with tools=TOOLS at num_ctx 8192 (our agent's call shape)
#   C. same but CPU only (num_gpu=0) — if C works and A/B fail, it is the CUDA kernels, not the model
#   D. same but num_ctx 4096 — if D works and B fails, it is a context/KV edge case
# The server log lines around each failure are captured too. Everything goes to evals/diag-<model>.txt.
# ~5 minutes; CPU-only runs are slow but short.

set -uo pipefail
cd ~/glassbox
LOG=/mnt/c/Users/Administrator/AppData/Local/Ollama/server.log

echo "Ollama: $(ollama.exe --version 2>&1)" | tee evals/diag-versions.txt
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null | tee -a evals/diag-versions.txt

for m in ornith-1.5:9b nemotron-3.5-lightning; do
  out="evals/diag-${m//[:\/]/_}.txt"
  echo "== $m  ($(date))" | tee "$out"
  ollama.exe stop "$m" >/dev/null 2>&1

  echo "--- A. plain run" | tee -a "$out"
  timeout 180 ollama.exe run "$m" "say hi in three words" >> "$out" 2>&1 && echo "   A ok" | tee -a "$out" || echo "   A FAILED" | tee -a "$out"
  ollama.exe ps >> "$out" 2>&1

  echo "--- B. python client, tools, num_ctx 8192" | tee -a "$out"
  uv run python - "$m" 8192 -1 << 'PY' >> "$out" 2>&1 && echo "   B ok" | tee -a "$out" || echo "   B FAILED" | tee -a "$out"
import sys, ollama
from tools import TOOLS
m, ctx, ngpu = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
opts = {"num_ctx": ctx, "num_predict": 60}
if ngpu >= 0: opts["num_gpu"] = ngpu
r = ollama.chat(model=m, messages=[{"role": "user", "content": "What are my four VLANs? Use a tool if you need to."}],
                tools=TOOLS, options=opts)
print("reply:", (r.message.content or "")[:200], "| tool_calls:", [c.function.name for c in (r.message.tool_calls or [])])
PY
  ollama.exe stop "$m" >/dev/null 2>&1

  echo "--- C. python client, tools, CPU only (num_gpu=0)" | tee -a "$out"
  uv run python - "$m" 8192 0 << 'PY' >> "$out" 2>&1 && echo "   C ok" | tee -a "$out" || echo "   C FAILED" | tee -a "$out"
import sys, ollama
from tools import TOOLS
m, ctx, ngpu = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
r = ollama.chat(model=m, messages=[{"role": "user", "content": "What are my four VLANs? Use a tool if you need to."}],
                tools=TOOLS, options={"num_ctx": ctx, "num_predict": 60, "num_gpu": ngpu})
print("reply:", (r.message.content or "")[:200], "| tool_calls:", [c.function.name for c in (r.message.tool_calls or [])])
PY
  ollama.exe stop "$m" >/dev/null 2>&1

  echo "--- D. python client, tools, GPU, num_ctx 4096" | tee -a "$out"
  uv run python - "$m" 4096 -1 << 'PY' >> "$out" 2>&1 && echo "   D ok" | tee -a "$out" || echo "   D FAILED" | tee -a "$out"
import sys, ollama
from tools import TOOLS
m, ctx, ngpu = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
r = ollama.chat(model=m, messages=[{"role": "user", "content": "What are my four VLANs? Use a tool if you need to."}],
                tools=TOOLS, options={"num_ctx": ctx, "num_predict": 60})
print("reply:", (r.message.content or "")[:200], "| tool_calls:", [c.function.name for c in (r.message.tool_calls or [])])
PY
  ollama.exe stop "$m" >/dev/null 2>&1

  echo "--- server.log: last 40 lines mentioning error/CUDA/kernel/arch/library" | tee -a "$out"
  grep -i -E "error|cuda|kernel|invalid|library|compute|sm_|arch|runner" "$LOG" | tail -40 >> "$out" 2>&1
  echo "--- model info" | tee -a "$out"
  ollama.exe show "$m" >> "$out" 2>&1
  echo | tee -a "$out"
done

echo "Done → evals/diag-*.txt.  git add -A && git commit -m 'research: crash diagnostics' && git push"
