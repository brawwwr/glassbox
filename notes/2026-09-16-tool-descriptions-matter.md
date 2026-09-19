---
title: Tool descriptions are the whole interface
date: 2026-09-16
tags: [glassbox, agents, design]
---

# Tool descriptions are the whole interface

Realisation while sketching the Phase 2 tools: the model never sees my code. It sees the name, the description,
and the parameter schema. That is the entire interface. If search_notes says "search notes" the model will use it
for everything; if it says "search the user's personal markdown notes by keyword; returns file paths and matching
lines; use before answering questions about what the user has written", it will use it correctly.

Same lesson as the custom connector at work. The description is the contract.

Also decided: read_note refuses any path outside the notes folder. First tool-safety rule.
