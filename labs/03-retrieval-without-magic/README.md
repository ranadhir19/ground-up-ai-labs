# Lab 03 — Retrieval Without Magic

**The need.** Retrieval-augmented generation is usually taught as
a library call: embed, index, query, receive chunks. When it
fails in production, the builder who only ever called the library
has no model of *why* — no sense of what a term weight is, what a
chunk does to the statistics, or why a question phrased the way
users actually phrase things can miss a document that plainly
answers it. This lab builds the retriever from arithmetic, then
measures where it bends.

**What you build.** In `run_lab.py`: a TF-IDF retriever written
from scratch — tokeniser, document frequencies, TF-IDF weighting,
cosine similarity, nothing imported beyond the standard library —
over a bundled corpus of twenty short original documents
(`corpus/`). Six of the documents are deliberate near-neighbours
of six others (a kombucha jar beside the sourdough jar, a fish
tank beside the pond), because a corpus of strangers is too easy
to teach anything. The retriever is scored under two indexing
modes — one vector per document, and one vector per paragraph
with the document inheriting its best paragraph's score — on 26
labelled questions, six of them paraphrases that avoid the
documents' own vocabulary.

**What the measurement shows** (full numbers in `RESULTS.md`).
Whole-document retrieval gets every question's document at rank
1. Chunking — the technique every RAG tutorial reaches for
first — *loses* two paraphrase questions to rank 2. Short texts
make noisy statistics: a single paragraph from a neighbouring
document can out-score the right document's best paragraph,
while whole-document aggregation averages that noise away. That
is not an argument against chunking; chunking exists to locate
the answer passage inside long documents, which is a different
job from ranking short ones. It is an argument for measuring the
configuration you actually run, on questions phrased the way
your users actually fail.

**Run it.**

```bash
cd labs/03-retrieval-without-magic
python3 run_lab.py
cat results.json
```

**Exercise.** Write two questions that push the correct document
out of rank 1 under *either* mode (the results name the two
questions that already manage it under chunking — beat the other
mode, or beat both). For each of your questions, diagnose the
failure from the term statistics: which terms did the question
share with the wrong document, which discriminating terms did it
lack, and what property of the weighting let the wrong document
win? Pass condition: both questions demonstrably rank a wrong
document first, and each diagnosis names specific terms — not
"the retriever got confused."

**The habit.** Every retrieval system is a bet about how
questions and documents share vocabulary. This lab is the bet
made visible — and, once visible, measurable every time the
corpus or the configuration changes.
