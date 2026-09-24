# ollama/ollama — last 3 releases



## v0.34.4 — 2026-09-23

## What's Changed

- Structured outputs on thinking models now apply in a single pass, making them faster and more reliable.
- Fixed intermittent "model not found" errors with a large local library
- Fixed the macOS app becoming unresponsive when checking if ChatGPT or Codex is running.
- Qwen 3.8 prompt processing is faster on Apple Silicon.
- Gemma 4 on Apple Silicon now picks the best image resolution per image, keeping more detail in high-resolution images.
- Updated llama.cpp, MLX, and XGrammar.
 

**Full Changelog**: https://github.com/ollama/ollama/compare/v0.34.3...v0.34.4


## v0.34.3 — 2026-09-19

## What's Changed

`GET /api/show` now advertises each model's thinking controls and default:

Available in the CLI with:
```
ollama show gemma4
```

```
    thinking
        levels     false, true
        default    true
```

Available in the API with:
```sh 
curl http://localhost:11434/api/show -d '{"model": "glm-5.3-flash:cloud"}'
```

```json
{
  "thinking": {
    "values": ["low", "high", "max"],
    "default": "max"
  }
}
```

Also available on ollama.com directly for cloud models.

* **Nemotron H** vision models are now supported on Apple Silicon with MLX
* Ollama's macOS app will now no longer reopen windows you've closed when activating it
* Fix for model pulls from HuggingFace

**Full Changelog**: https://github.com/ollama/ollama/compare/v0.34.2...v0.34.3


## v0.34.2 — 2026-09-15

## What's Changed

- Added first-run setup when running `ollama`, with options to sign in or continue locally. Setup completion is shared with the desktop app on macOS and Windows.
- Added `ollama://apps` to open the desktop app’s Apps page directly on macOS and Windows.
- Fixed excessive memory growth during long generations with MLX speculative decoding.
- Updated llama.cpp.


**Full Changelog**: https://github.com/ollama/ollama/compare/v0.34.1...v0.34.2