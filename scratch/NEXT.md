# NEXT — confirm the lineup, then Phase 4 (updated 24 Sep 2026)

Challenger bench done: gemma4:12b 20/20, granite4.1:8b 20/20, lfm2.5:8b 18/20 (fell for the trip decoy),
ornith-1.5:9b and nemotron-3.5-lightning crashed in Ollama's runner. Write-up in NOTES.md ("Interlude").
Proposed: **gemma4:12b** becomes the working model for Phases 5–8. Two confirmations first.

## [PC-PowerShell] — update Ollama to 0.34.4+ (fixes for new architectures likely)
Tray llama → check for updates, or run the installer from ollama.com over the top. Then:
```powershell
ollama --version
```

## [PC-Ubuntu] — ~10 minutes, unattended
```bash
cd ~/glassbox && git pull
bash scratch/06_confirm_lineup.sh
git add -A && git commit -m "research: lineup confirmation" && git push
```
Does: full temp-0 eval of qwen3:14b (like-for-like); bench.py speed/fit on 14b + gemma4:12b + granite4.1:8b + lfm2.5:8b;
retries the two crashed models on the new Ollama; pulls granite4.1-guardian (Phase 8 judge candidate).

## [Mac]
```bash
cd ~/projects/glassbox && git pull
```
Say "pulled". Claude finalises the lineup in NOTES.md and updates agent.py's default model if gemma4:12b holds up.

## Then Phase 4 — micro lens
Pre-run: `ollama stop <model>` [PC-PowerShell]; `uv add transformers accelerate matplotlib` [PC-Ubuntu].
Claude writes scratch/04_replay.py after reading TransformerLens 4.0 / transformers 5 release notes
(fetched to the repo by a scratch script if the Mac still has no web access).
