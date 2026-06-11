# Research Design Document: DARPA LYFT

## Vision Statement

Demonstrate that **meta-continual learning** enables AI models to continuously acquire new tactical and logistics knowledge without catastrophic forgetting, achieving a **2× improvement in forward transfer** over standard fine-tuning baselines, and validating deployment-readiness on edge hardware (Jetson Orin NX) — establishing a practical blueprint for lifelong learning systems in defense and logistics applications.

---

## Problem Statement & Novelty

Continual learning (CL) is well-studied in academic settings, but DARPA LYFT-relevant deployment scenarios introduce challenges that existing benchmarks (Split CIFAR, Permuted MNIST) do not capture:

1. **Task heterogeneity**: Real-world knowledge updates are irregular, task-order-dependent, and include rare but critical knowledge (new threat signatures, logistics exceptions).
2. **Edge deployment constraints**: Models must run on embedded hardware (Jetson Orin NX, ~21 TOPS) with strict latency and power budgets, ruling out large replay buffers.
3. **Forward transfer neglect**: Most CL research minimizes forgetting (backward interference) but ignores forward transfer (does prior knowledge help learn new tasks faster?).
4. **No realistic defense/logistics benchmark**: Existing CL benchmarks use academic datasets; mission-relevant tasks require specialized evaluation.

### Novel Contributions

| Contribution | Description |
|---|---|
| **LYFT-Bench** | 6-domain continual learning benchmark for defense/logistics knowledge acquisition |
| **FTR metric** | Forward Transfer Rate: how much faster new tasks are learned given prior task experience |
| **Meta-CL framework** | MAML-based meta-learning optimized for CL on edge hardware |
| **Edge efficiency score** | Composite of accuracy, latency, and power consumption on Jetson Orin NX |
| **Forgetting-transfer Pareto analysis** | First systematic analysis of forgetting vs. forward transfer tradeoff across CL methods |

### Key Metrics

```
FTR = (steps_to_criterion_no_prior - steps_to_criterion_with_prior) / steps_to_criterion_no_prior

  FTR > 0: positive forward transfer (prior knowledge helps)
  FTR < 0: negative forward transfer (prior knowledge hurts)
  Target: FTR ≥ 0.50 for our meta-CL method

Forgetting = mean(acc_at_end_of_task_k - acc_at_task_k) over all k
  Lower is better

Edge Efficiency Score = Accuracy × (budget_ms / P95_latency) × (budget_watts / P95_power)
```

---

## Research Objectives

1. Benchmark **6 continual learning methods** on LYFT-Bench across forgetting, forward transfer, and edge efficiency.
2. Demonstrate that **meta-CL** achieves FTR ≥ 0.50 — 2× higher than standard fine-tuning (FTR ≈ 0.25).
3. Characterize the **forgetting-transfer Pareto frontier**: is there a fundamental tradeoff, or can both be optimized simultaneously?
4. Validate **edge deployment**: measure inference latency, power, and memory on Jetson Orin NX under operational constraints.
5. Identify **task order effects**: does the sequence of knowledge acquisition matter, and how much?

---

## Dataset Construction (LYFT-Bench)

### 6 Domains for Continual Learning

| Domain | Task | Data Size | Notes |
|---|---|---|---|
| Threat classification | Image classification (aerial) | 5K images | Rare class injection |
| Logistics route optimization | Graph prediction | 2K routes | Dynamic graph structure |
| Sensor fusion | Time-series classification | 8K sequences | Multi-modal |
| Natural language orders | NLU classification | 3K orders | Military terminology |
| Equipment anomaly detection | Anomaly detection | 4K time series | Imbalanced |
| Terrain analysis | Semantic segmentation | 1K images | Domain shift |

### Task Sequence Design

```
Sequence A (forward transfer optimized): 
  Threat classification → Sensor fusion → Terrain analysis → ...
  (tasks with shared visual features ordered together)

Sequence B (adversarial): 
  NL orders → Threat classification → Logistics → ...
  (maximally dissimilar tasks to stress forgetting)
  
Sequence C (mission-realistic):
  Interleaved based on realistic deployment timeline
```

---

## Continual Learning Methods Compared

