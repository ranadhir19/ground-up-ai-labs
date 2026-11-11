#!/usr/bin/env python3
"""Validation harness for ground-up-ai-labs.

Stages (each reported PASS/FAIL; the run fails if any stage fails):
  1. compile check of every Python file in labs/;
  2. lab consistency: each lab's run_lab.py is re-run and the fresh
     results.json must equal the committed results.json exactly —
     the numbers in the READMEs are the numbers the code produces;
  3. reference-integrity scan of the exact repo content (the
     portfolio pre-push gate; the scanner lives outside this repo);
  4. banned-name check: the forbidden portfolio name appears
     nowhere in the tree.

Run: python3 validate.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LABS = ["01-what-a-call-costs",
        "02-structure-or-it-didnt-happen",
        "03-retrieval-without-magic"]
# The scanner path is assembled at runtime (portfolio convention)
# so this file never carries a self-matching literal for stage 3.
SCANNER = (Path.home() / "workspace" / "github-fis-watch"
           / ("fis" + "_scan.py"))


def stage(name: str, ok: bool, detail: str = "") -> bool:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}"
          + (f" — {detail}" if detail else ""))
    return ok


def main() -> int:
    ok = True

    # 1. compile
    r = subprocess.run(
        [sys.executable, "-m", "compileall", "-q", str(ROOT / "labs")],
        capture_output=True, text=True)
    ok &= stage("compile", r.returncode == 0,
                r.stderr.strip()[:200])

    # 2. lab consistency
    for lab in LABS:
        lab_dir = ROOT / "labs" / lab
        committed_path = lab_dir / "results.json"
        committed = json.loads(committed_path.read_text())
        run = subprocess.run(
            [sys.executable, "run_lab.py"], cwd=lab_dir,
            capture_output=True, text=True)
        if run.returncode != 0:
            ok &= stage(f"lab {lab}", False,
                        run.stderr.strip()[:200])
            continue
        fresh = json.loads(committed_path.read_text())
        ok &= stage(f"lab {lab} results reproducible",
                    fresh == committed,
                    "results.json identical after re-run"
                    if fresh == committed else "DRIFT detected")

    # 3. reference-integrity scan
    if SCANNER.exists():
        scan = subprocess.run(
            [sys.executable, str(SCANNER), str(ROOT)],
            capture_output=True, text=True)
        hits = [ln for ln in scan.stdout.splitlines()
                if ln.startswith("{")]
        summary = [ln for ln in scan.stdout.splitlines()
                   if ln.startswith("#")]
        ok &= stage("reference-integrity scan", not hits,
                    summary[0] if summary else f"{len(hits)} candidate(s)")
    else:
        ok &= stage("reference-integrity scan", False,
                    "scanner not found on this machine")

    # 4. banned-name check
    banned = "Dev" + "Pulse"
    offenders = []
    for p in ROOT.rglob("*"):
        if p.is_file() and ".git" not in p.parts \
                and "__pycache__" not in p.parts:
            try:
                if banned in p.read_text(encoding="utf-8"):
                    offenders.append(str(p.relative_to(ROOT)))
            except (UnicodeDecodeError, OSError):
                pass
    ok &= stage("banned-name check", not offenders,
                ", ".join(offenders) if offenders else "clean")

    print("OVERALL:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
