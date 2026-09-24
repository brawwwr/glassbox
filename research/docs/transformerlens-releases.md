# TransformerLensOrg/TransformerLens — last 4 releases



## v4.0.0 — 2026-09-21

## What's Changed
* Initial Driver System by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1335
* vLLM Batches by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1338
* vLLM Driver Bugs by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1343
* Inspect Driver by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1367
* Inspect & vLLM driver Features & Bugs by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1492
* vLLM & Inspect Driver Correctness Improvements by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1515
* Multi-GPU testing for vLLM systems by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1517
* Initial Setup for HookedTransformers Deprecation by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1538
* Comment cleanup jul 26 by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1541
* Release cleanup 3.6.0 Release port cleanup for 4.x  by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1550
* fix(bridge): make tokenizer assignment re-run wiring logic by @MdSadiqMd in https://github.com/TransformerLensOrg/TransformerLens/pull/1569
* docs: clarify gradient support during v3 migration by @lntutor in https://github.com/TransformerLensOrg/TransformerLens/pull/1571
* docs: add bridge capability migration recipes by @happykawayigt in https://github.com/TransformerLensOrg/TransformerLens/pull/1567
* fix(bridge): validate boot_native config type by @Austin1serb in https://github.com/TransformerLensOrg/TransformerLens/pull/1573
* Test Hooked from_pretrained deprecation warnings by @noor-ahmadi in https://github.com/TransformerLensOrg/TransformerLens/pull/1575
* 4.x Flaky test cleanup by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1583
* fix(bridge): add audio-specific guard for start_at_layer by @MdSadiqMd in https://github.com/TransformerLensOrg/TransformerLens/pull/1563
* feat(native): add param-free pre-norm (LNPre/RMSPre) and fold_ln support by @MdSadiqMd in https://github.com/TransformerLensOrg/TransformerLens/pull/1580
* Honor native bridge weight initialization config by @happykawayigt in https://github.com/TransformerLensOrg/TransformerLens/pull/1577
* fix(bridge): expand grouped K/V heads in QK/OV and composition circuits on GQA models by @TravisHaa in https://github.com/TransformerLensOrg/TransformerLens/pull/1593
* refactor(train): relocate to tools/training.py for bridge compatibility by @MdSadiqMd in https://github.com/TransformerLensOrg/TransformerLens/pull/1594
* fix(bridge): make native TransformerBridge state_dict()/load_state_dict() true inverses by @LightWork666 in https://github.com/TransformerLensOrg/TransformerLens/pull/1598
* docs: add boot_native train-from-scratch recipe to migration guide by @priyanka25aug in https://github.com/TransformerLensOrg/TransformerLens/pull/1600
* Add native bridge state dict regression tests by @ArS377 in https://github.com/TransformerLensOrg/TransformerLens/pull/1595
* fix(bridge): remove orphaned convert_weights override from nanogpt adapter by @sohv in https://github.com/TransformerLensOrg/TransformerLens/pull/1602
* feat(utilities): add one-time converter for legacy TL-format checkpoints by @LightWork666 in https://github.com/TransformerLensOrg/TransformerLens/pull/1599
* fix(bridge): remove dead _enable_ht_attention and its exclusive helpers by @sohv in https://github.com/TransformerLensOrg/TransformerLens/pull/1604
* Reanchoring tests and benchmarks by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1603
* fix(tests): un-quarantine encoder acceptance suites, sync quarantine inventory by @sohv in https://github.com/TransformerLensOrg/TransformerLens/pull/1606
* docs: demonstrate W_pos migration by @lntutor in https://github.com/TransformerLensOrg/TransformerLens/pull/1572
* docs: migrate executable doctests to TransformerBridge by @Austin1serb in https://github.com/TransformerLensOrg/TransformerLens/pull/1576
* Fix masked causal loss in TransformerBridge by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1608
* fix(bridge): derive position_ids from attention_mask for left-padded input by @sohv in https://github.com/TransformerLensOrg/TransformerLens/pull/1610
* Fix TransformerBridge loss with explicit labels by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1613
* `dev-4.x` contribution follow ups by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1614
* fix(bridge): accept attention_mask in generate() for pre-padded prompts by @sohv in https://github.com/TransformerLensOrg/TransformerLens/pull/1617
* feat(bridge): support disk device_map offload targets by @LightWork666 in https://github.com/TransformerLensOrg/TransformerLens/pull/1615
* Fix run_with_cache BOS handling for string inputs by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1625
* fix(tokenizer): do not strip a BOS token the tokenizer does not have by @sohv in https://github.com/TransformerLensOrg/TransformerLens/pull/1629
* fix(bridge): restore native stop_at_layer and input_to_embed by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1633
* fix(tokenizer): do not prepend a BOS token the tokenizer does not have by @Chinmayrawat15 in https://github.com/TransformerLensOrg/TransformerLens/pull/1634
* Fix TransformerBridge temporary hook cleanup by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1638
* Claude Code Architecture Adapter Creation Tool by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1641
* Stabilize Bridge numerical CI tests by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1654
* Fix gated Qwen W_Q analysis weights by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1653
* Expose BERT token-type embeddings through TransformerBridge by @LarryHu0217 in https://github.com/TransformerLensOrg/TransformerLens/pull/1664
* migrate the othello off hooked transformer by @MdSadiqMd in https://github.com/TransformerLensOrg/TransformerLens/pull/1667
* Fix recursive TransformerBridge state dict composition by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1661
* fix(model-bridge): restore native state dict round trips by @mikemikimike in https://github.com/TransformerLensOrg/TransformerLens/pull/1591
* fix(bridge): gate batched-list position_ids on the target model by @sohv in https://github.com/TransformerLensOrg/TransformerLens/pull/1627
* Fix batchless accumulated residual normalization by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1678
* Fix TransformerBridge adapter traversal coverage by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1671
* Bug/bridge hook gating followups by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1724
* fix(bridge): preserve split-component views under load_state_dict(assign=True) by @LightWork666 in https://github.com/TransformerLensOrg/TransformerLens/pull/1660
* Fixes to moe and composition scores by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1737
* Final deprecation prep by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1740
* Hooked Class Deprecation by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1759
* fix(demos): port LIT integration demo model loading to TransformerBridge by @ZacharyZcR in https://github.com/TransformerLensOrg/TransformerLens/pull/1758
* Fix IOIDataset BOS handling by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1773
* Fix flaky direct path patching correctness test by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1783
* feat(backward_lens): generalize Backward Lens to dense-MLP decoder-only Bridges (GPT-2, Pythia, GPT-NeoX) by @janmenjayap in https://github.com/TransformerLensOrg/TransformerLens/pull/1778
* Reject fabricated MoE weights in SVDInterpreter by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1780
* Add an analysis tool selection guide by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1782
* improved direct path patching test by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1786
* Require evaluation mode for attribution patching by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1788
* feat(attribution_patching): edge attribution (EAP) scoring on TransformerBridge by @janmenjayap in https://github.com/TransformerLensOrg/TransformerLens/pull/1781
* feat(model_bridge): shared LN/Identity/Half relevance-rule backend by @janmenjayap in https://github.com/TransformerLensOrg/TransformerLens/pull/1785
* fix: raise on stop_at_layer when no 'blocks' stack is registered by @Aurnawr in https://github.com/TransformerLensOrg/TransformerLens/pull/1789
* 4.x Merge into `dev` by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1790
* Release v4.0.0 by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1792

