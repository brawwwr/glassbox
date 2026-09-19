---
title: Desktop thermals under sustained GPU load
date: 2026-08-15
tags: [hardware, gpu, thermals]
---

# Desktop thermals under sustained GPU load

Ran a 30-minute GPU stress test to see whether the case cooling is adequate before starting the LLM project.

- RTX 4070: peaked at 71 C, fan at 68%. Fine.
- CPU: 82 C during the CPU-bound parts. Warmer than I would like. Case airflow is front-to-back with two
  intakes and one exhaust.
- NVMe (F:): 64 C during heavy writes.

Ordered a second exhaust fan. Will re-test after installing.
