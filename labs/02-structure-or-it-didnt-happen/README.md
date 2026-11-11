# Lab 02 — Structure, or It Didn't Happen

**The need.** Downstream code does not consume prose; it consumes
records. "The model usually returns JSON" is not an interface —
the failures live in the tail: the answer wrapped in a sentence,
the trailing comma, the number that arrived as a string. This lab
measures that tail and then engineers it down, one named defect
class at a time.

**What you build.** In `run_lab.py`: a generator that emits 200
task records as model-style output with a known, seeded mix of
defects, plus two extraction pipelines scored against the ground
truth the generator started from. The *naive* pipeline is what
most demos ship: `json.loads` and strict type checks. The
*repaired* pipeline adds exactly four things: locate the JSON
object inside surrounding prose, remove trailing commas, coerce
the documented type mismatches (number-as-string, boolean-as-word,
tags-as-string), and apply one documented default for a missing
field. Nothing else. Every repair is a named response to a named
defect — that discipline is the lesson.

**The distinction the numbers force.** Validity and correctness
are different metrics, and the repaired pipeline wins them by
different margins. The documented default for the missing `done`
field makes those records *valid* — and quietly wrong whenever
the true value was the other one. The field-accuracy figure in
the results is where that cost shows up. A default is a policy
decision wearing a repair's clothing; this lab makes you watch
it happen on data you control.

**Run it.**

```bash
cd labs/02-structure-or-it-didnt-happen
python3 run_lab.py
cat results.json
```

**Exercise.** Add one new defect class to the generator (your
choice — a plausible way real model output breaks) and one repair
rule that answers it, in the same named style. Re-run and report:
the new defect's case count, validity before and after your rule,
and whether field accuracy moved. Pass condition: your rule lifts
your defect class to full validity *without* lowering validity or
accuracy on any pre-existing class — the per-defect table in
`results.json` is where you prove it.

**The habit.** Never say "the model returns JSON." Say which
defect classes you have seen, which you repair, which you reject,
and what each choice costs — measured on cases whose truth you
know.
