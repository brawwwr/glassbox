---
title: JSONL logging pattern
date: 2026-07-15
tags: [python, logging]
---

# JSONL logging pattern

Pattern I use for anything I want to analyse later: one JSON object per line, appended to a file.

```python
import json, time
def log(path, **fields):
    fields["ts"] = time.time()
    with open(path, "a") as f:
        f.write(json.dumps(fields) + "\n")
```

Load with pandas.read_json(path, lines=True). No database, no schema migrations, greppable, and a broken
line only loses one record. For the agent loop this will record every model call and tool call.
