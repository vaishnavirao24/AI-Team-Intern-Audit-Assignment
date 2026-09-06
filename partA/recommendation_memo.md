# A4 - Recommendation memo

**Decision.** Do not assume a universal 6x Hindi token-cost premium and do not make routing decisions only from `REPORT_v0`. The correct approach is to evaluate complete model-tokenizer pairs and choose between them using measured task quality, token usage and latency.

**Corrected finding.** On the corrected evaluation using 1,012 aligned FLORES-200 sentences, GPT-2 produces about 7.42x as many tokens for Hindi as for English. For Kannada, Tamil and Telugu, the corresponding ratios are approximately 13.59x, 15.54x and 12.97x. In comparison, the multilingual mT5 tokenizer produces much smaller ratios, ranging from approximately 1.26x to 1.58x.

These results show that the original 6x Hindi result should not be treated as a fixed property of Hindi or Unicode text. Tokenization cost depends strongly on the tokenizer being used.

**Recommendation.** Evaluate only deployable model-tokenizer pairs that first satisfy the required task-quality threshold. For each candidate, replay a stratified and privacy-safe production-like dataset and measure:

- input tokens per successful request,
- output tokens per successful request,
- latency,
- task quality,
- language, and
- task type.

For offline cross-language comparison, tokens per aligned sentence is the primary metric because the aligned sentences approximately preserve the same underlying content. For production capacity and cost planning, actual tokens processed per successful request should be used.

A tokenizer should not normally be replaced independently of its model because the model's vocabulary, token IDs and embeddings are trained together with that tokenizer. Therefore, routing decisions should compare compatible model-tokenizer pairs rather than standalone tokenizers.

**Main limitation.** FLORES-200 is not representative of all real application traffic. It mainly contains translated formal text and does not adequately represent code-switching, Romanised Indic text, informal chat spelling, abbreviations, emojis or the application's real prompt-length distribution. Tokenizer efficiency also does not prove that a model will produce better answers.

**Production guardrail.** Monitor the p95 total processed or billed tokens per successful request, segmented by language and task, together with a fixed quality threshold. Compare each language's rolling seven-day token ratio against the pre-launch evaluation. If the ratio differs by more than 20%, investigate possible domain drift, language-detection errors, preprocessing differences or changes in traffic patterns.

The final routing decision should therefore be based on **quality first, followed by measured token cost and latency**, rather than on a fixed language multiplier.