## New Contributors
* @lntutor made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1571
* @happykawayigt made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1567
* @Austin1serb made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1573
* @noor-ahmadi made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1575
* @LightWork666 made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1598
* @ArS377 made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1595
* @sohv made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1602
* @LarryHu0217 made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1664
* @mikemikimike made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1591
* @ZacharyZcR made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1758
* @Aurnawr made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1789

**Full Changelog**: https://github.com/TransformerLensOrg/TransformerLens/compare/v3.9.0...v4.0.0


## v3.9.0 — 2026-09-11

## What's Changed
* CI Warnings Cleanup by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1732
* siglip vision tower hooking by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1734
* test(bert): add Bridge-to-HF parity coverage by @janmenjayap in https://github.com/TransformerLensOrg/TransformerLens/pull/1735
* Fix Legacy Audio System by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1736
* docs(jacobian_lens): add sparse decomposition demo by @janmenjayap in https://github.com/TransformerLensOrg/TransformerLens/pull/1738
* feat(jacobian_lens): anchored J-space coordinate patching (offline primitive) by @janmenjayap in https://github.com/TransformerLensOrg/TransformerLens/pull/1741
* Fix Cohere compatibility logit scaling by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1727
* feat(backward_lens): add vocabulary readout of GPT-2 MLP gradient factors by @janmenjayap in https://github.com/TransformerLensOrg/TransformerLens/pull/1723
* Creating a parameter swap utility by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1744
* fix(bridge): decode every batch row in generate_stream by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1757
* Require eval mode for JacobianLens fitting by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1763
* Fix batched hf_generate padding and attention masks by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1761
* feat(jacobian_lens): add dynamic J-space coordinate-patch hooks by @janmenjayap in https://github.com/TransformerLensOrg/TransformerLens/pull/1749
* feat(attribution_patching): node attribution-patching substrate on TransformerBridge by @janmenjayap in https://github.com/TransformerLensOrg/TransformerLens/pull/1750
* fix(neox): resolve unembedding as lm_head for transformers >= 5.13 by @janmenjayap in https://github.com/TransformerLensOrg/TransformerLens/pull/1752
* Clarify quantized dtype ownership; keep the whole-model skip (#1743) by @Canonik in https://github.com/TransformerLensOrg/TransformerLens/pull/1754
* refactor(jacobian_lens): extract estimator-independent fit driver by @janmenjayap in https://github.com/TransformerLensOrg/TransformerLens/pull/1764
* Followup review by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1770
* Fix JacobianLens dictionary cache invalidation by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1766
* Add clean-coordinate clamping for JacobianLens swaps by @koriyoshi2041 in https://github.com/TransformerLensOrg/TransformerLens/pull/1747
* feat(svd_circuits): per-head QK/OV SVD with degeneracy guard by @janmenjayap in https://github.com/TransformerLensOrg/TransformerLens/pull/1768
* fix(head_detector): forward keyword arguments on the multi-prompt path, and stop mutating the ActivationCache by @WatchTree-19 in https://github.com/TransformerLensOrg/TransformerLens/pull/1745
* Release v3.9.0 by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1771

## New Contributors
* @WatchTree-19 made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1745

**Full Changelog**: https://github.com/TransformerLensOrg/TransformerLens/compare/v3.8.1...v3.9.0


## v4.0.0b2 — 2026-09-02

## What's Changed
* Initial Driver System by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1335
* vLLM Batches by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1338
* vLLM Driver Bugs by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1343
* Inspect Driver by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1367
* Inspect & vLLM driver Features & Bugs by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1492
* vLLM & Inspect Driver Correctness Improvements by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1515
* Multi-GPU testing for vLLM systems by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1517
* Initial Setup for HookedTransformers Deprecation by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1538
* Comment cleanup jul 26 by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1541
* Release cleanup 3.6.0 Release port cleanup for 4.x  by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1550
* fix(bridge): make tokenizer assignment re-run wiring logic by @MdSadiqMd in https://github.com/TransformerLensOrg/TransformerLens/pull/1569
* docs: clarify gradient support during v3 migration by @lntutor in https://github.com/TransformerLensOrg/TransformerLens/pull/1571
* docs: add bridge capability migration recipes by @happykawayigt in https://github.com/TransformerLensOrg/TransformerLens/pull/1567
* fix(bridge): validate boot_native config type by @Austin1serb in https://github.com/TransformerLensOrg/TransformerLens/pull/1573
* Test Hooked from_pretrained deprecation warnings by @noor-ahmadi in https://github.com/TransformerLensOrg/TransformerLens/pull/1575
* 4.x Flaky test cleanup by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1583
* fix(bridge): add audio-specific guard for start_at_layer by @MdSadiqMd in https://github.com/TransformerLensOrg/TransformerLens/pull/1563
* feat(native): add param-free pre-norm (LNPre/RMSPre) and fold_ln support by @MdSadiqMd in https://github.com/TransformerLensOrg/TransformerLens/pull/1580
* Honor native bridge weight initialization config by @happykawayigt in https://github.com/TransformerLensOrg/TransformerLens/pull/1577
* fix(bridge): expand grouped K/V heads in QK/OV and composition circuits on GQA models by @TravisHaa in https://github.com/TransformerLensOrg/TransformerLens/pull/1593
* refactor(train): relocate to tools/training.py for bridge compatibility by @MdSadiqMd in https://github.com/TransformerLensOrg/TransformerLens/pull/1594
* fix(bridge): make native TransformerBridge state_dict()/load_state_dict() true inverses by @LightWork666 in https://github.com/TransformerLensOrg/TransformerLens/pull/1598
* docs: add boot_native train-from-scratch recipe to migration guide by @priyanka25aug in https://github.com/TransformerLensOrg/TransformerLens/pull/1600
* Add native bridge state dict regression tests by @ArS377 in https://github.com/TransformerLensOrg/TransformerLens/pull/1595
* fix(bridge): remove orphaned convert_weights override from nanogpt adapter by @sohv in https://github.com/TransformerLensOrg/TransformerLens/pull/1602
* feat(utilities): add one-time converter for legacy TL-format checkpoints by @LightWork666 in https://github.com/TransformerLensOrg/TransformerLens/pull/1599
* fix(bridge): remove dead _enable_ht_attention and its exclusive helpers by @sohv in https://github.com/TransformerLensOrg/TransformerLens/pull/1604
* Reanchoring tests and benchmarks by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1603
* fix(tests): un-quarantine encoder acceptance suites, sync quarantine inventory by @sohv in https://github.com/TransformerLensOrg/TransformerLens/pull/1606
* docs: demonstrate W_pos migration by @lntutor in https://github.com/TransformerLensOrg/TransformerLens/pull/1572
* docs: migrate executable doctests to TransformerBridge by @Austin1serb in https://github.com/TransformerLensOrg/TransformerLens/pull/1576
* Fix masked causal loss in TransformerBridge by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1608
* fix(bridge): derive position_ids from attention_mask for left-padded input by @sohv in https://github.com/TransformerLensOrg/TransformerLens/pull/1610
* Fix TransformerBridge loss with explicit labels by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1613
* `dev-4.x` contribution follow ups by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1614
* fix(bridge): accept attention_mask in generate() for pre-padded prompts by @sohv in https://github.com/TransformerLensOrg/TransformerLens/pull/1617
* feat(bridge): support disk device_map offload targets by @LightWork666 in https://github.com/TransformerLensOrg/TransformerLens/pull/1615
* Fix run_with_cache BOS handling for string inputs by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1625
* fix(tokenizer): do not strip a BOS token the tokenizer does not have by @sohv in https://github.com/TransformerLensOrg/TransformerLens/pull/1629
* fix(bridge): restore native stop_at_layer and input_to_embed by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1633
* fix(tokenizer): do not prepend a BOS token the tokenizer does not have by @Chinmayrawat15 in https://github.com/TransformerLensOrg/TransformerLens/pull/1634
* Fix TransformerBridge temporary hook cleanup by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1638
* Claude Code Architecture Adapter Creation Tool by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1641
* Stabilize Bridge numerical CI tests by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1654
* Fix gated Qwen W_Q analysis weights by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1653
* Expose BERT token-type embeddings through TransformerBridge by @LarryHu0217 in https://github.com/TransformerLensOrg/TransformerLens/pull/1664
* migrate the othello off hooked transformer by @MdSadiqMd in https://github.com/TransformerLensOrg/TransformerLens/pull/1667
* Fix recursive TransformerBridge state dict composition by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1661
* fix(model-bridge): restore native state dict round trips by @mikemikimike in https://github.com/TransformerLensOrg/TransformerLens/pull/1591
* fix(bridge): gate batched-list position_ids on the target model by @sohv in https://github.com/TransformerLensOrg/TransformerLens/pull/1627
* Fix batchless accumulated residual normalization by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1678
* Fix TransformerBridge adapter traversal coverage by @emerardd in https://github.com/TransformerLensOrg/TransformerLens/pull/1671
* Bug/bridge hook gating followups by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1724
* fix(bridge): preserve split-component views under load_state_dict(assign=True) by @LightWork666 in https://github.com/TransformerLensOrg/TransformerLens/pull/1660
* CI Warnings Cleanup by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1732
* siglip vision tower hooking by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1734
* test(bert): add Bridge-to-HF parity coverage by @janmenjayap in https://github.com/TransformerLensOrg/TransformerLens/pull/1735
* Fix Legacy Audio System by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1736
* Fixes to moe and composition scores by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1737
* Final deprecation prep by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1740

## New Contributors
* @lntutor made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1571
* @happykawayigt made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1567
* @Austin1serb made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1573
* @noor-ahmadi made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1575
* @LightWork666 made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1598
* @ArS377 made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1595
* @sohv made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1602
* @LarryHu0217 made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1664
* @mikemikimike made their first contribution in https://github.com/TransformerLensOrg/TransformerLens/pull/1591

**Full Changelog**: https://github.com/TransformerLensOrg/TransformerLens/compare/v3.8.1...v4.0.0b2


## v3.8.1 — 2026-09-01

## What's Changed
* Update lfm2 moe to use correct bridge elements by @TensorCruncher in https://github.com/TransformerLensOrg/TransformerLens/pull/1670
* Preserve alias hook replacements across no-op callbacks by @koriyoshi2041 in https://github.com/TransformerLensOrg/TransformerLens/pull/1722
* feat(projection_kernel): add attention-head subspace affinity by @janmenjayap in https://github.com/TransformerLensOrg/TransformerLens/pull/1721
* updating attention score sentinel to be slightly more relaxed by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1730
* Phase 4 Rescoring by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1731
* Release v3.8.1 by @jlarson4 in https://github.com/TransformerLensOrg/TransformerLens/pull/1733


**Full Changelog**: https://github.com/TransformerLensOrg/TransformerLens/compare/v3.8.0...v3.8.1