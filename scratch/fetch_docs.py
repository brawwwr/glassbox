"""
Save release notes / docs Claude needs for Phases 4–6 into research/docs/ (the Mac session has no web access).

    uv run scratch/fetch_docs.py
    git add -A && git commit -m "research: tool release notes" && git push

Standard library only. Pulls GitHub release bodies (markdown) and a few raw files. ~30 seconds.
"""

import json
import re
import time
import urllib.request
from pathlib import Path

UA = {"User-Agent": "glassbox-docs/0.1", "Accept": "application/vnd.github+json"}
OUT = Path("research/docs"); OUT.mkdir(parents=True, exist_ok=True)


def get(url, raw=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read().decode("utf-8", errors="replace")
    return data if raw else json.loads(data)


def save(name, text):
    (OUT / name).write_text(text, encoding="utf-8")
    print(f"  wrote research/docs/{name} ({len(text):,} chars)")


def releases(repo, n, fname):
    """Last n release bodies of a repo, newest first."""
    try:
        rel = get(f"https://api.github.com/repos/{repo}/releases?per_page={n}")
        parts = [f"# {repo} — last {n} releases\n"]
        for r in rel:
            parts.append(f"\n\n## {r.get('tag_name')} — {str(r.get('published_at',''))[:10]}\n\n{r.get('body') or '(no body)'}")
        save(fname, "\n".join(parts))
    except Exception as e:
        print(f"  {repo}: {e}")
    time.sleep(1)


def rawfile(url, fname):
    try:
        save(fname, get(url, raw=True))
    except Exception as e:
        print(f"  {url}: {e}")
    time.sleep(0.5)


print("TransformerLens (Phase 4)")
releases("TransformerLensOrg/TransformerLens", 4, "transformerlens-releases.md")
rawfile("https://raw.githubusercontent.com/TransformerLensOrg/TransformerLens/main/README.md", "transformerlens-README.md")
# the model registry tells us whether Qwen3 is supported and under what name
rawfile("https://raw.githubusercontent.com/TransformerLensOrg/TransformerLens/main/transformer_lens/loading_from_pretrained.py",
        "transformerlens-loading_from_pretrained.py")

print("transformers (Phase 4)")
releases("huggingface/transformers", 3, "transformers-releases.md")
rawfile("https://raw.githubusercontent.com/huggingface/transformers/main/docs/source/en/migration.md", "transformers-migration.md")

print("Qwen3 chat template (Phase 4 — how tools are rendered)")
rawfile("https://huggingface.co/Qwen/Qwen3-1.7B/raw/main/tokenizer_config.json", "qwen3-1.7b-tokenizer_config.json")
rawfile("https://huggingface.co/Qwen/Qwen3-1.7B/raw/main/config.json", "qwen3-1.7b-config.json")

print("MCP Python SDK (Phase 6)")
releases("modelcontextprotocol/python-sdk", 3, "mcp-python-sdk-releases.md")
rawfile("https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md", "mcp-python-sdk-README.md")

print("Gradio (Phase 5)")
releases("gradio-app/gradio", 2, "gradio-releases.md")

print("nnsight (Phase 4 fallback)")
releases("ndif-team/nnsight", 2, "nnsight-releases.md")

print("Ollama (runner bugs we hit)")
releases("ollama/ollama", 3, "ollama-releases.md")

# trim anything absurdly long so the repo stays light
for f in OUT.glob("*"):
    t = f.read_text(encoding="utf-8", errors="replace")
    if len(t) > 400_000:
        f.write_text(t[:400_000] + "\n\n[truncated]", encoding="utf-8")
print("done")
