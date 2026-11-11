# Lab 01 — Measured Results

Run of the committed code, stand-in client, seed 20261110,
2026-11-10. Reproduce with `python3 run_lab.py`; the harness in
the repo root re-runs this lab and fails if these numbers drift.

| Pass | Calls | Prompt tokens | Completion tokens | Cost (USD) | Latency mean | Latency p95 |
|---|---|---|---|---|---|---|
| Lean instructions | 12 | 222 | 1,473 | 0.003057 | 529.2 ms | 748.8 ms |
| Bloated instructions | 12 | 2,526 | 1,473 | 0.004209 | 558.0 ms | 848.0 ms |

Rates used (illustrative): $0.50 per million input tokens,
$2.00 per million output tokens.

**Instruction overhead:** the bloated block adds 2,304 prompt
tokens across the 12 calls — 1,037.8% of the lean pass's entire
prompt-token count — and raises the bill by $0.001152, or
**+37.7%**, for identical tasks and identical completions. Both
percentages are true; the first describes input volume, the
second describes money, and the gap between them is the output
tokens dominating the lean bill.

**Most input-dominated call:** "Give a one-line review of an
imaginary restaurant called The Salt Oak." — under the bloated
block it spends 214 prompt tokens to earn a 44-token completion
(83% of its tokens are input). Short calls are where shared
instruction overhead hurts most, which is why the exercise
targets exactly this call.

**Latency note:** the two passes' latency distributions are
close because the stand-in's modelled latency is driven by
completion length, and completions are identical across passes.
The honest reading is the narrow one: in this harness, verbose
instructions cost tokens and money, not meaningful time.
