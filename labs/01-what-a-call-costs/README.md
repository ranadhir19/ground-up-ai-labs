# Lab 01 — What a Call Actually Costs

**The need.** Almost every AI feature is priced, throttled and
judged by three numbers its builder has never measured: how many
tokens go in, how many come out, and how long the call takes.
Guesses compound — a prompt that is "a bit long" is pasted into
every request a product ever makes. This lab replaces the guess
with an instrument.

**What you build.** A small accounting harness (in `run_lab.py`)
that sends a fixed set of twelve task prompts through a client
twice — once under a lean instruction block and once under a
bloated one — and reports the latency distribution, the token
accounting, and the bill at stated, illustrative rates. The default
client is a deterministic local stand-in (see
`labs/common/client.py`): it exists so the numbers reproduce on any
machine at $0. Its token counts come from a documented estimator
and its latencies are *modelled*, labelled as such, never passed
off as network measurements. Point the environment variables
`GUAL_BASE_URL` / `GUAL_MODEL` / `GUAL_API_KEY` at any
OpenAI-compatible endpoint and the same harness measures the real
thing.

**What to notice when you run it.**

- The bloat is *shared* overhead: it is paid on every call, so its
  cost scales with call count, not with how good the answer is.
- Output tokens dominate the lean bill (they are priced higher and
  there are more of them), which is why the bloat shows up as a
  large percentage of *input* tokens but a smaller percentage of
  *total cost*. Both percentages are in the results; quoting only
  one of them would mislead in opposite directions.
- Latency in this harness is driven by completion length, so the
  two passes' latency distributions sit close together. Verbose
  instructions mostly cost money, not time. Verify that claim with
  the real endpoint if you have one — it is the kind of "everyone
  knows" that deserves a measurement.

**Run it.**

```bash
cd labs/01-what-a-call-costs
python3 run_lab.py
cat results.json
```

**Exercise.** Find the call in the results whose cost is most
dominated by its input side (the results name it). Cut that call's
total cost by at least a third *without changing its task or its
instruction's intent* — only its wording. Re-run and report the
before/after cost and the exact words you removed. Pass condition:
the one-third cut is visible in `results.json`, and your removed
text contains no instruction the lean version needed.

**The habit.** Instrument first. Every later lab in this series
assumes you can state, for any system you build, what one run of
it costs and how long it takes — because you measured, not because
the pricing page made you feel informed.
