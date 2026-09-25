# NEXT — Phase 5, one screen (updated 25 Sep 2026)

Written: `replay.py` (Phase 4 as an importable class), `app.py` (Gradio page), small additions to `agent.py`
(step-log callback, Langfuse trace URL in the result).

## [PC-Ubuntu]
```bash
cd ~/glassbox && git pull
uv add gradio
uv run app.py
```
Then open **http://localhost:7860** in a browser on the PC. Type a question, click Run.

What should happen: the step log fills line by line on the left as the agent works; the answer and a stats line
(steps · tokens · seconds · est. cost · Langfuse link) appear; then the log says it is unloading gemma4:12b and
replaying through Qwen3-1.7B (first time: ~10 s load); two pictures appear on the right.

Try three questions: the VLAN one (tool call), "What is 17 times 23?" (no tool), and the backups one (decoy).

If VRAM is tight or the replay errors, restart with:
```bash
uv run app.py --replay-device cpu
```
(replay ~30–60 s on CPU, but nothing gets evicted from the GPU.)

Stop the app with Ctrl+C in the terminal.

## Report back
Screenshot of the page after a run → screenshots/phase5-one-screen.png (Win+Shift+S, save to
\\wsl.localhost\Ubuntu-24.04\home\administrator\glassbox\screenshots\). Then:
```bash
git add -A && git commit -m "phase5: one screen" && git push
```
[Mac] `git pull` → "pulled". Claude writes the Phase 5 notes and checkpoint.

Things that may need a tweak on first run (tell Claude the error text): Gradio 6 component argument names;
the `type="filepath"` on gr.Image; port 7860 already in use (add `--port 7861`).
