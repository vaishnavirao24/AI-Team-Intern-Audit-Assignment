# Tokenizer and serving audit

This repository is a reproducible submission for the AI Team Intern Assignment.

## Reproduce

Use Python 3.11+ from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python partA/audit.py --all
python partB/analyse_capacity.py
```

The first Part A run downloads tokenizer assets for `google/mt5-small`. Results are written to `partA/results/`. All headline claims in the written answers are produced by these commands.

## Contents

- `NOTEBOOK.md`: chronological hypothesis-experiment-result-revision log
- `AI_USAGE.md`: honest AI-use disclosure
- `partA/`: FLORES corpus, corrected analyser, audit experiments, results and memo
- `partB/`: source benchmark files, arithmetic script and answers
- `partC/memo.md`: decision memo

## Important defense note

Do not submit this unchanged. Run every command on your own machine, compare the generated CSVs with the committed results, and edit `AI_USAGE.md` and `NOTEBOOK.md` so they truthfully describe your own work.

