#!/usr/bin/env bash
# Confirm the new lineup: speed/fit bench on the passers + like-for-like temp-0 eval of the 14B baseline.
#
#   [PC-PowerShell] first: update Ollama (tray → check for updates, or reinstall from ollama.com) → 0.34.4+
#   [PC-Ubuntu]     cd ~/glassbox && git pull && bash scratch/06_confirm_lineup.sh
#
# ~10 minutes. Then: git add -A && git commit -m "research: lineup confirmation" && git push

set -uo pipefail
cd ~/glassbox

echo "== Ollama version"; ollama.exe --version | tee evals/lineup-ollama-version.txt

echo; echo "== 1. full 20-question temp-0 run of the baseline (like-for-like with the challengers)"
uv run run_evals.py --model qwen3:14b > evals/lineup-qwen3_14b-t0.log 2>&1; tail -1 evals/lineup-qwen3_14b-t0.log

echo; echo "== 2. speed + fit bench on baseline and the three passers (bench.py, CTX 8192)"
# temporarily point bench.py at the lineup, run, restore
cp bench.py /tmp/bench.py.bak
python3 - << 'PY'
import re
s = open("bench.py").read()
s = re.sub(r"MODELS = \[.*?\]", 'MODELS = ["qwen3:14b", "gemma4:12b", "granite4.1:8b", "lfm2.5:8b"]', s, count=1, flags=re.S)
open("bench.py", "w").write(s)
PY
uv run bench.py > evals/lineup-bench.log 2>&1
cp /tmp/bench.py.bak bench.py
grep -E "PS:|ctx~ 4000 run1" evals/lineup-bench.log

echo; echo "== 3. retry the two that crashed (only if Ollama was updated)"
for m in ornith-1.5:9b nemotron-3.5-lightning; do
  echo "-- $m"
  uv run run_evals.py --model "$m" --ids 1 12 17 > "evals/lineup-retry-${m//[:\/]/_}.log" 2>&1
  tail -1 "evals/lineup-retry-${m//[:\/]/_}.log" | cut -c1-160
done

echo; echo "== 4. pull the Phase-8 judge candidate (small, 6.9 GB)"
ollama.exe pull granite4.1-guardian || echo "   (pull failed — check tag)"

echo; echo "Done. git add -A && git commit -m 'research: lineup confirmation' && git push"
