# Meta-CL for Defense/Logistics Continual Learning (DARPA LYFT) — Draft Skeleton

**Status: early draft / skeleton. Not submission-ready.** This document mirrors the
structure of `DESIGN_DOC.md` and separates (a) what has actually been built and
measured in this repository from (b) what is still projected/aspirational pending
full implementation. Do not cite the numbers below as experimental results until
the corresponding code in `methods/`, `experiments/`, and `edge/` (currently
unimplemented -- see "Implementation Status") exists and has been run.

## Abstract (draft)

Continual learning (CL) systems deployed in defense and logistics settings must
acquire new tactical/logistics knowledge over time without forgetting prior
knowledge, under tight edge-hardware constraints. We propose **LYFT-Bench**, a
6-domain CL benchmark spanning threat classification, logistics routing, sensor
fusion, NL orders, anomaly detection, and terrain analysis, and **Meta-CL**, a
meta-learning-based CL method targeting a Forward Transfer Rate (FTR) >= 0.50 --
2x the FTR of naive fine-tuning -- while simultaneously reducing catastrophic
forgetting. *(Projected, pending full experiment run: the FTR >= 0.50 and
forgetting < 0.10 targets are hypotheses from DESIGN_DOC.md, not yet
demonstrated by trained models.)*

## 1. Introduction (draft)

- Motivate the gap between academic CL benchmarks (Split CIFAR, Permuted MNIST)
  and deployment-realistic defense/logistics settings.
- State the four novel contributions claimed in `DESIGN_DOC.md`: LYFT-Bench,
  the FTR metric, the Meta-CL framework, and the forgetting-transfer Pareto
  analysis.
- *(To do: literature review -- EWC, iCaRL, GEM, MAML, Reptile; defense-AI CL
  surveys.)*

## 2. Metrics (implemented)

The following metrics are **implemented and unit-tested** in
`src/darpalyft/evaluate.py` and exercised against synthetic task sequences in
`src/darpalyft/data.py`:

- `backward_transfer` -- analogous to BWT in Lopez-Paz & Ranzato (2017); negative
  values indicate forgetting.
- `forward_transfer` -- analogous to FWT; measures zero-shot accuracy on a task
  before training on it.
- `continual_learning_score` -- a composite of normalized BWT and FWT.
- `plasticity_score`, `stability_score`, `domain_drift_penalty` -- auxiliary
  diagnostics.

These map conceptually to the FTR / Forgetting metrics defined in
`DESIGN_DOC.md`, but the *formula* used for FTR there (`steps_to_criterion`
ratio) is not what is implemented; the implemented `forward_transfer` is an
accuracy-based proxy, not a steps-to-criterion measure. This gap is tracked as
future work (Section 5).

## 3. Measured Results (real, computed by this repo's code)

`scripts/run_cl_experiments.py` runs the implemented metric suite over three
synthetic task-sequence generators (`make_task_sequence` with domain drift,
`make_iid_sequence`, `make_catastrophic_forgetting_sequence`) across 5 seeds
each. Full output: `results/cl_metrics.json` / `results/cl_metrics.md`.

Mean values across 5 seeds (computed from `results/cl_metrics.json`):

| Sequence type | Mean BWT | Mean FWT | Mean CL score | Mean plasticity |
|---|---|---|---|---|
| Domain-drift (6 tasks) | -0.061 | 0.079 | 0.274 | 0.613 |
| IID (6 tasks, no drift) | -0.062 | 0.081 | 0.275 | 0.750 |
| Catastrophic forgetting (5 tasks) | -0.595 | 0.022 | 0.112 | 0.810 |

**What this does and does not show**: this confirms the metric implementations
behave directionally as expected (catastrophic-forgetting sequences produce
strongly negative BWT and low CL score; IID sequences show no domain-drift
penalty). It does **not** constitute evidence for the design doc's claims about
Meta-CL vs. EWC/iCaRL/GEM/MAML, because none of those methods, nor LYFT-Bench's
6 real datasets, nor Jetson edge benchmarking are implemented yet (see below).
The "accuracy" values driving these metrics are synthetic, hand-authored curves
from `data.py`, not outputs of trained models.

## 4. Implementation Status vs. DESIGN_DOC.md

| Design doc component | Status |
|---|---|
| LYFT-Bench (6 real domain datasets) | **Not implemented.** No data/lyft_bench/ directory exists. |
| Task sequences A/B/C | **Not implemented** as specified; only synthetic drift/iid/catastrophic generators exist. |
| Fine-tuning, EWC, iCaRL, GEM, MAML, Meta-CL methods | **Not implemented.** No `methods/` directory; no model training code. |
| FTR / Forgetting / Edge Efficiency Score (as formally defined) | **Partially implemented** -- accuracy-based BWT/FWT proxies exist; steps-to-criterion FTR and Edge Efficiency Score are not implemented. |
| Experiments 0-5 | **Not implemented** as scripts (`experiments/exp0_baseline.py` etc. do not exist). |
| Jetson Orin NX edge validation | **Not implemented.** No `edge/jetson_benchmark.py`, no hardware-in-loop measurements. |
| Drone payload optimization (`src/darpalyft/core.py`, `data.py`, `evaluate.py` physics functions) | **Implemented and tested**, but this is a *different project* (DARPA LIFT drone payload optimization) than the continual-learning research described in DESIGN_DOC.md. The repository currently conflates the two. |

**Primary readiness gap**: the repository's actual code (drone payload
optimization + a small synthetic CL-metrics toy module) does not implement the
core experimental program in DESIGN_DOC.md (LYFT-Bench, the 6 CL methods, Pareto
analysis, task-order study, or Jetson deployment). A paper claiming the design
doc's headline result (2x FTR improvement, Pareto-dominant Meta-CL) cannot yet
be written with real evidence.

## 5. Future Work / Next Steps

1. Decide and document which project this repository is for (drone payload
   optimization vs. DARPA LYFT continual learning) -- currently the README and
   DESIGN_DOC.md describe two unrelated projects under one name.
2. If continuing the CL research direction: implement at least Fine-tuning and
   EWC as real trainable baselines on one real (even if small/public) dataset,
   to replace the current synthetic-curve stand-ins.
3. Implement the steps-to-criterion FTR formula and Edge Efficiency Score as
   specified in DESIGN_DOC.md; currently only accuracy-based proxies exist.
4. Build LYFT-Bench incrementally -- start with 1-2 of the 6 proposed domains
   using public/synthetic data per the design doc's data-sensitivity mitigation.
5. Defer Jetson Orin NX validation until server-side method comparisons (Exp 1)
   are real; do not report edge numbers without hardware-in-loop measurement.

## References (to fill in)

- Lopez-Paz & Ranzato, "Gradient Episodic Memory for Continual Learning" (GEM), NeurIPS 2017.
- Kirkpatrick et al., "Overcoming catastrophic forgetting in neural networks" (EWC), PNAS 2017.
- Rebuffi et al., "iCaRL: Incremental Classifier and Representation Learning", CVPR 2017.
- Finn et al., "Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks" (MAML), ICML 2017.
