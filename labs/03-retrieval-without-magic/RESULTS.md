# Lab 03 — Measured Results

Run of the committed code, 20 documents, 26 questions
(20 direct, 6 paraphrase), 2026-11-10. Reproduce with
`python3 run_lab.py`; the repo harness re-runs this lab and
fails if these numbers drift.

| Indexing mode | Recall@1 overall | Recall@3 overall | Recall@1 direct | Recall@1 paraphrase |
|---|---|---|---|---|
| Whole document | 1.000 (26/26) | 1.000 | 1.000 | 1.000 (6/6) |
| Paragraph chunks | 0.923 (24/26) | 1.000 | 1.000 | 0.667 (4/6) |

**The two misses, both under chunking, both paraphrases:**

1. "I need the lights and fridge to survive a long grey spell
   with barely any sun — how much stored power is enough?"
   Target: `solar-sizing.md`, ranked 2nd. Winner:
   `windsurfing.md` — a single paragraph there shares the
   question's weather-and-power vocabulary ("wind", "power",
   "spell" of conditions) while the solar document's answer is
   spread across paragraphs about loads, sun hours and storage,
   no one of which concentrates enough of the question's terms.
2. "My blueberry bushes keep yellowing even though I feed them —
   what hidden soil property should I check?" Target:
   `soil-ph.md`, ranked 2nd. Winner: `raised-beds.md`, whose
   paragraphs about feeding and soil mixes match the question's
   surface words; the target's discriminating terms (pH,
   acidity) are exactly the ones the paraphrase avoids.

**A note on how this corpus was built.** The first version held
14 documents, all topically isolated, and the retriever scored a
perfect 26-equivalent under both modes — a saturated benchmark
that teaches nothing. Six near-neighbour documents were added
(kombucha, aquarium, immersion coffee, homebrewing, raised beds,
windsurfing) precisely so that wrong answers became *plausible*.
The numbers above are from the hardened corpus.

**The honest reading:** at this scale, whole-document TF-IDF is
robust and chunking's rank-1 precision is fragile on
paraphrases — the opposite of the default assumption most RAG
tutorials install. Both modes put every correct document in the
top 3, so a system that shows three candidates survives either
way; a system that trusts rank 1 alone does not. Chunking earns
its place when documents are long and the task is locating a
passage, not ranking pamphlets — the configuration must be
measured on the corpus you have, in the mode you run.
