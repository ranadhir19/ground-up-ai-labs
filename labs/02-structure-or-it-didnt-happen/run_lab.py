#!/usr/bin/env python3
"""Lab 02 — Structure, or It Didn't Happen.

A stand-in generator emits 200 task records as "model output" text
with a known, seeded mix of defects (prose around the JSON, trailing
commas, numbers as strings, booleans as words, tags as a comma
string, a missing field). Two extraction pipelines are scored
against the ground truth:

- naive: ``json.loads`` and strict type checks, nothing else;
- repaired: locate the JSON object, remove trailing commas, coerce
  the documented type mismatches, apply the one documented default.

Metrics: strict validity rate and field-level accuracy.
Writes results.json and prints a GUAL-RESULT line. Deterministic.
"""

from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
N = 200
SEED = 20261110

TITLES = ["Fix the leaking tap", "Renew the library card",
          "Book the hall for Saturday", "Water the greenhouse",
          "Service the bicycle", "Call the electrician",
          "Order more seed packets", "Paint the shed door",
          "Back up the photo archive", "Sharpen the mower blade",
          "Replace the porch light", "Descale the kettle"]
TAGPOOL = ["home", "garden", "admin", "repair", "family", "finance",
           "health", "travel"]


def make_truth(rng: random.Random) -> list[dict]:
    out = []
    for i in range(N):
        out.append({
            "title": rng.choice(TITLES),
            "date": f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
            "tags": rng.sample(TAGPOOL, rng.randint(1, 3)),
            "priority": rng.randint(1, 5),
            "done": rng.random() < 0.4,
        })
    return out


def render(record: dict, rng: random.Random) -> tuple[str, str]:
    """Render one record as model output; return (text, defect)."""
    roll = rng.random()
    obj = dict(record)
    if roll < 0.55:
        return json.dumps(obj), "clean"
    if roll < 0.65:
        text = json.dumps(obj, indent=1)
        text = text.replace("\n}", ",\n}")
        return text, "trailing-comma"
    if roll < 0.75:
        return ("Here is the task you asked for:\n"
                + json.dumps(obj)
                + "\nLet me know if you need anything else!"), "prose-wrapper"
    if roll < 0.83:
        obj["priority"] = str(obj["priority"])
        return json.dumps(obj), "number-as-string"
    if roll < 0.90:
        obj["done"] = "yes" if obj["done"] else "no"
        return json.dumps(obj), "boolean-as-word"
    if roll < 0.95:
        obj["tags"] = ", ".join(obj["tags"])
        return json.dumps(obj), "tags-as-string"
    obj.pop("done")
    return json.dumps(obj), "missing-field"


def schema_valid(obj) -> bool:
    return (
        isinstance(obj, dict)
        and isinstance(obj.get("title"), str)
        and isinstance(obj.get("date"), str)
        and isinstance(obj.get("tags"), list)
        and all(isinstance(t, str) for t in obj["tags"])
        and isinstance(obj.get("priority"), int)
        and not isinstance(obj.get("priority"), bool)
        and isinstance(obj.get("done"), bool)
    )


def naive_parse(text: str):
    try:
        obj = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None
    return obj if schema_valid(obj) else None


def repaired_parse(text: str):
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return None
    snippet = text[start:end + 1]
    snippet = re.sub(r",\s*([}\]])", r"\1", snippet)  # trailing commas
    try:
        obj = json.loads(snippet)
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(obj, dict):
        return None
    if isinstance(obj.get("priority"), str) and obj["priority"].isdigit():
        obj["priority"] = int(obj["priority"])
    if isinstance(obj.get("done"), str):
        if obj["done"] in ("yes", "true"):
            obj["done"] = True
        elif obj["done"] in ("no", "false"):
            obj["done"] = False
    if isinstance(obj.get("tags"), str):
        obj["tags"] = [t.strip() for t in obj["tags"].split(",") if t.strip()]
    if "done" not in obj:
        obj["done"] = False  # the one documented default
    return obj if schema_valid(obj) else None


def field_accuracy(parsed: list, truth: list[dict]) -> float:
    total = correct = 0
    for got, want in zip(parsed, truth):
        if got is None:
            total += len(want)
            continue
        for key, value in want.items():
            total += 1
            if got.get(key) == value:
                correct += 1
    return round(correct / total, 4) if total else 0.0


def main() -> int:
    rng = random.Random(SEED)
    truth = make_truth(rng)
    rendered = [render(rec, rng) for rec in truth]
    defects = {}
    for _, defect in rendered:
        defects[defect] = defects.get(defect, 0) + 1

    naive = [naive_parse(text) for text, _ in rendered]
    repaired = [repaired_parse(text) for text, _ in rendered]

    per_defect = {}
    for defect in defects:
        idx = [i for i, (_, d) in enumerate(rendered) if d == defect]
        per_defect[defect] = {
            "cases": len(idx),
            "naive_valid": sum(naive[i] is not None for i in idx),
            "repaired_valid": sum(repaired[i] is not None for i in idx),
        }

    results = {
        "lab": "02-structure-or-it-didnt-happen",
        "cases": N,
        "seed": SEED,
        "defect_mix": defects,
        "naive": {
            "valid": sum(p is not None for p in naive),
            "valid_rate": round(sum(p is not None for p in naive) / N, 4),
            "field_accuracy": field_accuracy(naive, truth),
        },
        "repaired": {
            "valid": sum(p is not None for p in repaired),
            "valid_rate": round(sum(p is not None for p in repaired) / N, 4),
            "field_accuracy": field_accuracy(repaired, truth),
        },
        "per_defect": per_defect,
    }
    (HERE / "results.json").write_text(json.dumps(results, indent=2))
    print("GUAL-RESULT " + json.dumps({
        "naive_valid_rate": results["naive"]["valid_rate"],
        "repaired_valid_rate": results["repaired"]["valid_rate"],
        "repaired_field_accuracy": results["repaired"]["field_accuracy"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
