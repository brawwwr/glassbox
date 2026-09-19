---
title: Git workflow across two machines
date: 2026-08-01
tags: [git, workflow]
---

# Git workflow across two machines

Rules that stopped me losing work between the desktop and the laptop:

- Pull when you sit down. Push before you stand up.
- Never edit the same file on both machines without a push/pull in between.
- Commit messages: phase or area, then what. "phase1: bench results" not "updates".
- .gitignore before the first commit, not after the first leak. .env, .venv, keys, *.jsonl.
- If git says "ahead by 1", the push did not happen. Check before closing the laptop.