| Method | Type | Replay | Edge-Feasible | Notes |
|---|---|---|---|---|
| Fine-tuning | Naïve | No | Yes | Catastrophic forgetting baseline |
| EWC | Regularization | No | Yes | Elastic Weight Consolidation |
| iCaRL | Replay | Small buffer | Marginal | Exemplar replay |
| GEM | Replay | Small buffer | Marginal | Gradient projection |
| MAML (meta) | Meta-learning | No | Yes | Model-Agnostic Meta-Learning |
| Meta-CL (ours) | Meta + regularization | No | Yes | Our proposed method |

---

## Experimental Design

### Baseline Experiment (Experiment 0)
**Protocol**: Fine-tuning (naïve) on all 6 LYFT-Bench domains in Sequence A. Compute final accuracy, forgetting, FTR.

**Expected result**: Final accuracy ≈ 0.72 (only last task well-learned), forgetting ≈ 0.31, FTR ≈ 0.24. Establishes the catastrophic forgetting problem baseline.

---

### Experiment 1: CL Method Comparison
**Hypothesis**: Meta-CL achieves the best forgetting-FTR tradeoff: forgetting < 0.10 AND FTR > 0.50.

**Protocol**:
1. Run all 6 CL methods on Sequence A (standard order).
2. Compute after each task: accuracy on all previous tasks, FTR for current task.
3. Final metrics: mean accuracy, forgetting, FTR.
4. Statistical test: Wilcoxon signed-rank test comparing Meta-CL vs. each baseline.

**Expected results**:

| Method | Mean Accuracy | Forgetting | FTR | Edge-Feasible |
|---|---|---|---|---|
| Fine-tuning | 0.72 | 0.31 | 0.24 | Yes |
| EWC | 0.79 | 0.19 | 0.31 | Yes |
| iCaRL | 0.82 | 0.14 | 0.38 | Marginal |
| GEM | 0.83 | 0.12 | 0.41 | Marginal |
| MAML | 0.80 | 0.16 | 0.48 | Yes |
| Meta-CL (ours) | 0.86 | 0.09 | 0.54 | Yes |

- Meta-CL achieves best FTR (0.54) AND best forgetting (0.09) simultaneously — Pareto-dominant.

---

### Experiment 2: Forgetting-Transfer Pareto Analysis
**Hypothesis**: There is a fundamental tradeoff between forgetting and forward transfer; Meta-CL pushes the Pareto frontier by using task structure rather than replay.

**Protocol**:
1. Sweep regularization strength (λ) for EWC and Meta-CL to trace their Pareto curves.
2. Plot forgetting vs. FTR for all methods at all hyperparameter settings.
3. Compute Pareto front; measure Meta-CL's distance from optimal.

**Expected results**:
- EWC Pareto curve: strong regularization kills forgetting but reduces FTR; weak regularization reverses this.
- Meta-CL Pareto curve: dominates EWC at all operating points (same forgetting, higher FTR).
- Key finding: meta-learning escapes the forgetting-transfer tradeoff by learning task structure, not just regularizing weights.

---

### Experiment 3: Task Order Effects
**Hypothesis**: Task order accounts for ≥15 pp variance in final accuracy; Sequence A (transfer-optimized) significantly outperforms Sequence B (adversarial).

**Protocol**:
1. Run all methods on Sequences A, B, and C.
2. Compute mean accuracy variance across sequences per method.
3. Test: is Meta-CL more order-robust than EWC?

**Expected results**:
- Fine-tuning sequence variance: σ = 0.18 (high order sensitivity)
- EWC sequence variance: σ = 0.11
- Meta-CL sequence variance: σ = 0.07 (most order-robust)
- Sequence A vs. B gap (fine-tuning): 22 pp accuracy
- Sequence A vs. B gap (Meta-CL): 8 pp accuracy

---

### Experiment 4: Edge Deployment Validation
**Hypothesis**: Meta-CL achieves Edge Efficiency Score ≥ 0.80 on Jetson Orin NX under 50ms latency and 10W power constraints.

**Protocol**:
1. Deploy all edge-feasible methods (Fine-tuning, EWC, MAML, Meta-CL) on Jetson Orin NX.
2. Measure: inference latency (P50, P95), power consumption, memory usage.
3. Compute Edge Efficiency Score for each method.
4. Test: does Meta-CL's higher accuracy compensate for any latency overhead vs. simpler methods?

