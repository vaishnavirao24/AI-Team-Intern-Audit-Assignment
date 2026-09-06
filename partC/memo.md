# Part B - Capacity Reconciliation

## B1. KV-cache capacity

For every cached token, each transformer layer stores one key and one value for every KV head.

The KV-cache memory required per token is:

`2 (K and V) × 28 layers × 8 KV heads × 128 dimensions × 2 bytes (FP16)`

`= 114,688 bytes/token`

`= 112 KiB/token`

Using the decimal memory units implied by the 24 GB GPU specification:

- Usable GPU memory:

`24 GB × 0.92 = 22.08 GB`

- FP16 model weights:

`4.2 billion parameters × 2 bytes = 8.40 GB`

- Non-KV runtime overhead:

`1.60 GB`

Therefore, the memory available for KV cache is:

`22.08 - 8.40 - 1.60 = 12.08 GB`

The theoretical KV token capacity is:

`12.08e9 / 114,688 ≈ 105,329 tokens`

For a complete 4,096-token sequence:

`floor(105,329 / 4,096) = 25 complete sequences`

This is consistent with the benchmark behaviour.

At batch 24 with a 3,584-token prompt and 512 generated tokens, every request reaches 4,096 tokens:

`24 × 4,096 = 98,304 cached token slots`

The benchmark reports:

- KV utilisation = 0.93
- preemptions = 0

An independent estimate from this row is:

`98,304 / 0.93 ≈ 105,703 token slots`

This is only about 0.36% above the specification-based estimate of 105,329 tokens.

At batch 32 and batch 48, all active 4,096-token sequences cannot fit in the available KV cache. KV utilisation reaches approximately 0.97 and preemptions appear.

---

## B2. Long-context throughput anomaly

Normally, increasing batch size can improve throughput because more requests are processed together.

For the long-context workload, reported throughput increases initially:

- Batch 4: 565.4 tok/s
- Batch 8: 902.6 tok/s
- Batch 16: 1311.4 tok/s
- Batch 24: 1607.4 tok/s

However, performance then decreases:

- Batch 32: 1384.0 tok/s
- Batch 48: 1298.5 tok/s

The turning point corresponds with KV-cache saturation.

| Batch | KV utilisation | Preemptions |
|---:|---:|---:|
| 24 | 0.93 | 0 |
| 32 | 0.97 | 7 |
| 48 | 0.97 | 23 |

At batch 24, all active sequences fit without preemption.

At larger batches, the available KV cache cannot hold every active sequence. The scheduler therefore preempts some sequences. Resuming those requests may require recomputation or cache restoration, creating extra work and increasing latency.

Therefore, the decrease beyond batch 24 is consistent with a **memory-capacity limitation rather than useful batch scaling**.

### Deployment recommendation

For this measured workload, cap the number of simultaneously active long-context sequences at approximately 24 and queue additional requests.

Measured generated-token goodput changes from:

- Batch 48: 162.3 tok/s
- Batch 24: 200.9 tok/s

The predicted improvement is:

`200.9 / 162.3 - 1 ≈ 23.8%`

This recommendation is specific to the tested model, GPU configuration and 4,096-token workload. Queueing can increase request waiting time, so the complete system should still be load-tested before deployment.

---

## B3. Misinterpreted throughput column

The benchmark's `reported_tok_s` value counts both:

`prompt tokens + generated tokens`

Therefore, it represents total processed-token throughput, not generated-output throughput.

This distinction is important because a long prompt can make the reported number appear large even though users are not receiving output tokens at that rate.

For batch 24:

- requests = 24
- prompt length = 3,584 tokens
- generation length = 512 tokens
- wall time = 61.16 seconds

Actual generated-token goodput is:

`24 × 512 / 61.16`

`≈ 200.92 generated tokens/second`

The same value can be independently derived from the reported throughput:

`1607.4 × 512 / (3584 + 512)`

`≈ 200.93 generated tokens/second`

The two calculations agree within rounding.

Therefore, the correct interpretation is:

> Total processed-token throughput peaks at approximately 1607.4 tok/s at batch 24, while actual generated-token goodput is approximately 200.9 tok/s.

Beyond batch 24, KV-cache saturation introduces preemption and generated-token goodput falls:

- Batch 32: 173.0 tok/s
- Batch 48: 162.3 tok/s

Longer prompts should therefore not be encouraged simply to increase a throughput counter, and batch-48 performance should not be extrapolated linearly from smaller batches.

---

## B4. Confirmation metric

A useful production confirmation metric is the serving scheduler's cumulative sequence-preemption counter, measured separately for each benchmark run.

If KV-cache exhaustion is the main cause of the slowdown, the expected behaviour is approximately:

- Batch 24: 0 preemptions
- Batch 32: 7 preemptions
- Batch 48: 23 preemptions

This matches the supplied benchmark log.

A sharp increase in scheduler preemptions when KV-cache utilisation reaches approximately 0.97 would provide strong evidence that the slowdown is caused by KV-cache pressure rather than only by compute saturation.

Other useful production metrics include:

- KV-cache utilisation
- queue waiting time
- time to first token
- inter-token latency
- generated-token goodput
- request completion latency

These should be monitored together because limiting active sequences can reduce preemption while increasing queueing delay.

---

## Reproduction

Run:

```bash
python partB/analyse_capacity.py