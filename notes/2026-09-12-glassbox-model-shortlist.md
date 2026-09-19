---
title: GlassBox: model shortlist and why
date: 2026-09-12
tags: [glassbox, models]
---

# GlassBox: model shortlist and why

Shortlist for the 12 GB card.

- qwen3:14b: the working model. Good tool calling, fits at 4-bit with a moderate context.
- qwen3:30b-a3b: mixture of experts, 3B active. Will spill to RAM but should still be fast because so little
  is active per token. This is the "why a 30B can be fast" comparison.
- gpt-oss:20b: different training lineage, strong reasoning. Third data point so patterns are not one vendor's quirk.
- A small model (0.6B to 1.7B) for TransformerLens. Not an agent; a microscope.

Later additions to test: a dense 27B (expect it to be slow when spilled) and a couple of small fast ones.
