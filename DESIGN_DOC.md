# DarpaLyft — Research Design Document

## Goal

Develop and benchmark continual learning methods that prevent catastrophic forgetting when AI systems must adapt to sequential tactical domain shifts — establishing both the benchmark and a practical CL method that maintains performance on all prior domains while achieving near-from-scratch performance on new domains.

## Objective

1. Build a CL benchmark using sequences of tactical-environment-inspired domain shifts (weather, terrain, adversary doctrine, sensor modality)
2. Evaluate 6+ established CL methods (EWC, PackNet, A-GEM, ER, ER-ACE, DER++) on this benchmark under cloud and edge hardware constraints
3. Propose and evaluate a meta-continual learning approach that uses prior domain shifts to accelerate adaptation to new ones

## Background / Motivation

Deployed tactical AI systems face continuous distribution shift: a model trained on desert terrain must adapt to jungle terrain without forgetting desert performance. Standard fine-tuning catastrophically forgets: adapting to domain B erases domain A performance. Standard CL benchmarks (Split-CIFAR, Permuted MNIST) use artificial task boundaries that don't represent real-world domain shifts.

## Experimental Design

### Baseline Experiment

**Evaluate sequential fine-tuning (no CL) on a 5-domain tactical sequence: terrain classification across desert → jungle → arctic → urban → underwater**

- Metric: Average Accuracy (AA) across all 5 domains; Backward Transfer (BWT) = forgetting of earlier domains
- Purpose: quantify the catastrophic forgetting baseline
- Expected result: fine-tuning achieves ~85% on current domain but BWT ≈ −50% by domain 5

### Test Experiment 1: CL Method Comparison

Evaluate 6 CL methods: EWC, PackNet, A-GEM, ER-Reservoir, DER++, and proposed Task-Conditioned LoRA. Metrics: AA, BWT, FWT, model size (parameters), inference latency on edge hardware.

**Expected result:** Task-Conditioned LoRA matches or exceeds DER++ on AA and BWT while using 40% fewer parameters — the only method that works within the edge hardware 4GB RAM constraint

### Test Experiment 2: Meta-Continual Learning for Faster Adaptation

After training on domains 1–4, test meta-learning for domain 5 adaptation. Use MAML-style meta-training over the first 4 domain transitions to learn a "how to adapt" prior. Measure: how many labeled domain-5 examples are needed to reach 80% accuracy?

**Expected result:** meta-CL reduces the labeled-example requirement for new domain adaptation by 60–80%

### Test Experiment 3: Edge Hardware Validation

Deploy Task-Conditioned LoRA on Jetson Orin NX (16GB RAM, 20W power envelope). Measure: inference latency, memory footprint, adaptation time for 100 new-domain examples.

**Expected result:** Task-Conditioned LoRA adapts to a new domain in <5 minutes on Jetson Orin NX — within field adaptation time budget

## Expected Results

1. A 5-domain tactical CL benchmark using realistic remote sensing distribution shifts
2. CL method comparison table: AA, BWT, FWT, model size, latency across 6 methods
3. Meta-CL result: 60–80% reduction in labeled-example requirement
4. **Key finding:** "Task-Conditioned LoRA is the first CL method that achieves competitive accuracy AND fits on edge hardware"
5. Recommended deployment architecture with specific hardware thresholds

## Why This Matters / Why People Would Care

- **Defense AI programs:** tactical AI systems must work across environments; catastrophic forgetting is a known failure mode with no current solution
- **DARPA LYFT program office:** meta-CL directly addresses the program goal of rapid adaptation with few labeled examples
- **CL research community:** the tactical domain shift benchmark is more realistic than existing benchmarks
- **Edge ML practitioners** (robotics, autonomous vehicles): edge-hardware-constrained CL is underexplored; findings apply outside defense

## Timeline

| Month | Milestone |
|---|---|
| 1 | Benchmark construction (5-domain tactical sequence from public datasets) |
| 2 | CL method implementation and initial comparison |
| 3 | Meta-CL implementation and labeled-data efficiency experiment |
| 4 | Jetson edge hardware validation |
| 5 | Analysis + 5-seed variance experiments |
| 6 | Submission to ICML 2027 or NeurIPS 2026 |

## Related Issues

- Design doc GitHub issue: #18
- RSI connection issue: #17
- Target conferences: see issues labeled `conference-prep`
- Reproducibility package: see issues labeled `artifact-release`
