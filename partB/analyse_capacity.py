#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KV_BYTES_PER_TOKEN = 2 * 28 * 8 * 128 * 2
AVAILABLE_KV_BYTES = (24 * 0.92 - 4.2 * 2 - 1.6) * 1_000_000_000
CAPACITY_TOKENS = AVAILABLE_KV_BYTES / KV_BYTES_PER_TOKEN

print(f"KV bytes/token = {KV_BYTES_PER_TOKEN:,} B = {KV_BYTES_PER_TOKEN/1024:.0f} KiB")
print(f"KV budget = {AVAILABLE_KV_BYTES/1e9:.2f} GB")
print(f"Token capacity = {CAPACITY_TOKENS:,.0f}")
print(f"Full 4096-token sequences = {int(CAPACITY_TOKENS // 4096)}")
print()

with (ROOT / "bench_log.csv").open(newline="") as f:
    rows = list(csv.DictReader(f))

print("batch prompt reported all_tok/s output_goodput_tok/s recomputed_all_tok/s preemptions kv_util")
for row in rows:
    b, p, g = (int(row[k]) for k in ("batch_size", "prompt_len", "gen_len"))
    wall = float(row["wall_clock_s"])
    all_rate = b * (p + g) / wall
    goodput = b * g / wall
    print(f"{b:>5} {p:>6} {float(row['reported_tok_s']):>16.1f} {goodput:>20.1f} "
          f"{all_rate:>20.1f} {row['preempted_seqs']:>11} {row['kv_cache_util']:>7}")

