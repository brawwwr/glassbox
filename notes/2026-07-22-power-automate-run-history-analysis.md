---
title: Reading run history like a trace
date: 2026-07-22
tags: [power-automate, observability]
---

# Reading run history like a trace

Spent an hour reading run history for a slow flow. Each action has a start time, duration, inputs and
outputs. Laid out in order it is a trace: a waterfall of steps with timings.

Findings: 90% of the wall time was in one HTTP action waiting on an external system. Everything else was
milliseconds. Fixed by adding a retry policy with exponential backoff and moving the slow call to a child flow.

Note for the GlassBox project: this is what a Langfuse trace is. Where does the time go? Usually one step.
