---
title: uv cheat sheet
date: 2026-06-14
tags: [python, uv, tooling]
---

# uv cheat sheet

Switched from pip+venv to uv. The commands I actually use:

- uv init --python 3.12 : new project with pyproject.toml
- uv add requests : add a dependency (updates pyproject and uv.lock)
- uv add --index name=URL pkg : add from a specific index (PyTorch CUDA wheels)
- uv run script.py : run inside the project env without activating anything
- uv sync : recreate the env from the lockfile on a new machine
- uv python list : see installed interpreters

The lockfile is the point. Commit it.
