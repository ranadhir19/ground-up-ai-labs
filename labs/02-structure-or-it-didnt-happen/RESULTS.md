# Lab 02 — Measured Results

Run of the committed code, 200 cases, seed 20261110, 2026-11-10.
Reproduce with `python3 run_lab.py`; the repo harness re-runs
this lab and fails if these numbers drift.

| Pipeline | Valid records | Validity rate | Field accuracy |
|---|---|---|---|
| Naive (`json.loads` + strict types) | 115 / 200 | 57.5% | 57.5% |
| Repaired (locate, clean, coerce, one default) | 200 / 200 | 100% | 99.4% |

**Defect mix in the 200 cases:** clean 115, trailing comma 19,
prose wrapper 17, boolean-as-word 16, number-as-string 13,
missing field 13, tags-as-string 7. The naive pipeline accepts
exactly the clean cases and nothing else — its validity rate *is*
the clean rate, which is the point: an unrepaired pipeline's
reliability is set entirely by the generator's mood.

**Per-defect outcome:** every defect class goes from 0 valid
(naive) to fully valid (repaired) — except that the missing-field
class is where the accuracy cost hides. The 13 missing-`done`
records all become valid via the documented default `false`,
but the default is wrong for the share of those records whose
true value was `true`; that is the entire 0.6-point gap between
100% validity and 99.4% field accuracy (6 of 1,000 fields).

**The honest reading:** repair bought 42.5 points of validity
for 0.6 points of silent wrongness, concentrated in exactly one
policy decision. Whether that trade is acceptable depends on
what `done` means downstream — which is why the lab reports the
two metrics separately instead of blending them into a score
that would hide the trade.
