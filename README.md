# Ground-Up AI Labs

**A bench manual for AI engineering: one sitting, one runnable
experiment, one number you produced yourself.**

Most AI-engineering material is something you watch. This series
is something you *run*. Each lab is a standalone, framework-free
experiment — pure Python standard library, no API key, a few
minutes on any laptop — that builds one piece of an AI system
from first principles and ends with a measurement you reproduce
on your own machine, plus an exercise with a stated pass
condition.

The labs are the companion bench work for
**[The Architect's AI Workshop](https://www.youtube.com/@ArchitectsAIWorkshop)**
— *first principles on the whiteboard, built live in the editor,
measured honestly, failures included.* The channel's course
teaches the syllabus; these labs are where your hands learn it.
Every number printed in this repository was produced by running
the committed code, and the repo's own harness
(`python3 validate.py`) re-runs every lab and fails if a
committed number has drifted from the code that claims it.

## The labs

| # | Lab | The question it answers | Headline result |
|---|---|---|---|
| 01 | [What a Call Actually Costs](labs/01-what-a-call-costs/) | What do tokens, latency and instructions really cost? | A bloated instruction block added +37.7% to the bill for identical work |
| 02 | [Structure, or It Didn't Happen](labs/02-structure-or-it-didnt-happen/) | How often is "the model returns JSON" actually true? | Naive parsing: 57.5% valid. Named repairs: 100% valid, 99.4% accurate — and the gap is a lesson |
| 03 | [Retrieval Without Magic](labs/03-retrieval-without-magic/) | What does a retriever actually bet on? | Whole-document TF-IDF beat chunked indexing at rank 1 on paraphrases — the opposite of the usual assumption |
| 04 | Tools, Then a Loop *(planned)* | Does an agent loop beat one good retrieval? | — |
| 05 | Change One Thing *(planned)* | Did that change help, or did the noise move? | — |
| 06 | Break It Before Production Does *(planned)* | What does your system do when the API misbehaves? | — |

## Run one

```bash
git clone https://github.com/ranadhir19/ground-up-ai-labs
cd ground-up-ai-labs
python3 labs/01-what-a-call-costs/run_lab.py
cat labs/01-what-a-call-costs/results.json
```

Requires Python 3.10+. No dependencies, no accounts, no keys.

Every lab runs by default against a deterministic local stand-in
client (`labs/common/client.py`), so results reproduce exactly.
Point `GUAL_BASE_URL` / `GUAL_MODEL` / `GUAL_API_KEY` at any
OpenAI-compatible endpoint and the same code measures a real
model instead — the labs say plainly which numbers are modelled
and which are measured.

## How each lab is built

- **README.md** — the need, the build, what to notice, the
  exercise and its pass condition.
- **run_lab.py** — the complete experiment, standard library
  only.
- **RESULTS.md / results.json** — the measured outcome of the
  committed code, with the honest reading, including where the
  result embarrassed the obvious assumption.

## Validate the whole repo

```bash
python3 validate.py
```

Compiles every lab, re-runs each one and compares its fresh
`results.json` against the committed copy, scans the tree for
reference integrity, and checks the banned-name list. Green
means the numbers in this README are the numbers the code
produces.

## Licence

MIT. The corpus documents, questions, code and text in this
repository are original works written for this series.
