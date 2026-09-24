# ndif-team/nnsight — last 2 releases



## v0.8.0.rc1 — 2026-09-09

# nnsight v0.8.0 Release Notes

**0.8 is a ground-up rewrite of nnsight's execution engine.** The API you write is unchanged — open a `with model.trace(...)` block and read, edit and `.save()` a model's internals as ordinary Python — but the machinery underneath is new, and most of what follows falls out of it.

A handful of things moved, were deprecated, or now raise where they used to silently no-op. **Two can change your numbers without raising anything**; they are the first two entries under [Breaking Changes](#breaking-changes).

```bash
pip install --pre nnsight
```

Remote execution against NDIF stays on v0.7 until NDIF is upgraded.

---

## 🚀 Highlights

### Greenlets, not threads

Intervention code and the model's forward pass now interleave as **greenlets** — cooperative, single-threaded coroutines — instead of coordinating across OS worker threads. Each block runs in its own worker greenlet (a `Mediator`) that hands control back whenever it parks on a location. Only one greenlet runs at a time, so there are **no locks and no queues** anywhere in the engine. One shared `Interleaver` installs persistent pass-through forward hooks on every module; the worker/model event protocol is `VALUE` / `SWAP` / `SKIP` / `BARRIER`.

The engine (`src/nnsight/intervention/`) went from 7,336 to 4,911 lines of code, a 33% reduction, while model support grew.

Reading a location the model already ran past raises **`OutOfOrderError`**, naming the location and pointing the traceback at the line that was waiting. 0.7 raised here too, but as `MissedProviderError: ... was not provided. Did you call an Envoy out of order?`, which sent people looking for a module-path typo. The gain is the diagnosis.

### `TransformersModel` — one class for every `transformers` task

`TransformersModel("repo/id", task=...)` is the primary HuggingFace class, backed by a `transformers.pipeline`, so it works for any task the pipeline factory can build:

```python
from nnsight import TransformersModel

gpt2 = TransformersModel("openai-community/gpt2", task="text-generation")
bert = TransformersModel("google-bert/bert-base-uncased", task="fill-mask")
vlm  = TransformersModel("llava-hf/llava-interleave-qwen-0.5b-hf", task="image-text-to-text")
asr  = TransformersModel("openai/whisper-tiny", task="automatic-speech-recognition")
```

Also accepts a pre-loaded `torch.nn.Module`, `peft=<repo_id>` to graft a PEFT adapter at load, and `rename=` / `envoys=` for customization. Chunked tasks (token windows past the context limit, one entailment pair per zero-shot label, ASR windows) become **rows of the trace's single forward pass**, in the order the pipeline yields them.

`LanguageModel` and `VisionLanguageModel` are now deprecated thin subclasses that warn on construction.

### `generate` vs `pipe`

Two jobs, two methods:

- `model.generate(...)` runs the model's `generate` and returns **token ids** on `tracer.result`, decoding with the checkpoint's own `generation_config`.
- `model.pipe(...)` runs the whole task **pipeline** and returns its records (decoded text, labels). This is what the old `generate` returned.
- `model.trace(...)` runs one forward; `model.scan(...)` runs one forward under fake tensors for shape inference, with no dispatch and no weights.

### vLLM as a first-class runtime

Interventions run **inside the engine worker**, so PagedAttention, continuous batching and tensor parallelism keep working under a trace.

- **CUDA-graph taps.** `VLLM(..., taps=["model.layers.*.output"])` records the locations you name into the graph as breaks and serves them on every replay, keeping graphs on. Measured against vanilla vLLM: **96%** of throughput at 8B on one GPU, 93% at tp=4, 91% at tp=8, 95% at 70B/tp=8. A tap can reach a `.source` operation inside a forward.
- **Engine-wide `model.edit()`.** Installs a block on the engine once; every later request gets its own scoped copy, including requests from clients that never heard of nnsight. Name edits and select them per request with `edits=[...]`.
- **`nnsight-serve`.** One engine behind HTTP for GPU-less clients.
- **`mode="async"`** streams `RequestOutput`s from a trace via `tracer.backend`.
- Plus `n > 1`, MoE fragment handling, and a prefix-cache recompute so cached tokens still reach interventions.

### Tensor parallelism

Shard a model across GPUs with transformers' native tensor parallelism and trace it as though it were on one card:

```python
# torchrun --nproc_per_node=4 tp_trace.py
from transformers.distributed import DistributedConfig
from nnsight import TransformersModel

model = TransformersModel(
    "meta-llama/Llama-3.2-3B", task="text-generation", dispatch=True,
    distributed_config=DistributedConfig(tp_size=4),
)
```

nnsight gathers sharded activations before your intervention sees them and re-splits whatever you leave behind. **Requires transformers >= 5.16**, which rebuilt TP on DTensor; on 5.15 and earlier nothing is recognized as sharded and a trace sees one rank's slice.

### Quantization by dtype name

```python
model = TransformersModel("meta-llama/Llama-3.2-3B", task="text-generation", dtype="nf4")
```

`nf4` / `int4` / `4bit` mean NF4; `fp4`, `int8`, `fp8` mean what they say. Module paths and activations are unchanged. Needs `bitsandbytes` and `accelerate`, neither of which ships with nnsight. `fp8` is refused below compute capability 8.9, because transformers otherwise warns and silently loads bfloat16 at twice the requested width.

### Source tracing

`module.source.<op>` makes every call site inside a `forward` addressable, with the same `.input` / `.output` / `.skip` handles a module has. AST-rewritten, installed lazily on first access, inert outside a trace, and recursively drillable.

Since 0.7: **every assignment is an operation** on the same per-name counter as calls, and **decorated forwards no longer raise `SourceNotAvailable`** — a wrapper is peeled and rebuilt around the instrumented function, and closures and `super()` forwards are instrumented too. `SourceNotAvailable` now means only "no Python source" (a builtin or C function). See the label-shift note under Breaking Changes.

### `eproperty` — declare your own hookable values

`.input` / `.inputs` / `.output`, `tracer.result` and `VLLM.logits` / `.samples` are all built on the reintroduced `@eproperty` descriptor (`preprocess` / `.postprocess` / `.transform` / `.provide`, with `description=` surfacing a value in the Envoy repr tree). Declare your own on a model subclass.

### Packaging

`pip install nnsight` is a working local **and** remote install: transformers, huggingface-hub and the remote dependencies are core, with `dev` / `vllm` / `serve` extras. Metadata is populated, `nnsight.__version__` resolves via `importlib.metadata`, and the `nnsight` and `nnsight-serve` console entry points ship. **Python 3.10 through 3.14** are supported, with both ends tested in CI. `nnsight.login()` and `nnsight login` store and verify an NDIF key.

---

## Performance

Interleaving overhead, measured on a compute-free stack of 96 tiny blocks with the same model's untraced forward subtracted out, so the model's own compute cancels. CPU, pinned cores, median of two runs; the two versions' baseline forwards agreed to within 2%.

| | v0.7 | v0.8 | |
|---|---:|---:|---|
| Opening a trace with nothing in it | 1.12 ms | **0.51 ms** | |
| Each activation read | 36.7 µs | **11.8 µs** | 3.1x flatter |
| Each activation edited | 43.9 µs | **17.1 µs** | 2.6x flatter |
| Each extra prompt batched into one pass | 94.3 µs | **15.6 µs** | 6.0x flatter |

At the ends of those sweeps: 192 activations read in one pass costs 8.2 ms of nnsight on v0.7 and 2.8 ms on v0.8; 128 prompts batched into one forward costs 13.1 ms against 2.6 ms.

The batching column is where the rewrite shows most — 0.7's `Interleaver.handle` fanned every visit out to every mediator, so cost scaled with modules x invokes.

**On a real model with a handful of interventions you will not notice any of this.** A GPT-2 forward on CPU is roughly 50 ms and a dozen reads is 0.14 ms of nnsight, about a quarter of one percent. The engine pays off when a trace touches a lot of the model at once: caching everything, per-head sweeps, source tracing, large batches.

Repro: `tests/performance/interleave_bench.py`, which is version-agnostic — point `PYTHONPATH` at each tree and diff with `compare.py`.

---

## Other Improvements

- **`tracer.cache(...)`** records many modules at once — every layer, and every generation step — with a `non_blocking` flag for the device transfer.
- **`module.skip(replacement)`** bypasses a module; **`tracer.stop()`** exits a run early; **`tracer.barrier(n)`** synchronizes value sharing across invokes.
- **`model.edit()`** stores interventions on the envoy so every later trace replays them, on a shallow copy by default so the original stays clean.
- **`model.session()`** bundles several traces so values flow between them without `.save()`.
- **`DiffusionModel`** wraps any `diffusers` pipeline, UNet- or transformer-based (SD/SDXL, Flux/SD3/DiT), with `seed=`, per-invoke batching and denoising-step iteration. `automodel=` chooses the class the weights load through.
- **`remote="local"`** runs the serialize / deserialize / execute round trip in-process, so serialization problems surface offline without a key or a queue.
- **`AsyncRemoteBackend`** — `await` a job for its saves, `async for` streamed status. `model.session(remote=True)` bundles traces into one job. Model identity via `to_model_key()` / `from_model_key()`.
- **Batching** unifies direct and traced calls through one add/assemble path, with per-invoke row narrowing, left-padded `position_ids`, empty-invoke whole-batch semantics and multi-invoke `.skip()` reassembly. A write that changes an invoke's row count is refused.
- **Gradients** are fixed for batched invokes, and a freed autograd graph is explained in terms of invokes.
- **Config** is `CONFIG.API.HOST` / `APIKEY` / `COMPRESS` and `CONFIG.APP.DEBUG` / `REMOTE_LOGGING` / `PYMOUNT`, loaded from `~/.config/nnsight/config.yaml` over shipped defaults, then env (`NDIF_API_KEY`, `NDIF_HOST`, `NNSIGHT_DEBUG`). `-v` / `--verbose` flips DEBUG for full tracebacks.
- **Serialization** takes a remote block's scope from its AST rather than shipping unrelated globals, uses function scoping for a shipped def's captured names, and finds a function's symtable child by type (Python 3.14).
- torch C++ errors no longer segfault the process inside interleaving greenlets.

---

## Documentation

- **`docs/`** — 105 recipe-style pages (usage / concepts / patterns / errors / gotchas / remote / models / developing), routed for humans and agents by **`CLAUDE.md`**. Every claim was checked by executing it.
- **`NNsight.md`** — a design-and-implementation manual for the internals.
- **`NNsight_Walkthrough.ipynb`** — a runnable, Colab-ready guided tour, verified on CPU.
- Agent support via [Context7](https://context7.com/ndif-team/nnsight) and the [skills repository](https://github.com/ndif-team/skills).

---

## Pull Requests

The rewrite itself landed as [#686](https://github.com/ndif-team/nnsight/pull/686). Everything merged on top of it:

**Engine and tracing**

- [#690](https://github.com/ndif-team/nnsight/pull/690) vLLM edits and `n>1`, interleaver hot path, and fixes from an interpretability sweep
- [#720](https://github.com/ndif-team/nnsight/pull/720) interleaver: don't let a parked worker or an early stop escape cleanup
- [#721](https://github.com/ndif-team/nnsight/pull/721) envoy: mirror every module entry, not every distinct module
- [#723](https://github.com/ndif-team/nnsight/pull/723) source: rebindable controller object, the module's own forward as its body, and `.source` on callable instances
- [#724](https://github.com/ndif-team/nnsight/pull/724) tracer: keep the whole block body, and say why capture failed

**Models and runtimes**

- [#687](https://github.com/ndif-team/nnsight/pull/687) trace a model sharded with transformers tensor parallelism
- [#688](https://github.com/ndif-team/nnsight/pull/688) name a quantization where you would name a dtype
- [#697](https://github.com/ndif-team/nnsight/pull/697) vLLM: CUDA-graph taps, controller-only handoff, one request record, TP/DCP fixes
- [#709](https://github.com/ndif-team/nnsight/pull/709) tp: port to the transformers 5.16 DTensor backend
- [#712](https://github.com/ndif-team/nnsight/pull/712) diffusion: `automodel=` chooses the class the weights load through
- [#717](https://github.com/ndif-team/nnsight/pull/717) transformers: beam search, audio models on meta, and a task transformers 5 removed

**Correctness**

- [#698](https://github.com/ndif-team/nnsight/pull/698) fix(serialization): find the function's symtable child by type, not by count (Python 3.14) — @Hotragn
- [#699](https://github.com/ndif-team/nnsight/pull/699) feat(backward): explain the freed autograd graph in terms of invokes, and cover batched-invoke gradients — @Hotragn
- [#701](https://github.com/ndif-team/nnsight/pull/701) fix(envoy): reject a `rename` alias that would shadow something — @Hotragn
- [#703](https://github.com/ndif-team/nnsight/pull/703) fix(cache): stop conflating "not recorded" with a recorded `None` or empty — @Hotragn

**CI and documentation**

- [#707](https://github.com/ndif-team/nnsight/pull/707) ci: run on pushes to 0.8, and test both ends of the advertised Python range — @Hotragn
- [#710](https://github.com/ndif-team/nnsight/pull/710) 0.8 release audit: twelve code fixes and a docs pass with every claim executed
- [#718](https://github.com/ndif-team/nnsight/pull/718) docs: correct iteration, backward, skip, edit-attach and generate claims

---

## Breaking Changes

**These two change results without raising anything:**

1. **`.source` operation labels shifted.** Every assignment in an instrumented forward is now an operation in its own right, sharing the per-name counter with calls. GPT-2's attention call moved from `attention_interface_0` to `attention_interface_1`; `attention_interface_0` is now the line that *chooses* the implementation. Requesting the old label **does not raise** — it returns the assigned value instead. Print the source and re-check any label you hardcoded.
2. **A bounded `tracer.iter[:N]` that outruns the run is cut short**, with a warning. Values saved inside the loop are kept and statements after it are discarded, so a result can look complete while being shorter than the bound. 0.7 bounded `all()` internally; code written against it should hold the run to the count (`min_new_tokens=` on transformers, `min_tokens=` or `ignore_eos=True` on vLLM) or move trailing statements into a separate `tracer.invoke()`.

**These raise:**

3. **`x.save()` / `nnsight.save(x)` outside a trace now raises** (it used to be a silent no-op). To collect per-step values, save the container once and append raw values (`xs = nnsight.save([]); xs.append(...)`); appending `x.save()` drops values on remote.
4. **`model.generator.output` is deprecated** in favour of `tracer.result` (same tensor). `model.generator.streamer.output` still gives per-step tokens and is not deprecated.
5. **A saved value *is* the value.** `.value` on one raises `AttributeError`.
6. **`tracer.next()` / `module.next()` are gone**, and `with tracer.iter[...]:` / `with tracer.all():` are deprecated in favour of `for step in tracer.iter[...]:`. `model.iter` / `model.all()` are deprecated aliases of the tracer's.
7. **The v0.4-era namespace is removed**: `nnsight.apply()`, `log()`, `local()`, `cond()`, `iter()`, `session()` and the `nnsight.list/dict/int/...` type wrappers. Use plain Python and `model.session()`.
8. **`LanguageModel` / `VisionLanguageModel` warn on construction.** Use `TransformersModel(repo, task=...)`.
9. **`CONFIG.APP.CROSS_INVOKER`, `CACHE_DIR` and `TRACE_CACHING` are gone.**
10. **`tracer.local()` (hybrid streaming) is not ported.**
11. **Custom `_prepare_input` / `_batch` implementations** need updating to the new signatures.
12. **Tensor parallelism requires transformers >= 5.16.**

Everything reachable under an old name warns under `nnsight.NNsightDeprecationWarning`, a `FutureWarning` rather than a `DeprecationWarning` — Python's default filters only show a `DeprecationWarning` raised at the top level of the running script, so a package or helper module being ported would have warned to nobody. Silence nnsight's alone with:

```python
warnings.filterwarnings("ignore", category=nnsight.NNsightDeprecationWarning)
```

nnsight registers no filters of its own.

---

## Migration

| v0.7 | v0.8 |
|---|---|
| `LanguageModel(repo)` | `TransformersModel(repo, task="text-generation")` |
| `VisionLanguageModel(repo)` | `TransformersModel(repo, task="image-text-to-text")` |
| `model.generator.output` | `tracer.result` |
| decoded generation records | `model.pipe(...)` |
| `saved.value` | `saved` |
| `tracer.next()` / `module.next()` | `for step in tracer.iter[...]:` |
| `with tracer.iter[...]:` | `for step in tracer.iter[...]:` |
| `model.iter[...]` / `model.all()` | `tracer.iter[...]` / `tracer.all()` |
| `nnsight.apply/log/cond/iter/session(...)` | plain Python, `model.session()` |
| `nnsight.list/dict/int/...` | plain Python containers |
| `nnsight.ndif_status()` | `nnsight.status()` |
| `CONFIG.APP.CROSS_INVOKER` / `CACHE_DIR` / `TRACE_CACHING` | removed |

The full mapping, with the message each deprecation raises, is in [`docs/reference/version-history.md`](docs/reference/version-history.md).

---

## Contributors

- **@JadenFiotto-Kaufman** — the rewrite, the model classes, tensor parallelism, quantization, the vLLM runtime and the release audit.
- **@Hotragn** — the Python 3.14 serialization fix, the cache and `rename` correctness fixes, the freed-autograd-graph diagnostic, and the CI matrix.
- **@khaiwang** — vLLM worker-side construction and save marks across requests, constructor-argument routing, the barrier exception fix, and the backward-session refusal on tensors that don't require grad. Also the vLLM MoE fragment handling, `nnsight-serve` and the TP determinism fix that this branch inherited.
- **@elliottower** — remote execution for encoder models.
- **@J0YY** — logit-lens heatmap token labels.

Thank you all.


## What's Changed
* engineio version by @MichaelRipa in https://github.com/ndif-team/nnsight/pull/665
* perf: lazy-load model classes to cut import nnsight from 7.6s to 1.6s by @JadenFiotto-Kaufman in https://github.com/ndif-team/nnsight/pull/663
* Count source-op iterations per-fire instead of per-forward by @JadenFiotto-Kaufman in https://github.com/ndif-team/nnsight/pull/669
* fix(language): derive position_ids from the mask for left-padded batches by @khaiwang in https://github.com/ndif-team/nnsight/pull/673
* Clarify logit lens heatmap token labels by @J0YY in https://github.com/ndif-team/nnsight/pull/678
* fix(vllm): gather FusedMoE deferred-reduce partials on access; scale write-backs by @khaiwang in https://github.com/ndif-team/nnsight/pull/685
* Add contributing section to CLAUDE.md by @Butanium in https://github.com/ndif-team/nnsight/pull/683
* handle exceptions in converted functions by @lmjantsch in https://github.com/ndif-team/nnsight/pull/658
* Fix MissedProviderError in .backward() with multiple invokers (#664) by @azrabano23 in https://github.com/ndif-team/nnsight/pull/671
* Add nnsight login command and notebook helper (#506) by @EphraiemSarabamoun in https://github.com/ndif-team/nnsight/pull/668
* Trace a model sharded with transformers tensor parallelism by @JadenFiotto-Kaufman in https://github.com/ndif-team/nnsight/pull/687
* Name a quantization where you would name a dtype by @JadenFiotto-Kaufman in https://github.com/ndif-team/nnsight/pull/688
* vLLM edits and n>1, interleaver hot path, and fixes from an interpretability sweep by @JadenFiotto-Kaufman in https://github.com/ndif-team/nnsight/pull/690
* vLLM: CUDA-graph taps, controller-only handoff, one request record, T… by @JadenFiotto-Kaufman in https://github.com/ndif-team/nnsight/pull/697
* fix(serialization): find the function's symtable child by type, not by count (Python 3.14) by @Hotragn in https://github.com/ndif-team/nnsight/pull/698
* ci: run on pushes to 0.8, and test both ends of the advertised Python range by @Hotragn in https://github.com/ndif-team/nnsight/pull/707
* 0.8 release audit: twelve code fixes and a docs pass with every claim executed by @JadenFiotto-Kaufman in https://github.com/ndif-team/nnsight/pull/710
* tp: port to the transformers 5.16 DTensor backend by @JadenFiotto-Kaufman in https://github.com/ndif-team/nnsight/pull/709
* fix(cache): stop conflating "not recorded" with a recorded None or empty by @Hotragn in https://github.com/ndif-team/nnsight/pull/703
* fix(envoy): reject a `rename` alias that would shadow something by @Hotragn in https://github.com/ndif-team/nnsight/pull/701
* feat(backward): explain the freed autograd graph in terms of invokes, and cover batched-invoke gradients by @Hotragn in https://github.com/ndif-team/nnsight/pull/699
* diffusion: automodel= chooses the class the weights load through by @JadenFiotto-Kaufman in https://github.com/ndif-team/nnsight/pull/712
* transformers: beam search, audio models on meta, and a task transformers 5 removed by @JadenFiotto-Kaufman in https://github.com/ndif-team/nnsight/pull/717
* docs: correct iteration, backward, skip, edit-attach and generate claims by @JadenFiotto-Kaufman in https://github.com/ndif-team/nnsight/pull/718
* interleaver: don't let a parked worker or an early stop escape cleanup by @JadenFiotto-Kaufman in https://github.com/ndif-team/nnsight/pull/720
* envoy: mirror every module entry, not every distinct module by @JadenFiotto-Kaufman in https://github.com/ndif-team/nnsight/pull/721
* source: rebindable controller object, the module's own forward as its body, and .source on callable instances by @JadenFiotto-Kaufman in https://github.com/ndif-team/nnsight/pull/723
* tracer: keep the whole block body, and say why capture failed by @JadenFiotto-Kaufman in https://github.com/ndif-team/nnsight/pull/724
* vllm: rework #662 against 0.8 — token axis + NNSIGHT_VLLM_CLONE_READS by @JadenFiotto-Kaufman in https://github.com/ndif-team/nnsight/pull/727
* vllm: follow-ups from the v0.7.0 merges by @khaiwang in https://github.com/ndif-team/nnsight/pull/662
* 0.8 — the pipeline rewrite by @JadenFiotto-Kaufman in https://github.com/ndif-team/nnsight/pull/686

## New Contributors
* @J0YY made their first contribution in https://github.com/ndif-team/nnsight/pull/678
* @lmjantsch made their first contribution in https://github.com/ndif-team/nnsight/pull/658
* @azrabano23 made their first contribution in https://github.com/ndif-team/nnsight/pull/671
* @EphraiemSarabamoun made their first contribution in https://github.com/ndif-team/nnsight/pull/668
* @Hotragn made their first contribution in https://github.com/ndif-team/nnsight/pull/698

**Full Changelog**: https://github.com/ndif-team/nnsight/compare/v0.7.0...v0.8.0.rc1


## v0.7.0 — 2026-05-05

# nnsight v0.7.0 Release Notes

## 🚀 Highlights

### Lazy Hook Execution

The biggest architectural change in 0.7. Wrapped modules no longer carry permanent forward / pre-forward hooks. Instead, each `Mediator` registers a one-shot hook *only* when the worker thread actually accesses that module's `.input` / `.output`, and the hook self-removes after firing.

What this means in practice: **modules nobody touches pay zero per-forward overhead.** Across a representative sample of workloads we see **10–50% trace speedups** on top of v0.6's gains, with the largest improvements on real models with sparse instrumentation (a few `.save()` sites against a 30+ layer transformer).

Three pieces make this work:

- **A sentinel forward hook on every wrapped module.** PyTorch fast-paths past hook dispatch when `_forward_hooks` is empty; the sentinel keeps the dict non-empty so a hook added *during* a forward pass still fires.
- **`add_ordered_hook`.** Inserts a hook at the right position in PyTorch's hook dict by reading `mediator_idx` so multi-invoke traces fire hooks in invoke-definition order regardless of which mediator registered first.
- **`mediator.hooks` cleanup list.** Every dynamic hook (one-shot, persistent cache, iter-tracker, backward) registers there. `Mediator.remove_hooks()` drains the list at session cancel — idempotent, so hooks that already self-removed are no-ops.

The old `SkipException` machinery is gone with it. `Envoy.skip(value)` now stuffs `__nnsight_skip__` into the forward kwargs and the wrapped forward returns it directly. As a side benefit, multi-invoke `.skip(...)` calls on the same module now correctly accumulate per-invoke skip values and re-concatenate them on the way out, instead of the first invoke's value clobbering the rest.

For the architecture deep-dive, see [`docs/developing/lazy-hook-system.md`](docs/developing/lazy-hook-system.md).

---

### `nnsight-serve` — Single-Model HTTP Server Backed by vLLM

A lightweight FastAPI server that runs a vLLM engine and accepts serialized nnsight traces over HTTP. vLLM does the heavy lifting (continuous batching, paged KV cache, request scheduling); nnsight injects intervention hooks on top.

For users who want a persistent, intervention-capable inference endpoint without running an NDIF cluster.

**Start the server:**

```bash
nnsight-serve Qwen/Qwen3-30B-A3B --port 6677 --tensor-parallel-size 4 --api-key mysecret
```

**Client UX is identical to local nnsight** — just pass `serve="http://host:port"`. The client only needs a meta model; no GPU required.

```python
from nnsight.modeling.vllm import VLLM

model = VLLM("Qwen/Qwen3-30B-A3B")  # meta model on the client

with model.trace("The Eiffel Tower is in", serve="http://localhost:6677"):
    hidden = model.model.layers[24].output[0].save()
    logits = model.logits.save()

print(model.tokenizer.decode(logits.argmax(dim=-1)))  # Paris
print(hidden.shape)
```

Three modes:

- **Blocking** (default). `.save()` values appear in scope after the `with` block.
- **Non-blocking.** `blocking=False`; multiple traces fly concurrently inside vLLM's engine. Retrieve saves via `tracer.collect()`:
  ```python
  with model.trace("prompt 1", serve=url, blocking=False) as t1:
      out1 = model.logits.save()
  with model.trace("prompt 2", serve=url, blocking=False) as t2:
      out2 = model.logits.save()

  saves1 = t1.collect()  # blocks until response, returns {"out1": tensor}
  saves2 = t2.collect()
  ```
- **Multi-invoke.** Same as local — nest `tracer.invoke(...)`s inside one trace.

Optional API-key auth (`--api-key` on the server, `api_key=` on the client).

Limitations: vLLM only (no HuggingFace backend yet), no cross-trace tensor references, non-blocking mode can't inject saves into the caller frame (use `.collect()` to get a dict).

For the full guide and limitations, see [`src/nnsight/modeling/vllm/serve/README.md`](src/nnsight/modeling/vllm/serve/README.md).

Initial implementation contributed by [@khaiwang](https://github.com/khaiwang).

---

### `eproperty` — A Stable Extension API for Custom Hookable Values

`eproperty` is the descriptor that backs every `.output` / `.input` / `.inputs` / `.logits` / `.samples` access. In 0.7 it becomes a first-class public API for users to add their own hookable values to a model.

A custom Envoy subclass can now expose new attributes that participate in the same request/swap protocol as the built-ins:

```python
from nnsight import NNsight
from nnsight.intervention.envoy import Envoy
from nnsight.intervention.interleaver import eproperty
from nnsight.intervention.hooks import requires_output

class MyAttnEnvoy(Envoy):
    n_heads = 12

    @eproperty(key="output", description="Per-head attention view")
    @requires_output
    def heads(self): ...

    @heads.preprocess
    def heads(self, value):
        # Reshape so the user sees [batch, n_heads, seq, head_dim].
        B, S, H = value.shape
        return value.view(B, S, self.n_heads, H // self.n_heads).transpose(1, 2)

    @heads.transform
    @staticmethod
    def heads(value):
        # Reshape back to [batch, seq, hidden] before the model continues.
        return value.transpose(1, 2).reshape(value.shape[0], value.shape[2], -1)

with model.trace("Hello"):
    h = model.transformer.h[0].attn.heads     # [B, n_heads, S, head_dim]
    h[:, 4] = 0                                # ablate head 4
```

Three reshape hooks compose to give you full control over the read/write loop:

| Decorator | Fires on | Purpose |
|---|---|---|
| `@x.preprocess` | `__get__` | Reshape value before the user sees it. |
| `@x.postprocess` | `__set__` | Reshape user-supplied value before swapping into the model. |
| `@x.transform` | After value delivery, before next event | Reshape back after in-place edits and swap into the model. Closes the loop when `preprocess` returned a *new* object. |

Pre-setup decorators (`requires_output`, `requires_input`, `requires_operation_output`, `requires_operation_input`) handle hook installation. A bare `@eproperty()` with no setup decorator is also valid for values pushed in from outside any single `nn.Module` — vLLM's `logits` / `samples` work this way, as does `tracer.result`.

Anything that hosts an `eproperty` just needs to satisfy the lightweight `IEnvoy` protocol — an `interleaver` attribute and an optional `path: Optional[str]`. `Envoy`, `OperationEnvoy`, `InterleavingTracer`, and `VLLM` all satisfy it.

Eproperties with a `description=` show up in the model repr tree, and `Generic[T]` typing means IDEs see the right return type.

For the full extension guide, see [`docs/usage/extending.md`](docs/usage/extending.md) and [`docs/developing/eproperty-deep-dive.md`](docs/developing/eproperty-deep-dive.md).

---

### Custom Envoy Classes Per Module — `envoys=`

Pair `eproperty` with the new `envoys=` kwarg and you can attach per-module-type behavior to a whole model in one declaration:

```python
import torch
from nnsight import LanguageModel

model = LanguageModel(
    "gpt2",
    envoys={torch.nn.Linear: MyLinearEnvoy, "self_attn": MyAttnEnvoy},
)

with model.trace("Hello"):
    n = model.transformer.h[0].mlp.c_fc.normalized.save()  # MyLinearEnvoy
    h = model.transformer.h[0].attn.heads                  # MyAttnEnvoy
    h[:, 4] = 0
```

Three forms:

| Form | Behavior |
|---|---|
| `None` (default) | Every descendant wrapped in the base `Envoy`. |
| A single `Envoy` subclass | Every descendant wrapped in that class. |
| `Dict[type \| str, Type[Envoy]]` | Per-module mapping. |

- **Type keys** match against `type(module).__mro__`, so `{torch.nn.Linear: MyLinearEnvoy}` matches every concrete `Linear` subclass.
- **String keys** match a dotted suffix of the envoy path (component-wise, alias-aware via `rename`). Type keys win over string keys.
- **Subclass-level default.** Model wrapper classes (`LanguageModel`, `VLLM`, your own `NNsight` subclass) can set `envoys = {...}` as a class attribute so end users don't have to pass anything.
- **Propagates down the tree.** One declaration covers the whole model — each child Envoy is constructed with the same `envoys=` value.

---

### Source Tracing Rewrite

`module.source` exposes intermediate operations *inside* a module's forward — every call site becomes a hookable provider path. In 0.7 the implementation is split into a global accessor and a per-Envoy wrapper, which fixes a class of correctness bugs around multiple Envoys / Interleavers / sessions touching the same module.

| Layer | Global (per-module) | Per-Envoy wrapper |
|---|---|---|
| Module forward | `SourceAccessor` | `SourceEnvoy` |
| Single call site | `OperationAccessor` | `OperationEnvoy` |

The accessors are cached on the module itself as `module.__source_accessor__`, so the rewrite survives `torch.compile` re-binding `forward`, accelerate's hot-swap on dispatch, and meta-tensor weight loading. Multiple Envoys wrapping the same module share the underlying accessors — only the per-Envoy wrappers are duplicated.

Other concrete improvements:

- **`.source` works under `tracer.iter[:]`.** Operation iteration counters bump in lockstep with parent modules across multi-step generation.
- **Recursive `.source` is correct under shared accessors.** Descending into a called function (`...source.attention_interface_0.source.scaled_dot_product_attention_0.output`) reuses the cached nested accessor instead of building fresh state per access.
- **Friendlier errors.** Calling `.source` on a sub-module from inside another `.source` raises a clear `ValueError` directing you to access the sub-module directly. Calling `.source` outside a trace gives a friendly message instead of an obscure crash.
- **Cleaner repr.** Print a `SourceEnvoy` to see the rewritten forward with operation names and line numbers; print an `OperationEnvoy` to see it highlighted in surrounding context.

For the full architecture, see [`docs/concepts/source-tracing.md`](docs/concepts/source-tracing.md) and [`docs/developing/source-accessor-internals.md`](docs/developing/source-accessor-internals.md).

---

### vLLM Compatibility Refresh

The vLLM integration got a substantial cleanup pass:

- **The `==` version pin is gone.** `pyproject.toml` now declares `vllm` and `triton` without strict pins; the `ImportError: nnsight requires vLLM version X` failure on `import nnsight.modeling.vllm` is no more. nnsight now tracks current vLLM rather than locking users to one specific point release. Contributed by [@gsarti](https://github.com/gsarti).
- **vLLM 0.19+ tensor-parallel init fix.** Distributed init (`initialize_model_parallel`) is now wrapped in `set_current_vllm_config(VllmConfig())` and run *outside* the `init_empty_weights` meta context. This fixes the `Cannot copy out of meta tensor` failure on TP setups against vLLM 0.19+.
- **`logits` and `samples` are now `eproperty`s, not `WrapperModule`s.** This is a small API change with a big internal cleanup payoff. **(Breaking — see Migration below.)**
  ```python
  # 0.6
  with model.trace(prompt) as tracer:
      logits = model.logits.output.save()

  # 0.7
  with model.trace(prompt) as tracer:
      logits = model.logits.save()
  ```
- **`generator` is gone.** Generation outputs flow through the result mechanism instead of a `WrapperModule`.
- **`model.generate(...)` is now an alias for `model.trace(...)`** on `VLLM`, for cross-API portability with `LanguageModel`. `max_new_tokens` is rewritten to vLLM's `max_tokens`.
- **Tensor-parallel correctness fixes:**
  - **CUDA stream propagation to TP worker threads.** Workers no longer write to the default stream while the driver computes on a side stream; this was a source of silent non-determinism on TP setups. Diagnosed and fixed by [@khaiwang](https://github.com/khaiwang).
  - **TP gather/split now uses `add_ordered_hook`** so multiple invokes' hooks fire in mediator-defined order. (Previously the first invoke's hook would consume the whole batch.)
- **vLLM cache hooks rewritten.** Per-request cache capture and async saves work correctly across all four mode/backend combinations (sync/async × multiprocessing/Ray).

---

### `engineio` SSL Race-Condition Patch

Fixes a ~30–55% WebSocket connection failure rate when talking to NDIF over TLS. The patch is applied automatically at `import nnsight` (before any `socketio` imports), so you don't need to do anything.

The underlying problem: `python-engineio` started its read/write background threads concurrently after the WebSocket `connect` event, while still mid-handshake. Python's SSL sockets are not thread-safe for simultaneous read+write, and the resulting socket corruption manifested as flaky connections.

The patch serializes the handshake — flushes queued packets and receives the response synchronously in the main thread before starting background threads. Idempotent and a no-op for non-WebSocket transports. See [python-socketio#1568](https://github.com/miguelgrinberg/python-socketio/issues/1568) for upstream context.

Diagnosed and contributed by [@MichaelRipa](https://github.com/MichaelRipa).

---

### Frame-Based Root-Trace Detection (drop `Globals.stack`)

The process-wide `Globals.stack` counter that decided "is this trace the root or a nested one?" is gone. Whether a trace is the root (filter to saved values only) vs. an inner trace (push everything to the parent) is now determined by inspecting the *target* frame's locals — looking for `__nnsight_tracing_info__` to mean "this frame is another tracer's compiled body."

Why it matters:

- The counter approach broke under user-defined context-manager wrappers around `model.trace()` / `model.session()`.
- It made multi-tenant `nnsight-serve` workers harder — each request needed its own counter scope.
- Frame-based detection is robust to both.

`save` is now mounted lazily on first `.save()` use, not on every trace enter.

> ⚠️ **Heads-up:** the frame-based detection is new code on a hot path. If you encounter a situation where a value you expected to be saved comes back missing, please [open an issue](https://github.com/ndif-team/nnsight/issues) — we'd like to track edge cases as they surface.

---

### Async Submit + `handle_response` Split

For users running NDIF jobs from inside async event loops:

- **`RemoteBackend.submit_request`** and **`get_response`** each get an `async_*` sibling using `httpx.AsyncClient`. No more thread-blocking on remote submissions in async code.
- **Submit no longer auto-dispatches `handle_response`.** The caller decides when to run side effects, so async/streaming pipelines can yield the initial response (with the assigned `job_id`) before processing it.

The contract for both sync and async paths is now: `submit_request` returns the initial `ResponseModel` with `job_id` set; the caller invokes `handle_response` when ready.

---

## Other Improvements

- **Custom context managers around `model.trace()` / `model.session()` just work.** `Tracer.capture(frame=...)` now accepts an explicit frame, so wrappers no longer confuse the AST parser into capturing the wrong `with` block:

  ```python
  from contextlib import contextmanager

  @contextmanager
  def with_logging(model, prompt):
      print(f"Tracing on {prompt!r}")
      with model.trace(prompt) as tracer:
          yield tracer
      print("done.")

  with with_logging(model, "Hello") as tracer:
      out = model.transformer.h[0].output.save()
  ```

- **`trace=False` one-shot bypass on `Envoy`-bound methods.** For methods auto-discovered through `Envoy.__getattr__` (e.g. `model.generate(...)` on `LanguageModel`), pass `trace=False` to skip the implicit `.trace(...)` capture and call the underlying method directly:

  ```python
  # No tracing — calls HF's .generate() directly.
  output = model.generate(input_ids=ids, max_new_tokens=10, trace=False)
  ```

  `_prepare_input` is intentionally not applied in the `trace=False` path, since some methods don't expect prepared inputs.

- **`Envoy.__setattr__` is symmetric with reads.** Writes to a wrapper-claimed attribute (e.g. `config`) are now mirrored to *both* the Envoy's `__dict__` (so `__dict__` short-circuit reads stay coherent) and the underlying `_module` (so `__getattr__` fall-through reads stay consistent). This had been broken since v0.6.2 — code that did `model.config = new_config` would silently see a stale value on read because `model.__dict__` had the old one and `__getattr__` was never consulted.

  ```python
  import nnsight
  model = nnsight.LanguageModel("openai-community/gpt2")

  # Modify a field on the wrapper.
  model.config.use_cache = False

  # The underlying HF model now also sees the change.
  assert model._module.config.use_cache is False
  ```

  Internal config writes now use `self.__dict__["config"] = ...` so wrapper-side bookkeeping doesn't override the underlying HF model's config.

- **Multi-invoke `Envoy.skip(...)` accumulates correctly.** Calling `.skip(value)` on the same module from multiple invokes now accumulates per-invoke values and re-concatenates them on the way out, instead of the first invoke's value clobbering the rest.

- **`tracer.cache(...)` sub-views now scope correctly.** `CacheDict` views built for a module path scope iteration / `keys` / `repr` / IPython pretty-print to that path's keys (and nested keys), instead of leaking the parent's full storage. Fixes display weirdness and double-prefix lookup bugs when caching multiple module subtrees.

- **`DiffusionModel` no longer overrides the user's `device_map`.** Removed the `device_map = "balanced" if device_map in ("auto", None) else device_map` line. Whatever the caller passes propagates through unchanged, fixing `Expected all tensors on cuda:0, got cuda:1` failures when the caller passes an explicit single-device map.

- **`MetaMixin.dispatch()` is idempotent.** Calling twice no longer re-runs the load path.

- **Friendlier errors:**
  - New `MissedProviderError` parent class; `OutOfOrderError` is now a subclass. Cleaner surface for "you accessed a module out of forward-pass order."
  - `LanguageModel`: clear error when given a multimodal config (directs to `VisionLanguageModel`).
  - `LanguageModel`: clear error for empty tokenized input.
  - **Deferred exception envelope.** Exceptions raised inside vLLM workers now propagate via a typed envelope so the client sees the original exception class name, not a dynamically-substituted wrapper. Contributed by [@khaiwang](https://github.com/khaiwang).

- **Top-level `from nnsight import save`** re-export.

- **Agent-evals harness (`tests/agent-evals/`)** — the documentation benchmark we use to measure whether agents can use, guide, and develop with nnsight given the docs we ship. Adds doc-bundle benchmarking, multiple-choice questions, a Claude Code provider for Max-subscription users, browse mode, and full-bundle study with report + plots.

---

## Documentation

- The old monolithic `CLAUDE.md` is now a thin router; the actual content moved into `docs/` and is organized by intent: `concepts/`, `usage/`, `patterns/`, `models/`, `remote/`, `errors/`, `gotchas/`, `developing/`, `reference/`.
- New developer-facing deep-dives: [`architecture-overview`](docs/developing/architecture-overview.md), [`lazy-hook-system`](docs/developing/lazy-hook-system.md), [`eproperty-deep-dive`](docs/developing/eproperty-deep-dive.md), [`source-accessor-internals`](docs/developing/source-accessor-internals.md), [`tracing-pipeline`](docs/developing/tracing-pipeline.md), [`interleaver-internals`](docs/developing/interleaver-internals.md), [`batching-internals`](docs/developing/batching-internals.md), [`serialization`](docs/developing/serialization.md), [`vllm-integration`](docs/developing/vllm-integration.md), [`performance`](docs/developing/performance.md), [`testing`](docs/developing/testing.md), [`adding-a-new-backend`](docs/developing/adding-a-new-backend.md), [`adding-a-new-runtime`](docs/developing/adding-a-new-runtime.md).
- New error and gotcha cookbooks — one page per common failure mode.

---

## Breaking Changes

1. **vLLM `.logits` / `.samples` are now `eproperty`s.**
   - Old: `model.logits.output.save()`, `model.samples.output.save()`.
   - New: `model.logits.save()`, `model.samples.save()`.
   - `model.generator` is gone.
2. **`Envoy._interleaver` is now `Envoy.interleaver`** (no underscore). Subclasses or inspection code accessing the private name need to drop the underscore.
3. **`Globals.stack`, `Globals.enter()`, `Globals.exit()` removed.** Anything calling these directly breaks. The replacement is automatic — frame-based detection.
4. **vLLM version pin lifted.** Code that pinned to `vllm==0.15.1` because of nnsight no longer needs to. nnsight is tested against vLLM ≥ 0.19; very old vLLM versions may break in unrelated ways.
5. **`OperationEnvoy` lives in `intervention/source.py`, not `intervention/envoy.py`.** Public surface (`.output`, `.input`, `.inputs`, `.source`) is the same; imports need updating.
6. **`SkipException` is gone internally.** Custom backends or runtimes that caught it should switch to inspecting kwargs for `__nnsight_skip__`.
7. **`Envoy._fake_inputs` / `Envoy._fake_output` removed.** The fake-value bookkeeping for "model didn't execute" errors is replaced by the eproperty's own error path.
8. **Diffusion `device_map` no longer remapped to `"balanced"`.** If you depended on the old behavior, pass `device_map="balanced"` explicitly.
9. **transformers ≥ 5.0 dropped `CLIPTextModel.text_model`.** Diffusion-related code that walked through `.text_model.encoder` must drop the `.text_model` segment.

## Migration

Search-and-replace:

| Old | New |
|---|---|
| `model.logits.output` | `model.logits` (vLLM) |
| `model.samples.output` | `model.samples` (vLLM) |
| `._interleaver` | `.interleaver` |
| `text_encoder.text_model.encoder` | `text_encoder.encoder` (transformers ≥ 5) |
| `from nnsight.intervention.envoy import OperationEnvoy` | `from nnsight.intervention.source import OperationEnvoy` |

If you wrote a custom backend that caught `SkipException`, switch to inspecting kwargs for `__nnsight_skip__`. If you have a custom context manager around `model.trace(...)`, you can stop hand-rolling frame walks — `Tracer.capture(frame=...)` is now part of the public API.



## New Contributors
* @khaiwang made their first contribution in https://github.com/ndif-team/nnsight/pull/638
* @gsarti made their first contribution in https://github.com/ndif-team/nnsight/pull/649

**Full Changelog**: https://github.com/ndif-team/nnsight/compare/v0.6.3...v0.7.0