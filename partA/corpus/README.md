# Corpus provenance and limitations

This audit uses the 1,012-sentence FLORES-200 `devtest` split in five aligned languages: English (`eng_Latn`), Hindi (`hin_Deva`), Kannada (`kan_Knda`), Tamil (`tam_Taml`) and Telugu (`tel_Telu`). The files were obtained from the AI4Bharat CTQScorer repository, which contains these FLORES files. FLORES sentences originate from Wikinews, Wikibooks/Wikijunior and Wikivoyage and were professionally translated. The same line number represents the same underlying content in each language.

Source: https://github.com/AI4Bharat/CTQScorer/tree/main/dataset/test

FLORES description: https://github.com/facebookresearch/flores/tree/main/flores200

Preprocessing is intentionally minimal: blank lines are removed and text is NFC-normalised at analysis time. Case and punctuation are preserved for corrected headline results. The script asserts equal line counts before analysis.

## What this corpus cannot tell us

FLORES is much stronger than the ten-line smoke sample, but 1,012 translated sentences from news, educational and travel domains are not production traffic. It under-represents code-switching, Romanised Indic, chat abbreviations, spelling variation, emojis, application-specific prompts and long documents. Translations may also differ from native conversational writing. Therefore the results estimate relative tokenizer cost for aligned formal content, not a universal language multiplier. Production routing should be validated on privacy-safe traffic sampled by language, domain and prompt-length bucket.

