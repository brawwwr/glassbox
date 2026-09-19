---
title: Tokens are the cost
date: 2026-09-17
tags: [glassbox, agents, cost]
---

# Tokens are the cost

From the Phase 1 numbers: decode is 20-100 tokens per second depending on model and fit; prefill is thousands.
So the cost of an agent loop is dominated by two things: how many steps it takes, and how long its answers are.
Tool results appended to the context make every subsequent step's prefill longer, but prefill is cheap.
Long generated answers and thinking tokens are what actually burn time.

Implication for Phase 2: cap output tokens, turn thinking off for the loop, and print the running token
count every step so I can see the context growing.
