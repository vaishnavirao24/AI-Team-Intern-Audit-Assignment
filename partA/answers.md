# Part A - Tokenizer Audit

## A1. Evaluation corpus

The corrected evaluation replaces the original ten-line smoke sample with the 1,012 aligned `devtest` sentences from FLORES-200 for English, Hindi, Kannada, Tamil and Telugu. This gives 5,060 total text lines, with each line index representing approximately the same underlying content across all five languages.

The corrected analysis preserves original case and punctuation, removes blank lines, and applies Unicode NFC normalisation. Corpus source, preprocessing details and limitations are documented in `corpus/README.md`.

The main limitation is domain mismatch. FLORES mainly contains translated formal text such as news, educational and travel content. It does not adequately represent real production traffic such as code-switching, Romanised Indic text, informal spellings, abbreviations, emojis or the application's real prompt-length distribution. Therefore, these results should be validated on a privacy-safe production-like dataset before being used for final capacity or cost decisions.

## A2. Script and metric audit

### Flaw 1 - `split(" ")` can create false word counts

The original implementation uses `split(" ")`, which treats empty strings created by repeated ASCII spaces as additional elements.

For example, with mT5:

- `alpha beta` gives 1.00 token/word
- `alpha  beta` gives approximately 0.667 token/word

The underlying text meaning has not changed, yet the measured value appears about 33.3% better.

Using a whitespace-aware method such as `\S+` avoids counting empty strings and gives the same word count for both versions.

Evidence for this experiment is available under `split_space_bug` in:

`partA/results/audit_evidence.json`

### Flaw 2 - averaging sentence-level ratios is not the same as corpus fertility

The original calculation averages:

`tokens_i / words_i`

for every sentence.

This gives a short sentence the same statistical weight as a much longer sentence.

A more appropriate corpus-level fertility measure is:

`sum(all tokens) / sum(all words)`

On the FLORES evaluation with GPT-2:

- English changes from 1.2874 to 1.2348 token/word, approximately -4.08%
- Hindi changes from 7.8651 to 7.8269 token/word, approximately -0.49%

Because languages change by different amounts, the cross-language comparison can also change.

The supporting results are stored under `macro_vs_micro` in `audit_evidence.json`.

### Flaw 3 - lowercasing may not represent real serving cost

The service ultimately tokenizes the text actually submitted by users.

Automatically lowercasing the input changes the text before measuring token usage and may therefore produce a result that does not match production behaviour.

On this corpus:

- GPT-2 English tokens increase from 27,044 to 27,994 after lowercasing, approximately +3.51%
- Hindi changes by only about 0.004%

The Hindi/English token-per-word ratio is approximately:

- 6.12x after lowercasing
- 6.34x with original case preserved

Therefore, lowercasing should not be silently applied unless it is also part of the real serving pipeline.

### Conceptual flaw - words, characters and bytes do not hold meaning constant

Even a correctly calculated token-per-word ratio is not necessarily a fair cross-language cost comparison.

Different languages can encode different amounts of information in one orthographic word. Character counts also depend on script and Unicode representation, while UTF-8 uses different byte lengths for different scripts.

For this parallel corpus, the strongest available offline comparison is therefore:

**tokens per aligned sentence relative to English**

Aligned sentences approximately preserve the same underlying meaning across languages.

For real production systems, the stronger metric is actual input and output tokens per successful request, segmented by language and task.

### Suspicious but harmless - random seed

The original script contains:

`random.seed(1337)`

However, no random operation is used in the relevant calculation.

Running the original calculation with seeds such as 1, 1337 and 999999 produces the same GPT-2 English value:

`1.2873650862`

Therefore, the random seed is unnecessary cleanup, but it is not a numerical bug.

### NFC normalisation

NFC normalisation converts canonically equivalent Unicode representations into a consistent form.

In this corpus:

- mT5 token totals remain unchanged for all five languages
- GPT-2 Hindi changes from 200,483 to 200,704 tokens, approximately +0.11%

The corrected analysis retains NFC as an explicit preprocessing assumption, but it should only be considered correct if it matches the actual serving pipeline.

## A3. Corrected analysis

The following results are calculated over 1,012 case-preserved, NFC-normalised aligned sentences for every language.

| Tokenizer | Language | Tok/word | Tok/grapheme | Tok/UTF-8 byte | Tok/aligned sentence | Ratio vs English |
|---|---|---:|---:|---:|---:|---:|
| GPT-2 | English | 1.235 | 0.205 | 0.205 | 26.72 | 1.00x |
| GPT-2 | Hindi | 7.827 | 2.334 | 0.595 | 198.32 | 7.42x |
| GPT-2 | Kannada | 22.824 | 4.062 | 0.979 | 363.11 | 13.59x |
| GPT-2 | Tamil | 25.047 | 4.213 | 0.997 | 415.19 | 15.54x |
| GPT-2 | Telugu | 20.710 | 4.579 | 0.992 | 346.62 | 12.97x |
| mT5-small | English | 1.543 | 0.256 | 0.256 | 33.39 | 1.00x |
| mT5-small | Hindi | 2.086 | 0.622 | 0.159 | 52.86 | 1.58x |
| mT5-small | Kannada | 3.006 | 0.535 | 0.129 | 47.82 | 1.43x |
| mT5-small | Tamil | 2.541 | 0.427 | 0.101 | 42.12 | 1.26x |
| mT5-small | Telugu | 2.813 | 0.622 | 0.135 | 47.07 | 1.41x |

The primary offline metric used here for cross-language cost comparison is **tokens per aligned sentence relative to English**.

For Hindi:

`GPT-2 ratio = 200,704 / 27,044 ≈ 7.42x`

`mT5 ratio = 53,495 / 33,791 ≈ 1.58x`

For GPT-2, the tested Indic languages require approximately 7.42x to 15.54x as many tokens per aligned sentence as English.

For mT5, the same ratios are much smaller, approximately 1.26x to 1.58x.

These results do not support treating poor Indic tokenisation as an unavoidable property of Unicode text. Tokenizer design has a major effect on the measured token cost.

However, this does not prove that mT5 is the better model overall. Tokenizer efficiency and model response quality are separate questions and must be evaluated independently.

## Reproduction

Run:

```bash
python partA/audit.py --all