**Expected results**:

| Method | P95 Latency | Power | Edge Score |
|---|---|---|---|
| Fine-tuning | 28ms | 7.2W | 0.69 |
| EWC | 29ms | 7.4W | 0.77 |
| MAML | 32ms | 8.1W | 0.80 |
| Meta-CL (ours) | 34ms | 8.5W | 0.83 |

- Meta-CL meets 50ms and 10W constraints with margin.
- Higher accuracy more than compensates for small latency overhead.

---

### Experiment 5: Meta-CL Ablation
**Hypothesis**: Both the meta-learning component and the task-structure regularization are necessary; removing either reduces FTR by ≥10 pp.

**Protocol**:
1. Ablate Meta-CL: (a) meta-learning only, (b) regularization only, (c) full Meta-CL.
2. Measure FTR and forgetting for each variant.

**Expected results**:
- Meta-learning only: FTR = 0.47, forgetting = 0.13
- Regularization only: FTR = 0.36, forgetting = 0.10
- Full Meta-CL: FTR = 0.54, forgetting = 0.09
- Both components are necessary and complementary.

---

## Expected Results Summary

| Metric | Baseline (EWC) | Meta-CL | Improvement |
|---|---|---|---|
| Mean accuracy | 0.79 | 0.86 | +7 pp |
| Forgetting | 0.19 | 0.09 | −53% |
| FTR | 0.31 | 0.54 | +74% |
| Edge Efficiency Score | 0.77 | 0.83 | +8% |
| Order robustness (σ) | 0.11 | 0.07 | 36% lower variance |

**Primary claim**: Meta-CL achieves 2× higher forward transfer rate vs. EWC while simultaneously reducing forgetting by 53%, and is deployable on edge hardware with <35ms latency — making it the dominant continual learning approach for DARPA LYFT-relevant deployment scenarios.

---

## Why This Matters

**For researchers**: LYFT-Bench is the first realistic defense/logistics CL benchmark; the forgetting-transfer Pareto analysis provides the community with a new evaluation framework.

**For DARPA**: Meta-CL directly addresses LYFT program goals — AI systems that continuously learn from deployment experience without requiring full retraining.

**For edge deployment**: Validation on Jetson Orin NX demonstrates operational viability, not just academic feasibility.

**RSI connection**: A system with high FTR learns new tasks faster from prior experience — a direct instantiation of recursive self-improvement in the task-learning loop.

---

## Implementation Plan

```
research-darpalyft/
├── data/
│   ├── lyft_bench/      # 6 domain datasets
│   └── task_sequences/  # Sequences A, B, C definitions
├── methods/
│   ├── fine_tuning.py
│   ├── ewc.py
│   ├── maml.py
│   └── meta_cl.py       # Our proposed method
├── metrics/
│   ├── ftr.py
│   ├── forgetting.py
│   └── edge_efficiency.py
├── edge/
│   └── jetson_benchmark.py
├── experiments/
│   ├── exp0_baseline.py
│   ├── exp1_cl_comparison.py
│   ├── exp2_pareto.py
│   ├── exp3_task_order.py
│   ├── exp4_edge.py
│   └── exp5_ablation.py
```

---

## Timeline

| Phase | Duration | Deliverable |
|---|---|---|
| LYFT-Bench construction | 6 weeks | 6 domain datasets |
| Method implementation | 4 weeks | All CL methods |
| Experiments (server) | 5 weeks | All results |
| Edge validation (Jetson) | 3 weeks | Edge efficiency results |
| Paper writing | 4 weeks | ICML/NeurIPS submission |

**Target venue**: ICML 2027 or NeurIPS 2026

---

## Open Questions & Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Jetson Orin NX procurement | Medium | Order immediately; use Xavier as fallback |
| Defense domain data sensitivity | High | Use only public/synthetic data |
| MAML training instability | Medium | Second-order gradient approximations |
| Task order variance obscures results | Medium | Report mean + CI across 5 random orders |

---

## Related Issues

- RSI connection: FTR as RSI metric
- OrchestrateBench: multi-agent deployment of continual learning systems
- Reproducibility: task order randomization protocol
- Related work audit: EWC, iCaRL, GEM, MAML, Reptile
