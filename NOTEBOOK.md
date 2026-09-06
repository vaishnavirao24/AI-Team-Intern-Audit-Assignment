# Lab notebook

Date: 2026-09-06

This notebook records the work I personally performed while reproducing and verifying the submission. The initial solution, code and written analysis were substantially AI-assisted. Exact clock times were not recorded for every step, so the entries below are kept in chronological order rather than assigning invented timestamps.

## 1. Opened and inspected the submission

I extracted `AI_Team_Intern_Audit_Submission` and opened the extracted folder in VS Code.

I reviewed the project structure and identified the main scripts and result files required for verification.

## 2. Python environment issue

### Problem

The first command:

`py -m venv .venv`

failed because the `py` command was not recognised.

I then tried:

`python --version`

which also failed because Python was not available through the system PATH.

### Action

I installed Python 3.11 (64-bit) and ensured Python was available from the terminal.

## 3. Virtual environment setup

I ran:

`python -m venv .venv`

The first attempt was interrupted before completion, which resulted in a `KeyboardInterrupt` and an incomplete `.venv`.

I removed/recreated the virtual environment and verified that `.venv\Scripts` contained the required files.

I then activated it using:

`.\.venv\Scripts\Activate.ps1`

The terminal successfully showed the `(.venv)` prefix.

## 4. Dependency installation

I ran:

`python -m pip install -r requirements.txt`

The dependencies installed successfully, including packages used by the tokenizer analysis such as `tiktoken`, `sentencepiece`, `transformers`, `tokenizers`, and related libraries.

## 5. Part A reproduction

I ran:

`python partA/audit.py --all`

The command completed successfully and generated:

`partA/results/audit_evidence.json`

I then inspected:

`partA/results/corrected_metrics.csv`

The corrected evaluation contains 1,012 aligned sentences for each of the five languages.

Examples I verified from the generated output:

- GPT-2 English tokens: 27,044
- GPT-2 Hindi tokens: 200,704
- Hindi/English GPT-2 ratio: approximately 7.42x
- mT5 English tokens: 33,791
- mT5 Hindi tokens: 53,495
- Hindi/English mT5 ratio: approximately 1.58x

This confirmed that the submitted Part A results could be reproduced on my machine.

## 6. Part B reproduction

I ran:

`python partB/analyse_capacity.py`

The command completed successfully.

Important values reproduced from the output were:

- KV bytes per token: 114,688 B (112 KiB)
- KV budget: approximately 12.08 GB
- Token capacity: 105,329 tokens
- Full 4,096-token sequences: 25
- Batch 24 output goodput: 200.9 tok/s
- Batch 32 output goodput: 173.0 tok/s with 7 preemptions
- Batch 48 output goodput: 162.3 tok/s with 23 preemptions

The results show that batch 24 is the largest measured batch in this workload without preemption, while larger batches reach KV-cache saturation and reduce generated-token goodput.

## 7. AI disclosure review

I reviewed `AI_USAGE.md` and updated it to distinguish between work produced with AI assistance and work I personally reproduced and verified.

I did not claim that I independently wrote or discovered the complete initial solution.

## Before submission

Before submitting, I still need to:

1. Review the submitted answers and recommendation memos.
2. Understand the formulas used in Parts A and B.
3. Practise reproducing the important calculations without relying on the prepared answers.
4. Review possible live code modifications for the defence.
5. Re-run the scripts once more before creating the final submission ZIP.