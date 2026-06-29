# Novelty Notes: Claimed Contributions vs. Implemented Reality

`DESIGN_DOC.md` lists five "Novel Contributions" for the DARPA LYFT continual-learning
(CL) program. This note tracks, honestly, which of those are backed by code/data in
this repository today, versus which remain design-stage claims. It complements the
more detailed `PAPER_DRAFT.md` Section 4 ("Implementation Status vs. DESIGN_DOC.md")
with a contribution-by-contribution view, and is meant to stop the claimed novelty
from drifting further from the implemented reality as the repo evolves.

| Claimed contribution (DESIGN_DOC.md) | Implemented? | Notes |
|---|---|---|
| **LYFT-Bench** -- 6-domain CL benchmark for defense/logistics | No | No `data/lyft_bench/` directory, no real domain datasets (threat classification, logistics routing, sensor fusion, NL orders, anomaly detection, terrain analysis). Only synthetic, hand-authored task-sequence generators exist (`src/darpalyft/data.py`), which are not domain-specific and do not use real data. |
| **FTR metric** (Forward Transfer Rate, steps-to-criterion formula) | Partially | `forward_transfer()` in `src/darpalyft/evaluate.py` implements an *accuracy-based* proxy (mean zero-shot accuracy before training), not the steps-to-criterion ratio formula specified in `DESIGN_DOC.md`. The two are conceptually related but not interchangeable, and results computed with one should not be reported as the other. |
| **Meta-CL framework** (MAML + regularization for edge CL) | No | No `methods/` directory exists. Fine-tuning, EWC, iCaRL, GEM, MAML, and Meta-CL are all unimplemented; no model training code exists anywhere in the repo. |
| **Edge efficiency score** (accuracy x latency x power composite, validated on Jetson Orin NX) | No | No `edge/jetson_benchmark.py`; no hardware-in-loop measurements; no edge efficiency score implementation. |
| **Forgetting-transfer Pareto analysis** | No | No Pareto-curve computation over CL methods/hyperparameters exists. `src/darpalyft/evaluate.py` has no Pareto-front logic for this purpose (the *drone* module's `pareto_designs()` is for a different, unrelated optimization problem and is not reused here). |

## What is actually novel and working right now

- The **CL metric implementations** (`backward_transfer`, `forward_transfer`,
  `continual_learning_score`, `plasticity_score`, `stability_score`,
  `domain_drift_penalty`) are real, tested code (`tests/test_continual_learning.py`,
  16 tests) and produce real numbers when run against synthetic sequences
  (`results/cl_metrics.md`). This is useful infrastructure, but it is metric
  tooling, not a benchmark, a method, or an experimental result.
- The framing in `DESIGN_DOC.md` -- jointly optimizing forward transfer and
  forgetting under edge-hardware constraints, rather than only minimizing
  forgetting -- remains a reasonable and underexplored angle relative to most
  published CL work (see `PAPER_DRAFT.md` references). That assessment is about
  the *idea's* merit, independent of whether it has been executed here.

## Why this file exists

Several currently-open issues in this repository (e.g., the related-work audit,
statistical-rigor, and reproducibility-package issues) propose work that assumes
LYFT-Bench, the six CL methods, and the edge benchmark already exist in some form.
As of this writing they do not. Anyone picking up this repo should read this file
and `PAPER_DRAFT.md` Section 4 before treating any DESIGN_DOC.md number as an
experimental result.
