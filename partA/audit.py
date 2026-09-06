#!/usr/bin/env python3
"""Reproduce the tokenizer audit and corrected multilingual analysis."""

import argparse
import csv
import json
import random
import unicodedata
from pathlib import Path

import regex
import sentencepiece as spm
import tiktoken
from transformers.utils.hub import cached_file

ROOT = Path(__file__).resolve().parent
LANGS = {
    "eng": "eng_Latn.devtest",
    "hin": "hin_Deva.devtest",
    "kan": "kan_Knda.devtest",
    "tam": "tam_Taml.devtest",
    "tel": "tel_Telu.devtest",
}


def read_raw(path):
    return [line.rstrip("\r\n") for line in path.open(encoding="utf-8") if line.strip()]


def tokenizers():
    gpt2 = tiktoken.get_encoding("gpt2")
    model_path = cached_file("google/mt5-small", "spiece.model")
    mt5 = spm.SentencePieceProcessor(model_file=model_path)
    return {"gpt2": gpt2.encode, "mt5-small": mt5.encode}


def counts(lines, encode, lowercase=False, normalise=True):
    out = dict(tokens=0, words=0, graphemes=0, bytes=0, sentences=len(lines))
    ratios = []
    for raw in lines:
        text = unicodedata.normalize("NFC", raw) if normalise else raw
        if lowercase:
            text = text.lower()
        ntok = len(encode(text))
        # Unicode-aware whitespace words; unlike split(" "), repeated spaces do not make empty words.
        nword = len(regex.findall(r"\S+", text))
        ngrapheme = len(regex.findall(r"\X", text))
        out["tokens"] += ntok
        out["words"] += nword
        out["graphemes"] += ngrapheme
        out["bytes"] += len(text.encode("utf-8"))
        ratios.append(ntok / nword)
    out["macro_tok_per_word"] = sum(ratios) / len(ratios)
    out["tok_per_word"] = out["tokens"] / out["words"]
    out["tok_per_grapheme"] = out["tokens"] / out["graphemes"]
    out["tok_per_byte"] = out["tokens"] / out["bytes"]
    out["tok_per_sentence"] = out["tokens"] / out["sentences"]
    return out


def original_metric(lines, encode):
    vals = []
    for raw in lines:
        text = unicodedata.normalize("NFC", raw.strip()).lower()
        vals.append(len(encode(text)) / len(text.split(" ")))
    return sum(vals) / len(vals)


def run_all():
    corpus = {k: read_raw(ROOT / "corpus" / v) for k, v in LANGS.items()}
    lengths = {k: len(v) for k, v in corpus.items()}
    if len(set(lengths.values())) != 1:
        raise ValueError(f"Corpus is not parallel: {lengths}")

    rows = []
    evidence = {"corpus_lines": lengths, "experiments": {}}
    for tok_name, encode in tokenizers().items():
        for lang, lines in corpus.items():
            c = counts(lines, encode)
            rows.append({"tokenizer": tok_name, "language": lang, **c})

            old = original_metric(lines, encode)
            evidence["experiments"].setdefault("macro_vs_micro", []).append({
                "tokenizer": tok_name, "language": lang,
                "v0_macro_tok_per_word": old,
                "micro_tok_per_word": c["tok_per_word"],
                "relative_change_pct": 100 * (c["tok_per_word"] / old - 1),
            })

            lower = counts(lines, encode, lowercase=True)
            evidence["experiments"].setdefault("lowercasing", []).append({
                "tokenizer": tok_name, "language": lang,
                "original_tokens": c["tokens"], "lowercase_tokens": lower["tokens"],
                "change_pct": 100 * (lower["tokens"] / c["tokens"] - 1),
            })

            raw = counts(lines, encode, normalise=False)
            changed_lines = sum(a != unicodedata.normalize("NFC", a) for a in lines)
            evidence["experiments"].setdefault("nfc", []).append({
                "tokenizer": tok_name, "language": lang,
                "lines_changed": changed_lines,
                "raw_tokens": raw["tokens"], "nfc_tokens": c["tokens"],
            })

    # Isolated split(" ") bug: same visible words, one versus two spaces.
    split_bug = []
    for tok_name, encode in tokenizers().items():
        one, two = "alpha beta", "alpha  beta"
        split_bug.append({
            "tokenizer": tok_name,
            "one_space_v0": len(encode(one)) / len(one.split(" ")),
            "two_spaces_v0": len(encode(two)) / len(two.split(" ")),
            "one_space_correct": len(encode(one)) / len(regex.findall(r"\S+", one)),
            "two_spaces_correct": len(encode(two)) / len(regex.findall(r"\S+", two)),
        })
    evidence["experiments"]["split_space_bug"] = split_bug

    # random.seed in v0 looks relevant, but analyse() performs no random operation.
    seed_check = []
    for seed in (1, 1337, 999999):
        random.seed(seed)
        seed_check.append({"seed": seed, "gpt2_eng_v0": original_metric(corpus["eng"], tokenizers()["gpt2"])})
    evidence["experiments"]["unused_random_seed"] = seed_check

    outdir = ROOT / "results"
    outdir.mkdir(exist_ok=True)
    fields = list(rows[0])
    with (outdir / "corrected_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    (outdir / "audit_evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print((outdir / "corrected_metrics.csv").read_text(encoding="utf-8"))
    print("Evidence:", outdir / "audit_evidence.json")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--all", action="store_true", help="run all audit experiments")
    args = p.parse_args()
    run_all()
