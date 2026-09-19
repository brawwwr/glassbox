---
title: GlassBox: the idea
date: 2026-08-28
tags: [glassbox, ai, agents]
---

# GlassBox: the idea

I want to understand agents mechanically, not through a framework. The idea: build one agent by hand
on the home PC and look at it through two lenses.

Macro lens: traces. Which tool was called, how long each step took, how many tokens, what it would cost
on a hosted API. Langfuse self-hosted.

Micro lens: what the network attended to when it decided to call a tool. TransformerLens on a small model.

Rules: build each phase by hand before touching a framework. Every phase ends with something I can show
on screen. Write down measured numbers, not quoted ones.

Models to start with: qwen3:14b as the worker, a MoE 30B and gpt-oss:20b as comparisons.
