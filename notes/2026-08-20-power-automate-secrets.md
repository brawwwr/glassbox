---
title: Where secrets go in flows
date: 2026-08-20
tags: [power-automate, security]
---

# Where secrets go in flows

Never in the flow definition. Options ranked:

1. Connection references. The credential lives in the connection, not the flow. Best default.
2. Environment variables of type secret backed by a key vault. Good for API keys the connector cannot hold.
3. Anything else is a smell.

Also: turn on "secure inputs/outputs" on actions that touch tokens, or they show up in run history in
plain text for anyone with view access.
