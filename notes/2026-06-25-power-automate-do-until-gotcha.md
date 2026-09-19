---
title: Power Automate: Do-until limits are not what you think
date: 2026-06-25
tags: [power-automate, gotcha]
---

# Power Automate: Do-until limits are not what you think

Do-until has two limits: a count (default 60) and a timeout (default PT1H). The loop stops when EITHER is hit,
and it does not fail; it just exits. If your success condition is never met, you silently get 60 iterations
of nothing and the flow reports success.

Fix: after the loop, add a Condition that checks whether the exit was due to the success condition, and
Terminate as Failed otherwise. Also set the count to something meaningful for the job, not 60.

Analogy I keep coming back to: this is the step cap in an agent loop. Same failure mode, same fix.
