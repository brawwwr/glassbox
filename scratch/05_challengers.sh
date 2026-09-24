#!/usr/bin/env bash
# Challenger bench — pull the 24-Sep candidates and run them through the existing harness.
#
#   cd ~/glassbox && git pull && bash scratch/05_challengers.sh
#
# Step 1 pulls (~30 GB total; skip any you don't want by editing MODELS).
# Step 2 runs the 20 eval questions on each (temperature 0, traced to Langfuse if it is up).
# Step 3 writes a summary. Commit and push afterwards; Claude reads evals/*.csv and the summary.
#
# Ollama must be running on Windows. Each model swap costs 7–20 s (Phase 1 lesson).

set -uo pipefail
cd ~/glassbox

MODELS=(gemma4:12b lfm2.5:8b granite4.1:8b ornith-1.5:9b nemotron-3.5-lightning)

echo "== pulling"
for m in "${MODELS[@]}"; do
  echo "-- $m"; ollama.exe pull "$m" || echo "   pull failed for $m (check the tag on ollama.com/library)"
done

echo; echo "== evals (20 questions each, temperature 0)"
for m in "${MODELS[@]}"; do
  ollama.exe list | grep -q "^${m%%:*}" || { echo "-- skipping $m (not pulled)"; continue; }
  echo "-- $m"
  uv run run_evals.py --model "$m" > "evals/challenger-${m//[:\/]/_}.log" 2>&1
  tail -1 "evals/challenger-${m//[:\/]/_}.log"
done

echo; echo "== fit check (ollama ps after a 1-line question on each)"
for m in "${MODELS[@]}"; do
  ollama.exe list | grep -q "^${m%%:*}" || continue
  ollama.exe run "$m" "say hi in three words" > /dev/null 2>&1
  echo "-- $m"; ollama.exe ps | tail -n +2
done > evals/challenger-fit.txt 2>&1
cat evals/challenger-fit.txt

echo; echo "== summary of the last $(( ${#MODELS[@]} * 20 )) runs"
uv run scratch/03_trace_summary.py $(( ${#MODELS[@]} * 20 )) > evals/challenger-trace-summary.txt
tail -3 evals/challenger-trace-summary.txt

echo; echo "Done. Now:  git add -A && git commit -m 'research: challenger bench' && git push"
