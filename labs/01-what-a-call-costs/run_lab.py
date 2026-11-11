#!/usr/bin/env python3
"""Lab 01 — What a Call Actually Costs.

Runs a fixed set of task prompts through the shared client twice:
once under a lean instruction block and once under a bloated one.
Reports the latency distribution, the token accounting, a cost table
at illustrative rates, and exactly how much the bloat costs.

Writes results.json next to this file and prints a GUAL-RESULT line.
Deterministic with the stand-in client (the default).
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.client import default_client  # noqa: E402

HERE = Path(__file__).resolve().parent

LEAN = "Answer the request directly and concisely."

BLOATED = """You are a helpful, harmless, and honest AI assistant. You should
always be helpful, harmless and honest in everything you do. You must
answer questions to the best of your ability. You should be concise
but also complete, and complete but also concise. You must not refuse
unless refusal is necessary. You should use a friendly tone at all
times, and a professional tone at all times. You should format your
answers nicely, with good formatting, where formatting helps. You
should consider the user's request carefully, thinking step by step
about the request, the context of the request, and the best way to
answer the request, before answering the request. You are an AI
assistant whose purpose is to assist. Assistance means helping. When
helping, help helpfully. Always remember: be helpful, be harmless,
be honest, be concise, be complete, be friendly, be professional,
and above all, answer the request that the user has requested, in
response to their request, with an answer."""

PROMPTS = [
    "Summarise the plot of a mystery novel in two sentences.",
    "Give me a three-step plan to change a bicycle tyre.",
    "What is the difference between a virus and a bacterium?",
    "Write a haiku about rain on a tin roof.",
    "List five uses for a paperclip that are not holding paper.",
    "Explain photosynthesis to a ten-year-old.",
    "Draft a polite email declining a meeting invitation.",
    "What are the primary colours, and why those three?",
    "Give a one-line review of an imaginary restaurant called The Salt Oak.",
    "Describe how to make a cup of tea, step by step.",
    "Name three animals that change colour with the seasons.",
    "Write a single sentence that uses the word 'ledger' naturally.",
]

# Illustrative rates only — the shape of the bill is the lesson,
# not these particular numbers.
RATE_IN_PER_M = 0.50
RATE_OUT_PER_M = 2.00


def run_pass(client, system: str) -> dict:
    rows = []
    for prompt in PROMPTS:
        r = client.complete(prompt, system=system)
        rows.append({
            "prompt": prompt,
            "prompt_tokens": r.prompt_tokens,
            "completion_tokens": r.completion_tokens,
            "latency_ms": r.latency_ms,
            "cost_usd": (r.prompt_tokens * RATE_IN_PER_M
                         + r.completion_tokens * RATE_OUT_PER_M) / 1e6,
        })
    lat = [r["latency_ms"] for r in rows]
    return {
        "calls": len(rows),
        "prompt_tokens": sum(r["prompt_tokens"] for r in rows),
        "completion_tokens": sum(r["completion_tokens"] for r in rows),
        "cost_usd": round(sum(r["cost_usd"] for r in rows), 6),
        "latency_mean_ms": round(statistics.mean(lat), 1),
        "latency_p95_ms": round(sorted(lat)[int(0.95 * len(lat)) - 1], 1),
        "rows": rows,
    }


def main() -> int:
    client = default_client(seed=20261110)
    lean = run_pass(client, LEAN)
    bloated = run_pass(client, BLOATED)
    overhead_tokens = bloated["prompt_tokens"] - lean["prompt_tokens"]
    results = {
        "lab": "01-what-a-call-costs",
        "client_source": "stand-in (modelled latency)"
        if type(client).__name__ == "StandInClient" else "http (measured)",
        "rates_usd_per_million": {"input": RATE_IN_PER_M,
                                  "output": RATE_OUT_PER_M},
        "lean": {k: v for k, v in lean.items() if k != "rows"},
        "bloated": {k: v for k, v in bloated.items() if k != "rows"},
        "instruction_overhead": {
            "extra_prompt_tokens": overhead_tokens,
            "extra_prompt_tokens_pct_of_lean":
                round(100.0 * overhead_tokens / lean["prompt_tokens"], 1),
            "extra_cost_usd": round(bloated["cost_usd"] - lean["cost_usd"], 6),
            "extra_cost_pct": round(
                100.0 * (bloated["cost_usd"] - lean["cost_usd"])
                / lean["cost_usd"], 1),
        },
        "most_input_dominated_call": {
            **max(bloated["rows"],
                  key=lambda r: r["prompt_tokens"]
                  / (r["prompt_tokens"] + r["completion_tokens"])),
        },
        "per_prompt": lean["rows"],
    }
    (HERE / "results.json").write_text(json.dumps(results, indent=2))
    print("GUAL-RESULT " + json.dumps({
        "lean_cost_usd": results["lean"]["cost_usd"],
        "bloated_cost_usd": results["bloated"]["cost_usd"],
        "overhead_pct": results["instruction_overhead"]["extra_cost_pct"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
