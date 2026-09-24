# huggingface/transformers — last 3 releases



## v5.17.0 — 2026-09-09

# Release v5.17.0


## New Model additions

### HYV4

<img width="1503" height="827" alt="image" src="https://github.com/user-attachments/assets/e6ed85ee-eb1d-40eb-a0d4-c649f6337ca9" />


Hy4-Preview is a 780B-parameter mixture-of-experts language model that activates 49B parameters per
token. Each MoE layer holds 256 routed experts plus one always-active shared expert and routes every
token to 8 of them. The context window is 1M tokens.

The architecture combines four features:

- **Multi-head Latent Attention (MLA)** compresses keys and values into a low-rank latent
  (`kv_lora_rank`) that `kv_b_proj` expands back to one key/value per query head.
- **DeepSeek Sparse Attention (DSA)** selects `index_topk` keys per query with a lightweight indexer.
  Following [IndexShare](https://huggingface.co/papers/2603.12201), only the layers marked `"full"`
  in `indexer_types` run an indexer; `"shared"` layers reuse the previous full layer's selection.
- **Gated MLA with learnable attention sinks**, where each head owns a sink logit that participates
  in the softmax and contributes no value, as in [GPT-OSS](./gpt_oss).
- **Independent Hyper-Connections (iHC)** replace the plain residual path with `hc_mult` parallel
  residual streams that are collapsed before, and redistributed after, every sublayer.

The implementation does not execute the multi-token prediction (MTP) layers. Released checkpoints
keep those weights so that other runtimes can use them for speculative decoding; they are ignored
at load time.

**Links:** [Documentation](https://huggingface.co/docs/transformers/main/en/model_doc/hy_v4)
* Add h4 (#48473) by @ArthurZucker in [#48473](https://github.com/huggingface/transformers/pull/48473)

### VibeVoice

<img width="2140" height="1188" alt="image" src="https://github.com/user-attachments/assets/29ccea01-a855-4d4f-a6af-61bc4fc883a4" />

[VibeVoice](https://huggingface.co/papers/2508.19205) is a novel framework for synthesizing high-fidelity, long-form speech with multiple speakers by employing a next-token diffusion approach within a Large Language Model (LLM) structure. It's designed to capture the authentic conversational "vibe" and is particularly suited for generating audio content like podcasts and multi-participant audiobooks.

**Links:** [Documentation](https://huggingface.co/docs/transformers/main/en/model_doc/vibevoice)
* Implement VibeVoice  (#40546) by @pengzhiliang in [#40546](https://github.com/huggingface/transformers/pull/40546)

### NeoMME

NeoMME is a family of efficient 260M and 800M parameter multimodal-native multilingual foundation encoders from H Company. It processes multilingual text tokens and raw image patches in a single bidirectional Transformer encoder, without a separately pretrained vision tower or causal language model.

NeoMME-Retriever is a model fine-tuned from the NeoMME backbone for visual document retrieval with joint late-interaction and dense objectives. It takes text queries and documents (text or page screenshots) and produces multi-vector embeddings for MeanMaxSim scoring (late-interaction) and mean-pooled embeddings for cosine similarity (dense).

**Links:** [Documentation](https://huggingface.co/docs/transformers/main/en/model_doc/neomme)
* Add NeoMME and NeoMME-Retriever (#47992) by @tonywu71 in [#47992](https://github.com/huggingface/transformers/pull/47992)

### Fun-ASR-Nano

Fun-ASR-Nano is an 800M-parameter end-to-end speech recognition model developed by Alibaba DAMO Academy's FunAudioLLM team. It achieves state-of-the-art performance on Chinese, English, and Japanese ASR benchmarks while being significantly smaller than comparable models.

Key features are
- **Chinese, English, and Japanese**, including 7 Chinese dialects and 26 regional accents
- **Hotword customization** for domain-specific vocabulary
- **Native punctuation** output (no separate punctuation model needed)

**Links:** [Documentation](https://huggingface.co/docs/transformers/main/en/model_doc/fun_asr_nano)
* Add Fun-ASR-Nano model (#46180) by @LauraGPT in [#46180](https://github.com/huggingface/transformers/pull/46180)

### KimiLinear

Kimi Linear is a hybrid linear attention architecture from Moonshot AI, introduced in
[Kimi Linear: An Expressive, Efficient Attention Architecture](https://huggingface.co/papers/2510.26692).

At its core is **Kimi Delta Attention (KDA)**, a refinement of [Gated DeltaNet](https://huggingface.co/papers/2412.06464)
that gives each key channel its own forget gate, so the recurrent state decays per channel instead of per head. KDA is
used in most layers; every fourth layer keeps a full-attention block that reuses DeepSeek-V3's Multi-head Latent
Attention (MLA), and the feed-forward blocks are DeepSeek-V3-style MoE with a shared expert.

**Links:** [Documentation](https://huggingface.co/docs/transformers/main/en/model_doc/kimi_linear)
* Kimi linear (#48250) by @remi-or in [#48250](https://github.com/huggingface/transformers/pull/48250)

### Canary

Canary-1B-v2, a fast, robust multilingual model for Automatic Speech Recognition (ASR) and Speech-to-Text Translation (AST):

Canary reuses the [Fast Conformer](https://huggingface.co/papers/2305.05084) encoder from [Parakeet](./parakeet.md) (loaded through [`ParakeetEncoder`] / [`ParakeetEncoderConfig`]) and pairs it with a Transformer decoder that uses fixed sinusoidal positional embeddings, cross-attention to the encoder outputs and tied input/output embeddings. The task is selected through a decoder prompt prefix built by [`CanaryProcessor`] of the form `<|startofcontext|> <|startoftranscript|> <|emo:undefined|> <source_lang> <target_lang> <pnc|nopnc> <|noitn|> <|notimestamp|> <|nodiarize|>`, where `source_lang == target_lang` selects transcription and otherwise selects translation.

**Links:** [Documentation](https://huggingface.co/docs/transformers/main/en/model_doc/canary)
* model: Add NVIDIA Canary-1B-v2 to Transformers (#46825) by @harshaljanjani in [#46825](https://github.com/huggingface/transformers/pull/46825)


### NeuCodec

The NeuCodec model was proposed in [Finite Scalar Quantization Enables Redundant and Transmission-Robust Neural Audio Compression at Low Bit-rates](https://huggingface.co/papers/2509.09550).

NeuCodec is a neural audio codec extending on XCodec2. It takes advantage of the following features:

- Finite Scalar Quantization (FSQ) quantisation resulting in a **single codebook**, making it ideal for downstream modeling with Speech Language Models.
- Trained with CC data such that there are **no Non-Commercial data restrictions**.
- At 50 tokens/sec and 16 bits per token, the overall bit-rate is **0.8kbps**.
- The codec takes in 16kHz input and outputs **24kHz** using an **upsampling decoder**.
- The FSQ encoding scheme allows for bit-level error resistance suitable for unreliable and noisy channels.

**Links:** [Documentation](https://huggingface.co/docs/transformers/main/en/model_doc/neucodec)
* Add support for NeuCodec (#47143) by @harryjulian in [#47143](https://github.com/huggingface/transformers/pull/47143)



## Breaking changes

Vision rotary embeddings (2D/3D) have been standardized into a unified RoPE frequency computation module, so users with custom vision models relying on attention-layer-level or model-specific RoPE grid interleaving logic must migrate to the new centralized `modeling_rope_utils.py` implementation.
* :rotating_light: Vision (2d/3d) rotary embeddings  (#48105) by @zucchini-nlp



## Generation

Generation improvements include a performance optimization that avoids unnecessary accelerator synchronization on every decode step (reducing per-step overhead), and a fix to prevent unconditional downloading of remote hub files during generation. Several correctness fixes were also applied, including enforcing auto-compile cache checks for encoder-decoder models, standardizing `past_key_values` naming in AfMoE, and resolving flaky export and integration test failures.


* [`Generate`] Avoid unconditionally downloading remote hub file (#48620) by @vasqu in [#48620]
* [generate] stop synchronizing the accelerator on every decode step (#47975) by @SunMarc in [#47975]
* [AfMoE] Standardize past_key_values argument naming across forward and generate (#48430) by @shenhuaqingshi in [#48430]
* Fix MTP generation test regex gate for escaped layer ignore keys (#48003) (#48262) by @Noxtimo in [#48262]
* fix(generation): Enforce the auto-compile cache check for encoder-decoder models (#48364) by @harshaljanjani in [#48364]
* [serge] Fix 4 integration tests for model `generation` failing with `output_mismatch` (list output differs (4)) (#48133) by @sergereview[bot] in [#48133]
* [VibeVoice] Skip generate export tests (flaky) (#48396) by @ydshieh in [#48396]


## Cache

Fixed several cache-related bugs, including a quantized cache issue in VibeVoice, incorrect rejection of non-static cache implementations in VoxtralRealtime, missing auto-compile cache checks for encoder-decoder models, and a silent failure when paged attention is called without a cache. Documentation was also updated to clarify `ContinuousBatchingConfig` usage and sliding window model limitations.


* vibevoice: fix bug for quant cache (#48487) by @kaixuanliu in [#48487]
* Fix VoxtralRealtime rejecting non-static cache implementations (#48082) by @jiqing-feng in [#48082]
* Raise when a paged attention forward is called with no cache (#48297) by @qgallouedec in [#48297]
* [docs] Pass ContinuousBatchingConfig and sliding window models  (#48381) by @stevhliu in [#48381]
* Retry get_daily_ci_runs on stale GitHub API cache (#48374) by @ydshieh in [#48374]


## Kernels

Kernel support was improved with fixes for nested FLA kernel imports when only `fla-core` is installed, a warning when hub-kernel functions silently fall back to slower pure-PyTorch reference implementations, and the ability to register standalone functions (e.g., RoPE) in `KernelConfig` with optional non-inheritance of default mappings. Additional fixes include corrected repository paths for ESMFold2 kernels and updated documentation for `KernelConfig` customization.


* Support nested FLA kernel imports for fla-core (#48221) by @DimensionSTP in [#48221]
* Warn once when a hub-kernel function falls back to its reference PyTorch path (#48185) by @qgallouedec in [#48185]
* [docs] Kernel updates (#48465) by @stevhliu in [#48465]
* [`Kernels`] Enable functions into kernels registry and allow non inheritance (#48443) by @vasqu in [#48443]
* Fix kernel commit and repo paths for ESMFold2 (#48186) by @Rocketknight1 in [#48186]


## Quantization

Fixed several quantization bugs, including a quant cache issue in VibeVoice, incorrect FP8 embedding handling for Qwen models, missing FP8 tensor parallelism layer overrides, and unnecessary MXFP4 weight dequantization on XPU devices.


* fix qwen4exp-fp8 ple embedding (#48368) by @JJJYmmm in [#48368]
* Keep MXFP4 weights quantized on XPU when use_kernels is set (#47923) by @jiqing-feng in [#47923]
* Fix missing FP8 TP layer overrides (#48343) by @changwangss in [#48343]


## Bugfixes and improvements

* MRoPE continued (#48594) by @zucchini-nlp in [#48594]
* [fix] Update stale expected strings in HunYuanVL integration tests (#48646) by @ydshieh in [#48646]
* [Quantizaiton]support 5/6/7 bits in AutoRound (#48481) by @wenhuach21 in [#48481]
* [fix] Update stale golden values and fix expected_logits shape in FlavaForPreTraining integration tests (#48639) by @ydshieh in [#48639]
* Fix YOLOS device mismatch with device_map="auto" (#46886) by @swankystark in [#46886]
* Honor `shift_labels` in decoder-only LLM/VLM losses (#48493) by @qgallouedec in [#48493]
* [KimiLinear] Fix test_cpu_offload: set num_local_experts=4 in model tester (#48624) by @ydshieh in [#48624]
* [docs] Per-layer config (#48601) by @stevhliu in [#48601]
* Fix `generate_flags` parsing in `transformers chat` (#48597) by @SunMarc in [#48597]
* [fix] Fix how we read package versions - triggered by torch 2.14+ (#48615) by @ydshieh in [#48615]
* [Docker] Upgrade CPU torch to <=2.14.0, torchcodec to <=0.16.0 (#48614) by @ydshieh in [#48614]
* Fix AttributeError in gradient_checkpointing_enable(offload=True) (#48590) by @tarekziade in [#48590]
* Another day fixing CI (#48591) by @zucchini-nlp in [#48591]
* esmfold2: keep `distogram_head` in fp32 as well (#48488) by @kaixuanliu in [#48488]
* Add `supports_context_parallel` to `PreTrainedModel` (#48442) by @qgallouedec in [#48442]
* [docs] mlinter reference (#48460) by @stevhliu in [#48460]
* [docs] Add a LiteRT page under community integrations (#48540) by @john-rocky in [#48540]
* [GLM 5.3 Flash] Fix NaN gradients in chunked KDA (#48455) by @imvladikon in [#48455]
* [docs] Fix [[autodoc]] directives in ALBERT model documentation (#48593) by @samyuktahegde in [#48593]
* [Fix] Fix A10 expectations for a test (#48454) by @remi-or in [#48454]
* Add PR comment CI for AMD (MI300) (#48065) by @ydshieh in [#48065]
* docs: fix docstring parameter names that do not match signatures (#48575) by @simpleqt in [#48575]
* docs: remove phantom parameters from docstrings (#48576) by @simpleqt in [#48576]
* extend some case to xpu as well (#48502) by @sywangyi in [#48502]
* [serge] Fix 2 integration tests for model `glm4_moe` failing with `OOM` (other (2)) (#48551) by @sergereview[bot] in [#48551]
* [serge] Fix 2 integration tests for model `nemotron` failing with `import_or_config` (other (2)) (#48582) by @sergereview[bot] in [#48582]
* Compress the agent conventions file and document two modular pitfalls (#48586) by @tarekziade in [#48586]
* Guard against a None video processor class when the backend is unavailable (#48557) by @caiotheodoro in [#48557]
* [serge] Fix 2 integration tests regressed by commit 83d46aa2a2c4 (PR #47625) (#48580) by @sergereview[bot] in [#48580]
* [nit] use requires_backends (#47576) by @eustlb in [#47576]
* [serge] Fix 2 integration tests for model `kosmos2` failing with `import_or_config` (other (2)) (#48552) by @sergereview[bot] in [#48552]
* Fix failing tests for cohere_compass (#48005) by @kaixuanliu in [#48005]
* [Fix] Use dedicated helpers for DeepGEMM and SonicMoE tests (#48523) by @remi-or in [#48523]
* CI: Point test fixtures at hf-internal-testing copies we already host (#48521) by @tarekziade in [#48521]
* fix failed test cases for glm5_next (#48497) by @kaixuanliu in [#48497]
* Pass kwargs to the Mamba2 mixer in Nemotron-H, Falcon-H1 and Mamba2 (#48490) by @kfastino in [#48490]
* Retire test_multi_gpu_data_parallel_forward (#48508) by @tarekziade in [#48508]
* Processing tests [part 2] (#47922) by @zucchini-nlp in [#47922]
* QA: Add noisy comment checker (#48484) by @tarekziade in [#48484]
* Allow nested rope params for tiny models (#48435) by @zucchini-nlp in [#48435]
* Fix sliding-window mask `layer_idx` in Gemma3/Gemma4 `create_masks_for_vision_model` (#48482) by @jiqing-feng in [#48482]
* add xpu expectations for hunyuan_vl model tests (#48504) by @kaixuanliu in [#48504]
* [`Qwen 3.5 Moe`] Fix decorators (#48436) by @vasqu in [#48436]
* Infinite loop in dependency search (#48393) by @zucchini-nlp in [#48393]
* [serge] Fix 2 integration tests for model `fsmt` failing with `output_mismatch` (tensor values differ (2)) (#48496) by @sergereview[bot] in [#48496]
* Fix some tests by removing the deprecation cycle (#48503) by @Cyrilvallez in [#48503]
* Remove deprecation (#48500) by @Cyrilvallez in [#48500]
* Fix Pix2StructTextAttention init using hidden_size instead of d_kv (#47558) by @<NOT FOUND> in [#47558]
* Fix pre patch release utility (#48499) by @Cyrilvallez in [#48499]
* Update dev version (#48498) by @Cyrilvallez in [#48498]
* Fix Inkling inputs_embeds and add more tests (#47827) by @Cyrilvallez in [#47827]
* Simplify and fix qwen4 tests (#48340) by @Cyrilvallez in [#48340]
* [docs] Partial checkpointing and group_by_length (#48463) by @stevhliu in [#48463]
* doc: fix syntax error and typos in VibeVoice documentation (#48489) by @VimalN2005 in [#48489]
* [`Qwen4 Exp`] Use partial to avoid skipping mask more easily (#48456) by @vasqu in [#48456]
* Add support for NeuCodec (#47143) by @harryjulian in [#47143]
* [serge] Fix 1 integration tests regressed by commit bd9509355c8a (PR #47493) (#48426) by @sergereview[bot] in [#48426]
* Fix rotary embedding regression (#48477) by @Cyrilvallez in [#48477]
* Remove deprecated mask functions (#48476) by @Cyrilvallez in [#48476]
* [MTP] Save memory by only capturing the last layer's hidden_states (#48475) by @Cyrilvallez in [#48475]
* Allow capturing only necessary hidden_states with capture_outputs (#48081) by @sywangyi in [#48081]
* Support per-layer MTP configuration (#48264) by @eladsegal in [#48264]
* [docs] Fix code snippets (#47772) by @stevhliu in [#47772]
* [Fix] Sparse TikToken tokenizers silently fail (#48446) by @remi-or in [#48446]
* No inherit decorator for NeoMME (#48457) by @zucchini-nlp in [#48457]
* Batch Rebalance Data Sampler (#47340) by @delock in [#47340]
* [serge] Fix 2 integration tests for model `cwm` failing with `import_or_config` (other (2)) (#48414) by @sergereview[bot] in [#48414]
* fix: Add DEIMv2 attribution (#48448) by @harshaljanjani in [#48448]
* [fix] inkling: mps + cuda mel spec extraction (#47432) by @eustlb in [#47432]
* fix: decode() batch path respects self.clean_up_tokenization_spaces (#47793) by @lorenzozanee in [#47793]
* Grounding dino fp16 dtype [backlog] (#48438) by @molbap in [#48438]
* Init the process group with a load-scaled timeout for sharded loading (#48228) by @qgallouedec in [#48228]
* Raise a clear error when a token is both forced and suppressed (#47511) by @qgallouedec in [#47511]
* Clarify device placement in pipelines (#47367) by @LysandreJik in [#47367]
* Add offload to gradient checkpointing (#48444) by @qgallouedec in [#48444]
* [MiniCPMV4_6] Update test_small_model_vision_generation_batch expected output (value drift) (#48406) by @ydshieh in [#48406]
* [serge] Fix 2 integration tests for model `hyperclovax` failing with `other` (other (2)) (#48440) by @sergereview[bot] in [#48440]
* fix(models): Drop the position-indexed token type lookup in RoPE encoders (#48407) by @harshaljanjani in [#48407]
* Document image_hidden_states/pixel_values mutual exclusivity for SmolVLM/Idefics2/Idefics3 (#47714) by @verma8076 in [#47714]
* Re-order a bit for easier navigation (#48434) by @zucchini-nlp in [#48434]
* Deprecated stuff gone (#48367) by @zucchini-nlp in [#48367]
* [serge] Fix 6 integration tests for model `seamless_m4t_v2` failing with `other` (other (6)) (#48425) by @sergereview[bot] in [#48425]
* [Docs]: Update GLM 5.3 (#48401) by @Dovis01 in [#48401]
* Avoid print to stdout that fails the job `check_failed_tests` job (#48391) by @ydshieh in [#48391]
* Fix incorrect tuple return annotations on forward methods returning a Tensor (#48359) by @Gronoxx in [#48359]
* Fix interval merge invariant in _find_disjoint (#47860) by @sharmax-vikas in [#47860]
* skip mtp slow tests for now (#48328) (#48329) by @tarekziade in [#48329]
* Update Tailscale action version in workflow (#48394) by @glegendre01 in [#48394]
* fix some failure in xpu (#48252) by @sywangyi in [#48252]
* [Improvement] Make gated delta rule more explicit  (#47625) by @remi-or in [#47625]
* [CB] Fix wrong device scoping (#48370) by @remi-or in [#48370]
* Bump transformers-mlinter to 0.1.5 and clear the new findings (#48259) by @tarekziade in [#48259]
* fix: flash-attn fallback failing on torch2.13 (#48388) by @NanoCode012 in [#48388]
* [LongcatFlash] Fix test_longcat_generation_cpu: use device_map="cpu" to avoid MoE disk offload issue (#48377) by @ydshieh in [#48377]
* [Qwen3VLMoe] Update `test_small_model_integration_test_batch` expected output (value drift) (#48376) by @ydshieh in [#48376]
* [ONNX] Skip affected models on torch 2.13 (two dynamo regressions) (#48191) by @ydshieh in [#48191]
* Fix `safe_open` mmap memory exhaustion on Windows by using `pread` backend (#48341) by @eryk-roch in [#48341]
* Fix Zamba2 construction for num_mem_blocks > 1 checkpoints (#48325) by @john-rocky in [#48325]
* [Docs] Change 5.3 Flash pos in toc (#48366) by @Dovis01 in [#48366]
* [conftest] Use get_cpu_ram_total_gib for psutil patch (cgroup-aware) (#48290) by @ydshieh in [#48290]
* Fix flaky test_training_gradient_checkpointing for BigBirdPegasus (fp noise filter) (#48332) by @ydshieh in [#48332]
* Quiet continuous batching at default verbosity (#48314) by @qgallouedec in [#48314]
* Wait for the first request in the async continuous batching bootstrap (#48304) by @qgallouedec in [#48304]
* Ignore a stale best checkpoint recorded in a resumed trainer state (#48319) by @VaggelisGian in [#48319]
* [docs] Fix links and remove TokenizerFast (#47748) by @stevhliu in [#47748]
* Fix incorrect token classification prefix for ESMC (#48348) by @Rocketknight1 in [#48348]
* Create the continuous batching CPU group with local synchronization (#48302) by @qgallouedec in [#48302]
* Resolve continuous batching config against the text config for composite models (#48299) by @qgallouedec in [#48299]
* [`CI`] Unblock fast CI for now (failing tests) (#48344) by @vasqu in [#48344]
* [qwen4_exp] disable torch/onnx export tests due to data-dependent control flow (#48345) by @ydshieh in [#48345]
* [debug] Trace previous CI run selection in get_previous_daily_ci.py (#48338) by @ydshieh in [#48338]
* Normalize HunYuanVL's legacy field aliases via attribute_map (#48261) by @hmellor in [#48261]

## Significant community contributions

The following contributors have made significant changes to the library over the last release:

* @ydshieh
    * [fix] Update stale expected strings in HunYuanVL integration tests (#48646)
    * [fix] Update stale golden values and fix expected_logits shape in FlavaForPreTraining integration tests (#48639)
    * [tests] Fix integration test golden values broken by fast image processor default (PR #41388) (#48637)
    * [KimiLinear] Fix test_cpu_offload: set num_local_experts=4 in model tester (#48624)
    * Fix GPU memory teardown in CLI serve tests (#48618)
    * [fix] Fix how we read package versions - triggered by torch 2.14+ (#48615)
    * [Docker] Upgrade CPU torch to <=2.14.0, torchcodec to <=0.16.0 (#48614)
    * Add PR comment CI for AMD (MI300) (#48065)
    * [MiniCPMV4_6] Update test_small_model_vision_generation_batch expected output (value drift) (#48406)
    * Avoid print to stdout that fails the job `check_failed_tests` job (#48391)
    * [VibeVoice] Skip generate export tests (flaky) (#48396)
    * [LongcatFlash] Fix test_longcat_generation_cpu: use device_map="cpu" to avoid MoE disk offload issue (#48377)
    * [Qwen3VLMoe] Update `test_small_model_integration_test_batch` expected output (value drift) (#48376)
    * [ONNX] Skip affected models on torch 2.13 (two dynamo regressions) (#48191)
    * Retry get_daily_ci_runs on stale GitHub API cache (#48374)
    * [conftest] Use get_cpu_ram_total_gib for psutil patch (cgroup-aware) (#48290)
    * Fix flaky test_training_gradient_checkpointing for BigBirdPegasus (fp noise filter) (#48332)
    * [qwen4_exp] disable torch/onnx export tests due to data-dependent control flow (#48345)
    * [debug] Trace previous CI run selection in get_previous_daily_ci.py (#48338)
* @LauraGPT
    * Add Fun-ASR-Nano model (#46180)
* @tarekziade
    * Fix AttributeError in gradient_checkpointing_enable(offload=True) (#48590)
    * Compress the agent conventions file and document two modular pitfalls (#48586)
    * CI: Point test fixtures at hf-internal-testing copies we already host (#48521)
    * Retire test_multi_gpu_data_parallel_forward (#48508)
    * QA: Add noisy comment checker (#48484)
    * skip mtp slow tests for now (#48328) (#48329)
    * Bump transformers-mlinter to 0.1.5 and clear the new findings (#48259)
* @remi-or
    * [Fix] Fix A10 expectations for a test (#48454)
    * Kimi linear (#48250)
    * [Fix] Use dedicated helpers for DeepGEMM and SonicMoE tests (#48523)
    * [Fix] Sparse TikToken tokenizers silently fail (#48446)
    * [Improvement] Make gated delta rule more explicit  (#47625)
    * [CB] Fix wrong device scoping (#48370)
    * [CB] Fail faster (#48334)
* @ArthurZucker
    * Add h4 (#48473)
* @harryjulian
    * Add support for NeuCodec (#47143)
* @delock
    * Batch Rebalance Data Sampler (#47340)
* @harshaljanjani
    * fix: Add DEIMv2 attribution (#48448)
    * model: Add NVIDIA Canary-1B-v2 to Transformers (#46825)
    * fix(generation): Enforce the auto-compile cache check for encoder-decoder models (#48364)
    * fix(models): Drop the position-indexed token type lookup in RoPE encoders (#48407)
* @tonywu71
    * Add NeoMME and NeoMME-Retriever (#47992)
* @Dovis01
    * [Docs]: Update GLM 5.3 (#48401)
    * [Docs] Change 5.3 Flash pos in toc (#48366)
    * [Glm 5.3 Flash] GLM 5.3 Flash Support (#48342)
* @pengzhiliang
    * Implement VibeVoice  (#40546)


## v5.16.1 — 2026-08-26

# Release v5.16.1

This is a special release as we include GLM! (and a few small fixes)

# GLM-5.3-Flash

<img width="4239" height="2643" alt="image" src="https://github.com/user-attachments/assets/17bc9c29-758b-44c8-8230-42f945ded209" />

GLM-5.3-Flash, the first **natively multimodal model** in the GLM-5 series. With 320B total parameters and just 18B active parameters, it outperforms GLM-5.2 across benchmarks and real-world workloads at one-tenth the price, while approaching Claude Opus 4.8 on coding and agentic benchmarks.

GLM-5.3-Flash starts from a newly trained base model, with its architecture and training recipe redesigned around capability and efficiency. For the first time in the GLM series, we introduce a hybrid architecture combining sparse and linear attention, sharply reducing long-context serving costs while preserving precise long-context capabilities. The model also adopts Manifold-Constrained Hyper-Connections (mHC) to further improve scaling efficiency. Together with our latest **30T-token** multimodal pre-training corpus, these changes enable GLM-5.3-Flash to deliver more intelligence with less compute.

**Links:** [Documentation](https://huggingface.co/docs/transformers/main/en/model_doc/glm5_next)
* [Glm 5.3 Flash] GLM 5.3 Flash Support (#48342) by @Dovis01 in [#48342](https://github.com/huggingface/transformers/pull/48342)


## Small patch fixes

Mainly BC behavior for TP and pinning a hf kernel for security reasons :hugs: 

- Restore BC for the tensor-parallel API (#48300) by @ArthurZucker 
- Fix kernel commit and repo paths for ESMFold2 (#48186) by @Rocketknight1 

**Full Changelog**: https://github.com/huggingface/transformers/compare/v5.16.0...v5.16.1


## v5.16.0 — 2026-08-26

# Release v5.16.0


## New Model additions

### Qwen4-Exp

<img width="2241" height="693" alt="image" src="https://github.com/user-attachments/assets/c838b5ba-ffea-42da-baa9-3f66178e3671" />

Qwen4-Exp builds on Qwen3.5's hybrid text and multimodal architecture with three key components: GatedResidual (GR), Qwen Sparse Attention (QSA), and Per-Layer Embedding (PLE).

GR is a Qwen-developed residual architecture that combines Hyper-Connection with GatedNorm. It mixes multiple residual streams with fine-grained elementwise gating before each attention and Mixture-of-Experts (MoE) block, then controls how much of the block output is injected back into each stream.

QSA uses multiple query heads to score compressed key blocks, selects the most relevant contiguous token blocks, and keeps the incomplete trailing block uncompressed. This block-level selection reduces indexing overhead and improves memory locality for long sequences. Combined with Gated DeltaNet, QSA makes Qwen4-Exp the first hybrid architecture to integrate linear and sparse attention, substantially improving inference efficiency for long-context workloads.

PLE enriches selected decoder layers with layer-specific lexical features derived from hashed token n-grams and a dilated depthwise convolution.

**Links:** [Documentation](https://huggingface.co/docs/transformers/main/en/model_doc/qwen4_exp)
* Add Qwen4Exp model (#48337) by @Cyrilvallez in [#48337](https://github.com/huggingface/transformers/pull/48337)

### GraniteSpeech5

<img width="1600" height="1440" alt="image" src="https://github.com/user-attachments/assets/106ef712-9f45-43c9-98b7-ce6e4a7c136d" />

Granite Speech 5.0 Turbo CTC is a lightweight (~470M parameters) conformer encoder for automatic speech recognition, trained with Connectionist Temporal Classification (CTC) on BPE targets. It is a fast, encoder-only member of the [Granite Speech](https://huggingface.co/papers/2505.08699) family: transcription requires a single forward pass followed by greedy CTC decoding, with no autoregressive decoder.

Architecturally, it extends the Granite Speech conformer CTC encoder with:

1. **Frame stacking + block-wise time subsampling**: the feature extractor stacks pairs of log-mel(+delta) frames (2x), and the first two conformer blocks each subsample time by 2 through a stride-2 depthwise convolution (with a mean-pooled residual), for a total 8x time reduction at 10 ms mel hop.

2. **Block attention with Shaw's relative positional embeddings**: attention is computed over fixed-size blocks (the sequence is right-padded to a whole number of blocks, with padded frames masked out), using separate bias-free query/key/value projections.

3. **Self-conditioned CTC**: the CTC posteriors of the middle layer are projected and fed back into the hidden states, and the CTC head is shared between this mid-layer self-conditioning and the final prediction.

**Links:** [Documentation](https://huggingface.co/docs/transformers/main/en/model_doc/granite_speech5)
* Add Granite Speech 5.0 - (#48288) by @eustlb in [#48288](https://github.com/huggingface/transformers/pull/48288)

### Step3p7

Step-3.7-Flash was proposed in [Step 3.7 Flash](https://static.stepfun.com/blog/step-3.7-flash/) by StepFun. It is a 198B-parameter sparse Mixture-of-Experts vision-language model, pairing a 196B-parameter MoE language backbone with a 1.8B-parameter vision encoder for native image understanding.

StepFun hasn't published a technical report for Step-3.7-Flash, so the details below are drawn from the released checkpoint's configuration rather than a paper.

- **Sparse MoE decoder**: all but the first 3 decoder layers route through a MoE block of 288 routed experts (top-8 per token) plus a single shared expert. The router scores experts with a sigmoid and a learned per-expert bias instead of an auxiliary load-balancing loss, the same strategy as [DeepSeek-V3](./deepseek_v3).
- **Gated attention**: each attention layer adds an extra projection whose sigmoid output gates the attention output per head, before the output projection — the same *Gated Attention* mechanism used in [Qwen3-Next](./qwen3_next). A subset of layers use fewer heads and a sliding window instead of full attention.
- **Multi-token prediction**: some checkpoints ship extra decoder layers trained for multi-token prediction, which [`~GenerationMixin.generate`] can use for speculative decoding via `use_mtp=True`.
- **Vision encoder**: a SigLIP-style ViT with 2-D rotary position embeddings and a learned per-layer scale on the attention and MLP branches. Its output is downsampled 4x by two stride-2 convolutions before a linear projector maps it into the text model's hidden size.
- **Dynamic image tiling**: instead of a fixed tile grid, the image processor picks its tiling window from each image's own aspect ratio, producing one downscaled global view plus zero or more local high-resolution crops per image.

**Links:** [Documentation](https://huggingface.co/docs/transformers/main/en/model_doc/step3p7)
* [new model] step 3.7 (#46658) by @itazap in [#46658](https://github.com/huggingface/transformers/pull/46658)

### CohereCompass

CohereCompass is the base architecture for small, specialized (vision-)language models trained by Cohere.

**Links:** [Documentation](https://huggingface.co/docs/transformers/main/en/model_doc/cohere_compass)
* Add CohereCompass modeling (#47878) by @calpt in [#47878](https://github.com/huggingface/transformers/pull/47878)



### ESMC and ESMFold2

ESMC and ESMFold2 are new state-of-the-art protein language and folding models from BioHub. ESMC is trained with a masked language modeling objective, and it can be easily transferred to sequence and token classification tasks for proteins. Checkpoints exist in various sizes, from 300M parameters up to 6B parameters. It works as a drop-in replacement for older ESM-2 and ESM-3 models, with significantly higher accuracy.

ESMFold2 is a state-of-the-art protein folding model which produces high accuracy predictions. It uses an iterated diffusion approach that is significantly different from the original ESMFold, offering huge improvements in accuracy for more complex structures.


**Links:** [Documentation ESMC](https://huggingface.co/docs/transformers/main/en/model_doc/esmc), [Documentation ESMFold2](https://huggingface.co/docs/transformers/main/en/model_doc/esmfold2)
* Port ESMC and ESMFold2 to Transformers (#46419) by @Rocketknight1 in [#46419](https://github.com/huggingface/transformers/pull/46419)


## Breaking changes

The legacy tensor-parallel implementation has been replaced with a DTensor-native backend, so users relying on the previous TP API for inference or training must migrate to the new DTensor-based interface.
* 🚨 TP dtensor API inference + training (#47579) by @3outeille

`attn_implementation="sdpa"` dispatch is now properly supported for wav2vec2_conformer, wav2vec2-bert, and SeamlessM4T/v2 models, which may change initialization behavior for users who previously worked around this limitation.
* 🚨[wav2vec2] Support attn_implementation=sdpa dispatch (#46196) by @YangKai0616

`FuyuProcessor` no longer returns the `image_patch_indices` output, so any code that depends on this field must be updated to remove references to it.
* :rotating_light: Leftover processors (#47924) by @zucchini-nlp



## Cache

Several cache-related bugs were fixed in this release, including an off-by-one error in the sliding window cache, Whisper speculative decoding cache corruption, CpmAnt use-cache failures, Qwen2.5-Omni/Qwen3-Omni-MoE generation with compilable caches, and compressed-tensors loading for KV-cache-only quantized models. Documentation was also added for cache token removal using negative values, and per-layer cache configuration support (allowing models to use different cache settings per layer) was introduced.


* Cpmant fix use cache (#48013) by @jiqing-feng in [#48013]
* [docs] Cache crop (#47950) by @stevhliu in [#47950]
* Revert "Support per-layer cache configuration and attention-mask selection" (#48175) by @Cyrilvallez in [#48175]
* Support per-layer cache configuration and attention-mask selection (#47901) by @eladsegal in [#47901]
* Fix Qwen2.5-Omni / Qwen3-Omni-MoE generation with a compilable cache (#47872) by @jiqing-feng in [#47872]
* Fix sliding window cache index off-by-one on wraparound (#47708) by @hameedibrh in [#47708]
* [Whisper] Fix speculative decoding: UnboundLocalError, cache corruption, and speed regression (#48000) by @ydshieh in [#48000]
* Fix compressed-tensors loading for KV-cache-only quantized models (#47904) by @kylesayrs in [#47904]


## Generation

This release fixes several generation bugs across multiple models, including Whisper speculative decoding issues (UnboundLocalError, cache corruption, speed regression, and left-padded batch position IDs), broken image generation in Emu3, garbage output in OLMo/GPTNeoX, and Qwen2.5-Omni/Qwen3-Omni-MoE generation with compilable caches. Additionally, logit distributions for candidate generators using sampling are now aligned by returning logits after applying logit processors.


* [Whisper] Fix speculative decoding: preserve cleared suppress tokens through super().generate() (#48108) by @ydshieh in [#48108]
* [Whisper] Fix decoder position IDs for left-padded batches in longform generation (#48028) by @ydshieh in [#48028]
* [serge] Fix 2 integration tests for model `generation` failing with `import_or_config` (other (2)) (#48061) by @sergereview[bot] in [#48061]
* Align logit distributions for CandidateGenerators using sampling (#48007) by @Cyrilvallez in [#48007]
* [GPTNeoX] Fix post_processor not overridden when loading from pretrained (OLMo garbage generation) (#47988) by @ydshieh in [#47988]
* [emu3] 🦮 Black Labrador is back! Fix image generation broken since #37033 (#47948) by @ydshieh in [#47948]


## Attention

Several attention-related bug fixes were made in this release, including correcting a SigLIP2 documentation typo, fixing Flash/SDPA attention dispatch tests for xcodec2 and ROCm RDNA GPUs, resolving a GPT2 cross-attention mask being silently discarded, and enabling SDPA support declaration in `TimmWrapper`. Per-layer cache configuration and attention-mask selection support was also introduced, allowing models with heterogeneous layer configurations to use distinct `sliding_window`, `attention_chunk_size`, and `number_of_conv_states` values per layer.


*  doc: Fix typo in SigLIP2 Flash Attention code example (#48197) by @VimalN2005 in [#48197]
* [xcodec2] Fix flex attention and flash dispatch tests (#48244) by @jiqing-feng in [#48244]
* Fix ROCm SDPA-flash skip guard that crashes on RDNA GPUs (#47965) by @Abdennacer-Badaoui in [#47965]
* [GPT2] Fix encoder_attention_mask being silently discarded in cross-attention (#47946) by @DavidJohnQuinlan in [#47946]
* Declare sdpa support in `TimmWrapper` (#47939) by @jiqing-feng in [#47939]


## Quantization

Quantization improvements include adding NVFP4 quantization support via HF kernels (enabling on-the-fly BF16 weight quantization with ~50% memory reduction), and fixing several bugs: reverting a regression in `is_quantization_compressed` that caused incorrect module layouts for packed-format checkpoints, fixing CLIP weight initialization failures with quantized checkpoints, and restoring KV-cache quantization setup for KV-cache-only quantized models.


* Revert "[Quantization]: Refactor is_quantization_compressed for format-based detection" (#48072) by @subin9 in [#48072]
* feat: add nvfp4 quantization (#47883) by @drbh in [#47883]
* [DeepSeekV2] Fix integration tests OOM: use device_map=auto instead of 8-bit quantization (#47991) by @ydshieh in [#47991]
* Fix CLIP _init_weights when a child module carries quantized weights (#47921) by @Bluear7878 in [#47921]


## Parallelization

Introduced a naive pipeline parallel inference engine supporting tied/untied weight embeddings with seamless `generate()` integration, while restoring backward compatibility for the tensor-parallel API with a deprecation cycle for `tp_plan` in `from_pretrained()`. Additionally fixed a model parallel bug in the BLT model affecting beam search.


* Restore BC for the tensor-parallel API (#48300) by @ArthurZucker in [#48300]
* fix bug for blt model parallel bug (#48327) by @kaixuanliu in [#48327]
* Pipeline parallel naive inference (#47289) by @3outeille in [#47289]


## Kernels

Kernel support was improved with documentation updates highlighting supported models, a fix for export crashes on kernel-decorated functions by adding a `is_torchdynamo_exporting` guard, and the default Flash Attention 2 hub kernel version was bumped to v3 to resolve compatibility issues with newer PyTorch versions.


* [docs] Kernel supported models (#48258) by @stevhliu in [#48258]
* [Fix] Export crashes on kernel-decorated function (#47808) by @remi-or in [#47808]
* Bump default flash-attn2 hub kernel version to v3 (#47863) by @jiqing-feng in [#47863]


## Bugfixes and improvements

* Fix video-llama modular conversion (#48336) by @zucchini-nlp in [#48336]
* CI: gate the hunyuan-moe slow test  (#48330) by @tarekziade in [#48330]
*  Add a regression test for force_accelerate_hooks signature preservation  (#48260) by @wtdcode in [#48260]
* Add an opt-in per-frame pixel cap (cap_pixels_per_frame) to the Qwen3-VL video processor (#48071) by @dkrisman in [#48071]
* Fix `scores` type in stopping criteria docstrings (#47676) by @qgallouedec in [#47676]
* Docstring check didn't match some file - fix it (#48121) by @zucchini-nlp in [#48121]
* Add shared ImageProcessingTester (#47745) by @guarin in [#47745]
* Fix AutoTokenizer returning TokenizersBackend for DeepSeek-R1-Distill-Qwen models (#48211) by @ydshieh in [#48211]
* [docs] Fix failing doctests (#47687) by @stevhliu in [#47687]
* Fix build_2d_sinusoidal_position_embedding on MPS (#47897) by @guarin in [#47897]
* [Gemma4] Investigate flaky test_generation_beyond_sliding_window_1_eager (#48236) by @ydshieh in [#48236]
* Let gradient checkpointing skip layers with every_n_layers (#48200) by @qgallouedec in [#48200]
* Disable daily nightly CI (#48292) by @remi-or in [#48292]
* gs (#48288) by @eustlb in [#48288]
* CI: fix muse OOMs (#48284) by @tarekziade in [#48284]
* Fix `BayesianDetectorModel.from_pretrained()` by calling `post_init()` (#48254) by @woojinpaik in [#48254]
* [Fix] Avoid duplicating tests in CI (#48287) by @remi-or in [#48287]
* [`GDN`] Fix recurrent FLA fallback (#48266) by @vasqu in [#48266]
* Fix `tie_word_embeddings` not lifted from `text_config` for some VLM configs (BC regression) (#45857) by @qgallouedec in [#45857]
* replace xpu-smi subprocess call in benchmark_v2 (#48083) by @kaixuanliu in [#48083]
* ignore mlinter ci file (#48267) by @tarekziade in [#48267]
* Fix dtype mismatch in grouped_mm_fallback for LoRA training on Mamba+… (#47933) by @adh-aakriti in [#47933]
* Compute MoE load-balancing loss per layer to avoid giant one-hot materialization −99.7% @ 128k (#48131) by @qgallouedec in [#48131]
* deterministic layer_types buffer registration in multiple models (#48162) by @mowoe in [#48162]
* Fix nemotron_h save_pretrained emitting singular backbone.embedding.weight (#48075) by @yuekaizhang in [#48075]
* `force_accelerate_hooks` should not hide the signature it wraps (#48156) by @SunMarc in [#48156]
* fix(data_collator): align TokenClassification numpy_call with torch_call (#48212) by @<NOT FOUND> in [#48212]
* Fix a typo in a use of a local variable field_ in a test (#48184) by @AleksMat in [#48184]
* [serge] Fix 2 integration tests regressed by commit 16780c86b20a (PR #47622) (#48134) by @sergereview[bot] in [#48134]
* [Gemma4] Fix stale expected values in integration tests (#48233) by @ydshieh in [#48233]
* [TableTransformer, PI0] Fix stale expected values and OOM in integration tests (#48198) by @ydshieh in [#48198]
* Post two CI badges on a PR: CPU PR CI and GPU run-slow (#48190) by @tarekziade in [#48190]
* Fix stale expected values in integration tests (cuda sm_86 / Aug04 regressions) (#48171) by @ydshieh in [#48171]
* Assign a reviewer even when a codeowner has left, and route models by modality (#48085) by @tarekziade in [#48085]
* [VITS] Un-skip test_model_forward (#46375) by @blipbyte in [#46375]
* Apply context parallelism to the evaluation path (#48167) by @qgallouedec in [#48167]
* Fix `gpt_oss` runs on GPU (#48118) by @tarekziade in [#48118]
* [EsmFold2] Fix stale expected distogram logit values (#48182) by @ydshieh in [#48182]
* Fix Apr 05 integration test regressions (cuda sm_86) (#48170) by @ydshieh in [#48170]
* Add MLU support to is_flash_linear_attention_available (#46995) by @atri2549 in [#46995]
* Fix integration test expected values for cuda sm_86 (Mar 15 regressions) (#48168) by @ydshieh in [#48168]
* Fix DynamicCache reconstruction during ExecuTorch export (#47900) by @eladsegal in [#47900]
* [LLaVA] Fix pixtral integration tests for cuda sm_86 (#48166) by @ydshieh in [#48166]
* Port ESMC and ESMFold2 to Transformers (#46419) by @Rocketknight1 in [#46419]
* [Qwen2.5-Omni] Update stale expected values for cuda sm_86 (#48164) by @ydshieh in [#48164]
* [Mistral3] Fix batched integration tests: padding_side=left + update expected values (#48161) by @ydshieh in [#48161]
* Fix DeepSeek V2 default vocab size (#48159) by @hmellor in [#48159]
* [InternVL] Fix stale expected values for Llama integration tests (cuda sm_80) (#48153) by @ydshieh in [#48153]
* Retry transient network errors (RemoteDisconnected) in github_utils (#48124) by @ydshieh in [#48124]
* fix bugs for clvp model (#47127) by @kaixuanliu in [#47127]
* Always tie embeddings for LongT5 and Pop2Piano (#47620) by @jiqing-feng in [#47620]
* Use generator with seed for LengthGroupedSampler in Trainer._get_eval_sampler for deterministic eval order with per_device_eval_batch_size > 1 (#48025) by @philipshurpik in [#48025]
* Enable mlinter findings artifact for inline PR reviews (#48117) by @ydshieh in [#48117]
* Fix CpmAnt loading: size lm_head to vocab_size (#48012) by @jiqing-feng in [#48012]
* Delete old mlinter review comments before posting new ones (#48107) by @ydshieh in [#48107]
* [Video] Warn and return all frames when num_frames exceeds total_num_frames (#48074) by @carlszk in [#48074]
* Accept artifact dir as argument in post_mlinter_review.py (#48106) by @ydshieh in [#48106]
* Fix mlinter artifact path (#48088) by @ydshieh in [#48088]
* [Video] Fix convert_to_rgb channel slicing and alpha blending for RGBA videos (#48053) by @<NOT FOUND> in [#48053]
* [PE] Skip test_sdpa_can_dispatch_on_flash for TimmWrapper-backed models (#48064) by @ydshieh in [#48064]
* fix(pipeline): preserve model.generation_config precedence over pipeline defaults (#47752) (#47953) by @nithin42 in [#47953]
* [Gemma3] Update integration test expected values for A10G (#48036) by @ydshieh in [#48036]
* Fallback from 'lanczos' to 'bicubic' when on cuda (#48026) by @zucchini-nlp in [#48026]
* [serge] Fix 2 integration tests regressed by commit b9090ae58cda (PR #47096) (#48060) by @sergereview[bot] in [#48060]
* [Fix] Small FA-related test failures in CB (#47341) by @remi-or in [#47341]
* fix: honor empty processor_kwargs={} in multimodal pipelines (#48044) by @<NOT FOUND> in [#48044]
* [CircleCI] Enable CI for private forks, no-op for public repo (#48056) by @ydshieh in [#48056]
* Support `BatchFeature` in length-grouped samplers (#48034) by @qgallouedec in [#48034]
* Fix EOS for candidate generators (#47931) by @<NOT FOUND> in [#47931]
* [Gemma3n] Update integration test expected values for A10G + torch 2.13 (#48035) by @ydshieh in [#48035]
* fix failed test cases for muse_glimmer (#48011) by @kaixuanliu in [#48011]
* Cohere compass tests (#47895) by @zucchini-nlp in [#47895]
* docs: use relative paths for README language menus and add fa/ro entries (#47777) by @Priyans-Lathiya in [#47777]
* Moving mlinter to 0.1.4 (#47918) by @tarekziade in [#47918]
* [MoE] Fix Blackwell GPU crash with torch._grouped_mm on torch <= 2.8 (#48014) by @<NOT FOUND> in [#48014]
* [docs] Muse Glimmer (#47882) by @stevhliu in [#47882]
* [Florence2] Fix two integration test failures caused by torch 2.13 and auto-dtype (#48031) by @ydshieh in [#48031]
* Proper separation of tests (#47943) by @zucchini-nlp in [#47943]
* unpin `pytest` in the `examples_torch` deps (#48023) by @tarekziade in [#48023]
* [CI] Fix startup failure in pr_build_doc_with_comment workflow by adding missing get-pr-number dependency (#47971) by @<NOT FOUND> in [#47971]
* Let the GPU verify caller turn on the memory probe (#48001) by @tarekziade in [#48001]
* Fix MTP config when mlp_layer_types is absent (#48015) by @Cyrilvallez in [#48015]
* Remove duplicate block_sparse_moe assignment in GraniteMoeDecoderLayer (#47876) by @Aman2394 in [#47876]
* [ModernVBERT] Fix integration test checkpoint (404 since April) (#48009) by @ydshieh in [#48009]
* Fix cropping (#48006) by @Cyrilvallez in [#48006]
* Fix DFlash candidate token device mismatch with device_map="auto" (#47877) by @sywangyi in [#47877]
* :red_circle: Allow tokenizers 0.23.1 (#46381) by @ArthurZucker in [#46381]
* [Whisper] Fix batch decode_with_timestamps in WhisperTokenizer.decode() (#47997) by @ydshieh in [#47997]
* [OLMoE] Update expected logits for A10G and add torch.no_grad() (#47989) by @ydshieh in [#47989]
* [OLMo] Fix OOM in logits tests by adding torch.no_grad() (#47986) by @ydshieh in [#47986]
* [AXK1] Fix expected logits for CUDA A10G (#47980) by @ydshieh in [#47980]
* [Gemma] Update expected values for A10G (#47976) by @ydshieh in [#47976]
* Fix gemma4 video to device (#47896) by @guarin in [#47896]
* Remove stale (None, None) fallback in qwen2_5_vl batch_different_resolutions test (#47972) by @ydshieh in [#47972]
* Potential fix for code scanning alert no. 267: Artifact poisoning (#47949) by @tarekziade in [#47949]
* Fix GatedDeltaNet A_log dtype to prevent -inf under bfloat16 init (#47944) by @Nkluge-correa in [#47944]
* [serge] Fix 2 integration tests for model `got_ocr2` failing with `other` (other (2)) (#47937) by @sergereview[bot] in [#47937]
* Fix Jinja block endings in CHAT WITH MODELS' Writing a chat template … (#47960) by @ak1for2business-prog in [#47960]
* [tests] Fix expected output for Qwen2.5-VL batch_wo_image on CUDA (#47968) by @ydshieh in [#47968]
* [serge] Fix 2 integration tests for model `opt` failing with `other` (other (2)) (#47909) by @sergereview[bot] in [#47909]
* Scan a diff in trufflehog, not the whole repo history (#47945) by @tarekziade in [#47945]
* [serge] Fix 2 integration tests for model `vivit` failing with `output_mismatch` (tensor values differ (2)) (#47566) by @sergereview[bot] in [#47566]
* Fix Gemma `sliding_window` being halved on every config save/reload (#47940) by @Bluear7878 in [#47940]
* docs: fix incorrect PEFT anchor link in fine-tuning section (#47927) by @dsulot in [#47927]
* CI: add vllm-test-init and vllm-test-transformers jobs on dedicated runners (#47934) by @ydshieh in [#47934]
* Make muse glimmer exportable (#47871) by @IlyasMoutawwakil in [#47871]
* docs: add installation instructions for NVIDIA Spark (ARM64) devices (#47906) by @mfuntowicz in [#47906]
* [CohereCompass] Minor docs fixes (#47903) by @calpt in [#47903]
* fix: correct checkpoints, config annotations, and create_dummy_models improvements (#47902) by @ydshieh in [#47902]
* Transform paths and repeat joining for response parsing (#47648) by @Rocketknight1 in [#47648]
* [docs] Update toctree (#47781) by @stevhliu in [#47781]
* Add `CI_CPU_MEMORY_LIMIT_GB` to check_failed_tests workflow (#47884) by @ydshieh in [#47884]
* Use tiny Hub checkpoint in Qwen3ASR processor test (#47833) by @ydshieh in [#47833]
* Update AutoRound XPU/CPU backend (#47826) by @yiliu30 in [#47826]
* docs(tests): fix typos in test comments (#47859) by @zhaoxinyi02 in [#47859]
* Update version post release (#47870) by @Cyrilvallez in [#47870]

## Significant community contributions

The following contributors have made significant changes to the library over the last release:

* @tarekziade
    * CI: gate the hunyuan-moe slow test  (#48330)
    * CI: fix muse OOMs (#48284)
    * ignore mlinter ci file (#48267)
    * Post two CI badges on a PR: CPU PR CI and GPU run-slow (#48190)
    * Assign a reviewer even when a codeowner has left, and route models by modality (#48085)
    * Fix `gpt_oss` runs on GPU (#48118)
    * Moving mlinter to 0.1.4 (#47918)
    * unpin `pytest` in the `examples_torch` deps (#48023)
    * Let the GPU verify caller turn on the memory probe (#48001)
    * Potential fix for code scanning alert no. 267: Artifact poisoning (#47949)
    * Scan a diff in trufflehog, not the whole repo history (#47945)
* @dkrisman
    * Add an opt-in per-frame pixel cap (cap_pixels_per_frame) to the Qwen3-VL video processor (#48071)
* @jiqing-feng
    * Cpmant fix use cache (#48013)
    * [xcodec2] Fix flex attention and flash dispatch tests (#48244)
    * Always tie embeddings for LongT5 and Pop2Piano (#47620)
    * Fix CpmAnt loading: size lm_head to vocab_size (#48012)
    * Fix Qwen2.5-Omni / Qwen3-Omni-MoE generation with a compilable cache (#47872)
    * Bump default flash-attn2 hub kernel version to v3 (#47863)
    * Declare sdpa support in `TimmWrapper` (#47939)
* @ydshieh
    * Fix AutoTokenizer returning TokenizersBackend for DeepSeek-R1-Distill-Qwen models (#48211)
    * [Gemma4] Investigate flaky test_generation_beyond_sliding_window_1_eager (#48236)
    * [Gemma4] Fix stale expected values in integration tests (#48233)
    * [TableTransformer, PI0] Fix stale expected values and OOM in integration tests (#48198)
    * Fix stale expected values in integration tests (cuda sm_86 / Aug04 regressions) (#48171)
    * [EsmFold2] Fix stale expected distogram logit values (#48182)
    * Fix Apr 05 integration test regressions (cuda sm_86) (#48170)
    * Fix integration test expected values for cuda sm_86 (Mar 15 regressions) (#48168)
    * [LLaVA] Fix pixtral integration tests for cuda sm_86 (#48166)
    * [Qwen2.5-Omni] Update stale expected values for cuda sm_86 (#48164)
    * [Mistral3] Fix batched integration tests: padding_side=left + update expected values (#48161)
    * [InternVL] Fix stale expected values for Llama integration tests (cuda sm_80) (#48153)
    * Retry transient network errors (RemoteDisconnected) in github_utils (#48124)
    * [Whisper] Fix speculative decoding: preserve cleared suppress tokens through super().generate() (#48108)
    * Enable mlinter findings artifact for inline PR reviews (#48117)
    * Delete old mlinter review comments before posting new ones (#48107)
    * Accept artifact dir as argument in post_mlinter_review.py (#48106)
    * Fix mlinter artifact path (#48088)
    * [Whisper] Fix decoder position IDs for left-padded batches in longform generation (#48028)
    * [PE] Skip test_sdpa_can_dispatch_on_flash for TimmWrapper-backed models (#48064)
    * [Gemma3] Update integration test expected values for A10G (#48036)
    * [CircleCI] Enable CI for private forks, no-op for public repo (#48056)
    * [Gemma3n] Update integration test expected values for A10G + torch 2.13 (#48035)
    * [Florence2] Fix two integration test failures caused by torch 2.13 and auto-dtype (#48031)
    * [ModernVBERT] Fix integration test checkpoint (404 since April) (#48009)
    * [Whisper] Fix speculative decoding: UnboundLocalError, cache corruption, and speed regression (#48000)
    * [Whisper] Fix batch decode_with_timestamps in WhisperTokenizer.decode() (#47997)
    * [Whisper] Fix integration test failures on A10G (dtype, stale values, API changes) (#47995)
    * [DeepSeekV2] Fix integration tests OOM: use device_map=auto instead of 8-bit quantization (#47991)
    * [OLMoE] Update expected logits for A10G and add torch.no_grad() (#47989)
    * [OLMo] Fix OOM in logits tests by adding torch.no_grad() (#47986)
    * [GPTNeoX] Fix post_processor not overridden when loading from pretrained (OLMo garbage generation) (#47988)
    * [AXK1] Fix expected logits for CUDA A10G (#47980)
    * [Gemma] Update expected values for A10G (#47976)
    * [emu3] 🦮 Black Labrador is back! Fix image generation broken since #37033 (#47948)
    * Remove stale (None, None) fallback in qwen2_5_vl batch_different_resolutions test (#47972)
    * [tests] Fix expected output for Qwen2.5-VL batch_wo_image on CUDA (#47968)
    * CI: add vllm-test-init and vllm-test-transformers jobs on dedicated runners (#47934)
    * fix: correct checkpoints, config annotations, and create_dummy_models improvements (#47902)
    * Add `CI_CPU_MEMORY_LIMIT_GB` to check_failed_tests workflow (#47884)
    * Use tiny Hub checkpoint in Qwen3ASR processor test (#47833)
* @eustlb
    * gs (#48288)
* @eladsegal
    * Fix DynamicCache reconstruction during ExecuTorch export (#47900)
    * Support per-layer cache configuration and attention-mask selection (#47901)
* @YangKai0616
    * 🚨[wav2vec2] Support attn_implementation=sdpa dispatch (#46196)
* @drbh
    * feat: add nvfp4 quantization (#47883)
* @Priyans-Lathiya
    * docs: use relative paths for README language menus and add fa/ro entries (#47777)
* @itazap
    * [new model] step 3.7 (#46658)
* @calpt
    * [CohereCompass] Minor docs fixes (#47903)
    * Add CohereCompass modeling (#47878)