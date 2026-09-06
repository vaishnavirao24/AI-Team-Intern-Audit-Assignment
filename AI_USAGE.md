# AI usage disclosure

I used ChatGPT/Codex extensively while completing this assignment. AI was used to inspect the assignment requirements, identify possible audit issues, develop the initial Python analysis, check calculations, structure the written answers and memos, and prepare the first version of the submission. A substantial part of the initial code and prose was AI-assisted/generated.

The AI-assisted analysis identified issues such as the tokenizer comparison denominator, the inclusion of prompt tokens in reported throughput, KV-cache capacity calculations, macro/micro averaging, Unicode grapheme counting, and reproducible evaluation of the supplied data.

I did not treat the generated solution as final without verification. I set up the project locally on my own machine and reproduced the analysis. Python was initially unavailable in my environment, so I installed Python 3.11, created a virtual environment, and installed the dependencies from `requirements.txt`.

I personally ran:

`python partA/audit.py --all`

and

`python partB/analyse_capacity.py`

I inspected the generated `partA/results/corrected_metrics.csv` and verified key tokenizer results. The evaluation contains 1,012 aligned sentences per language. For example, GPT-2 produced 200,704 Hindi tokens compared with 27,044 English tokens, giving approximately 7.42x, while mT5 produced 53,495 Hindi tokens compared with 33,791 English tokens, giving approximately 1.58x.

I also reproduced the capacity-analysis output, including approximately 114,688 KV-cache bytes per token, capacity for 25 full 4,096-token sequences, batch-24 output goodput of approximately 200.9 tok/s, and the appearance of preemptions beyond batch size 24.

Before submission and defence, I am reviewing the code, calculations, assumptions, and written recommendations so that I can explain and reproduce the submitted results. I understand that I am responsible for the correctness of the final submission even where AI assistance was used.