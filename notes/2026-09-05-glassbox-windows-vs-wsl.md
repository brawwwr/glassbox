---
title: GlassBox: what runs where
date: 2026-09-05
tags: [glassbox, wsl, ollama]
---

# GlassBox: what runs where

Decision: Ollama runs natively on Windows (simplest GPU path), Python and Docker run in WSL2 Ubuntu.
With networkingMode=mirrored in .wslconfig, localhost means the same thing in both, so Python in WSL
talks to Ollama on Windows at localhost:11434.

Everything data-heavy goes on F:: the WSL disk image, the Ollama models folder, the Docker disk image.
The programs themselves can stay on C:.

Rule of thumb for which window: ollama, wsl, notepad are PowerShell; sudo, apt, uv, curl, git are Ubuntu.
