# Multirotor Flight Testing: Clarification for DARPA Lift Challenge Team

**Submitted by:** Natan Vidra & Team Anote  
**Date:** June 11, 2026  
**Re:** DARPA Lift Challenge — Multirotor Testing & Primary Design Relationship

---

## Summary

The multirotor flight tests visible in our uploaded footage are **physics validation and calibration flights**, not demonstrations of our final competition design. These flights are a deliberate step in our AI-driven design pipeline: we use real flight data to ground-truth the physics models that our optimizer relies on before committing designs to hardware.

Our primary UAS design concept is detailed in the attached concept paper:  
**`Anote_Final_Concept_Paper.pdf`** (see `/docs/` in this repository).

---

## How Multirotor Testing Fits the Pipeline

Our design methodology proceeds in three stages:

### Stage 1 — Physics Model Calibration (Multirotor Test Flights)

We fly off-the-shelf multirotor platforms (quadcopters and hexacopters) to validate the core physics relationships our optimizer uses:

| Model Parameter | Formula | Validated Against |
|---|---|---|
| Thrust | `T = 10 × N_motors × D_prop² × throttle` | Hover thrust measurements at varying throttle |
| Payload capacity | `payload = (T / 9.81) − total_mass` | Known payload added incrementally to test vehicle |
| Structural safety factor | `mean_UTS / 100 MPa` | Load deflection of carbon fiber vs. aluminum frames under simulated payload stress |
| Thrust-to-weight ratio | `T / (mass × 9.81) ≥ 1.5` | Minimum throttle required to lift at various mass configurations |

The test vehicles are **not** the competition design. They are instrumented benches used to confirm that our simplified actuator disk model, structural equations, and feasibility constraints reflect real-world behavior before we run the optimizer at scale.

### Stage 2 — AI-Driven Design Optimization

With validated physics models, we run our optimization pipeline (`src/darpalyft/`) over a large design space:

- **Materials:** carbon fiber, aluminum alloy, titanium, fiberglass, ABS plastic
- **Motor count:** 4, 6, or 8
- **Propeller diameter:** 0.2–0.5 m
- **Battery capacity:** 400–1,200 Wh
- **Component masses:** per-component continuous variables

The optimizer maximizes `score = payload_kg / total_mass_kg` subject to all physics and structural constraints, using Pareto front analysis to surface non-dominated designs.

### Stage 3 — Primary Design Selection & Refinement

The highest-scoring feasible designs from Stage 2 feed into our primary UAS design (detailed in the concept paper). The concept paper describes the specific airframe configuration, propulsion system, and structural approach we are proposing for the competition — informed by, but distinct from, the generic multirotor test platforms.

---

## Why Test Multirotors Instead of the Final Design Directly?

Testing the final design first would conflate calibration errors with design errors. By validating physics on known, off-the-shelf platforms — where ground truth is well-characterized — we ensure our optimizer is working from accurate physical models. Only after that validation do we trust the optimizer's output as a guide for the competition design.

This approach also lets us iterate quickly: multirotor test platforms are cheap and fast to reconfigure, while the primary design involves more specialized manufacturing.

---

## Reference Documents

| Document | Location | Description |
|---|---|---|
| Concept Paper | `docs/Anote_Final_Concept_Paper.pdf` | Full primary UAS design concept for DARPA Lift |
| Physics model | `src/darpalyft/core.py` | Thrust, structural, and payload calculations |
| Optimizer | `src/darpalyft/core.py` — `DesignOptimizer` | Design search and feasibility filtering |
| Evaluation metrics | `src/darpalyft/evaluate.py` | Payload-per-weight scoring and Pareto analysis |
| Optimization pipeline | `scripts/run_optimization.py` | End-to-end run script |

---

## Contact

**Natan Vidra** — natan@anote.ai  
**Anote, Inc.** — [anote.ai](https://anote.ai)
