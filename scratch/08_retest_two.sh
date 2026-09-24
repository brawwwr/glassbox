#!/usr/bin/env bash
# Retest after diagnosis (Ollama 0.34.4):
#   ornith-1.5:9b            — fixed by the update → full 20-question eval
#   nemotron-3.5-lightning   — GPU kernel bug above ~4k context → eval at 4096, then probe 6144
#
#   [PC-Ubuntu] cd ~/glassbox && git pull && bash scratch/08_retest_two.sh
#   then: git add -A && git commit -m "research: retest ornith-1.5 + nemotron" && git push

set -uo pipefail
cd ~/glassbox

echo "== ornith-1.5:9b — full eval, temp 0, ctx 8192"
uv run run_evals.py --model ornith-1.5:9b > evals/retest-ornith-1.5_9b.log 2>&1; tail -1 evals/retest-ornith-1.5_9b.log
ollama.exe stop ornith-1.5:9b >/dev/null 2>&1

echo; echo "== nemotron-3.5-lightning — ctx 4096 (known good), 4 questions"
uv run run_evals.py --model nemotron-3.5-lightning --ctx 4096 --ids 1 12 17 20 > evals/retest-nemotron-ctx4096.log 2>&1
grep -E "PASS|FAIL|auto-pass" evals/retest-nemotron-ctx4096.log | cut -c1-140
ollama.exe stop nemotron-3.5-lightning >/dev/null 2>&1

echo; echo "== nemotron-3.5-lightning — ctx 6144 probe, 2 questions"
uv run run_evals.py --model nemotron-3.5-lightning --ctx 6144 --ids 1 12 > evals/retest-nemotron-ctx6144.log 2>&1
grep -E "PASS|FAIL|auto-pass|CUDA|Error" evals/retest-nemotron-ctx6144.log | cut -c1-140 | tail -5
ollama.exe stop nemotron-3.5-lightning >/dev/null 2>&1

echo; echo "== if 4096 passed fully: full 20 at 4096"
if grep -q "4/4 auto-pass" evals/retest-nemotron-ctx4096.log; then
  uv run run_evals.py --model nemotron-3.5-lightning --ctx 4096 > evals/retest-nemotron-full-ctx4096.log 2>&1
  tail -1 evals/retest-nemotron-full-ctx4096.log
else
  echo "(skipped — 4096 did not pass all four)"
fi

echo; echo "Done. git add -A && git commit -m 'research: retest ornith-1.5 + nemotron' && git push"
