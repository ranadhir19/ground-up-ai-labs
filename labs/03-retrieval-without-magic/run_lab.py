#!/usr/bin/env python3
"""Lab 03 — Retrieval Without Magic.

TF-IDF retrieval built from scratch (tokeniser, document
frequencies, TF-IDF weighting, cosine similarity — standard
library only) over the bundled corpus of 14 original documents.

Two indexing modes are compared on a 20-question labelled set
(16 direct questions, 4 deliberate paraphrases):
  - whole-document: one vector per document;
  - chunked: one vector per paragraph, a document's score is its
    best chunk's score.

Metrics: recall@1 and recall@3, overall and for the paraphrase
subset. Writes results.json and prints a GUAL-RESULT line.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus"

STOP = set("""a an the and or of to in is it its as at on for with by
from that this be are was were has have had not no do does did how what
why when which who will would can could should i you he she they we
my your his her their our me him them one two""".split())


def tokenise(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", text.lower())
            if t not in STOP and len(t) > 1]


class TfidfIndex:
    def __init__(self, units: list[tuple[str, str]]) -> None:
        """units: list of (doc_name, text)."""
        self.units = units
        tokenised = [tokenise(text) for _, text in units]
        n = len(units)
        df: Counter = Counter()
        for toks in tokenised:
            df.update(set(toks))
        self.idf = {t: math.log((n + 1) / (c + 1)) + 1.0
                    for t, c in df.items()}
        self.vectors = [self._vectorise(toks) for toks in tokenised]

    def _vectorise(self, toks: list[str]) -> dict[str, float]:
        counts = Counter(toks)
        vec = {}
        for term, c in counts.items():
            tf = 1.0 + math.log(c)
            vec[term] = tf * self.idf.get(term, 1.0)
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {t: v / norm for t, v in vec.items()}

    def rank(self, query: str) -> list[tuple[str, float]]:
        qcounts = Counter(tokenise(query))
        qvec = {}
        for term, c in qcounts.items():
            if term in self.idf:
                qvec[term] = (1.0 + math.log(c)) * self.idf[term]
        norm = math.sqrt(sum(v * v for v in qvec.values())) or 1.0
        qvec = {t: v / norm for t, v in qvec.items()}
        best: dict[str, float] = {}
        for (doc, _), vec in zip(self.units, self.vectors):
            score = sum(w * vec.get(t, 0.0) for t, w in qvec.items())
            if score > best.get(doc, -1.0):
                best[doc] = score
        return sorted(best.items(), key=lambda kv: -kv[1])


def load_units(mode: str) -> list[tuple[str, str]]:
    units = []
    for path in sorted(CORPUS.glob("*.md")):
        text = path.read_text()
        if mode == "whole":
            units.append((path.name, text))
        else:
            for para in text.split("\n\n"):
                if para.strip():
                    units.append((path.name, para))
    return units


def evaluate(index: TfidfIndex, questions: list[dict]) -> dict:
    rows = []
    for item in questions:
        ranked = [doc for doc, _ in index.rank(item["q"])]
        target = item["doc"]
        rows.append({
            "q": item["q"], "doc": target, "kind": item["kind"],
            "rank": ranked.index(target) + 1 if target in ranked else None,
            "top1": ranked[0] if ranked else None,
        })

    def block(subset: list[dict]) -> dict:
        if not subset:
            return {"n": 0, "recall@1": 0.0, "recall@3": 0.0}
        return {
            "n": len(subset),
            "recall@1": round(sum(r["rank"] == 1 for r in subset)
                              / len(subset), 4),
            "recall@3": round(sum(r["rank"] is not None and r["rank"] <= 3
                                  for r in subset) / len(subset), 4),
        }

    return {
        "overall": block(rows),
        "direct": block([r for r in rows if r["kind"] == "direct"]),
        "paraphrase": block([r for r in rows if r["kind"] == "paraphrase"]),
        "rows": rows,
    }


def main() -> int:
    questions = json.loads((HERE / "questions.json").read_text())
    results = {"lab": "03-retrieval-without-magic",
               "documents": len(list(CORPUS.glob('*.md'))),
               "questions": len(questions)}
    for mode in ("whole", "chunked"):
        index = TfidfIndex(load_units(mode))
        results[mode] = evaluate(index, questions)
    (HERE / "results.json").write_text(json.dumps(results, indent=2))
    print("GUAL-RESULT " + json.dumps({
        "whole_recall@1": results["whole"]["overall"]["recall@1"],
        "chunked_recall@1": results["chunked"]["overall"]["recall@1"],
        "whole_paraphrase_recall@1":
            results["whole"]["paraphrase"]["recall@1"],
        "chunked_paraphrase_recall@1":
            results["chunked"]["paraphrase"]["recall@1"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
